"""CLI narration, interactive decisions, persistence and measured acceptance."""
import argparse
import datetime
import json
from pathlib import Path
import platform
import sys
import unittest

from proof.m2.__main__ import EvidenceResult, NARRATION as A_NARRATION, write_json
from proof.m2.world import InvalidSnapshot, Rejected
from .scenario import CASES, prepare, run_until, observe
from .world import SurvivalWorld, PROFILE, CONTRACT, RUNTIME

ROOT = Path(__file__).resolve().parents[2]
CASE_FILE = ROOT / 'tests/specs/m2_core_b_cases.json'
LABELS = {'conservative':'Alimentación controlada','lethal':'Frenesí sin intervención',
          'lucid_escape':'Una acción lúcida','botch':'Fracaso grave', 'early_removal':'Retirada temprana',
          'denied_access':'Acceso denegado','insufficient_directive':'Encargo incompleto'}
NARRATION = dict(A_NARRATION, **{
    'NightBloodSpent':'La noche consume un punto de sangre.',
    'FeedingStarted':'Comienza la alimentación sobre una víctima accesible.',
    'FrenzyStarted':'La Bestia toma el gobierno de las acciones.',
    'BloodExtracted':'Se extrae sangre de la víctima y se incorpora a la reserva.',
    'VictimConditionChanged':'La víctima muestra una consecuencia física de la pérdida.',
    'FeedingStopped':'La alimentación se detiene; las consecuencias permanecen.',
    'BiteWoundSealed':'Se cierran las perforaciones de los colmillos.',
    'WillpowerSpent':'Se paga voluntad por una sola acción lúcida.',
    'LucidActionStarted':'Comienza la acción lúcida de tres segundos.',
    'BeastControlResumed':'La Bestia retoma el gobierno; la lucidez no terminó el episodio.',
    'FrenzyEnded':'Termina el episodio tras el intervalo de calma.',
    'MoralIncidentAssessed':'Se evalúa una vez el incidente moral.',
    'TraumaPendingSelection':'Se conserva una consecuencia traumática pendiente de desarrollar.',
    'SleepStarted':'El protagonista duerme; los demás procesos continúan.'})


def matches(actual, spec):
    return all(actual.get(k)==v for k,v in spec['expected'].items()) and all(
        actual['public'].get(k)==v for k,v in spec.get('public_expected',{}).items())


def narrate(world, since=0):
    ordered=sorted(world.s['events'].values(), key=lambda e:int(e['id'].split(':')[1]))
    for ev in ordered:
        number=int(ev['id'].split(':')[1])
        if number<=since:continue
        kind=ev['type']
        if kind=='MoralRiskWarning':
            print(f"s{ev['tick']} · Aviso: {ev['payload']['text']}")
        elif kind in NARRATION:
            detail=''
            if kind=='BloodExtracted':detail=f" ({ev['payload']['amount']} puntos)"
            elif kind=='VictimConditionChanged':detail=' ('+{'medical_emergency':'emergencia médica','weak':'debilidad','dead':'muerte','no_emergency':'sin emergencia'}[ev['payload']['condition']]+')'
            elif kind=='MoralIncidentAssessed':detail=' ('+{'NOT_REQUIRED':'no requiere tirada','SUCCESS':'conservás Humanidad','FAILURE':'perdés Humanidad','BOTCH':'perdés Humanidad y Conciencia'}[ev['payload']['result']]+')'
            print(f"s{ev['tick']} · {NARRATION[kind]}{detail}")
    view=world.player_view()
    control={'NORMAL':'vos','RESISTING':'vos, resistiendo','BEAST':'la Bestia','LUCID_ACTION':'vos, durante una acción lúcida'}[view['governance']]
    print(f"Sangre: {view['blood']}/10 · Voluntad: {view['willpower']}/5 · Humanidad: {view['humanity']} · Hambre: {'sí' if view['hungry'] else 'no'} · Control: {control}")


