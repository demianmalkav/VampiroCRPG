"""Behavioral acceptance of M2 core A; outcomes are never runtime inputs."""
import copy
import json
import unittest

from proof.m2.scenario import observe, prepare, read_fixture, run, run_until
from proof.m2.world import InvalidSnapshot, Rejected, WorkLimit, World


def change(path, value):
    return {"path": path, "value": value}


def events(world, kind):
    return [e for e in world.s["events"].values() if e["type"] == kind]


class TracingWorld(World):
    """Observe every atomic boundary, optionally serializing at every commit."""
    def __init__(self, fixture, reload_each=False):
        super().__init__(fixture)
        self.reload_each = reload_each
        self.checkpoints = []

    def _atomic(self, action):
        before = self.snapshot()
        if self.reload_each:
            self.load(before)
        result = super()._atomic(action)
        after = self.snapshot()
        self.checkpoints.append(json.loads(after))
        if self.reload_each:
            self.load(after)
        return result


class CoreAcceptance(unittest.TestCase):
    def test_NQR01_direct_observation_and_transformed_hearsay(self):
        fixture, _ = prepare()
        w = run_until(World(fixture), fixture, 2)
        self.assertTrue(w.has_claim("actor:W1", "anomaly"))
        for actor in ("actor:W2", "actor:I1", "actor:G1"):
            self.assertFalse(w.has_claim(actor, "anomaly"))
        self.assertEqual(w.s["relationships"]["relationship:W1-V0"]["dimensions"], {"fear": "increased", "trust": "reduced"})
        w.advance_to(3)
        self.assertTrue(w.has_claim("actor:W2", "anomaly"))
        memory = next(m for m in w.s["memories"].values() if m["holder"] == "actor:W2")
        self.assertEqual(memory["provenance"], "hearsay")
        self.assertNotIn("contact_details", memory["content"]["features"])
        self.assertIn("MessageReceived", {e["type"] for e in w.why_believes("actor:W2", "anomaly")[0]})
        self.assertFalse(w.has_claim("actor:I1", "anomaly"))
        self.assertEqual(w.s["institutions"]["institution:P1"]["cases"], ["process:CASE"])

    def test_NQR02_camera_only_and_authorized_alias_matching(self):
        changes = [change("scenario_profile.witness_enabled", False)]
        w, f, _ = run(changes=changes, tick=7)
        self.assertNotIn("message:TESTIMONY", w.s["messages"])
        self.assertNotIn("record:REC_REPORT", w.s["records"])
        self.assertFalse(w.has_claim("actor:W1", "anomaly"))
        self.assertFalse(w.has_claim("actor:I1", "anomaly"))
        run_until(w, f)
        self.assertEqual(w.s["processes"]["process:CASE"]["review_support"], ["record:REC_COPY"])
        self.assertTrue(w.has_claim("actor:I1", "alias_attribution"))
        w, _, _ = run(changes=changes + [change("world.actors.5.prior_alias_appearance_sample", False)])
        self.assertTrue(w.has_claim("actor:I1", "anomaly"))
        self.assertFalse(w.has_claim("actor:I1", "alias_attribution"))
        self.assertFalse(w.has_claim("actor:V0", "alias_inquiry"))

    def test_NQR02_witness_only(self):
        w, _, _ = run(changes=[change("world.device.capture_enabled", False)])
        self.assertNotIn("record:REC_ORIG", w.s["records"])
        self.assertNotIn("record:REC_COPY", w.s["records"])
        self.assertTrue(w.has_claim("actor:W2", "anomaly"))
        self.assertEqual(w.s["processes"]["process:CASE"]["review_support"], ["record:REC_REPORT"])

    def test_NQR02_no_channels_no_omniscient_case(self):
        w, _, _ = run(changes=[change("scenario_profile.witness_enabled", False), change("world.device.capture_enabled", False)])
        self.assertNotIn("process:CASE", w.s["processes"])
        self.assertFalse(events(w, "VisitPlanned"))
        self.assertEqual(w.s["actors"]["actor:M0"]["condition"], "resolved_incident_victim")
        self.assertFalse(w.has_claim("actor:I1", "anomaly"))

    def test_NQR03_late_cleanup_and_causes(self):
        w, _, expected = run()
        self.assertEqual(observe(w), expected)
        original = w.s["records"]["record:REC_ORIG"]
        copy_record = w.s["records"]["record:REC_COPY"]
        self.assertEqual(copy_record["derived_from"], original["id"])
        self.assertEqual(copy_record["integrity"], "intact")
        self.assertEqual(copy_record["custody"], "institution:P1")
        self.assertIn("TravelStarted", {e["type"] for e in w.ancestors(original["removed_by"])})
        self.assertIn("ResolvedIncident", {e["type"] for e in w.ancestors(copy_record["cause"])})
        self.assertEqual(sum(e["payload"].get("charged", 0) for e in events(w, "TravelStarted")), 1)

    def test_NQR04_early_removal_preserves_testimony(self):
        w, _, expected = run("early_removal")
        self.assertEqual(observe(w), expected)
        self.assertEqual(events(w, "RecordRemoved")[0]["tick"], 3)
        self.assertTrue(events(w, "CopyBlocked"))
        self.assertTrue(w.has_claim("actor:W1", "anomaly"))
        self.assertTrue(w.has_claim("actor:W2", "anomaly"))

    def test_NQR05_denied_access_and_missing_information(self):
        for key in ("denied_access", "insufficient_directive"):
            with self.subTest(case=key):
                w, _, expected = run(key)
                self.assertEqual(observe(w), expected)
                travel = [e for e in events(w, "TravelStarted") if e["source"] == "actor:G1"]
                self.assertEqual(len(travel), int(key == "denied_access"))

    def test_NQR05_idempotency_after_save_and_collision(self):
        fixture, _ = prepare()
        w = run_until(World(fixture), fixture, 6)
        row = fixture["external_inputs"][1]
        payload = {k: v for k, v in row.items() if k not in ("type", "tick", "input_seq")}
        command_id = "command:input-2"
        prior = w.explain_command(command_id)["result"]
        w.load(w.snapshot())
        before = w.snapshot()
        self.assertEqual(w.command(command_id, "SendMessage", payload), prior)
        self.assertEqual(w.snapshot(), before)
        payload["directive"]["deadline_tick"] = 99
        self.assertEqual(w.command(command_id, "SendMessage", payload)["reason"], "COMMAND_ID_COLLISION")
        self.assertEqual(w.snapshot(), before)

    def test_NQR05_insufficient_resources_and_expired_deadline(self):
        w, _, _ = run(changes=[change("world.actors.4.task_budget", 0)])
        self.assertEqual(w.s["processes"]["process:CLEANUP"]["result"], "insufficient_resources")
        self.assertEqual(w.s["actors"]["actor:G1"]["reservation"], 0)
        w, _, _ = run(changes=[change("external_inputs.1.directive.deadline_tick", 4)])
        self.assertEqual(w.s["processes"]["process:CLEANUP"]["result"], "deadline_expired")
        self.assertEqual(w.s["actors"]["actor:G1"]["task_budget"], 1)
        self.assertTrue(w.s["records"]["record:REC_ORIG"]["available"])

    def test_NQR05_revalidate_availability_and_permission_at_action(self):
        for actor_unavailable in (False, True):
            f, _ = prepare()
            w = run_until(World(f), f, 5)
            if actor_unavailable:
                w.command("command:unavailable", "ChangeAvailability", {"actor": "actor:G1", "value": "unavailable"})
            else:
                w.s["grants"]["grant:ORIGINAL_ACCESS"]["enabled"] = False  # Harness configuration intervention.
            run_until(w, f)
            self.assertTrue(w.s["records"]["record:REC_ORIG"]["available"])
            self.assertEqual(w.s["processes"]["process:CLEANUP"]["state"], "blocked")

    def test_unavailable_agent_cannot_report_until_reactivated(self):
        w, f, _ = run(tick=5)
        w.command("command:unavailable", "ChangeAvailability", {"actor": "actor:G1", "value": "unavailable"})
        run_until(w, f)
        self.assertNotIn("message:RESULT", w.s["messages"])
        self.assertTrue(events(w, "TaskReportDeferred"))
        w.command("command:reactivated", "ChangeAvailability", {"actor": "actor:G1", "value": "active"})
        w.advance_to(12)
        self.assertEqual(w.s["messages"]["message:RESULT"]["status"], "received")

    def test_NQR06_cleanup_access_trace_is_acquired(self):
        f, _ = prepare()
        f["scenario_profile"]["access_log_enabled"] = True
        w = run_until(World(f), f, 7)
        log = w.s["records"]["record:ACCESS_LOG"]
        self.assertEqual(log["content"]["actor"], "actor:G1")
        self.assertFalse(w.has_claim("actor:I1", "cleanup_by_G1"))
        run_until(w, f)
        self.assertTrue(w.has_claim("actor:I1", "cleanup_by_G1"))
        self.assertTrue(w.who_accessed(log["id"]))
        acquired = next(m for m in w.s["memories"].values() if m["holder"] == "actor:I1" and "cleanup_by_G1" in m["content"].get("claims", []))
        self.assertNotIn("location:L_HAV", json.dumps(acquired))
        self.assertNotIn("clan", json.dumps(acquired))
        self.assertIn("record:REC_REPORT", w.s["records"])

    def test_NQR07_refusal_to_report_and_independent_video(self):
        changes = [change("scenario_profile.recipient_reports", False)]
        w, _, _ = run(changes=changes)
        self.assertTrue(w.has_claim("actor:W2", "anomaly"))
        self.assertNotIn("record:REC_REPORT", w.s["records"])
        self.assertEqual(w.s["processes"]["process:CASE"]["review_support"], ["record:REC_COPY"])
        w, _, _ = run(changes=changes + [change("world.device.capture_enabled", False)])
        self.assertNotIn("process:CASE", w.s["processes"])

    def test_NQR07_inaccessible_record_denies_content_without_effects(self):
        w, _, _ = run(tick=5)
        before = w.snapshot()
        result = w.command("command:copy-spying", "InspectRecord", {"actor": "actor:G1", "record": "record:REC_COPY"})
        self.assertEqual(result["reason"], "ACCESS_DENIED")
        self.assertEqual(w.snapshot(), before)
        w.advance_to(6)
        before = w.snapshot()
        result = w.command("command:removed-reading", "InspectRecord", {"actor": "actor:I1", "record": "record:REC_ORIG"})
        self.assertEqual(result["reason"], "RECORD_INACCESSIBLE")
        self.assertEqual(w.snapshot(), before)

    def test_NQR08_all_cases_equal_at_every_commit_before_and_after_reload(self):
        for case in read_fixture()["cases"]:
            with self.subTest(case=case["id"]):
                f, expected = prepare(case["id"])
                continuous = run_until(TracingWorld(f), f)
                restored = run_until(TracingWorld(f, reload_each=True), f)
                self.assertEqual(restored.checkpoints, continuous.checkpoints)
                self.assertEqual(restored.snapshot(), continuous.snapshot())
                self.assertEqual(observe(restored), expected)
                self.assertTrue(any(e["type"] == "VisitPlanned" for e in restored.s["events"].values()))
                self.assertEqual(len(events(restored, "RecordCopied")), int(expected["copy_exists"]))
                self.assertEqual(len(events(restored, "RecordRemoved")), int(not expected["original_available"]))

    def test_NQR08_visit_is_pending_at_save_and_arrives_later(self):
        w, f, _ = run(tick=9)
        self.assertTrue(w.s["actors"]["actor:I1"]["travelling"])
        self.assertEqual(w.s["actors"]["actor:I1"]["location"], "location:L_REG")
        self.assertEqual(w.player_view()["actions"], ["ChangeAvailability"])
        pending = next(q for q in w.pending_world_work() if q["payload"].get("actor") == "actor:I1")
        self.assertEqual(pending["due_tick"], 12)
        w.load(w.snapshot())
        run_until(w, f)
        self.assertEqual(w.s["processes"]["process:CASE"]["visit_tick"], 12)

    def test_NQR09_causal_explanations_and_player_projection(self):
        w, _, _ = run()
        kinds = {e["type"] for e in w.why_process_started("process:CASE")}
        self.assertTrue({"ResolvedIncident", "IncidentObserved", "MessageSent", "MessageReceived", "ReportSubmitted", "CaseOpened"}.issubset(kinds))
        self.assertEqual(w.s["actors"]["actor:V0"]["location"], "location:L_INC")
        self.assertTrue(w.has_claim("actor:V0", "alias_inquiry"))
        self.assertFalse(w.has_claim("actor:V0", "anomaly"))
        self.assertNotIn("record:REC_COPY", json.dumps(w.player_view()))
        source = events(w, "ResolvedIncident")[0]["id"]
        self.assertIn("RecordCopied", {e["type"] for e in w.descendants(source)})
        self.assertIn("VisitPlanned", {e["type"] for e in w.descendants(source)})
        before = w.snapshot()
        w.why_believes("actor:I1", "anomaly")
        w.why_process_started("process:CASE")
        w.descendants(source)
        w.who_accessed("record:REC_COPY")
        w.pending_world_work()
        w.explain_command("command:input-2")
        w.player_view()
        self.assertEqual(w.snapshot(), before)

    def test_NQR09_world_consequence_without_player_discovery(self):
        f, _ = prepare()
        f["scenario_profile"]["player_observes_visit"] = False
        w = run_until(World(f), f)
        self.assertEqual(w.s["processes"]["process:CASE"]["visit_tick"], 12)
        self.assertFalse(w.has_claim("actor:V0", "alias_inquiry"))


