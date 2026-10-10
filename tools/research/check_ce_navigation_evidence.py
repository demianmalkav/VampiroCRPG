#!/usr/bin/env python3
"""Check the scope and integrity of measured CE navigation, never Vampiro acceptance."""
import argparse
import hashlib
import json
from pathlib import Path

from run_fallout_ce_lab import CE_REVISION, INPUTS

ELF_SHA = "70516cf855af0b8a5c826b0f090f646b29e5672c48e9b981322448edc6dc636c"
LABELS = {f"{prefix}-{d}" for prefix in ("direction", "return") for d in range(6)}
LABELS |= {f"target-{i}-{tile}" for i, tile in enumerate(
    (13912, 13911, 13915, 14310, 12519, 13710, 13909, 14902, 14499))}


def neighbors(tile):
    # Object-grid parity, width 200, pinned CE tile.cc; not the square C grid.
    offsets = (-201, -1, 200, 1, -199, -200) if tile % 2 else (-1, 199, 200, 201, 1, -200)
    return [tile + offset for offset in offsets]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(evidence):
    require(evidence["ce_revision"] == CE_REVISION, "CE identity mismatch")
    require(evidence["binary_sha256"] == ELF_SHA, "Executable identity mismatch")
    require(evidence["input_hashes"] == INPUTS, "DAT identity mismatch")
    require(evidence["original_inputs_unchanged"] == {name: True for name in INPUTS}, "DAT changed or missing check")
    cases = evidence["cases"]
    require(len(cases) == len(LABELS) and {c["label"] for c in cases} == LABELS,
            "Measured case set incomplete or duplicated")
    motion = evidence["native_tile_transitions"]
    require(bool(motion), "Native motion log missing")
    require(all(m["blocker_at_actor"] is None for m in motion), "Observed occupied actor tile")
    require(all(a["sdl_tick_ms"] <= b["sdl_tick_ms"] for a, b in zip(motion, motion[1:])), "Motion clock regressed")
    by_label = {c["label"]: c for c in cases}
    previous_end = 13915
    accounted = 1  # Initial observation, before any movement request.
    require(motion[0]["dude"]["tile"] == previous_end, "Unexpected initial actor tile")
    for case in cases:
        label, target = case["label"], case["requested_tile"]
        require(case["settled"], f"{label}: observation timed out")
        require(case["projection"]["requested_tile"] == target and case["projection"]["roundtrip_tile"] == target,
                f"{label}: projection selects wrong tile")
        require(case["cursor_verified"]["cursor_tile_before"] == target and case["cursor_verified"]["mouse_mode"] == 0,
                f"{label}: native movement cursor selects wrong tile")
        before, after = case["before"]["dude"], case["after"]["dude"]
        require(before["tile"] == previous_end, f"{label}: case continuity lost")
        require(before["elevation"] == after["elevation"] == 0, f"{label}: unexpected elevation")
        lo, hi = case["input_sequence_range"]
        require(lo == case["before"]["sequence"] and hi == case["after"]["sequence"] and lo < hi,
                f"{label}: input boundaries mismatch")
        events = [m for m in motion if lo <= m["input_sequence"] <= hi]
        accounted += len(events)
        native_route = [before["tile"]] + [m["dude"]["tile"] for m in events]
        require(native_route == case["route"], f"{label}: sampled and native routes disagree")
        require(native_route[-1] == after["tile"], f"{label}: endpoint mismatch")
        require(all(b in neighbors(a) for a, b in zip(native_route, native_route[1:])), f"{label}: skipped hex")
        require(case["before"]["neighbors"] == neighbors(before["tile"]), f"{label}: native neighbor table differs")
        if label.startswith("direction-"):
            direction = int(label.rsplit("-", 1)[1])
            require(before["tile"] == 13915 and target == neighbors(13915)[direction] and after["tile"] == target,
                    f"{label}: native direction not reached")
        elif label.startswith("return-"):
            require(target == after["tile"] == 13915, f"{label}: return incomplete")
        blocker = case["projection"]["blocker"]
        if blocker is None:
            require(after["tile"] == target, f"{label}: chosen free destination not reached")
        else:
            require(target not in native_route, f"{label}: occupied destination entered")
        previous_end = after["tile"]
    require(accounted == len(motion), "Unattributed native transition or overlapping case ranges")
    for tile, label in ((13912, "target-0-13912"), (14310, "target-3-14310"),
                        (12519, "target-4-12519"), (13710, "target-5-13710")):
        c = by_label[label]
        require(c["projection"]["blocker"] is not None and c["after"]["dude"]["tile"] in neighbors(tile),
                f"{label}: occupied-destination adjacent approach missing")
    bypass = by_label["target-2-13915"]["route"]
    require(len(bypass) > 2 and 13912 not in bypass, "Streetlight bypass missing")
    for label in ("target-7-14902", "target-8-14499"):
        require(by_label[label]["route"] == [13909], f"{label}: inaccessible-building observation changed")
    return {"status": "MEASURED_SCOPE_CHECKS_PASS", "cases": len(cases), "native_tile_observations": len(motion),
            "a2_01": "REFERENCE_PARTIAL", "a2_02": "REFERENCE_PARTIAL", "vampiro_acceptance": "NOT_VERIFIED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--check-source-hashes", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.evidence.read_text())
    if args.check_source_hashes:
        for name, key in (("ce_navigation_input.cc", "adapter_source_sha256"),
                          ("probe_ce_navigation.py", "controller_sha256")):
            actual = hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            require(actual == data[key], "Measured source mismatch: " + name)
    print(json.dumps(check(data), indent=2))


if __name__ == "__main__":
    main()
