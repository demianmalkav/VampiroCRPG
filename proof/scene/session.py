"""Player projection and a small, transactional presentation adapter."""
import copy
import json
import uuid

from proof.m2.world import InvalidSnapshot, Rejected, canonical
from proof.m2b.scenario import prepare, run_until
from proof.m2b.world import SurvivalWorld, V0, M0

MODES = {'control': 'conservative', 'pressure': 'lethal'}
SAVE_FORMAT = 'm2-scene-envelope-1'
LOCATIONS = {'location:L_INC': 'Callejón', 'location:L_HAV': 'Refugio', 'location:L_REG': 'Archivo'}
LABELS = {'actor:V0': 'Vos', 'actor:M0': 'Adulto', 'actor:W1': 'Testigo', 'actor:G1': 'Contacto', 'actor:I1': 'Investigador', 'actor:W2': 'Empleado'}
CONDITIONS = {'weak': 'Se ve débil.', 'medical_emergency': 'Muestra una emergencia médica.', 'dead': 'Ha muerto.', 'no_emergency': 'No muestra una emergencia.'}
OWN_EVENTS = {
    'NightBloodSpent': 'La noche consume un punto de sangre.',
    'FeedingStarted': 'Comenzás a alimentarte.',
    'FrenzyStarted': 'La Bestia toma el control.',
    'BloodExtracted': 'Tu reserva de sangre aumenta.',
    'VictimConditionChanged': 'Percibís un cambio en la víctima.',
    'FeedingStopped': 'Se interrumpe la alimentación.',
    'BiteWoundSealed': 'Cerrás las marcas de los colmillos; el daño permanece.',
    'WillpowerSpent': 'Gastás un punto de voluntad.',
    'LucidActionStarted': 'Tenés una acción lúcida; el episodio continúa.',
    'BeastControlResumed': 'La Bestia recupera el control.',
    'FrenzyEnded': 'Recuperás el control tras el intervalo de calma.',
    'MoralIncidentAssessed': 'Se evalúa el incidente moral.',
    'TraumaPendingSelection': 'Queda una consecuencia traumática pendiente.',
    'SleepStarted': 'Te dormís; el mundo sigue funcionando.',
    'WillpowerRecovered': 'La nueva noche recupera voluntad si hay lugar.',
    'TravelStarted': 'Iniciás el traslado.', 'TravelArrived': 'Llegás a destino.'}


def fixture_for(mode):
    if mode not in MODES:
        raise Rejected('UNKNOWN_SCENE_MODE')
    fixture = prepare(MODES[mode])
    # Only the night boundary is supplied by this harness. All later decisions
    # come from the user; no scripted escape, sleep, cleanup or case endpoint.
    fixture['external_inputs'] = fixture['external_inputs'][:1]
    return fixture


