"""Survival owners layered on the existing transactional causal world.

Only the approved narrow profile is claimed. Unsupported contexts reject
atomically. No renderer, LLM, clock, expected outcome or mission-stage setter.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from proof.m2.world import (World, Rejected, InvalidSnapshot, canonical,
                            SCHEMA as A_SCHEMA, CONTRACT as A_CONTRACT,
                            RUNTIME as A_RUNTIME, PROFILE as A_PROFILE)
from .rules import ALGORITHM, classify, draw

SCHEMA = 'm2-b-proof-json-1'
CONTRACT = 'm2-b-0.1'
RUNTIME = 'm2-b-python-proof-1'
PROFILE = 'm2-b-proof-profile-1'
RULE_FILE = Path(__file__).resolve().parents[2] / 'tests/specs/m2_core_b_profile.json'
V0 = 'actor:V0'
M0 = 'actor:M0'


class SurvivalWorld(World):
    def __init__(self, fixture):
        if fixture['fixture_version'] != PROFILE:
            raise Rejected('INCOMPATIBLE_PROFILE')
        rules = json.loads(RULE_FILE.read_text(encoding='utf-8'))
        if rules['status'] != 'APPROVED_FOR_PROOF' or rules['profile_version'] != PROFILE:
            raise Rejected('RULES_NOT_APPROVED')
        self._rule_hash = hashlib.sha256(canonical(rules).encode()).hexdigest()
        identity = {k: v for k, v in fixture.items() if k not in ('expected', 'coverage')}
        self._fixture_hash = hashlib.sha256(canonical(identity).encode()).hexdigest()
        base = copy.deepcopy(fixture)
        base['fixture_version'] = A_PROFILE
        self._building = True
        super().__init__(base)
        self.s.update(schema=SCHEMA, contract=CONTRACT, runtime=RUNTIME, profile_version=PROFILE)
        self.s['config'].update(survival_rules=rules, rules_hash=self._rule_hash,
                                fixture_hash=self._fixture_hash, harness=fixture.get('harness', False),
                                test_vectors=copy.deepcopy(fixture.get('test_vectors', {})))
        self._config_hash = hashlib.sha256(canonical(self.s['config']).encode()).hexdigest()
        self.s['rng'] = dict(algorithm=ALGORITHM, seed_hex=rules['rng']['seed_hex'],
                             streams={s: 0 for s in rules['rng']['streams']}, vector_cursors={})
        defaults = rules['vampire']
        v = {k: defaults[k] for k in ('generation', 'blood_capacity', 'self_control', 'humanity',
                                      'conscience', 'willpower_rating', 'willpower_current')}
        v['blood_current'] = defaults['blood_before_night_cost']
        v.update(fixture.get('vampire_initial', {}))
        actor = self.s['actors'][V0]
        actor.update(vampire=v, governance='NORMAL', episode=None, feeding=None, action=None,
                     night_id=None, night_receipts={}, wake_receipts={})
        actor['initial_vampire'] = copy.deepcopy(v)
        self._initial_vampire = copy.deepcopy(v)
        vessel = dict(capacity=rules['vessel']['capacity'], blood_current=fixture.get('vessel_initial_blood', 10),
                      accessible=fixture.get('vessel_accessible', True), nonresisting=True, punctures_open=False)
        vessel['initial_blood'] = vessel['blood_current']
        self._initial_vessel_blood = vessel['initial_blood']
        self.s['actors'][M0].update(vessel=vessel)
        self._update_condition(M0)
        self.schedule('NightBoundary', 0, {'night_id': 'night:1'}, V0, [])
        self.schedule('NightBoundary', rules['time']['next_night_starts'], {'night_id': 'night:2'}, V0, [])
        self._building = False
        self.validate(self.s)

    @property
    def rules(self):
        return self.s['config']['survival_rules']

    @property
    def vampire(self):
        return self.s['actors'][V0]['vampire']

    @property
    def actor(self):
        return self.s['actors'][V0]

    def hungry(self):
        return self.vampire['blood_current'] < max(0, 7 - self.vampire['self_control'])

    def episode(self):
        key = self.actor['episode']
        return self.s['processes'].get(key) if key else None

    def feeding(self):
        key = self.actor['feeding']
        p = self.s['processes'].get(key) if key else None
        return p if p and p['state'] == 'ACTIVE' else None

    def check(self, system, pool, difficulty, causes):
        if type(pool) is not int or pool < 1:
            raise Rejected('UNSUPPORTED_EMPTY_POOL')
        stream = V0 + '/' + system
        vectors = self.s['config']['test_vectors'].get(system, [])
        cursor = self.s['rng']['vector_cursors'].get(stream, 0)
        before = self.s['rng']['streams'][stream]
        if self.s['config']['harness'] and cursor < len(vectors):
            dice = vectors[cursor]
            if len(dice) != pool:
                raise Rejected('TEST_VECTOR_POOL_MISMATCH')
            self.s['rng']['vector_cursors'][stream] = cursor + 1
            mode = 'TEST_VECTOR'
        else:
            dice = []
            for _ in range(pool):
                die, after = draw(self.s['rng']['seed_hex'], stream, self.s['rng']['streams'][stream])
                self.s['rng']['streams'][stream] = after
                dice.append(die)
            mode = 'RNG'
        result = classify(dice, difficulty)
        result.update(system=system, pool=pool, stream=stream, mode=mode,
                      algorithm=ALGORITHM, seed_hex=self.s['rng']['seed_hex'],
                      counter_before=before, counter_after=self.s['rng']['streams'][stream])
        if mode == 'TEST_VECTOR':
            result['vector_index'] = cursor
        ev = self.event('CheckResolved', V0, causes=causes, payload=result)
        return result, ev

    def _available(self):
        if self.actor['availability'] in ('asleep', 'unavailable') or self.actor['travelling']:
            raise Rejected('ACTOR_UNAVAILABLE')
        if self.actor['night_id'] is None:
            raise Rejected('NIGHT_NOT_STARTED')

    def _normal(self):
        self._available()
        if self.actor['governance'] not in ('NORMAL', 'RESISTING'):
            raise Rejected('BEAST_OWNS_ACTION')
        if self.actor['action'] or self.feeding():
            raise Rejected('ACTION_BUSY')

    def _source(self, target, *, feeding=True):
        a = self.get('actors', target)
        if 'vessel' not in a:
            raise Rejected('UNSUPPORTED_SOURCE')
        v = a['vessel']
        self._available()
        if (a['location'] != self.actor['location'] or a['travelling'] or not v['accessible']
                or a['availability'] == 'unavailable' or not v['nonresisting']):
            raise Rejected('SOURCE_INACCESSIBLE')
        if feeding and (v['blood_current'] == 0 or self.vampire['blood_current'] >= self.vampire['blood_capacity']):
            raise Rejected('SOURCE_EMPTY_OR_VAMPIRE_FULL')
        return a

    def _cancel(self, predicate, cause):
        retained = []
        for item in self.s['queue']:
            if predicate(item):
                self.event('WorkCancelled', item['owner'], causes=[cause, *item['causes']],
                           payload={'work_id': item['id'], 'kind': item['kind']})
            else:
                retained.append(item)
        self.s['queue'] = retained

    def _dispatch_command(self, kind, p, harness):
        if kind == 'InjectResolvedIncident':
            raise Rejected('RESOLVED_INCIDENT_NOT_ALLOWED_IN_B')
        if kind == 'NightStarted':
            return self.night_started(p['night_id'])
        if kind == 'Wake':
            return self.wake(p['night_id'])
        if kind in ('Sleep', 'SleepUntil'):
            self._normal()
            if kind == 'SleepUntil':
                until = p['until']
                if type(until) is not int or until <= self.s['tick']:
                    raise Rejected('INVALID_SLEEP_BOUNDARY')
            ev = self.event('SleepStarted', V0)
            self.actor['availability'] = 'asleep'
            if kind == 'SleepUntil':
                night_id = 'night:' + str(p['until'] // self.rules['time']['next_night_starts'] + 1)
                self.schedule('WakeBoundary', p['until'], {'night_id': night_id}, V0, [ev])
            return {'ok': True, 'events': [ev]}
        if kind == 'AttemptFeed':
            self._normal()
            return self.start_feed(p['target'], p.get('amount', self.rules['feeding']['conservative_target']))
        if kind == 'SealBite':
            self._normal()
            return self.start_action('SealBite', p['target'])
        if kind == 'LucidAction':
            return self.lucid(p)
        if kind == 'AssessMoral':
            if p.get('use_willpower'):
                raise Rejected('WILLPOWER_FORBIDDEN_FOR_DEGENERATION')
            incident = self.get('processes', p['incident'])
            if incident['type'] != 'moral_incident' or incident['state'] != 'CLOSED':
                raise Rejected('MORAL_INCIDENT_NOT_CLOSED')
            ev = self.assess(incident)
            return {'ok': True, 'events': [ev] if ev else []}
        if kind in ('ObserveBlood', 'WithdrawBloodStimulus', 'SeedMoralFacts'):
            if not harness or not self.s['config']['harness']:
                raise Rejected('HARNESS_ONLY')
            if kind == 'SeedMoralFacts':
                key = self.alloc('process')
                ev = self.event('HarnessMoralFacts', V0, [p['target']], payload={'context': p['context']})
                inc = self.put('processes', dict(id=key, type='moral_incident', owner=V0,
                              target=p['target'], state='CLOSED', started_by=ev, refs=[V0, p['target'], ev],
                              context=p['context'], death=p.get('death', True), hungry_at_start=p.get('hungry', True),
                              during_frenzy=p.get('during_frenzy', False), evaluated=False, close_cause=ev))
                return {'ok': True, 'events': [ev], 'incident': inc['id']}
            if kind == 'WithdrawBloodStimulus':
                ep = self.episode()
                if ep:
                    ev = self.event('BloodStimulusWithdrawn', V0, causes=[ep['started_by']])
                    ep['stimuli'] = []
                    if ep['state'] == 'RESISTED':
                        ep['state'] = 'CANCELLED'
                    return {'ok': True, 'events': [ev]}
                return {'ok': True, 'events': []}
            self._source(p['target'])
            ev = self.event('BloodStimulusObserved', V0, [p['target']], payload={'sense': p['sense']})
            self.pressure(p['target'], p['sense'], ev)
            return {'ok': True, 'events': [ev]}
        if kind == 'ChangeAvailability' and p.get('actor') == V0:
            raise Rejected('USE_SLEEP_OR_WAKE')
        if kind == 'SendMessage' and p.get('sender') == V0:
            self._normal()
        if kind in ('StartTravel', 'InspectRecord', 'RemoveRecord') and p.get('actor') == V0:
            self._normal()
        return super()._dispatch_command(kind, p, harness)

    def night_started(self, night_id):
        if night_id in self.actor['night_receipts']:
            return copy.deepcopy(self.actor['night_receipts'][night_id])
        index = self.s['tick'] // self.rules['time']['next_night_starts'] + 1
        if night_id != f'night:{index}' or self.s['tick'] % self.rules['time']['next_night_starts']:
            raise Rejected('INVALID_NIGHT_BOUNDARY')
        if self.vampire['blood_current'] < self.rules['night_boundaries']['minimum_blood_before_cost_in_supported_cases']:
            raise Rejected('UNSUPPORTED_EXHAUSTION')
        cost = self.rules['night_boundaries']['blood_cost']
        self.vampire['blood_current'] -= cost
        ev = self.event('NightBloodSpent', V0, payload={'night_id': night_id, 'amount': cost})
        self.actor['night_id'] = night_id
        result = {'ok': True, 'events': [ev]}
        self.actor['night_receipts'][night_id] = copy.deepcopy(result)
        if self.actor['availability'] == 'awake':
            self._recover_willpower(night_id, ev)
        return result

    def _recover_willpower(self, night_id, cause):
        if night_id in self.actor['wake_receipts']:
            return self.actor['wake_receipts'][night_id]
        gain = min(self.rules['night_boundaries']['wake_willpower_recovery'],
                   self.vampire['willpower_rating'] - self.vampire['willpower_current'])
        self.vampire['willpower_current'] += gain
        ev = self.event('WillpowerRecovered', V0, causes=[cause], payload={'night_id': night_id, 'amount': gain})
        self.actor['wake_receipts'][night_id] = ev
        return ev

    def wake(self, night_id):
        if night_id != self.actor['night_id']:
            raise Rejected('NIGHT_COST_NOT_COMMITTED')
        if self.actor['availability'] == 'awake':
            return {'ok': True, 'events': []}
        if self.actor['travelling'] or self.actor['action'] or self.feeding():
            raise Rejected('ACTION_BUSY')
        result = super()._dispatch_command('ChangeAvailability', {'actor': V0, 'value': 'awake'}, False)
        self._recover_willpower(night_id, result['events'][0])
        return result

    def on_NightBoundary(self, q):
        self.night_started(q['payload']['night_id'])

    def on_WakeBoundary(self, q):
        self.wake(q['payload']['night_id'])

    def _update_condition(self, target):
        a = self.s['actors'][target]
        v = a['vessel']
        loss = v['capacity'] - v['blood_current']
        r = self.rules['vessel']
        a['condition'] = ('dead' if v['blood_current'] == 0 else
                          'medical_emergency' if loss >= r['medical_emergency_loss_min'] else
                          'weak' if loss >= r['weakness_loss_min'] else 'no_emergency')

    def start_feed(self, target, amount, *, beast=False, causes=()):
        source = self._source(target)
        if self.feeding() or self.actor['action']:
            raise Rejected('ACTION_BUSY')
        if type(amount) is not int or amount <= 0 or amount > self.vampire['blood_capacity']:
            raise Rejected('INVALID_FEED_TARGET')
        if not beast and not self.hungry():
            raise Rejected('UNSUPPORTED_MORAL_CONTEXT')
        key = self.alloc('process')
        incident_key = self.alloc('process')
        proc = self.put('processes', dict(id=key, owner=V0, type='feeding', state='ACTIVE', target=target,
                         requested=amount, extracted=0, incident=incident_key, refs=[V0, target], started_by=None))
        ev = self.event('FeedingStarted', V0, [target, key], causes, {'visible_fangs': True, 'policy': 'BEAST' if beast else 'conservative'})
        proc['started_by'] = ev
        proc['refs'].append(ev)
        inc = self.put('processes', dict(id=incident_key, owner=V0, type='moral_incident', state='OPEN',
                       target=target, started_by=ev, close_cause=None, context='feeding',
                       hungry_at_start=self.hungry(), during_frenzy=False, death=False,
                       evaluated=False, refs=[V0, target, ev, key]))
        proc['refs'].append(inc['id'])
        source['vessel']['punctures_open'] = True
        self.actor['feeding'] = key
        self.schedule('FeedExtract', self.s['tick'] + 3, {'process': key}, V0, [ev])
        # First contact starts the bounded A inquiry; later contacts still
        # create perceivable memories/records, without faking a second report.
        if not self.s.get('public_feeding_published', False):
            self.observe_incident(ev, self.actor['location'], ['visible_fangs', 'anomalous_contact'])
            self.s['public_feeding_published'] = True
        else:
            content = {'features':['visible_fangs','anomalous_contact'], 'claims':['anomaly']}
            witness = self.s['actors']['actor:W1']
            if self.profile['witness_enabled'] and witness['location'] == self.actor['location']:
                seen = self.event('AdditionalContactObserved', witness['id'], causes=[ev], payload=content)
                self.learn(witness['id'], content, 'direct', seen)
            cam = self.s['devices']['device:D_CAM']
            if cam['capture_enabled'] and cam['location'] == self.actor['location']:
                captured = self.event('CameraCapturedAndArchived', cam['id'], [cam['storage']], [ev], {'channel':cam['transport']})
                self.make_record('record:FEED_'+key.split(':')[1], 'video', content, captured,
                                 source_device=cam['id'], captured_tick=self.s['tick'])
        taste = self.event('BloodStimulusObserved', V0, [target], [ev], {'sense': 'taste'})
        self.pressure(target, 'taste', taste)
        self.warn_moral([ev])
        return {'ok': True, 'events': [ev], 'process': key, 'incident': incident_key}

    def warn_moral(self, causes):
        self.event('MoralRiskWarning', V0, causes=causes,
                   payload={'text': 'Seguir alimentándote durante el frenesí puede matar y provocar degeneración. Una acción lúcida cuesta un punto de voluntad.'})

    def pressure(self, target, sense, cause):
        if sense not in self.rules['beast']['trigger_difficulties']:
            raise Rejected('UNSUPPORTED_STIMULUS')
        if not self.hungry():
            return
        ep = self.episode()
        if ep and ep['state'] in ('RESISTING', 'BEAST', 'LUCID_ACTION', 'RESISTED'):
            if ep['target'] != target:
                raise Rejected('OVERLAPPING_PRESSURE_UNSUPPORTED')
            ep['stimuli'] = sorted(set(ep['stimuli'] + [sense]))
            ep['quiet_since'] = None
            return
        key = self.alloc('process')
        ep = self.put('processes', dict(id=key, owner=V0, target=target, type='hunger_pressure',
                      started_by=cause, refs=[V0, target, cause], state='RESISTING', stimuli=[sense],
                      accumulated=0, botch=False, quiet_since=None))
        self.actor['episode'] = key
        self.actor['governance'] = 'RESISTING'
        self.resist(ep, [cause])

    def resist(self, ep, causes):
        if not self.hungry() or not ep['stimuli']:
            ep['state'] = 'CANCELLED'
            self.actor['governance'] = 'NORMAL'
            self.event('HungerPressureEnded', V0, [ep['id']], causes)
            return
        difficulty = max(self.rules['beast']['trigger_difficulties'][x] for x in ep['stimuli'])
        pool = min(self.vampire['self_control'], self.vampire['blood_current'])
        result, check = self.check('beast', pool, difficulty, causes)
        ep['accumulated'] += result['net_successes']
        if ep['accumulated'] >= self.rules['beast']['resistance_target_successes']:
            ep['state'] = 'RESISTED'
            self.actor['governance'] = 'NORMAL'
            self.event('HungerPressureResisted', V0, [ep['id']], [check])
        elif result['net_successes']:
            delay = result['net_successes'] * self.rules['beast']['partial_seconds_per_net_success']
            self.schedule('ControlRetry', self.s['tick'] + delay, {'process': ep['id']}, V0, [check])
        else:
            ep['state'] = 'BEAST'
            ep['botch'] = result['result'] == 'BOTCH'
            self.actor['governance'] = 'BEAST'
            ev = self.event('FrenzyStarted', V0, [ep['id']], [check], {'botch': ep['botch']})
            self.schedule('BeastTick', self.s['tick'] + 3, {'process': ep['id']}, V0, [ev])

    def on_ControlRetry(self, q):
        ep = self.s['processes'][q['payload']['process']]
        if ep['state'] == 'RESISTING':
            self.resist(ep, q['causes'])

    def on_FeedExtract(self, q):
        proc = self.s['processes'][q['payload']['process']]
        if proc['state'] != 'ACTIVE' or self.actor['feeding'] != proc['id']:
            return
        if self.actor['governance'] == 'LUCID_ACTION':
            raise Rejected('PARALLEL_EXTRACTION')
        try:
            source = self._source(proc['target'])
        except Rejected as exc:
            self.stop_feed(proc, str(exc), q['causes'])
            return
        v = source['vessel']
        cap = self.vampire['blood_capacity'] - self.vampire['blood_current']
        limits = [self.rules['feeding']['maximum_extraction_per_action'], v['blood_current'], cap]
        if self.actor['governance'] != 'BEAST':
            limits.append(proc['requested'] - proc['extracted'])
        amount = min(limits)
        if amount <= 0:
            self.stop_feed(proc, 'LIMIT_REACHED', q['causes'])
            return
        before_condition = source['condition']
        v['blood_current'] -= amount
        self.vampire['blood_current'] += amount
        proc['extracted'] += amount
        self._update_condition(proc['target'])
        ev = self.event('BloodExtracted', V0, [proc['target'], proc['id']], q['causes'],
                        {'amount': amount, 'retained': amount, 'government': self.actor['governance']})
        inc = self.s['processes'][proc['incident']]
        inc['refs'].append(ev)
        inc['during_frenzy'] |= self.actor['governance'] == 'BEAST'
        if source['condition'] != before_condition:
            changed = self.event('VictimConditionChanged', proc['target'], causes=[ev], payload={'condition': source['condition']})
            self.learn(V0, {'features':[source['condition']], 'claims':[]}, 'direct', changed, [proc['target']])
        inc['death'] = source['condition'] == 'dead'
        if (v['blood_current'] == 0 or self.vampire['blood_current'] == self.vampire['blood_capacity']
                or (self.actor['governance'] != 'BEAST' and proc['extracted'] >= proc['requested'])):
            self.stop_feed(proc, 'EXTRACTION_COMPLETE', [ev])
        else:
            self.schedule('FeedExtract', self.s['tick'] + 3, {'process': proc['id']}, V0, [ev])
            self.warn_moral([ev])

    def stop_feed(self, proc, reason, causes):
        if proc['state'] != 'ACTIVE':
            return
        ev = self.event('FeedingStopped', V0, [proc['id']], causes, {'reason': reason})
        proc['state'] = 'STOPPED'
        self.actor['feeding'] = None
        self._cancel(lambda q: q['kind'] == 'FeedExtract' and q['payload'].get('process') == proc['id'], ev)
        inc = self.s['processes'][proc['incident']]
        inc.update(state='CLOSED', close_cause=ev)
        inc['refs'].append(ev)
        self.schedule('MoralAssessment', self.s['tick'], {'process': inc['id']}, V0, [ev])

    def assess(self, inc):
        if inc['evaluated']:
            return inc.get('assessment_event')
        if inc['context'] not in ('feeding', 'accidental_hunger_death_outside_frenzy'):
            raise Rejected('UNSUPPORTED_MORAL_CONTEXT')
        if inc['death']:
            if inc['during_frenzy']:
                level = 4
            elif inc['hungry_at_start']:
                level = 6
            else:
                raise Rejected('UNSUPPORTED_MORAL_CONTEXT')
        else:
            level = 8
        if level > self.vampire['humanity']:
            result = 'NOT_REQUIRED'
            h_delta = c_delta = 0
            causes = [inc['close_cause']]
        else:
            roll, check = self.check('moral', self.vampire['conscience'], self.rules['morality']['difficulty'], [inc['close_cause']])
            result = roll['result']
            h_delta = -int(result != 'SUCCESS')
            c_delta = -int(result == 'BOTCH')
            if self.vampire['humanity'] + h_delta < 1 or self.vampire['conscience'] + c_delta < 1:
                raise Rejected('UNSUPPORTED_EXHAUSTED_MORAL_TRAIT')
            self.vampire['humanity'] += h_delta
            self.vampire['conscience'] += c_delta
            causes = [check]
        ev = self.event('MoralIncidentAssessed', V0, [inc['id']], causes,
                        {'level': level, 'result': result, 'humanity_delta': h_delta, 'conscience_delta': c_delta})
        inc.update(evaluated=True, assessment_event=ev, level=level, result=result)
        inc['refs'].append(ev)
        if result == 'BOTCH':
            trauma = self.event('TraumaPendingSelection', V0, [inc['id']], [ev], {'behavior': 'NOT_IMPLEMENTED'})
            inc['trauma'] = trauma
            inc['refs'].append(trauma)
        return ev

    def on_MoralAssessment(self, q):
        self.assess(self.s['processes'][q['payload']['process']])

    def _beast_sources(self):
        choices = []
        for a in self.s['actors'].values():
            if 'vessel' not in a:
                continue
            try:
                self._source(a['id'])
            except Rejected:
                continue
            choices.append(a)
        return sorted(choices, key=lambda a: (a.get('proximity', 0), a['id']))

    def on_BeastTick(self, q):
        ep = self.s['processes'][q['payload']['process']]
        if ep['state'] != 'BEAST':
            return
        if self.actor['availability'] in ('asleep', 'unavailable'):
            raise Rejected('UNSUPPORTED_UNAVAILABLE_FRENZY')
        if not self.feeding() and self.vampire['blood_current'] < self.vampire['blood_capacity']:
            sources = self._beast_sources()
            if sources:
                self.start_feed(sources[0]['id'], self.vampire['blood_capacity'], beast=True, causes=q['causes'])
        quiet = not self.hungry() and not self.feeding() and not self.actor['action']
        if not quiet:
            ep['quiet_since'] = None
        elif ep['quiet_since'] is None:
            ep['quiet_since'] = self.s['tick']
        required = self.rules['beast']['botch_calm_required_windows' if ep['botch'] else 'calm_required_windows'] * 3
        if quiet and self.s['tick'] - ep['quiet_since'] >= required:
            ep['state'] = 'ENDED'
            self.actor['governance'] = 'NORMAL'
            self.event('FrenzyEnded', V0, [ep['id']], q['causes'], {'reason': 'CALM_WINDOWS', 'seconds': required})
            return
        self.schedule('BeastTick', self.s['tick'] + 3, {'process': ep['id']}, V0, q['causes'])

    def start_action(self, kind, target=None, *, lucid=False):
        self._available()
        if self.actor['action']:
            raise Rejected('ACTION_BUSY')
        if kind == 'SealBite':
            source = self._source(target, feeding=False)
            if not source['vessel']['punctures_open']:
                raise Rejected('NO_OPEN_PUNCTURES')
        elif kind == 'MoveTo':
            self.get('locations', target)
            if self.route(self.actor['location'], target) != 3:
                raise Rejected('LUCID_ROUTE_EXCEEDS_WINDOW')
        elif kind not in ('ReleaseVictim', 'Wait'):
            raise Rejected('UNSUPPORTED_LUCID_ACTION')
        if kind == 'ReleaseVictim' and not self.feeding():
            raise Rejected('NO_FEEDING_CONTACT')
        ep = self.episode()
        if lucid:
            if not ep or ep['state'] != 'BEAST' or self.actor['governance'] != 'BEAST':
                raise Rejected('NO_ACTIVE_FRENZY')
            if self.vampire['willpower_current'] < self.rules['beast']['lucid_cost']:
                raise Rejected('WILLPOWER_UNAVAILABLE')
            self.vampire['willpower_current'] -= self.rules['beast']['lucid_cost']
            paid = self.event('WillpowerSpent', V0, [ep['id']], [ep['started_by']], {'amount': self.rules['beast']['lucid_cost']})
            ep.update(state='LUCID_ACTION', quiet_since=None)
            self.actor['governance'] = 'LUCID_ACTION'
            self._cancel(lambda q: q['kind'] == 'BeastTick' and q['payload'].get('process') == ep['id'], paid)
            causes = [paid]
        else:
            causes = []
        action_id = self.alloc('action')
        ev = self.event('LucidActionStarted' if lucid else 'ActionStarted', V0, causes=causes,
                        payload={'action': kind, 'duration': 3, 'token': action_id})
        self.actor['action'] = dict(token=action_id, kind=kind, target=target, until=self.s['tick'] + 3,
                                    lucid=lucid, started_by=ev)
        feed = self.feeding()
        if feed:
            if kind in ('ReleaseVictim', 'MoveTo', 'SealBite'):
                self.stop_feed(feed, 'LUCID_RELEASE', [ev])
            else:
                self._cancel(lambda q: q['kind'] == 'FeedExtract' and q['payload'].get('process') == feed['id'], ev)
        if kind == 'MoveTo':
            self.travel(V0, target, [ev], None)
        self.schedule('ActionComplete', self.s['tick'] + 3, {'token': action_id}, V0, [ev])
        return {'ok': True, 'events': [ev], 'token': action_id}

    def lucid(self, p):
        return self.start_action(p['action'], p.get('target'), lucid=True)

    def on_ActionComplete(self, q):
        action = self.actor['action']
        if not action or action['token'] != q['payload']['token']:
            raise Rejected('INVALID_ACTION_TOKEN')
        if action['kind'] == 'SealBite':
            source = self._source(action['target'], feeding=False)
            source['vessel']['punctures_open'] = False
            self.event('BiteWoundSealed', V0, [action['target']], q['causes'])
        ev = self.event('ActionCompleted', V0, causes=q['causes'], payload={'action': action['kind'], 'token': action['token']})
        self.actor['action'] = None
        if action['lucid']:
            ep = self.episode()
            ep['state'] = 'BEAST'
            self.actor['governance'] = 'BEAST'
            ep['quiet_since'] = self.s['tick'] if not self.hungry() and not self.feeding() else None
            self.event('BeastControlResumed', V0, [ep['id']], [ev])
            feed = self.feeding()
            if feed:
                self.schedule('FeedExtract', self.s['tick'] + 3, {'process': feed['id']}, V0, [ev])
            self.schedule('BeastTick', self.s['tick'] + 3, {'process': ep['id']}, V0, [ev])

    def dispatch_cleanup_travel(self, actor, destination, causes, process):
        task = self.s['processes'][process]
        not_before = task['directive'].get('not_before', self.s['tick'])
        if type(not_before) is not int or not_before < self.s['tick']:
            raise Rejected('INVALID_TASK_START_TIME')
        if not_before > self.s['tick']:
            task['state'] = 'accepted_waiting'
            self.schedule('CleanupDeparture', not_before, {'process': process, 'actor': actor, 'to': destination}, actor, causes)
        else:
            super().dispatch_cleanup_travel(actor, destination, causes, process)

    def on_CleanupDeparture(self, q):
        task = self.s['processes'][q['payload']['process']]
        if task['state'] != 'accepted_waiting':
            return
        try:
            self.travel(q['payload']['actor'], q['payload']['to'], q['causes'], task['id'])
        except Rejected as exc:
            self.block_task(str(exc), q['causes'])

    def on_PlanVisitAttempt(self, q):
        case = self.s['processes'].get('process:CASE')
        if not case or not case['review_support'] or 'review_cause' not in case:
            return super().on_PlanVisitAttempt(q)
        ev = self.event('VisitPlanned', 'actor:I1', [case['id'], 'location:L_INC'], [case['review_cause'], *q['causes']])
        departure = self.profile['visit_due_tick'] - self.route(self.s['actors']['actor:I1']['location'], 'location:L_INC')
        self.schedule('VisitDeparture', departure, {'process': case['id']}, 'actor:I1', [ev])
        case['state'] = 'visit_planned'
        case['refs'].append(ev)

    def on_VisitDeparture(self, q):
        case = self.s['processes'][q['payload']['process']]
        if case['state'] == 'visit_planned':
            self.travel('actor:I1', 'location:L_INC', q['causes'], None)

    def player_view(self, actor=V0):
        result = super().player_view(actor)
        if actor != V0:
            return result
        result.update(blood=self.vampire['blood_current'], hungry=self.hungry(),
                      willpower=self.vampire['willpower_current'], humanity=self.vampire['humanity'],
                      governance=self.actor['governance'], active_action=copy.deepcopy(self.actor['action']))
        if self.actor['governance'] == 'BEAST':
            result['actions'] = ['LucidAction'] if self.vampire['willpower_current'] and not self.actor['action'] else []
        elif self.actor['action'] or self.actor['availability'] in ('asleep', 'unavailable'):
            result['actions'] = []
        else:
            result['actions'] = ['Sleep', 'Wake', 'SendMessage', 'StartTravel', 'AttemptFeed', 'SealBite']
        result['warnings'] = [e['payload']['text'] for e in self.s['events'].values() if e['type'] == 'MoralRiskWarning'][-1:]
        return result

    def validate(self, s):
        if getattr(self, '_building', False):
            return super().validate(s)
        if (s['schema'], s['contract'], s['runtime'], s['profile_version']) != (SCHEMA, CONTRACT, RUNTIME, PROFILE):
            raise InvalidSnapshot('INCOMPATIBLE_B_VERSION')
        base = dict(s, schema=A_SCHEMA, contract=A_CONTRACT, runtime=A_RUNTIME, profile_version=A_PROFILE)
        super().validate(base)
        config = s['config']
        if (config['rules_hash'] != self._rule_hash or config['fixture_hash'] != self._fixture_hash
                or hashlib.sha256(canonical(config['survival_rules']).encode()).hexdigest() != self._rule_hash
                or hashlib.sha256(canonical(config).encode()).hexdigest() != self._config_hash):
            raise InvalidSnapshot('INCOMPATIBLE_B_RULES_OR_CASE')
        a = s['actors'][V0]
        v = a['vampire']
        for key, value in v.items():
            if type(value) is not int:
                raise InvalidSnapshot('INVALID_VAMPIRE_TRAIT')
        if (not 1 <= v['blood_current'] <= v['blood_capacity'] or not 1 <= v['self_control'] <= 5
                or not 1 <= v['humanity'] <= 10 or not 1 <= v['conscience'] <= 5
                or not 0 <= v['willpower_current'] <= v['willpower_rating'] <= 10):
            raise InvalidSnapshot('INVALID_VAMPIRE_RESOURCES')
        es = list(s['events'].values())
        def total(kind, field):
            return sum(e['payload'][field] for e in es if e['type'] == kind and e['source'] == V0)
        initial = a['initial_vampire']
        if initial != self._initial_vampire or any(v[k] != initial[k] for k in ('generation','blood_capacity','self_control','willpower_rating')):
            raise InvalidSnapshot('IMMUTABLE_TRAIT_OR_OPENING_LEDGER_CHANGED')
        if v['generation'] != 13 or v['blood_capacity'] != self.rules['vampire']['blood_capacity']:
            raise InvalidSnapshot('UNSUPPORTED_GENERATION_PROFILE')
        if (v['blood_current'] != initial['blood_current'] + total('BloodExtracted', 'retained') - total('NightBloodSpent', 'amount')
                or v['willpower_current'] != initial['willpower_current'] - total('WillpowerSpent', 'amount') + total('WillpowerRecovered', 'amount')
                or v['humanity'] != initial['humanity'] + total('MoralIncidentAssessed', 'humanity_delta')
                or v['conscience'] != initial['conscience'] + total('MoralIncidentAssessed', 'conscience_delta')):
            raise InvalidSnapshot('RESOURCE_LEDGER_MISMATCH')
        for source in s['actors'].values():
            if 'vessel' not in source:
                continue
            vessel = source['vessel']
            if vessel['capacity'] != self.rules['vessel']['capacity'] or vessel['initial_blood'] != self._initial_vessel_blood:
                raise InvalidSnapshot('OPENING_SOURCE_LEDGER_CHANGED')
            if type(vessel['blood_current']) is not int or not 0 <= vessel['blood_current'] <= vessel['capacity']:
                raise InvalidSnapshot('INVALID_SOURCE_BLOOD')
            extracted = sum(e['payload']['amount'] for e in es if e['type'] == 'BloodExtracted' and source['id'] in e['targets'])
            if vessel['blood_current'] != vessel['initial_blood'] - extracted:
                raise InvalidSnapshot('SOURCE_LEDGER_MISMATCH')
            loss = vessel['capacity'] - vessel['blood_current']
            expected = ('dead' if vessel['blood_current'] == 0 else 'medical_emergency' if loss >= 5 else 'weak' if loss >= 3 else 'no_emergency')
            if source['condition'] != expected:
                raise InvalidSnapshot('VICTIM_CONDITION_MISMATCH')
            if any(e['payload']['amount'] != e['payload']['retained'] or not 1 <= e['payload']['amount'] <= 3 for e in es if e['type'] == 'BloodExtracted'):
                raise InvalidSnapshot('INVALID_BLOOD_TRANSFER')
        for key in ('episode', 'feeding'):
            if a[key] is not None and a[key] not in s['processes']:
                raise InvalidSnapshot('MISSING_SURVIVAL_REFERENCE')
        if a['governance'] not in ('NORMAL', 'RESISTING', 'BEAST', 'LUCID_ACTION'):
            raise InvalidSnapshot('INVALID_GOVERNANCE')
        episode = s['processes'].get(a['episode'])
        if a['governance'] in ('RESISTING', 'BEAST', 'LUCID_ACTION') and (not episode or episode['state'] != a['governance']):
            raise InvalidSnapshot('GOVERNANCE_EPISODE_MISMATCH')
        if episode and episode['state'] in ('RESISTING','BEAST','LUCID_ACTION') and a['governance'] != episode['state']:
            raise InvalidSnapshot('GOVERNANCE_EPISODE_MISMATCH')
        action = a['action']
        if action and (action['started_by'] not in s['events'] or action['until'] < s['tick']
                       or (action['target'] is not None and action['target'] not in {*s['actors'], *s['locations']})):
            raise InvalidSnapshot('INVALID_ACTION_RESERVATION')
        if a['governance'] == 'LUCID_ACTION' and (not action or not action['lucid']):
            raise InvalidSnapshot('MISSING_LUCID_RESERVATION')
        completions = [q for q in s['queue'] if q['kind'] == 'ActionComplete']
        if action:
            if (len(completions) != 1 or completions[0]['payload']['token'] != action['token']
                    or completions[0]['due_tick'] != action['until']
                    or (action['lucid'] and a['governance'] != 'LUCID_ACTION')):
                raise InvalidSnapshot('ACTION_FUTURE_MISMATCH')
        elif completions:
            raise InvalidSnapshot('ORPHAN_ACTION_FUTURE')
        feeds = [p for p in s['processes'].values() if p['type'] == 'feeding' and p['state'] == 'ACTIVE']
        if len(feeds) > 1 or (feeds and feeds[0]['id'] != a['feeding']):
            raise InvalidSnapshot('PARALLEL_FEEDING')
        extractions = [q for q in s['queue'] if q['kind']=='FeedExtract']
        expected_count = int(bool(feeds) and a['governance'] != 'LUCID_ACTION')
        if len(extractions) != expected_count or (extractions and extractions[0]['payload']['process'] != a['feeding']):
            raise InvalidSnapshot('FEEDING_FUTURE_MISMATCH')
        for proc in s['processes'].values():
            if proc['type'] in ('feeding', 'moral_incident', 'hunger_pressure'):
                if proc['target'] not in s['actors']:
                    raise InvalidSnapshot('MISSING_VESSEL_TARGET')
                if proc['type'] == 'feeding' and proc['incident'] not in s['processes']:
                    raise InvalidSnapshot('MISSING_MORAL_INCIDENT')
                if proc['type'] == 'moral_incident' and proc['evaluated'] and proc['assessment_event'] not in s['events']:
                    raise InvalidSnapshot('MISSING_MORAL_ASSESSMENT')
        rng = s['rng']
        if (rng['algorithm'] != ALGORITHM or rng['seed_hex'] != self.rules['rng']['seed_hex']
                or set(rng['streams']) != set(self.rules['rng']['streams'])
                or any(type(c) is not int or not 0 <= c < 2**64 for c in rng['streams'].values())):
            raise InvalidSnapshot('INVALID_RNG_STATE')
        counters = {stream:0 for stream in rng['streams']}
        vector_cursors = {}
        for ev in es:
            if ev['type'] != 'CheckResolved':
                continue
            r = ev['payload']; stream = r['stream']
            if stream not in counters or r['counter_before'] != counters[stream]:
                raise InvalidSnapshot('RNG_TRACE_POSITION_MISMATCH')
            classified = classify(r['dice'],r['difficulty'])
            if any(classified[k] != r[k] for k in classified) or len(r['dice']) != r['pool']:
                raise InvalidSnapshot('DICE_TRACE_MISMATCH')
            if r['mode'] == 'RNG':
                dice = []
                for _ in range(r['pool']):
                    value,counters[stream] = draw(rng['seed_hex'],stream,counters[stream])
                    dice.append(value)
                if dice != r['dice']:
                    raise InvalidSnapshot('RNG_DICE_MISMATCH')
            elif r['mode'] == 'TEST_VECTOR' and config['harness']:
                cursor = vector_cursors.get(stream,0)
                vectors = config['test_vectors'].get(r['system'],[])
                if cursor >= len(vectors) or cursor != r['vector_index'] or vectors[cursor] != r['dice']:
                    raise InvalidSnapshot('TEST_VECTOR_TRACE_MISMATCH')
                vector_cursors[stream] = cursor+1
            else:
                raise InvalidSnapshot('UNSUPPORTED_DICE_MODE')
            if r['counter_after'] != counters[stream]:
                raise InvalidSnapshot('RNG_TRACE_POSITION_MISMATCH')
        if rng['streams'] != counters or rng['vector_cursors'] != vector_cursors:
            raise InvalidSnapshot('RNG_CURSOR_LEDGER_MISMATCH')
        nightly = {e['payload']['night_id']:e['id'] for e in es if e['type']=='NightBloodSpent'}
        rises = {e['payload']['night_id']:e['id'] for e in es if e['type']=='WillpowerRecovered'}
        if (len(nightly) != len([e for e in es if e['type']=='NightBloodSpent'])
                or set(a['night_receipts']) != set(nightly) or a['wake_receipts'] != rises
                or any(receipt['events'] != [nightly[night]] for night,receipt in a['night_receipts'].items())):
            raise InvalidSnapshot('NIGHT_RECEIPT_LEDGER_MISMATCH')
        for night, receipt in a['night_receipts'].items():
            if any(e not in s['events'] for e in receipt['events']):
                raise InvalidSnapshot('MISSING_NIGHT_RECEIPT')
        if any(e not in s['events'] for e in a['wake_receipts'].values()):
            raise InvalidSnapshot('MISSING_WAKE_RECEIPT')
