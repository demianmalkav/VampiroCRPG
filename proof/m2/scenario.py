"""Fixture construction, stimulus delivery and observation; no outcome forcing."""
import copy
import json
from pathlib import Path

from .world import World

FIXTURE = Path(__file__).resolve().parents[2] / "tests/specs/m2_core_a_cases.json"


def read_fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def prepare(case_id="late_copy", changes=None):
    fixture = read_fixture()
    fixture["case_id"] = case_id
    case = next(c for c in fixture["cases"] if c["id"] == case_id)
    for override in case["overrides"] + (changes or []):
        parts = override["path"].split(".")
        node = fixture
        for part in parts[:-1]:
            node = node[int(part)] if isinstance(node, list) else node[part]
        key = int(parts[-1]) if isinstance(node, list) else parts[-1]
        node[key] = copy.deepcopy(override["value"])
    return fixture, copy.deepcopy(case["expected"])


def run_until(world, fixture, tick=12):
    for row in fixture["external_inputs"]:
        if row["input_seq"] > world.s["input_cursor"] and row["tick"] <= tick:
            result = world.apply_input(row)
            if not result["ok"]:
                raise AssertionError(f"Input rejected: {row!r}: {result!r}")
    world.advance_to(tick)
    return world


def run(case_id="late_copy", changes=None, tick=12):
    fixture, expected = prepare(case_id, changes)
    world = run_until(World(fixture), fixture, tick)
    return world, fixture, expected


def observe(world):
    r = world.s["records"]
    task = world.s["processes"].get("process:CLEANUP", {})
    case = world.s["processes"].get("process:CASE", {})
    result = world.s["messages"].get("message:RESULT", {})
    view = world.player_view()
    # The copy knowledge check evaluates the authorized player projection.
    return {"original_available": r.get("record:REC_ORIG", {}).get("available", False),
            "copy_exists": "record:REC_COPY" in r,
            "report_exists": "record:REC_REPORT" in r,
            "case_open": bool(case), "review_support": case.get("review_support", []),
            "task_terminal": task.get("state"), "g1_budget": world.s["actors"]["actor:G1"]["task_budget"],
            "g1_reservation": world.s["actors"]["actor:G1"]["reservation"],
            "result_message": result.get("content", {}).get("result"),
            "v0_knows_copy": "record:REC_COPY" in json.dumps(view),
            "visit_fired_tick": case.get("visit_tick"),
            "v0_observed_alias_inquiry": world.has_claim("actor:V0", "alias_inquiry")}