class Session:
    def __init__(self, mode='control'):
        self.reset(mode)

    def reset(self, mode):
        fixture = fixture_for(mode)
        world = run_until(SurvivalWorld(fixture), fixture, 0)
        self.mode, self.world = mode, world
        self.revision = uuid.uuid4().hex
        self.receipts = {}

    def candidates(self):
        w = self.world
        actions = {
            'feed': ('AttemptFeed', {'target': M0, 'amount': 2}, 'Alimentarte · objetivo 2'),
            'seal': ('SealBite', {'target': M0}, 'Cerrar marcas · 3 s'),
            'retreat': ('StartTravel', {'actor': V0, 'to': 'location:L_HAV'}, 'Ir al refugio · 3 s'),
            'return': ('StartTravel', {'actor': V0, 'to': 'location:L_INC'}, 'Volver al callejón · 3 s'),
            'lucid_retreat': ('LucidAction', {'action': 'MoveTo', 'target': 'location:L_HAV'}, 'Retirarte · 1 voluntad'),
            'lucid_release': ('LucidAction', {'action': 'ReleaseVictim'}, 'Soltar · 1 voluntad'),
            'lucid_wait': ('LucidAction', {'action': 'Wait'}, 'Esperar lúcidamente · 1 voluntad')}
        if 'message:DIRECTIVE' not in w.s['messages']:
            # Find the approved directive by type, not the scenario row position.
            directive = next(copy.deepcopy(r) for r in prepare('conservative')['external_inputs'] if r['type'] == 'SendMessage')
            actions['cleanup'] = ('SendMessage', {k: v for k, v in directive.items() if k not in ('type', 'tick', 'input_seq')}, 'Encargar retirar el video')
        if w.actor['location'] == 'location:L_HAV' and w.s['tick'] < 86400:
            actions['sleep'] = ('SleepUntil', {'until': 86400}, 'Dormir hasta la próxima noche')
        return actions

    def legal_actions(self):
        if self.world.s['tick'] >= 86460:
            return []
        legal = []
        for key, (kind, payload, label) in self.candidates().items():
            # Probe the actual command owner on an isolated clone. Rendering
            # neither publishes side effects nor duplicates eligibility rules.
            probe = copy.deepcopy(self.world)
            if probe.command('command:scene-probe', kind, payload)['ok']:
                legal.append({'id': key, 'label': label})
        return legal

    def view(self):
        w = self.world
        own = w.player_view()
        awake = own['availability'] not in ('asleep', 'unavailable')
        observed = None
        for memory in own['memories']:
            for feature in memory.get('features', []):
                if feature in CONDITIONS:
                    observed = feature
        visible = []
        if awake and not w.actor['travelling']:
            for key, actor in w.s['actors'].items():
                if actor['location'] == own['location'] and not actor['travelling'] and actor['availability'] not in ('asleep', 'unavailable'):
                    visible.append({'id': key, 'label': LABELS[key], 'condition': observed if key == M0 else None})
        observed_causes = {o['cause'] for o in w.s['observations'].values() if o['holder'] == V0}
        log = []
        for ev in sorted(w.s['events'].values(), key=lambda e: int(e['id'].split(':')[1])):
            if ev['type'] not in OWN_EVENTS or (ev['source'] != V0 and ev['id'] not in observed_causes):
                continue
            text = OWN_EVENTS[ev['type']]
            if ev['type'] == 'VictimConditionChanged':
                text = CONDITIONS[ev['payload']['condition']]
            elif ev['type'] == 'MoralIncidentAssessed':
                text = {'NOT_REQUIRED': 'Este incidente no exige tirada moral.', 'SUCCESS': 'Conservás Humanidad.', 'FAILURE': 'Perdés un punto de Humanidad.', 'BOTCH': 'Perdés Humanidad y Conciencia.'}[ev['payload']['result']]
            log.append({'tick': ev['tick'], 'text': text})
        for memory in own['memories']:
            if 'public_inquiry' in memory.get('features', []):
                log.append({'tick': None, 'text': 'Observaste una visita que pregunta por tu alias.' if 'alias_inquiry' in memory.get('claims', []) else 'Observaste una visita que pregunta por el incidente.'})
        for message in own['messages']:
            if 'result' in message:
                log.append({'tick': None, 'text': 'Tu contacto informa: ' + ('retiró el video original y no observó otras copias' if message['result'] == 'removed_original_no_other_copy_observed' else 'no pudo completar el encargo') + '. Esto no garantiza borrar otras pruebas.'})
        action = own['active_action']
        return {'revision': self.revision, 'mode': self.mode,
                'demonstration': 'Dados de ensayo para mostrar el frenesí.' if self.mode == 'pressure' else 'Dados reproducibles del perfil.',
                'tick': w.s['tick'], 'location': own['location'], 'location_label': LOCATIONS[own['location']],
                'travelling': w.actor['travelling'], 'availability': own['availability'],
                'blood': own['blood'], 'willpower': own['willpower'], 'humanity': own['humanity'],
                'hungry': own['hungry'], 'governance': own['governance'],
                'action_until': action['until'] if action else None,
                'visible': visible, 'camera_visible': awake and not w.actor['travelling'] and own['location'] == 'location:L_INC',
                'warnings': own['warnings'], 'log': log, 'actions': self.legal_actions()}

    def save(self):
        # This is an intentionally private save, never an ordinary view response.
        return canonical({'format': SAVE_FORMAT, 'mode': self.mode, 'world': json.loads(self.world.snapshot())})

    def mutate(self, request):
        if not isinstance(request, dict) or set(request) - {'revision', 'request_id', 'action', 'mode', 'snapshot'}:
            raise Rejected('INVALID_REQUEST')
        request_id = request.get('request_id')
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 80:
            raise Rejected('INVALID_REQUEST_ID')
        identity = canonical(request)
        prior = self.receipts.get(request_id)
        if prior:
            if identity != prior['identity']:
                raise Rejected('REQUEST_ID_COLLISION')
            return copy.deepcopy(prior['result'])
        if request.get('revision') != self.revision:
            raise Rejected('STALE_VIEW')
        action = request.get('action')
        if action == 'reset':
            self.reset(request.get('mode', self.mode))
        elif action == 'load':
            text = request.get('snapshot')
            if not isinstance(text, str):
                raise InvalidSnapshot('INVALID_SAVE')
            # Reuse the strict duplicate-key/NaN parser and B validator for the
            # inner save. Outer envelope is likewise parsed without ambiguity.
            def unique(pairs):
                obj = {}
                for k, v in pairs:
                    if k in obj: raise InvalidSnapshot('DUPLICATE_JSON_KEY')
                    obj[k] = v
                return obj
            data = json.loads(text, object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(InvalidSnapshot('INVALID_CONSTANT')))
            if not isinstance(data, dict) or set(data) != {'format','mode','world'} or data['format'] != SAVE_FORMAT:
                raise InvalidSnapshot('INCOMPATIBLE_SCENE_SAVE')
            candidate = SurvivalWorld(fixture_for(data['mode']))
            candidate.load(canonical(data['world']))
            self.world, self.mode = candidate, data['mode']
            self.revision = uuid.uuid4().hex
        else:
            if self.world.s['tick'] >= 86460:
                raise Rejected('SCENE_TIME_LIMIT')
            candidate = copy.deepcopy(self.world)
            if action in ('advance', 'minute', 'wake'):
                if action == 'minute' and (candidate.feeding() or candidate.actor['governance'] != 'NORMAL'):
                    raise Rejected('USE_SHORT_STEPS')
                if action == 'wake' and candidate.actor['availability'] != 'asleep':
                    raise Rejected('NOT_ASLEEP')
                destination = 86400 if action == 'wake' else (min(86460, candidate.s['tick'] + 60) if action == 'minute' else candidate.s['tick'] + 3)
                if destination > 86460:
                    raise Rejected('SCENE_TIME_LIMIT')
                candidate.advance_to(destination)
            else:
                definition = self.candidates().get(action)
                if not definition:
                    raise Rejected('UNKNOWN_SCENE_ACTION')
                kind, payload, _ = definition
                row = dict(tick=candidate.s['tick'], input_seq=candidate.s['input_cursor'] + 1, type=kind, **payload)
                result = candidate.apply_input(row)
                if not result['ok']:
                    raise Rejected(result['reason'])
            self.world = candidate
            self.revision = uuid.uuid4().hex
        result = self.view()
        self.receipts[request_id] = {'identity': identity, 'result': copy.deepcopy(result)}
        if len(self.receipts) > 256:
            del self.receipts[next(iter(self.receipts))]
        return result
