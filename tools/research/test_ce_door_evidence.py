"""Reject unsupported claims based on door observations."""
import copy
import json
from pathlib import Path
import unittest
from check_ce_door_evidence import check


class DoorEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture=json.loads((Path(__file__).resolve().parents[2]/"research/FALLOUT2/CE_DOOR_2026-10-10.json").read_text())

    def setUp(self): self.data=copy.deepcopy(self.fixture)

    def test_partial_observation(self): self.assertEqual(check(self.data)["A2-05"],"REFERENCE_PARTIAL")

    def test_wrong_selection(self):
        self.data["runs"][0]["cases"][0]["before"]["selected_object"]["pid"]=50333170
        with self.assertRaisesRegex(ValueError,"Wrong selected"):check(self.data)

    def test_changed_data(self):
        self.data["runs"][0]["original_inputs_unchanged"]["master.dat"]=False
        with self.assertRaisesRegex(ValueError,"DAT preservation"):check(self.data)

    def test_missing_repetition(self):
        self.data["runs"]=self.data["runs"][:1]
        with self.assertRaisesRegex(ValueError,"independent repetition"):check(self.data)

    def test_premature_passage(self):
        records=self.data["runs"][0]["native_pose_changes"]
        r=next(r for r in records if r["door"]["frame"]==3)
        r["door_blocker"]=None
        with self.assertRaisesRegex(ValueError,"blocking distinction|Premature"):check(self.data)

    def test_occupied_actor(self):
        self.data["runs"][0]["native_pose_changes"][-1]["blocker_at_actor"]={"tile":15709}
        with self.assertRaisesRegex(ValueError,"Occupied actor"):check(self.data)

    def test_incomplete_arrival(self):
        self.data["runs"][0]["cases"][2]["settled"]=False
        with self.assertRaisesRegex(ValueError,"Arrival not measured"):check(self.data)

    def test_acceptance_overclaim(self):
        self.data["a2_05"]="ACCEPTED"
        with self.assertRaisesRegex(ValueError,"Scope overclaim"):check(self.data)

    def test_failed_locker_cannot_certify_reachability(self):
        run=next(r for r in self.data["runs"] if any(c["label"]=="reachable-locker-approach" for c in r["cases"]))
        case=next(c for c in run["cases"] if c["label"]=="reachable-locker-approach")
        case["after"]["dude"]["tile"]=15709
        with self.assertRaisesRegex(ValueError,"Locker not reached"):check(self.data)


if __name__ == "__main__":unittest.main()
