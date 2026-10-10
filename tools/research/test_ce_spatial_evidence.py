"""Archive corruption/rejection tests; no game runtime or assets required."""
import copy
import json
from pathlib import Path
import unittest
from check_ce_spatial_evidence import check,case

class SpatialEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.base=json.loads((Path(__file__).resolve().parents[2]/'research/FALLOUT2/CE_SPATIAL_2026-10-10.json').read_text())
    def setUp(self):self.d=copy.deepcopy(self.base)
    def run_for(self,role):return next(r for r in self.d['runs'] if r['plan']['role']==role)
    def reject(self):
        with self.assertRaises(ValueError):check(self.d)
    def test_archived_scope_passes(self):self.assertEqual(check(self.d)['native_pose_observations'],575)
    def test_wrong_reference_rejected(self):self.d['runs'][0]['binary_sha256']='0'*64;self.reject()
    def test_feature_acceptance_rejected(self):self.d['vampiro_status']='ACCEPTED';self.reject()
    def test_private_text_rejected(self):self.d['runs'][0]['monitor_recent_hex']=['41'];self.reject()
    def test_forged_pixel_rejected(self):self.d['runs'][0]['cases'][0]['point_trials'][0]['after']['cursor_before']=[1,1];self.reject()
    def test_behind_opaque_selected_rejected(self):
        c=self.run_for('selection-balanced')['cases'][0]
        t=next(t for t in c['point_trials'] if not t['after']['cursor_point']['roof'] and len(t['after']['cursor_point']['hits'])>=2)
        t['after']['selected_object']=t['after']['cursor_point']['hits'][0]['object'];self.reject()
    def test_roof_suppression_rejected(self):
        t=self.d['runs'][0]['cases'][0]['point_trials'][0];t['after']['selected_object']=t['after']['cursor_point']['hits'][0]['object'];self.reject()
    def test_actor_collision_rejected(self):self.d['runs'][0]['native_pose_changes'][0]['blocker_at_actor']={'pid':1};self.reject()
    def test_unexplained_route_gap_rejected(self):self.d['runs'][0]['native_pose_changes'][2]['dude']['tile']=39999;self.reject()
    def test_bridge_removed_rejected(self):self.d['transition_log_gaps'][0]['bridge_input_sequences']=[31,37];self.reject()
    def test_closed_barrier_effect_rejected(self):case(self.run_for('closed-open-access'),'closed-access-use')['samples'][0]['inventory_visible']=True;self.reject()
    def test_wrong_open_inventory_target_rejected(self):case(self.run_for('closed-open-access'),'open-access-use')['after']['inventory_target']['pid']=4;self.reject()
    def test_wrong_visor_target_rejected(self):case(self.run_for('wall-ground-input-hidden-roof-repeat'),'hidden-locker-hover')['observed']['hover_look_target']['pid']=4;self.reject()
    def test_disclosure_erased_rejected(self):self.d['reference_deviations']=[];self.reject()
    def test_perimeter_failure_rejected(self):self.run_for('depth-streetlight')['cases'][0]['after']['dude']['tile']=13915;self.reject()
    def test_video_missing_rejected(self):r=self.run_for('depth-streetlight');r['captures'].pop(r['cases'][0]['label']+'.gif');self.reject()
    def test_probe_binding_rejected(self):self.d['runs'][0]['controller_sha256']='0'*64;self.reject()

if __name__=='__main__':unittest.main()
