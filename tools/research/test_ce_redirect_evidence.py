"""Guard measured A2-03 claims against missing input, phases and false cancellation."""
import copy
import json
from pathlib import Path
import unittest

from check_ce_redirect_evidence import check


class RedirectEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((Path(__file__).resolve().parents[2]/
            "research/FALLOUT2/CE_REDIRECTION_2026-10-10.json").read_text())

    def setUp(self):
        self.data=copy.deepcopy(self.fixture)

    def case(self,name):
        return next(c for c in self.data["cases"] if c["scenario"]==name)

    def test_five_reference_probes_are_not_vampiro_acceptance(self):
        result=check(self.data)
        self.assertEqual(result["scenarios"],5)
        self.assertEqual(result["A2-03"],"REFERENCE_PARTIAL")
        self.assertEqual(result["vampiro_acceptance"],"NOT_VERIFIED")

    def test_incomplete_run_rejected(self):
        self.data["failure"]="missing input acknowledgement"
        with self.assertRaisesRegex(ValueError,"Incomplete experiment"):
            check(self.data)

    def test_wrong_internal_cursor_rejected(self):
        self.case("single")["actions"][0]["verified"]["cursor_tile_before"]=13911
        with self.assertRaisesRegex(ValueError,"native cursor mismatch"):
            check(self.data)

    def test_node_aligned_input_cannot_prove_midstep_redirect(self):
        before=self.case("single")["actions"][0]["release_before_handling"]["dude"]
        before["x"]=before["y"]=0
        with self.assertRaisesRegex(ValueError,"not partial step"):
            check(self.data)

    def test_smoothing_claim_cannot_overwrite_measured_anchor_delta(self):
        self.case("rapid")["interrupt_boundaries"][0]["delta_anchor_xy"]=[0,0]
        with self.assertRaisesRegex(ValueError,"boundary measurement mismatch"):
            check(self.data)

    def test_escape_cannot_be_reported_as_route_cancellation(self):
        self.case("escape")["endpoint"]["dude"]["tile"]=13915
        with self.assertRaisesRegex(ValueError,"endpoint mismatch"):
            check(self.data)

    def test_last_rapid_order_must_determine_final_destination(self):
        self.case("rapid")["endpoint"]["dude"]["tile"]=14115
        with self.assertRaisesRegex(ValueError,"endpoint mismatch"):
            check(self.data)


if __name__=="__main__":
    unittest.main()