def suite(report_path):
    tests=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_m2_core_*.py')
    result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2,resultclass=EvidenceResult).run(tests)
    cases=[]
    for spec in json.loads(CASE_FILE.read_text())['cases']:
        f=prepare(spec['id']); w=run_until(SurvivalWorld(f),f,spec['until']); actual=observe(w)
        cases.append(dict(case=spec['id'],status='PASS' if matches(actual,spec) else 'FAIL',
                          tick=w.s['tick'], actual=actual, expected=spec['expected'],
                          public_expected=spec.get('public_expected',{}),
                          rng_mode='TEST_VECTOR_HARNESS' if f['harness'] else 'RNG',
                          seed_hex=w.s['rng']['seed_hex'], state_sha256=w.digest(),
                          domain_events=len(w.s['events']), pending_work=len(w.s['queue']),
                          inputs=f['external_inputs']))
    prefixes=[('NQR',i) for i in range(1,13)]+[('F',i) for i in range(1,8)]+[('BF',i) for i in range(1,9)]+[('BI',1)]
    coverage={}
    for prefix,i in prefixes:
        name=(f'B-F{i:02d}' if prefix=='BF' else f'B-I{i:02d}' if prefix=='BI' else f'{prefix}-{i:02d}')
        found=[r for r in result.evidence if f'test_{prefix}{i:02d}_' in r['test']]
        coverage[name]=dict(status='PASS' if found and all(r['status']=='PASS' for r in found) else 'FAIL_OR_MISSING',tests=[r['test'] for r in found])
    passed=result.wasSuccessful() and all(c['status']=='PASS' for c in cases) and all(c['status']=='PASS' for c in coverage.values())
    report=dict(status='PASS' if passed else 'FAIL', profile=PROFILE, contract=CONTRACT, runtime=RUNTIME,
                generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),python=platform.python_version(),
                command='python3 -m proof.m2b --suite --report tests/results/m2_core_b_run.json',
                tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                a_regression_tests=sum('test_m2_core_a.' in r['test'] and r['status']=='PASS' for r in result.evidence),
                test_results=result.evidence, coverage=coverage, cases=cases,
                snapshot_comparison='semantic state/causes/queue/resources/RNG before and after every atomic commit in seven B cases',
                limitations=['headless proof only','synthetic calendar','test vectors explicitly labeled',
                             'trauma marker has no derangement behavior','no zero blood/torpor/full morality/combat/inventory/graphics'])
    if report_path:write_json(report_path,report)
    print(f"Resultado: {report['status']}; {result.testsRun} pruebas; {len(cases)} escenarios B.")
    return int(not passed)


def interactive(world):
    print('Decisiones: Enter avanza 3 segundos; v compra retirarse al refugio; r compra soltar; e espera lúcidamente; q termina.')
    while True:
        try:choice=input('> ').strip().lower()
        except EOFError:break
        if choice=='q':break
        last=world.s['allocator']
        if choice=='':world.advance_to(world.s['tick']+3)
        elif choice in ('v','r','e'):
            payload={'action':{'v':'MoveTo','r':'ReleaseVictim','e':'Wait'}[choice]}
            if choice=='v':payload['target']='location:L_HAV'
            row=dict(tick=world.s['tick'],input_seq=world.s['input_cursor']+1,type='LucidAction',**payload)
            result=world.apply_input(row)
            if not result['ok']:print('Acción rechazada: '+result['reason'])
        else:print('Elegí Enter, v, r, e o q.')
        narrate(world,last)


def main():
    parser=argparse.ArgumentParser(description='La Noche que Recuerda — supervivencia sin gráficos')
    parser.add_argument('--case',choices=CASES,default='conservative')
    parser.add_argument('--until',type=int)
    parser.add_argument('--suite',action='store_true')
    parser.add_argument('--report')
    parser.add_argument('--trace')
    parser.add_argument('--save')
    parser.add_argument('--load')
    parser.add_argument('--interactive',action='store_true')
    args=parser.parse_args()
    if args.suite:return suite(args.report)
    f=prepare(args.case)
    if args.interactive:f['external_inputs']=f['external_inputs'][:2]
    world=SurvivalWorld(f)
    try:
        if args.load:world.load(Path(args.load).read_text(encoding='utf-8'))
        end=args.until if args.until is not None else (30 if args.case in ('lethal','lucid_escape','botch') else 86460)
        if args.interactive:
            if not args.load:run_until(world,f,0)
        else:run_until(world,f,end)
        print('La Noche que Recuerda — '+LABELS[args.case])
        if f['harness']:print('Modo de demostración: dados de prueba explícitos; no se atribuyen al seed.')
        narrate(world)
        if args.interactive:interactive(world)
        actual=observe(world)
        expected=next(s for s in json.loads(CASE_FILE.read_text())['cases'] if s['id']==args.case)
        if not args.interactive and world.s['tick']==expected['until']:
            ok=matches(actual,expected);print('Expectativas: '+('PASS' if ok else 'FAIL'))
        else:ok=True
        if args.trace:write_json(args.trace,dict(case=args.case,events=list(world.s['events'].values()),
                                               player_view=world.player_view(),actual=actual,
                                               state_sha256=world.digest(),rng=world.s['rng']))
        if args.save:Path(args.save).write_text(world.snapshot()+'\n',encoding='utf-8')
        return int(not ok)
    except (Rejected,InvalidSnapshot,ValueError,AssertionError) as exc:
        parser.error(str(exc))


if __name__=='__main__':raise SystemExit(main())
