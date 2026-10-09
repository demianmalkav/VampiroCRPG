"""Behavioral acceptance of blood, governance, morality and integration."""
import copy
import json
import unittest
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

from proof.m2.world import InvalidSnapshot, Rejected
from proof.m2b.rules import classify, draw
from proof.m2b.scenario import prepare, run, run_until, observe, CASES
from proof.m2b.world import SurvivalWorld, V0, M0


def events(w, kind):
    return [e for e in w.s['events'].values() if e['type']==kind]


def command(w, kind, **payload):
    return w.command('command:test-'+str(len(w.s['receipts'])),kind,payload)


def ready(case='conservative', **kwargs):
    f=prepare(case,**kwargs)
    w=SurvivalWorld(f)
    w.advance_to(0)
    return w,f


class TracingSurvival(SurvivalWorld):
    def __init__(self, fixture, reload_each=False):
        super().__init__(fixture)
        self.reload_each=reload_each
        self.checkpoints=[]

    def _atomic(self, action):
        if self.reload_each:
            self.load(self.snapshot())
        result=super()._atomic(action)
        self.checkpoints.append(json.loads(self.snapshot()))
        if self.reload_each:
            self.load(self.snapshot())
        return result


class SurvivalAcceptance(unittest.TestCase):
    def test_NQR10_safe_transfer_and_seal_preserve_evidence(self):
        w,f=run(tick=6)
        self.assertEqual((w.vampire['blood_current'],w.s['actors'][M0]['vessel']['blood_current']),(4,8))
        self.assertEqual(w.s['actors'][M0]['condition'],'no_emergency')
        self.assertFalse(w.s['actors'][M0]['vessel']['punctures_open'])
        self.assertTrue(w.has_claim('actor:W1','anomaly'))
        self.assertIn('record:REC_ORIG',w.s['records'])
        self.assertEqual(len(events(w,'NightBloodSpent')),1)
        self.assertEqual([e['payload']['amount'] for e in events(w,'BloodExtracted')],[2])
        self.assertFalse(events(w,'ResolvedIncident'))
        run_until(w,f,86460)
        self.assertIn('record:REC_COPY',w.s['records'])
        self.assertFalse(w.s['records']['record:REC_ORIG']['available'])
        self.assertTrue(w.has_claim('actor:W1','anomaly'))
        self.assertIn('FeedingStarted',{e['type'] for e in w.why_process_started('process:CASE')})

    def test_NQR10_duplicate_feed_and_seal_do_not_repeat(self):
        w,f=run(tick=6)
        for row in f['external_inputs'][1:3]:
            before=w.snapshot()
            p={k:v for k,v in row.items() if k not in ('tick','type','input_seq')}
            r=w.command('command:input-'+str(row['input_seq']),row['type'],p)
            self.assertTrue(r['ok'])
            self.assertEqual(w.snapshot(),before)
        self.assertEqual(len(events(w,'BiteWoundSealed')),1)

    def test_NQR11_lucid_escape_spends_once_and_restores_beast(self):
        w,f=run('lucid_escape',tick=4)
        self.assertEqual((w.vampire['blood_current'],w.vampire['willpower_current']),(5,4))
        self.assertEqual(w.actor['governance'],'LUCID_ACTION')
        self.assertEqual(w.s['actors'][M0]['condition'],'medical_emergency')
        w.load(w.snapshot())
        before=w.snapshot()
        p={'action':'MoveTo','target':'location:L_HAV'}
        self.assertTrue(w.command('command:input-3','LucidAction',p)['ok'])
        self.assertEqual(w.snapshot(),before)
        self.assertFalse(command(w,'LucidAction',**p)['ok'])
        w.advance_to(6)
        self.assertEqual(w.actor['governance'],'BEAST')
        self.assertEqual(len(events(w,'BloodExtracted')),1)
        w.advance_to(14)
        self.assertEqual(w.actor['governance'],'BEAST')
        w.advance_to(15)
        self.assertEqual(w.actor['governance'],'NORMAL')
        self.assertEqual(w.vampire['willpower_current'],4)
        self.assertEqual(w.s['actors'][M0]['vessel']['blood_current'],5)

    def test_NQR11_filling_or_losing_hunger_does_not_end_frenzy(self):
        w,_=run('lethal',tick=3)
        self.assertFalse(w.hungry())
        self.assertEqual(w.actor['governance'],'BEAST')
        w.advance_to(9)
        self.assertEqual(w.vampire['blood_current'],10)
        self.assertEqual(w.actor['governance'],'BEAST')
        w.advance_to(17)
        self.assertEqual(w.actor['governance'],'BEAST')
        w.advance_to(18)
        self.assertEqual(w.actor['governance'],'NORMAL')

    def test_NQR12_grave_frenzy_incident_success_failure_and_botch(self):
        for dice, h,c,trauma in (([8,6,4],7,3,0),([4,6,2],6,3,0),([1,6,4],6,2,1),([8,1,1],6,3,0)):
            with self.subTest(dice=dice):
                w,_=run('lethal',vectors={'beast':[[2,4]],'moral':[dice]})
                actual=observe(w)
                self.assertEqual((actual['blood'],actual['victim_blood']),(10,0))
                self.assertEqual((actual['humanity'],actual['conscience'],actual['trauma_pending']),(h,c,trauma))
                self.assertEqual(actual['moral_levels'],[4])
                self.assertEqual(actual['evaluations'],1)
                self.assertEqual([e['payload']['amount'] for e in events(w,'BloodExtracted')],[3,3,2])
                self.assertEqual(len(events(w,'MoralIncidentAssessed')),1)

    def test_NQR12_forbidden_willpower_does_not_suppress_pending_assessment(self):
        w,_=run('lethal',tick=6)
        while w.s['queue'][0]['kind']!='MoralAssessment':
            w.step()
        incident=next(p for p in w.s['processes'].values() if p['type']=='moral_incident')
        before=w.snapshot()
        r=command(w,'AssessMoral',incident=incident['id'],use_willpower=True)
        self.assertEqual(r['reason'],'WILLPOWER_FORBIDDEN_FOR_DEGENERATION')
        self.assertEqual(w.snapshot(),before)
        w.step()
        self.assertTrue(w.s['processes'][incident['id']]['evaluated'])
        self.assertEqual(w.vampire['willpower_current'],5)

    def test_NQR12_warning_precedes_fatal_action_even_under_beast(self):
        w,_=run('lethal')
        death=next(e for e in events(w,'VictimConditionChanged') if e['payload']['condition']=='dead')
        warnings=events(w,'MoralRiskWarning')
        self.assertTrue(any(e['tick']<death['tick'] for e in warnings))
        self.assertNotIn('victim_blood',json.dumps(w.player_view()))
        for record in w.s['records'].values():
            public=json.dumps(record['content'])
            for private in ('humanity','conscience','blood_current','dice','seed_hex','government'):
                self.assertNotIn(private,public)

    def test_BF01_night_cost_while_asleep_and_wake_recovery_once(self):
        w,f=run('lucid_escape',tick=30)
        self.assertTrue(command(w,'Sleep')['ok'])
        w.advance_to(86400)
        self.assertEqual(w.actor['availability'],'asleep')
        self.assertEqual(w.vampire['blood_current'],4)
        self.assertEqual(w.vampire['willpower_current'],4)
        self.assertTrue(command(w,'Wake',night_id='night:2')['ok'])
        self.assertEqual(w.vampire['willpower_current'],5)
        for _ in range(2):
            self.assertTrue(command(w,'Sleep')['ok'])
            self.assertTrue(command(w,'Wake',night_id='night:2')['ok'])
            self.assertTrue(command(w,'NightStarted',night_id='night:2')['ok'])
            w.load(w.snapshot())
        self.assertEqual(len(events(w,'NightBloodSpent')),2)
        self.assertEqual(sum(e['payload']['amount'] for e in events(w,'WillpowerRecovered')),1)

    def test_BF01_initial_awake_receipt_prevents_same_night_farming(self):
        w,_=ready(vampire={'willpower_current':2})
        self.assertEqual(w.vampire['willpower_current'],3)
        self.assertTrue(command(w,'Sleep')['ok'])
        self.assertTrue(command(w,'Wake',night_id='night:1')['ok'])
        self.assertEqual(w.vampire['willpower_current'],3)
        self.assertEqual(len(events(w,'WillpowerRecovered')),1)

    def test_BF01_unsupported_exhaustion_rejects_without_repair(self):
        w=SurvivalWorld(prepare(vampire={'blood_current':1}))
        before=w.snapshot()
        r=command(w,'NightStarted',night_id='night:1')
        self.assertEqual(r['reason'],'UNSUPPORTED_EXHAUSTION')
        self.assertEqual(w.snapshot(),before)
        with self.assertRaisesRegex(Rejected,'UNSUPPORTED_EXHAUSTION'):
            w.step()
        self.assertEqual(w.snapshot(),before)

    def test_BF02_inaccessible_or_unseen_sources_do_not_roll_or_transfer(self):
        for inaccessible in ('grant','location','asleep'):
            f=prepare(harness=True,accessible=inaccessible!='grant')
            if inaccessible=='location': f['world']['actors'][1]['location']='location:L_REG'
            w=SurvivalWorld(f);w.advance_to(0)
            if inaccessible=='asleep': command(w,'Sleep')
            before=w.snapshot()
            self.assertFalse(command(w,'AttemptFeed',target=M0)['ok'])
            self.assertEqual(w.snapshot(),before)
            self.assertFalse(events(w,'CheckResolved'))
        w,_=ready(harness=True)
        before=w.snapshot()
        self.assertEqual(command(w,'ObserveBlood',target=M0,sense='sight')['reason'],'HARNESS_ONLY')
        self.assertEqual(w.snapshot(),before)

    def test_BF03_five_accumulated_successes_and_current_pool(self):
        w,_=ready(harness=True,vectors={'beast':[[3,7],[4,8],[3,2]]})
        r=w.command('command:stimulus','ObserveBlood',{'target':M0,'sense':'smell'},harness=True)
        self.assertTrue(r['ok'])
        self.assertEqual(w.episode()['accumulated'],2)
        w.advance_to(5);self.assertEqual(len(events(w,'CheckResolved')),1)
        w.advance_to(6);self.assertEqual(w.episode()['accumulated'],4)
        w.advance_to(12)
        self.assertEqual(w.episode()['state'],'RESISTED')
        self.assertEqual(w.episode()['accumulated'],5)
        self.assertEqual([e['payload']['pool'] for e in events(w,'CheckResolved')],[2,2,2])
        self.assertFalse(events(w,'FrenzyStarted'))

    def test_BF03_pressure_withdrawal_and_feed_same_tick_cancel_retry(self):
        w,_=ready(harness=True,vectors={'beast':[[3,7]]})
        w.command('command:stimulus','ObserveBlood',{'target':M0,'sense':'smell'},harness=True)
        w.command('command:withdraw','WithdrawBloodStimulus',{},harness=True)
        w.advance_to(6)
        self.assertEqual(len(events(w,'CheckResolved')),1)
        self.assertEqual(w.actor['governance'],'NORMAL')
        w,_=run(tick=3)
        self.assertEqual(w.s['rng']['streams'][V0+'/beast'],2)
        self.assertEqual(len(events(w,'CheckResolved')),1)
        self.assertEqual(w.actor['governance'],'NORMAL')
        self.assertTrue(events(w,'HungerPressureEnded'))

    def test_BF03_beast_waits_without_source_and_cannot_issue_player_actions(self):
        w,f=run('lethal',tick=0)
        for kind,p in [('Sleep',{}),('StartTravel',{'actor':V0,'to':'location:L_HAV'}),
                       ('SendMessage',{k:v for k,v in prepare()['external_inputs'][3].items() if k not in ('tick','type','input_seq')})]:
            before=w.snapshot()
            self.assertEqual(command(w,kind,**p)['reason'],'BEAST_OWNS_ACTION')
            self.assertEqual(w.snapshot(),before)
        # A legal lucid departure before extraction leaves the hungry Beast active.
        self.assertTrue(command(w,'LucidAction',action='MoveTo',target='location:L_HAV')['ok'])
        w.advance_to(30)
        self.assertEqual(w.actor['governance'],'BEAST')
        self.assertTrue(w.hungry())
        self.assertFalse(events(w,'BloodExtracted'))
        self.assertEqual(len(events(w,'CheckResolved')),1)

    def test_BF04_revised_cancellation_and_botch_vectors(self):
        for row in json.loads(Path('tests/specs/m2_core_b_profile.json').read_text())['reference_vectors_not_observed']:
            r=classify(row['dice'],row['difficulty'])
            for key in ('raw_successes','one_count','net_successes','result'):
                self.assertEqual(r[key],row[key])
        w,_=run('botch',tick=26)
        self.assertEqual(w.actor['governance'],'BEAST')
        w.advance_to(27)
        self.assertEqual(w.actor['governance'],'NORMAL')
        self.assertEqual(events(w,'FrenzyEnded')[0]['payload']['seconds'],18)

    def test_BF04_rng_format_references_rejection_sampling_and_overflow(self):
        w,_=ready()
        for row in w.rules['rng_format_reference_values']:
            count=0;actual=[]
            for _ in range(5):
                die,count=draw(w.s['rng']['seed_hex'],row['stream'],count)
                actual.append(die)
            self.assertEqual(actual,row['first_five_dice'])
            self.assertEqual(count,5)
        class Digest:
            def __init__(self,n):self.n=n
            def digest(self):return self.n.to_bytes(4,'big')+bytes(28)
        with patch('proof.m2b.rules.hashlib.sha256',side_effect=[Digest(4294967295),Digest(4)]):
            self.assertEqual(draw(w.s['rng']['seed_hex'],V0+'/beast',0),(5,2))
        with self.assertRaisesRegex(Rejected,'RNG_EXHAUSTED'):
            draw(w.s['rng']['seed_hex'],V0+'/beast',2**64-1)

    def test_BF04_next_night_pool_is_recomputed_and_contact_observed_again(self):
        w,_=run()
        self.assertEqual(w.vampire['blood_current'],3)
        self.assertTrue(command(w,'AttemptFeed',target=M0)['ok'])
        self.assertEqual(events(w,'CheckResolved')[-1]['payload']['pool'],3)
        self.assertTrue(events(w,'AdditionalContactObserved'))
        self.assertEqual(len([r for r in w.s['records'].values() if r['kind']=='video']),3)

    def test_BF05_full_capacity_and_death_block_additional_extraction(self):
        w,_=run('lethal')
        before=w.snapshot()
        self.assertFalse(command(w,'AttemptFeed',target=M0)['ok'])
        self.assertEqual(w.snapshot(),before)
        w,_=run('lethal',vessel_blood=10,tick=30)
        self.assertEqual((w.vampire['blood_current'],w.s['actors'][M0]['vessel']['blood_current']),(10,2))
        self.assertEqual([e['payload']['amount'] for e in events(w,'BloodExtracted')],[3,3,2])
        self.assertEqual(w.s['actors'][M0]['condition'],'medical_emergency')
        self.assertFalse(any(e['payload']['condition']=='dead' for e in events(w,'VictimConditionChanged')))

    def test_BF05_invalid_lucid_action_and_empty_willpower_are_atomic(self):
        w,_=run('lethal',tick=3)
        for p in ({'action':'MoveTo','target':'location:L_REG'}, {'action':'CastPower'},
                  {'action':'MoveTo','target':'location:MISSING'}):
            before=w.snapshot()
            self.assertFalse(command(w,'LucidAction',**p)['ok'])
            self.assertEqual(w.snapshot(),before)
        w,_=run('lethal',tick=3,vampire={'willpower_current':0})
        # Initial optional rise restored one; use it, then the next purchase fails.
        command(w,'LucidAction',action='Wait')
        w.advance_to(6)
        before=w.snapshot()
        self.assertEqual(command(w,'LucidAction',action='Wait')['reason'],'WILLPOWER_UNAVAILABLE')
        self.assertEqual(w.snapshot(),before)

    def test_BF05_wait_lucid_window_suspends_feeding_not_extra_turn(self):
        w,_=run('lethal',tick=3)
        self.assertTrue(command(w,'LucidAction',action='Wait')['ok'])
        w.advance_to(6)
        self.assertEqual([e['tick'] for e in events(w,'BloodExtracted')],[3])
        self.assertEqual(w.actor['governance'],'BEAST')
        w.advance_to(9)
        self.assertEqual([e['tick'] for e in events(w,'BloodExtracted')],[3,9])
        self.assertEqual(w.vampire['willpower_current'],4)

    def test_BF06_every_atomic_commit_save_load_continuity(self):
        for case in CASES:
            with self.subTest(case=case):
                f=prepare(case)
                end=30 if case in ('lethal','lucid_escape','botch') else 86460
                plain=TracingSurvival(f)
                resumed=TracingSurvival(f,reload_each=True)
                run_until(plain,f,end);run_until(resumed,f,end)
                self.assertEqual(plain.checkpoints,resumed.checkpoints)
                self.assertEqual(plain.snapshot(),resumed.snapshot())
                self.assertEqual(plain.s['rng'],resumed.s['rng'])

    def test_BF06_injected_extraction_failure_rolls_back_both_resources_rng_queue(self):
        w,_=run('lethal',tick=0)
        before=w.snapshot()
        original=w.event
        def fail(kind,*args,**kwargs):
            if kind=='BloodExtracted':raise RuntimeError('injected mid-transfer failure')
            return original(kind,*args,**kwargs)
        with patch.object(w,'event',side_effect=fail):
            with self.assertRaisesRegex(RuntimeError,'mid-transfer'):
                w.step()
        self.assertEqual(w.snapshot(),before)
        w.step()
        self.assertEqual(w.vampire['blood_current'],5)

    def test_BF06_bad_snapshots_do_not_replace_live_world(self):
        w,_=run('lucid_escape',tick=4)
        original=json.loads(w.snapshot())
        for field in ('blood','governance','rng','rng_positive','action','profile','source','reference','night_receipt','action_future','opening_ledger','condition'):
            bad=copy.deepcopy(original)
            if field=='blood':bad['actors'][V0]['vampire']['blood_current']=9
            elif field=='governance':bad['actors'][V0]['governance']='NORMAL'
            elif field=='rng':bad['rng']['streams'][V0+'/beast']=-1
            elif field=='rng_positive':bad['rng']['streams'][V0+'/beast']=50
            elif field=='action':bad['actors'][V0]['action']['until']=3
            elif field=='profile':bad['profile_version']='m2-a-proof-profile-1'
            elif field=='source':bad['actors'][M0]['vessel']['blood_current']=9
            elif field=='reference':bad['actors'][V0]['episode']='process:missing'
            elif field=='night_receipt':bad['actors'][V0]['night_receipts']={}
            elif field=='action_future':bad['queue']=[q for q in bad['queue'] if q['kind']!='ActionComplete']
            elif field=='opening_ledger':bad['actors'][V0]['initial_vampire']['blood_current']=8
            elif field=='condition':bad['actors'][M0]['condition']='no_emergency'
            before=w.snapshot()
            with self.subTest(field=field),self.assertRaises(InvalidSnapshot):w.load(json.dumps(bad))
            self.assertEqual(w.snapshot(),before)
        other=SurvivalWorld(prepare('lethal'))
        with self.assertRaises(InvalidSnapshot):other.load(w.snapshot())

    def test_BF07_hierarchy_context_threshold_and_single_evaluation(self):
        for context,fr,humanity,expected in [('accidental_hunger_death_outside_frenzy',False,7,6),
                                           ('accidental_hunger_death_outside_frenzy',True,7,4)]:
            w,_=ready(harness=True,vectors={'moral':[[8,6,4]]},vampire={'humanity':humanity})
            r=w.command('command:fact','SeedMoralFacts',{'target':M0,'context':context,'during_frenzy':fr},harness=True)
            command(w,'AssessMoral',incident=r['incident'])
            self.assertEqual(w.s['processes'][r['incident']]['level'],expected)
            before=len(events(w,'CheckResolved'))
            w.load(w.snapshot());command(w,'AssessMoral',incident=r['incident'])
            self.assertEqual(len(events(w,'CheckResolved')),before)
            self.assertEqual(len(events(w,'MoralIncidentAssessed')),1)
        w,_=run(tick=6)
        self.assertEqual(events(w,'MoralIncidentAssessed')[0]['payload']['result'],'NOT_REQUIRED')
        w,_=ready(harness=True)
        r=w.command('command:fact','SeedMoralFacts',{'target':M0,'context':'premeditated_murder'},harness=True)
        before=w.snapshot()
        self.assertEqual(command(w,'AssessMoral',incident=r['incident'])['reason'],'UNSUPPORTED_MORAL_CONTEXT')
        self.assertEqual(w.snapshot(),before)

    def test_BF08_rendering_unload_camera_and_private_morality_independence(self):
        outcomes=[]
        for camera,witness in ((True,True),(False,False)):
            w,_=run('lethal',camera=camera,witness=witness)
            outcomes.append((w.vampire['humanity'],w.vampire['conscience'],w.s['rng']))
            before=w.snapshot()
            w.player_view();w.pending_world_work();w.snapshot()
            command(w,'UnloadPresentation',location='location:L_INC')
            # The receipt is the only domain change for this presentation command.
            after=json.loads(w.snapshot());old=json.loads(before)
            after['receipts']=old['receipts']
            self.assertEqual(after,old)
        self.assertEqual(outcomes[0],outcomes[1])

    def test_BI01_daytime_case_and_next_night_visit_follow_feeding(self):
        w,f=run(tick=43620)
        self.assertEqual(w.actor['availability'],'asleep')
        self.assertEqual(w.s['processes']['process:CLEANUP']['state'],'completed')
        self.assertEqual(w.s['messages']['message:RESULT']['status'],'waiting')
        self.assertEqual(w.s['processes']['process:CASE']['state'],'visit_planned')
        self.assertTrue(any(q['kind']=='VisitDeparture' for q in w.pending_world_work()))
        w.load(w.snapshot())
        run_until(w,f,86460)
        self.assertEqual(w.s['processes']['process:CASE']['visit_tick'],86460)
        self.assertTrue(w.has_claim(V0,'alias_inquiry'))
        self.assertFalse(w.has_claim(V0,'anomaly') and w.has_claim(V0,'record:REC_COPY'))
        self.assertFalse(observe(w)['public']['v0_knows_copy'])
        self.assertEqual(w.actor['location'],'location:L_INC')
        self.assertTrue(events(w,'BeastControlResumed')==[])

    def test_BI01_early_denied_and_incomplete_cleanup_preserve_boundaries(self):
        for case in ('early_removal','denied_access','insufficient_directive'):
            with self.subTest(case=case):
                w,_=run(case)
                p=observe(w)['public']
                self.assertEqual(p['copy_exists'],case!='early_removal')
                self.assertEqual(p['original_available'],case!='early_removal')
                self.assertEqual(p['task_terminal'],'completed' if case=='early_removal' else 'blocked')
                self.assertTrue(p['report_exists'])
                self.assertTrue(p['v0_observed_alias_inquiry'])
                self.assertFalse(p['v0_knows_copy'])

    def test_BF06_resolved_incident_and_profile_tampering_cannot_bypass_owners(self):
        w,_=ready()
        before=w.snapshot()
        self.assertEqual(w.command('command:cheat','InjectResolvedIncident',{},harness=True)['reason'],'RESOLVED_INCIDENT_NOT_ALLOWED_IN_B')
        self.assertEqual(w.snapshot(),before)
        candidate=json.loads(before)
        candidate['config']['survival_rules']['feeding']['maximum_extraction_per_action']=99
        with self.assertRaises(InvalidSnapshot):w.load(json.dumps(candidate))
        self.assertEqual(w.snapshot(),before)

    def test_BF06_cli_disk_save_resume_and_wrong_case_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            saved=Path(folder)/'mid.json';resumed=Path(folder)/'resumed.json';plain=Path(folder)/'plain.json'
            def cli(*args):
                return subprocess.run([sys.executable,'-m','proof.m2b',*args],capture_output=True,text=True)
            r=cli('--case','lucid_escape','--until','4','--save',str(saved));self.assertEqual(r.returncode,0,r.stderr)
            r=cli('--case','lucid_escape','--load',str(saved),'--save',str(resumed));self.assertEqual(r.returncode,0,r.stderr)
            r=cli('--case','lucid_escape','--save',str(plain));self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads(resumed.read_text()),json.loads(plain.read_text()))
            r=cli('--case','lethal','--load',str(saved));self.assertNotEqual(r.returncode,0)
            self.assertIn('INCOMPATIBLE_B_RULES_OR_CASE',r.stderr)

    def test_BF06_cli_interactive_decision_changes_actual_outcome(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'interactive.json'
            r=subprocess.run([sys.executable,'-m','proof.m2b','--case','lethal','--interactive','--save',str(path)],
                             input='\nv\n\n\n\n\nq\n',capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            saved=json.loads(path.read_text())
            self.assertEqual(saved['actors'][M0]['vessel']['blood_current'],5)
            self.assertEqual(saved['actors'][V0]['vampire']['willpower_current'],4)
            self.assertEqual(saved['actors'][V0]['governance'],'NORMAL')
if __name__=='__main__':unittest.main()
