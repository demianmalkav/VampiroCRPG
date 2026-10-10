import copy,json,unittest
from pathlib import Path
from check_ce_pickup_cycle_evidence import check

class PickupCycleEvidenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=json.loads((Path(__file__).resolve().parents[2]/'research/FALLOUT2/CE_PICKUP_CYCLE_2026-10-10.json').read_text())
 def data(self):return copy.deepcopy(self.base)
 def run_case(self,d,n,label):return next(c for r in d['runs'] if r['run_id']==n for c in r['cases'] if c['label']==label)
 def reject(self,d):
  with self.assertRaises(ValueError):check(d)
 def test_baseline(self):self.assertEqual(check(self.data())['status'],'MEASURED_SCOPE_CHECKS_PASS')
 def test_binary_drift(self):
  d=self.data();d['runs'][0]['binary_sha256']='0'*64;self.reject(d)
 def test_two_delay_chain_missing(self):
  d=self.data()
  for s in d['runs'][0]['native_pose_changes']:
   for q in s['actor_sequences']:
    if len(q['descriptions'])==7:q['descriptions'][5]['delay']=0
  self.reject(d)
 def test_wrong_pickup_callback(self):
  d=self.data()
  for s in d['runs'][0]['native_pose_changes']:
   for q in s['actor_sequences']:
    if len(q['descriptions'])==7:q['descriptions'][6]['callback']='other'
  self.reject(d)
 def test_premature_sampled_transfer(self):
  d=self.data();r=d['runs'][0];s=next(x for x in r['native_pose_changes'] if ((x['dude']['fid']>>16)&255)==10 and x['dude']['frame']==4);s['watched_owner']=copy.deepcopy(s['dude']);self.reject(d)
 def test_early_cancel_release_after_effect(self):
  d=self.data();s=self.run_case(d,'cycle-07','cancel-gesture')['release'];s['watched_owner']=copy.deepcopy(s['dude']);self.reject(d)
 def test_post_effect_owner_loss(self):
  d=self.data();self.run_case(d,'cycle-05','cancel-after-effect-request')['release']['watched_owner']=None;self.reject(d)
 def test_duplicate_quantity(self):
  d=self.data();self.run_case(d,'cycle-06','repeat-gesture')['after']['actor_inventory'][0]['quantity']=2;self.reject(d)
 def test_load_does_not_restore_ground(self):
  d=self.data();s=self.run_case(d,'cycle-08','before-effect-loaded')['state'];s['watched_owner']=copy.deepcopy(s['dude']);self.reject(d)
 def test_no_distinct_state_before_load(self):
  d=self.data();c=self.run_case(d,'cycle-09','after-effect-before-load');saved=self.run_case(d,'cycle-09','after-effect-saved');c['state']['dude']['tile']=saved['after']['dude']['tile'];self.reject(d)
 def test_atomic_overclaim(self):
  d=self.data();d['effect_boundary_status']='ATOMIC_PROVEN';self.reject(d)
 def test_raw_game_text_leak(self):
  d=self.data();d['monitor_recent_hex']=['00'];self.reject(d)

if __name__=='__main__':unittest.main()
