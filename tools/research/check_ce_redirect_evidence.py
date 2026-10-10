#!/usr/bin/env python3
"""Reject incomplete/misidentified A2-03 evidence; do not certify Vampiro behavior."""
import argparse
import hashlib
import json
from pathlib import Path

from ce_reference_identity import CE_REVISION, INPUTS
from check_ce_navigation_evidence import ELF_SHA, neighbors, require


def animation(dude):
    return (dude["fid"] >> 16) & 255


def pose(dude):
    return tuple(dude[k] for k in ("tile", "x", "y", "frame", "rotation", "fid"))


def native_poses(data):
    keys = data["native_pose_columns"]
    result = []
    for row in data["native_pose_rows"]:
        require(len(row) == len(keys), "Native pose row schema mismatch")
        item = dict(zip(keys, row))
        result.append(dict(sdl_tick_ms=item["sdl_tick_ms"],input_sequence=item["input_sequence"],
            dude={k:item[k] for k in ("id","tile","x","y","frame","rotation","fid","flags","elevation")},
            anchor_xy=[item["anchor_x"],item["anchor_y"]],blocker_at_actor=item["blocker_at_actor"]))
    return result


def check(data):
    require(data["ce_revision"] == CE_REVISION and data["binary_sha256"] == ELF_SHA, "Reference identity mismatch")
    require(data["input_hashes"] == INPUTS and data["original_inputs_unchanged"] == {n:True for n in INPUTS}, "DAT preservation mismatch")
    require(data["failure"] is None, "Incomplete experiment")
    cases = data["cases"]
    require(len(cases)==5 and {c["scenario"] for c in cases}=={"single","repeated","rapid","escape","stop"}, "Scenario coverage incomplete")
    records = native_poses(data)
    require(bool(records) and all(r["blocker_at_actor"] is None for r in records), "Occupied actor tile or missing log")
    require(all(a["sdl_tick_ms"]<=b["sdl_tick_ms"] and a["input_sequence"]<=b["input_sequence"] for a,b in zip(records,records[1:])), "Native chronology regressed")
    require(all(a["dude"]["tile"]==b["dude"]["tile"] or b["dude"]["tile"] in neighbors(a["dude"]["tile"]) for a,b in zip(records,records[1:])), "Native route skipped hex")
    expected={"single":14115,"repeated":13911,"rapid":13716,"escape":13911,"stop":13915}
    for case in cases:
        name=case["scenario"]
        require(case.get("complete") is True and case["start"]["dude"]["tile"]==13915, name+": incomplete or wrong start")
        require(case["initial"]["target"]==13911, name+": initial walking request mismatch")
        end=case["endpoint"]["dude"]
        require(end["tile"]==expected[name] and animation(end)==0 and end["x"]==end["y"]==0, name+": standing endpoint mismatch")
        require(animation(case["trigger"]["dude"])==1 and (case["trigger"]["dude"]["x"] or case["trigger"]["dude"]["y"]), name+": missing partial-walk trigger")
        for action in [case["initial"]]+case["actions"]:
            require(action["projection"]["roundtrip_tile"]==action["target"]==action["projection"]["requested_tile"], name+": projected destination mismatch")
            require(action["verified"]["cursor_tile_before"]==action["target"] and action["verified"]["mouse_mode"]==0, name+": native cursor mismatch")
        require(len(case["actions"])==(0 if name=="escape" else 2 if name=="rapid" else 1), name+": action count mismatch")
        targets={"single":[14115],"repeated":[13911],"rapid":[14115,13716],"escape":[],"stop":[13915]}
        require([a["target"] for a in case["actions"]]==targets[name], name+": interruption target mismatch")
        require(len(case["interrupt_boundaries"])==len(case["actions"]), name+": boundary count mismatch")
        for action,boundary in zip(case["actions"],case["interrupt_boundaries"]):
            receipt=action["release_before_handling"];before=receipt["dude"]
            require(before["x"] or before["y"], name+": input was at a node, not partial step")
            require(any(r["input_sequence"]==receipt["sequence"] and r["sdl_tick_ms"]<=receipt["sdl_tick_ms"] and pose(r["dude"])==pose(before) and r["anchor_xy"]==receipt["anchor_xy"] for r in records), name+": pre-input pose absent from native log")
            candidates=[r for r in records if receipt["sequence"]<=r["input_sequence"]<=case["endpoint"]["sequence"] and receipt["sdl_tick_ms"]<r["sdl_tick_ms"]<=case["endpoint"]["sdl_tick_ms"] and pose(r["dude"])!=pose(before)]
            require(bool(candidates), name+": no post-input pose")
            first=candidates[0];derived=boundary["first_changed_pose"]
            require(pose(first["dude"])==pose(derived["dude"]) and first["anchor_xy"]==derived["anchor_xy"] and first["sdl_tick_ms"]==derived["sdl_tick_ms"], name+": claimed first changed pose differs from log")
            delta=[b-a for a,b in zip(receipt["anchor_xy"],first["anchor_xy"])]
            require(delta==boundary["delta_anchor_xy"] and boundary["elapsed_native_ms"]==first["sdl_tick_ms"]-receipt["sdl_tick_ms"], name+": boundary measurement mismatch")
            require(first["dude"]["tile"]==before["tile"] and first["dude"]["frame"]==0, name+": same-tile frame reset not observed")
            if name=="repeated":
                require(animation(before)==1 and animation(first["dude"])==19, "Repeated destination did not select running animation")
            elif name=="stop":
                require(action["target"]==before["tile"] and animation(first["dude"])==0 and first["dude"]["x"]==first["dude"]["y"]==0, "Current-tile stop not observed")
            else:
                require(animation(first["dude"])==1 and first["dude"]["rotation"]!=before["rotation"], name+": changed-direction walking pose missing")
        if name=="escape":
            opened,later=case["options_open"],case["options_later"]
            require(later["sdl_tick_ms"]-opened["sdl_tick_ms"]>=700 and pose(opened["dude"])==pose(later["dude"]), "Options pose not held for measured interval")
            interval=[r for r in records if opened["sdl_tick_ms"]<=r["sdl_tick_ms"]<=later["sdl_tick_ms"]]
            require(interval and all(pose(r["dude"])==pose(opened["dude"]) for r in interval), "Movement continued inside options interval")
            require(pose(case["after_options_close"]["dude"])!=pose(opened["dude"]), "Original route did not resume")
    return {"status":"MEASURED_SCOPE_CHECKS_PASS","scenarios":len(cases),"native_pose_snapshots":len(records),"A2-03":"REFERENCE_PARTIAL","vampiro_acceptance":"NOT_VERIFIED"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence",type=Path)
    parser.add_argument("--check-source-hashes",action="store_true")
    args=parser.parse_args();data=json.loads(args.evidence.read_text())
    if args.check_source_hashes:
        for file,key in (("ce_redirect_input.cc","adapter_source_sha256"),("probe_ce_redirect.py","controller_sha256")):
            require(hashlib.sha256(Path(__file__).with_name(file).read_bytes()).hexdigest()==data[key], "Measured source mismatch: "+file)
    print(json.dumps(check(data),indent=2))


if __name__=="__main__":
    main()
