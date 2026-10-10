"""Reject false pickup, cancellation, ownership and contact claims."""
import copy
import json
from pathlib import Path
import unittest
from check_ce_pickup_evidence import check
class PickupEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.fixture=json.loads((Path(__file__).resolve().parents[2]/'research/FALLOUT2/CE_PICKUP_2026-10-10.json').read_text())
    def setUp(self):self.data=copy.deepcopy(self.fixture)
    def case(self,label,run=0):return next(c for c in self.data['runs'][run]['cases'] if c['label']==label)
    def reject(self,text):
        with self.assertRaisesRegex(ValueError,text):check(self.data)
    def test_partial_scope(self):self.assertEqual(check(self.data)['a2_08'],'REFERENCE_PARTIAL')
    def test_wrong_selection(self):
        self.case('pickup-complete')['before']['selected_object']['id']=201;self.reject('Wrong pickup selection')
    def test_owner_missing(self):
        self.case('pickup-complete')['effect']['watched_owner']=None;self.reject('Ownership/map transition')
    def test_item_still_on_map(self):
        self.case('pickup-complete')['after']['watched_on_map']=True;self.reject('Ownership/map transition')
    def test_duplicate_quantity(self):
        self.case('pickup-complete')['after']['actor_inventory'][0]['quantity']=2;self.reject('Ownership/map transition')
    def test_cancel_transfers(self):
        self.case('pickup-cancel-approach',1)['after']['watched_on_map']=False;self.reject('Cancelled pickup transferred')
    def test_dat_drift(self):
        self.data['runs'][0]['original_inputs_unchanged']['critter.dat']=False;self.reject('DAT preservation')
    def test_wrong_fixture(self):
        self.data['reference']['observed_initial_tile']=23895;self.reject('Wrong map fixture')
    def test_contact_overclaim(self):
        self.data['effect_boundary_status']='ATOMIC_CONTACT_VERIFIED';self.reject('Scope overclaim')
    def test_private_content(self):
        self.case('pickup-complete')['before']['monitor_recent_hex']=[];self.reject('Private content')
if __name__=='__main__':unittest.main()
