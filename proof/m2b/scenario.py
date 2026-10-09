"""Initial conditions and inputs, with observations kept outside authority."""
import copy

from proof.m2.scenario import prepare as prepare_a, observe as observe_a
from .world import SurvivalWorld, PROFILE, V0, M0

CASES = ('conservative', 'lethal', 'lucid_escape', 'botch', 'early_removal', 'denied_access', 'insufficient_directive')


def prepare(case='conservative', *, harness=None, vectors=None, vampire=None, vessel_blood=None,
            camera=True, witness=True, accessible=True):
    if case not in CASES:
        raise ValueError('UNKNOWN_B_CASE')
    fixture, _ = prepare_a()
    fixture.update(fixture_version=PROFILE, case_id=case, scope='B', tick_unit='second')
    fixture.pop('cases', None)
    fixture.pop('expected', None)
    fixture['world']['device']['capture_enabled'] = camera
    fixture['scenario_profile'].update(witness_enabled=witness, witness_transmission_tick=43260,
                                      copy_tick=43320, review_tick=43560, visit_planning_tick=43620,
                                      visit_due_tick=86460, action_delay_after_arrival=60,
                                      report_delay_after_action=60, deadline_tick=43500)
    for route in fixture['world']['routes']:
        if route['from'] == 'location:L_HAV' and route['to'] == 'location:L_REG':
            route['duration'] = 120 if case != 'early_removal' else 1
        elif route['from'] == 'location:L_REG' and route['to'] == 'location:L_INC':
            route['duration'] = 60
        else:
            route['duration'] = 3
    if case == 'early_removal':
        fixture['scenario_profile']['action_delay_after_arrival'] = 1
    if case == 'denied_access':
        fixture['world']['grant']['enabled'] = False
    original_directive = copy.deepcopy(fixture['external_inputs'][1])
    original_directive['directive'].update(deadline_tick=43500, not_before=43260)
    if case == 'insufficient_directive':
        original_directive['directive']['office'] = None
    fixture['vessel_initial_blood'] = vessel_blood if vessel_blood is not None else (8 if case in ('lethal','lucid_escape','botch') else 10)
    fixture['vessel_accessible'] = accessible
    fixture['vampire_initial'] = vampire or {}
    fixture['harness'] = (case in ('lethal','lucid_escape','botch')) if harness is None else harness
    fixture['test_vectors'] = copy.deepcopy(vectors if vectors is not None else
        ({'beast': [[2,4]], 'moral': [[4,6,2]]} if case in ('lethal','lucid_escape') else
         {'beast': [[1,2]], 'moral': [[1,4,6]]} if case == 'botch' else {}))
    rows = [dict(tick=0,type='NightStarted',night_id='night:1'),
            dict(tick=0,type='AttemptFeed',target=M0,amount=2)]
    if case == 'lucid_escape':
        rows.append(dict(tick=3,type='LucidAction',action='MoveTo',target='location:L_HAV'))
    elif case not in ('lethal','botch'):
        rows.append(dict(tick=3,type='SealBite',target=M0))
        original_directive.update(tick=12)
        rows += [original_directive,
                 dict(tick=12,type='StartTravel',actor=V0,to='location:L_HAV'),
                 dict(tick=15,type='SleepUntil',until=86400),
                 dict(tick=15,type='UnloadPresentation',location='location:L_INC'),
                 dict(tick=86400,type='StartTravel',actor=V0,to='location:L_INC')]
    for index,row in enumerate(rows,1):
        row['input_seq'] = index
    fixture['external_inputs'] = rows
    return fixture


def run_until(world, fixture, tick):
    for row in fixture['external_inputs']:
        if row['input_seq'] > world.s['input_cursor'] and row['tick'] <= tick:
            result = world.apply_input(row)
            if not result['ok']:
                raise AssertionError(f'B input rejected: {row}: {result}')
    world.advance_to(tick)
    return world


def run(case='conservative', tick=None, **kwargs):
    fixture = prepare(case, **kwargs)
    if tick is None:
        tick = 30 if case in ('lethal','lucid_escape','botch') else 86460
    world = run_until(SurvivalWorld(fixture), fixture, tick)
    return world, fixture


def observe(world):
    sources = world.s['actors'][M0]
    incidents = [p for p in world.s['processes'].values() if p['type']=='moral_incident']
    return dict(blood=world.vampire['blood_current'], victim_blood=sources['vessel']['blood_current'],
                victim_condition=sources['condition'], punctures_open=sources['vessel']['punctures_open'],
                willpower=world.vampire['willpower_current'], humanity=world.vampire['humanity'],
                conscience=world.vampire['conscience'], governance=world.actor['governance'],
                moral_incidents=len(incidents), evaluations=sum(p['evaluated'] for p in incidents),
                moral_levels=[p.get('level') for p in incidents],
                trauma_pending=sum('trauma' in p for p in incidents), public=observe_a(world))