class BoundaryAcceptance(unittest.TestCase):
    def ordered_race(self, copy_first):
        f, _ = prepare()
        f["scenario_profile"]["copy_tick"] = 100  # Replace the authored attempt with a harness race.
        w = run_until(World(f), f, 5)
        old = next(q for q in w.s["queue"] if q["kind"] == "RemovalAttempt")
        w.s["queue"].remove(old)
        actions = [("CopyAttempt", "institution:P1"), ("RemovalAttempt", "actor:G1")]
        if not copy_first:
            actions.reverse()
        for kind, owner in actions:
            w.schedule(kind, 6, {}, owner, old["causes"])
        sequence = [q["enqueue_seq"] for q in w.s["queue"]]
        w.load(w.snapshot())
        self.assertEqual([q["enqueue_seq"] for q in w.s["queue"]], sequence)
        w.advance_to(6)
        return w

    def test_F01_same_tick_copy_first(self):
        w = self.ordered_race(True)
        self.assertIn("record:REC_COPY", w.s["records"])
        self.assertFalse(w.s["records"]["record:REC_ORIG"]["available"])
        ordered = [e["type"] for e in w.s["events"].values() if e["tick"] == 6]
        self.assertLess(ordered.index("RecordCopied"), ordered.index("RecordRemoved"))

    def test_F02_same_tick_removal_first(self):
        w = self.ordered_race(False)
        self.assertNotIn("record:REC_COPY", w.s["records"])
        self.assertTrue(events(w, "CopyBlocked"))
        self.assertIn("record:REC_REPORT", w.s["records"])

    def test_F03_presentation_discard_keeps_world_work(self):
        w, _, _ = run(tick=1)
        w.schedule_presentation("location:L_INC", "visual_callback")
        pending = w.pending_world_work()
        actors = copy.deepcopy(w.s["actors"])
        result = w.command("command:unload", "UnloadPresentation", {"location": "location:L_INC"})
        self.assertTrue(result["ok"])
        self.assertNotIn("location:L_INC", w.presentation)
        self.assertEqual(w.pending_world_work(), pending)
        self.assertEqual(w.s["actors"], actors)
        self.assertNotIn("presentation", json.loads(w.snapshot()))

    def test_F04_work_limit_is_persistent_and_preserves_pending_work(self):
        f, _ = prepare()
        w = World(f)
        def stress(world, q):
            world.schedule("Stress", world.s["tick"], {}, "institution:P1", q["causes"])
        w.extra_handlers["Stress"] = stress
        w.schedule("Stress", 0, {}, "institution:P1", [])
        with self.assertRaises(WorkLimit):
            w.advance_to(0)
        self.assertEqual(w.s["handlers_this_tick"], 128)
        self.assertEqual(sum(q["kind"] == "Stress" for q in w.s["queue"]), 1)
        saved = w.snapshot()
        w.load(saved)
        with self.assertRaises(WorkLimit):
            w.advance_to(0)
        self.assertEqual(w.snapshot(), saved)

    def test_F05_invalid_load_preserves_previous_world(self):
        w, _, _ = run(tick=9)
        prior = w.snapshot()
        for mutation in ("missing_actor", "version", "target", "allocator", "cause", "order", "counter"):
            with self.subTest(mutation=mutation):
                s = json.loads(prior)
                if mutation == "missing_actor":
                    del s["actors"]["actor:I1"]
                elif mutation == "version":
                    s["schema"] = "future-save"
                elif mutation == "target":
                    s["queue"][0]["payload"]["to"] = "location:MISSING"
                elif mutation == "allocator":
                    s["allocator"] = 0
                elif mutation == "cause":
                    first = next(iter(s["events"].values()))
                    first["causes"] = [first["id"]]
                elif mutation == "order":
                    s["queue"].reverse()
                    # Ensure invalid order even if only one pending work item.
                    s["queue"][0]["enqueue_seq"] = s["enqueue_seq"] + 1
                else:
                    s["handlers_this_tick"] = 129
                with self.assertRaises(InvalidSnapshot):
                    w.load(json.dumps(s))
                self.assertEqual(w.snapshot(), prior)

    def test_invalid_json_profile_and_duplicate_keys_fail_without_publication(self):
        w, _, _ = run(tick=9)
        prior = w.snapshot()
        incompatible = json.loads(prior)
        incompatible["profile_version"] = "unimplemented-rules"
        invalids = ["{", prior[:-1] + ',"tick":999}', json.dumps(incompatible)]
        for text in invalids:
            with self.assertRaises(InvalidSnapshot):
                w.load(text)
            self.assertEqual(w.snapshot(), prior)

    def test_F06_replay_and_pure_queries(self):
        a, _, _ = run()
        b, _, _ = run()
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.s["rng"]["draws"], 0)
        f, _ = prepare()
        w = World(f)
        before = w.snapshot()
        with self.assertRaises(Rejected):
            w.apply_input({**f["external_inputs"][0], "input_seq": 2})
        self.assertEqual(w.snapshot(), before)
        w.advance_to(1)
        before = w.snapshot()
        with self.assertRaises(Rejected):
            w.schedule("CopyAttempt", 0, {}, "institution:P1", [])
        self.assertEqual(w.snapshot(), before)

    def test_F07_original_copy_and_grants_have_separate_authority(self):
        w, f, _ = run(tick=4)
        copied = copy.deepcopy(w.s["records"]["record:REC_COPY"])
        memories = {key: copy.deepcopy(m) for key, m in w.s["memories"].items() if m["holder"] == "actor:W1"}
        run_until(w, f)
        self.assertEqual(w.s["records"]["record:REC_COPY"], copied)
        self.assertEqual({key: m for key, m in w.s["memories"].items() if m["holder"] == "actor:W1"}, memories)
        w, _, _ = run("denied_access")
        self.assertTrue(w.who_accessed("record:REC_COPY"))

    def test_transaction_rollback_includes_clock_resources_receipts_and_queue(self):
        f, _ = prepare()
        w = World(f)
        def explode(world, q):
            world.s["actors"]["actor:G1"]["task_budget"] -= 1
            world.event("PartialEffect", "actor:G1", causes=q["causes"])
            world.schedule("CopyAttempt", world.s["tick"], {}, "institution:P1", q["causes"])
            raise RuntimeError("injected interruption")
        w.extra_handlers["Explode"] = explode
        w.schedule("Explode", 1, {}, "institution:P1", [])
        before = w.snapshot()
        with self.assertRaisesRegex(RuntimeError, "injected interruption"):
            w.step()
        self.assertEqual(w.snapshot(), before)

    def test_cancel_after_removal_does_not_resurrect_evidence(self):
        w, f, _ = run(tick=6)
        self.assertFalse(w.s["records"]["record:REC_ORIG"]["available"])
        self.assertTrue(w.command("command:cancel", "CancelTask", {"actor": "actor:G1", "process": "process:CLEANUP"})["ok"])
        run_until(w, f)
        self.assertFalse(w.s["records"]["record:REC_ORIG"]["available"])
        self.assertIn("record:REC_COPY", w.s["records"])
        self.assertEqual(w.s["processes"]["process:CLEANUP"]["state"], "cancelled")
        self.assertTrue(events(w, "WorkCancelled"))

    def test_incident_injection_is_not_a_player_command(self):
        f, _ = prepare()
        w = World(f)
        before = w.snapshot()
        row = f["external_inputs"][0]
        payload = {k: v for k, v in row.items() if k not in ("type", "tick", "input_seq")}
        self.assertEqual(w.command("command:cheat", "InjectResolvedIncident", payload)["reason"], "HARNESS_ONLY")
        self.assertEqual(w.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
