#!/usr/bin/env python3
"""Validate archived door observations, without executing Fallout or accepting A2."""
import argparse
import hashlib
import json
from pathlib import Path

from ce_reference_identity import CE_REVISION, INPUTS
from check_ce_navigation_evidence import ELF_SHA, neighbors, require

DOOR = (26, 33555281, 15710, 0)


def identity(obj):
    return tuple(obj[k] for k in ("id", "pid", "tile", "elevation")) if obj else None


def check(data):
    require(data["a2_05"] == "REFERENCE_PARTIAL" and data["vampiro_status"] == "NOT_VERIFIED", "Scope overclaim")
    require(len(data["runs"]) >= 2, "Missing independent repetition")
    total = 0
    for run in data["runs"]:
        require(run["ce_revision"] == CE_REVISION and run["binary_sha256"] == ELF_SHA, "Reference identity mismatch")
        require(run["input_hashes"] == INPUTS and run["original_inputs_unchanged"] == {n: True for n in INPUTS}, "DAT preservation mismatch")
        cases = {c["label"]: c for c in run["cases"]}
        require({"normal-door-use", "cross-open-door", "inside-door"} <= cases.keys(), "Incomplete door sequence")
        use = cases["normal-door-use"]
        require(identity(use["before"]["selected_object"]) == DOOR and use["before"]["mouse_mode"] == 1, "Wrong selected object or mode")
        require(identity(use["before"]["door_blocker"]) == DOOR and use["before"]["door_open_flags"] == 0, "Missing closed baseline")
        records = run["native_pose_changes"]
        require(bool(records), "Missing native log")
        require(all(identity(r["door"]) == DOOR for r in records), "Door identity changed")
        require(all(r["blocker_at_actor"] is None for r in records), "Occupied actor tile")
        require(all(a["sdl_tick_ms"] <= b["sdl_tick_ms"] and a["input_sequence"] <= b["input_sequence"] for a,b in zip(records,records[1:])), "Chronology regressed")
        require(all(a["dude"]["tile"] == b["dude"]["tile"] or b["dude"]["tile"] in neighbors(a["dude"]["tile"]) for a,b in zip(records,records[1:])), "Route skipped hex")
        require(set(range(8)) <= {r["door"]["frame"] for r in records}, "Incomplete opening frames")
        early = [r for r in records if r["door_open_flags"] & 1 and not r["door"]["flags"] & 16]
        require(early and all(identity(r["door_blocker"]) == DOOR for r in early), "Early logical-open/blocking distinction lost")
        free = [r for r in records if r["door_blocker"] is None]
        require(free and all(r["door"]["frame"] == 7 and r["door"]["flags"] & 16 and r["door_open_flags"] & 1 for r in free), "Premature passage or inconsistent opening")
        require(all(r["door_blocker"] is None for r in records if r["dude"]["tile"] == 15710), "Crossing closed door")
        for label, target in (("cross-open-door",15710),("inside-door",15709)):
            case = cases[label]
            require(case["settled"] and case["after"]["dude"]["tile"] == target, "Arrival not measured")
            require(case["before"]["door_blocker"] is None, "Movement requested before opening")
            require(case["projection"]["roundtrip_tile"] == case["cursor_verified"]["cursor_tile_before"] == target and case["cursor_verified"]["mouse_mode"] == 0, "Wrong movement cursor")
            observed=[]
            lo,hi=case["input_sequence_range"]
            for r in records:
                if lo <= r["input_sequence"] <= hi and (not observed or observed[-1] != r["dude"]["tile"]):observed.append(r["dude"]["tile"])
            require(observed == case["route"], "Sampled and native routes disagree")
        if "reachable-locker-approach" in cases:
            case=cases["reachable-locker-approach"]
            require(case["requested_tile"] == 14499 and case["before"]["dude"]["tile"] == 15709, "Wrong locker approach")
            require(case["projection"]["blocker"] is not None and case["cursor_verified"]["cursor_tile_before"] == 14499, "Locker target not verified")
            require(case["settled"] and case["after"]["dude"]["tile"] in neighbors(14499) and len(case["route"]) > 1, "Locker not reached")
            lo,hi=case["input_sequence_range"];observed=[]
            for r in records:
                if lo <= r["input_sequence"] <= hi and (not observed or observed[-1] != r["dude"]["tile"]):observed.append(r["dude"]["tile"])
            require(observed == case["route"], "Locker route differs from native log")
        total += len(records)
    return {"status":"MEASURED_SCOPE_CHECKS_PASS","runs":len(data["runs"]),"native_pose_changes":total,"A2-05":"REFERENCE_PARTIAL","vampiro_acceptance":"NOT_VERIFIED"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("evidence",type=Path)
    p.add_argument("--check-source-hashes",action="store_true")
    a=p.parse_args();data=json.loads(a.evidence.read_text());result=check(data)
    if a.check_source_hashes:
        root=Path(__file__).resolve().parents[2]
        for name, expected in data["measured_source_hashes"].items():
            require(hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,"Measured source changed: "+name)
    print(json.dumps(result))


if __name__ == "__main__": main()
