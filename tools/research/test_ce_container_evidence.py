"""Reject overclaims and broken causal evidence for container interaction."""
import copy
import json
from pathlib import Path
import unittest
from check_ce_container_evidence import check

class ContainerEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.fixture=json.loads((Path(__file__).resolve().parents[2]/'research/FALLOUT2/CE_CONTAINER_2026-10-10.json').read_text())
    def setUp(self):self.data=copy.deepcopy(self.fixture)
    def case(self,role):return next(r for r in self.data['runs'] if r['role']==role)['cases'][0]
    def rejects(self,message):
        with self.assertRaisesRegex(ValueError,message):check(self.data)
    def test_partial_scope(self):self.assertEqual(check(self.data)['A2-08'],'NOT_EXECUTED')
    def test_wrong_selection(self):
        self.case('empty-open')['before']['selected_object']['id']=491;self.rejects('Wrong selected')
    def test_visor_missing(self):
        self.case('empty-open')['before']['monitor_line_kinds']=['OTHER','OTHER'];self.rejects('Visor observation')
    def test_locked_refusal_missing(self):
        self.case('locked')['effect']['inventory_visible']=True;self.rejects('Locked container')
    def test_inventory_target_mismatch(self):
        self.case('empty-open')['effect']['inventory_target']['id']=491;self.rejects('Inventory opening')
    def test_cancel_after_open(self):
        self.case('cancel-approach')['effect']['locker']['frame']=1;self.rejects('Cancelled action still')
    def test_ownership_change(self):
        self.case('empty-open')['after']['actor_inventory']=[{'quantity':1}];self.rejects('Ownership changed')
    def test_drifted_dat(self):
        self.data['runs'][0]['original_inputs_unchanged']['master.dat']=False;self.rejects('DAT preservation')
    def test_scope_overclaim(self):
        self.data['a2_08']='REFERENCE_PARTIAL';self.rejects('Scope overclaim')
    def test_raw_content_leak(self):
        self.case('empty-open')['before']['monitor_recent_hex']=[];self.rejects('Private content')

if __name__=='__main__':unittest.main()
