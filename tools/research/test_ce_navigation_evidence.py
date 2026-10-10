"""Reject misleading navigation evidence without executing or distributing Fallout."""
import copy
import json
from pathlib import Path
import unittest

from check_ce_navigation_evidence import check


class NavigationEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((Path(__file__).resolve().parents[2] /
            "research/FALLOUT2/CE_NAVIGATION_2026-10-10.json").read_text())

    def setUp(self):
        self.data = copy.deepcopy(self.fixture)

    def test_measured_scope_is_partial_not_vampiro_acceptance(self):
        result = check(self.data)
        self.assertEqual(result["cases"], 21)
        self.assertEqual(result["a2_02"], "REFERENCE_PARTIAL")
        self.assertEqual(result["vampiro_acceptance"], "NOT_VERIFIED")

    def test_clipped_cursor_cannot_certify_requested_destination(self):
        self.data["cases"][0]["cursor_verified"]["cursor_tile_before"] = 15299
        with self.assertRaisesRegex(ValueError, "cursor selects wrong"):
            check(self.data)

    def test_partial_run_cannot_certify_complete_measured_scope(self):
        self.data["cases"].pop()
        with self.assertRaisesRegex(ValueError, "case set incomplete"):
            check(self.data)

    def test_occupied_actor_tile_rejects_collision_claim(self):
        self.data["native_tile_transitions"][2]["blocker_at_actor"] = {"tile": 13915}
        with self.assertRaisesRegex(ValueError, "occupied actor"):
            check(self.data)

    def test_lost_transition_rejects_sampled_route(self):
        self.data["native_tile_transitions"].pop(2)
        with self.assertRaisesRegex(ValueError, "routes disagree"):
            check(self.data)

    def test_input_change_rejects_preservation_claim(self):
        self.data["original_inputs_unchanged"]["master.dat"] = False
        with self.assertRaisesRegex(ValueError, "DAT changed"):
            check(self.data)

    def test_timed_out_observation_cannot_certify_arrival(self):
        self.data["cases"][0]["settled"] = False
        with self.assertRaisesRegex(ValueError, "timed out"):
            check(self.data)


if __name__ == "__main__":
    unittest.main()
