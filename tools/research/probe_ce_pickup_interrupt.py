#!/usr/bin/env python3
"""Private CE ground pickup experiment, on an original ground item in a distinct starting-map fixture.

Preserves the upstream executable and data. Outputs are private, including PNGs.
Exploration/observations only: a successful process exit is not A2 acceptance.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import time

from PIL import ImageGrab
from run_fallout_ce_lab import CE_REVISION, CONFIGS, INPUTS, sha, symbols, read_state

BASELINE_BINARY = "70516cf855af0b8a5c826b0f090f646b29e5672c48e9b981322448edc6dc636c"
NAMES = {
    "DUDE": "fallout::gDude", "ELEVATION": "fallout::gElevation",
    "CURSOR_X": "fallout::gMouseCursorX", "CURSOR_Y": "fallout::gMouseCursorY",
    "HOT_X": "fallout::_mouse_hotx", "HOT_Y": "fallout::_mouse_hoty",
    "PROJECT": "fallout::tileToScreenXY(int, int*, int*, int)",
    "UNPROJECT": "fallout::tileFromScreenXY(int, int, int, bool)",
    "NEIGHBOR": "fallout::tileGetTileInDirection(int, int, int)",
    "BLOCKING": "fallout::_obj_blocking_at(fallout::Object*, int, int)",
    "MOUSE_MODE": "fallout::gGameMouseMode",
    "OBJECT_TABLE": "fallout::gObjectListHeadByTile",
    "RECT": "fallout::objectGetRect(fallout::Object*, fallout::Rect*)",
    "SELECT": "fallout::gameMouseGetObjectUnderCursor(int, bool, int)",
    "DISTANCE": "fallout::objectGetDistanceBetween(fallout::Object*, fallout::Object*)",
    "INV_INIT": "fallout::_inven_is_initialized", "INV_WINDOW": "fallout::gInventoryWindow",
    "WINDOW_BUFFER": "fallout::windowGetBuffer(int)", "INV_TARGET": "fallout::_target_stack",
    "MONITOR_START": "fallout::_disp_start", "MONITOR_CAP": "fallout::gDisplayMonitorLinesCapacity",
    "MONITOR_LINES": "fallout::gDisplayMonitorLines",
    "ITEM_TYPE":"fallout::itemGetType(fallout::Object*)",
    "CAN_PICKUP":"fallout::_proto_action_can_pickup(int)",
    "CAN_USE":"fallout::_obj_action_can_use(fallout::Object*)",
    "CAN_USE_ON":"fallout::_proto_action_can_use_on(int)",
    "CAN_UNLOAD":"fallout::weaponCanBeUnloaded(fallout::Object*)",
    "INV_CURSOR":"fallout::gInventoryCursor",
    "INV_SCROLL":"fallout::_stack_offset",
    "WINDOW_RECT":"fallout::windowGetRect(int, fallout::Rect*)",
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--ce-source", type=Path, required=True)
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--targets", type=int, nargs="*", default=[])
    p.add_argument("--six-directions", action="store_true")
    p.add_argument("--center-after-move", action="store_true",
                   help="Use CE's native Home key to recenter the camera after each observed move")
    p.add_argument("--record-frames", action="store_true",
                   help="Capture actual X frames at about 10 FPS for private visual evidence")
    p.add_argument("--locker-tile",type=int,default=12477)
    p.add_argument("--locker-id",type=int,default=200)
    p.add_argument("--locker-pid",type=int,default=4)
    p.add_argument("--scenario",choices=["complete","cancel-gesture","cancel-after","repeat-gesture","save-before","save-after","save-gesture"],default="complete")
    p.add_argument("--lab-deps",type=Path,required=True)
    args = p.parse_args()
    deps=args.lab_deps.resolve()
    assert 0<=args.locker_tile<40000 and args.locker_pid>=0 and args.locker_id>=0
    binary, source, inputs, out = [v.resolve() for v in (args.binary, args.ce_source, args.inputs, args.output)]
    assert sha(binary) == BASELINE_BINARY, "Wrong reference executable"
    assert subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() == CE_REVISION
    assert not subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"], text=True)
    for name, expected in INPUTS.items():
        assert sha(inputs/name) == expected, "Wrong DAT identity: " + name
    out.mkdir(parents=True, exist_ok=False)
    work = out/"work"; work.mkdir(); (work/"data").mkdir()
    for name in INPUTS: (work/name).symlink_to(inputs/name)
    (work/"fallout2-ce").symlink_to(binary)
    configs={k:v.replace("NCR1.MAP","DENBUS1.MAP") for k,v in CONFIGS.items()}
    for name,text in configs.items():(work/name).write_text(text)
    layout_tool=out/"layout"
    include=["-I"+str(deps/"usr/include/SDL2"),"-I"+str(deps/"usr/include/x86_64-linux-gnu"),"-I"+str(source/"src")]
    layout_source=Path(__file__).with_name("ce_animation_layout.cc").resolve()
    subprocess.run(["g++","-std=c++17","-O2","-ffunction-sections","-fdata-sections",*include,str(layout_source),"-Wl,--gc-sections","-o",str(layout_tool)],check=True)
    layout=json.loads(subprocess.check_output([str(layout_tool)],text=True))
    assert layout["sequence_size"]==4416 and layout["description_size"]==80,"Wrong native layout"
    nm = subprocess.check_output(["nm", "-C", str(binary)], text=True)
    addresses = {line.split(maxsplit=2)[2]: int(line.split()[0], 16)
                 for line in nm.splitlines() if len(line.split(maxsplit=2)) == 3
                 and line.split(maxsplit=2)[2] in NAMES.values()}
    NAMES.update(SEQUENCES="fallout::gAnimationSequences",PICKUP="fallout::_obj_pickup(fallout::Object*, fallout::Object*)",NEXT_TO="fallout::_is_next_to(fallout::Object*, fallout::Object*)",AP_COST="fallout::_check_scenery_ap_cost(fallout::Object*, fallout::Object*)")
    addresses.update({line.split(maxsplit=2)[2]:int(line.split()[0],16) for line in nm.splitlines() if len(line.split(maxsplit=2))==3 and line.split(maxsplit=2)[2] in NAMES.values()})
    offsets = {key: addresses[name] for key, name in NAMES.items()}
    (out/"ce_probe_offsets.h").write_text("\n".join(f"constexpr uintptr_t OFF_{key}=0x{v:x};" for key,v in offsets.items())+"\n"+"\n".join(f"constexpr size_t LAY_{key.upper()}={value};" for key,value in layout.items())+"\n")
    adapter_source = Path(__file__).with_name("ce_pickup_cycle_input.cc").resolve()
    adapter = out/"ce_pickup_input.so"
    subprocess.run(["g++", "-shared", "-fPIC", "-std=c++17", "-O2", *include, "-I"+str(out), str(adapter_source), "-o", str(adapter), "-ldl"], check=True)
    env = os.environ.copy()
    env["PATH"]=str(deps/"usr/bin")+os.pathsep+env["PATH"]
    env["LD_LIBRARY_PATH"]=str(deps/"usr/lib/x86_64-linux-gnu")+(os.pathsep+env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    env.update(CE_CONTAINER_TILE=str(args.locker_tile),CE_CONTAINER_ID=str(args.locker_id),CE_CONTAINER_PID=str(args.locker_pid),DISPLAY="127.0.0.1:27875", SDL_AUDIODRIVER="dummy", DEBUGACTIVE="log",
               LD_PRELOAD=str(adapter), CE_PROBE_COMMAND=str(out/"command"), CE_PROBE_RECEIPT=str(out/"receipt.json"),
               CE_PROBE_MOTION=str(out/"motion.jsonl"))
    trace, cases = [], []
    seq = 0; start = time.monotonic()
    def note(event, **data): trace.append(dict(t_ms=round((time.monotonic()-start)*1000),event=event,**data))
    def command(tile=-1, buttons=0, xy=(0,0)):
        nonlocal seq
        seq += 1
        tmp = out/"command.tmp"; tmp.write_text(f"{seq} {tile} {buttons} {xy[0]} {xy[1]}\n"); tmp.replace(out/"command")
        for _ in range(100):
            try:
                r = json.loads((out/"receipt.json").read_text())
                if r["sequence"] == seq:
                    note("native_input_receipt", **r)
                    return r
            except (OSError, json.JSONDecodeError): pass
            if game.poll() is not None: raise RuntimeError("CE exited")
            time.sleep(.02)
        raise RuntimeError("Input receipt timed out")
    def capture(name):
        ImageGrab.grab(xdisplay=env["DISPLAY"]).save(out/(name+".png"))
        note("capture", file=name+".png")
    def move(tile, label):
        before = command()
        receipt = command(tile)
        time.sleep(.1)
        actual = command()
        if receipt["roundtrip_tile"] != tile or actual["cursor_tile_before"] != tile:
            raise RuntimeError("Requested tile does not match native cursor selection")
        command(buttons=1); time.sleep(.2); command(buttons=0)
        samples = []; move_start = time.monotonic(); settled = 0; prior = None
        frames = []; frame_times = []; last_frame = -1
        while time.monotonic()-move_start < 12:
            state = read_state(game.pid,binary,symbols_cache)["actor"]
            sample = dict(dt_ms=round((time.monotonic()-move_start)*1000),**state)
            samples.append(sample)
            if args.record_frames and sample["dt_ms"]-last_frame >= 100:
                frames.append(ImageGrab.grab(xdisplay=env["DISPLAY"]))
                frame_times.append(sample["dt_ms"]); last_frame=sample["dt_ms"]
            pose = (state["tile"],state["x"],state["y"],state["frame"],state["fid"])
            settled = settled+1 if pose == prior else 0; prior = pose
            if time.monotonic()-move_start > .8 and settled >= 10: break
            time.sleep(.04)
        after = command()
        if frames:
            durations=[max(20,b-a) for a,b in zip(frame_times,frame_times[1:])]+[600]
            frames[0].save(out/(label+".gif"),save_all=True,append_images=frames[1:],duration=durations,loop=0)
        if args.center_after_move:
            subprocess.run(["xdotool", "key", "Home"], env=env, check=True)
            note("key", key="Home")
            time.sleep(.5)
        capture(label)
        route=[]
        for sample in samples:
            if not route or route[-1] != sample["tile"]: route.append(sample["tile"])
        case=dict(label=label,requested_tile=tile, before=before, projection=receipt,
                  cursor_verified=actual, samples=samples, route=route, after=after,
                  settled=settled >= 10, sampling_limit_seconds=12,
                  captured_frame_times_ms=frame_times,
                  input_sequence_range=[before["sequence"],after["sequence"]])
        cases.append(case)
        print(label, "target",tile,"route",route,"end",after["dude"]["tile"],flush=True)
        return after
    symbols_cache=symbols(binary)
    with (out/"xvfb.log").open("w") as xl,(out/"runtime.log").open("w") as rl:
        x=subprocess.Popen(["Xvfb",":27875","-screen","0","800x600x24","-nolisten","unix","-nolisten","local","-listen","tcp","-ac"],stdout=xl,stderr=xl,env=env)
        game=None
        try:
            for _ in range(50):
                try:
                    with socket.create_connection(("127.0.0.1",33875),timeout=.1): break
                except OSError: time.sleep(.1)
            game=subprocess.Popen(["./fallout2-ce"],cwd=work,env=env,stdout=rl,stderr=rl)
            time.sleep(5)
            subprocess.run(["xdotool","key","n"],env=env,check=True);time.sleep(2)
            subprocess.run(["xdotool","key","t"],env=env,check=True);time.sleep(2)
            subprocess.run(["xdotool","key","Escape"],env=env,check=True);time.sleep(5)
            capture("startup-before-ready")
            deadline=time.monotonic()+40
            prior_ready=None
            while time.monotonic()<deadline:
                ready=read_state(game.pid,binary,symbols_cache)
                if (ready["map_name"],ready["actor"]["tile"])!=prior_ready:
                    note("startup_native_state",state=ready);print("startup",ready,flush=True);prior_ready=(ready["map_name"],ready["actor"]["tile"])
                if ready["map_name"]=="DENBUS1.MAP" and ready["actor"]["tile"]==13292:break
                if game.poll() is not None:raise RuntimeError("CE exited during map load")
                time.sleep(.25)
            else:raise RuntimeError("DENBUS1 initial actor not ready within 40 seconds")
            time.sleep(1)
            capture("initial")
            census=command(-2);(out/"initial-census.json").write_text(json.dumps(census,indent=2)+"\n")
            origin=census["dude"]["tile"]
            def key(name):
                subprocess.run(["xdotool","key",name],env=env,check=True);note("key",key=name);time.sleep(.25)
            def click(button=1):
                command(buttons=button);time.sleep(.12);return command()
            def mode(wanted):
                if command()["mouse_mode"]!=wanted:click(4);time.sleep(.15)
                assert command()["mouse_mode"]==wanted
            def select_watched():
                mode(1);state=command();rect=state["watched_rect"];selected=None
                for fy in (.5,.25,.75):
                    for fx in (.5,.25,.75):
                        xy=(round(rect[0]+(rect[2]-rect[0])*fx),round(rect[1]+(rect[3]-rect[1])*fy))
                        command(-3,xy=xy);time.sleep(.08);state=command();o=state.get("selected_object")
                        if o and o["id"]==state["watched_item"]["id"] and o["pid"]==state["watched_item"]["pid"]:selected=xy;break
                    if selected:break
                assert selected,"Ground item not selectable through normal UI"
                time.sleep(.3);return selected,command()
            def owned(state):
                owner=state.get("watched_owner");return owner is not None and owner["id"]==state["dude"]["id"] and owner["pid"]==state["dude"]["pid"]
            def await_pickup(label):
                frames=[];times=[];samples=[];begin=time.monotonic();effect=None;settled=0
                for i in range(140):
                    frames.append(ImageGrab.grab(xdisplay=env["DISPLAY"]));times.append(round((time.monotonic()-begin)*1000));time.sleep(.08);state=command();samples.append(state)
                    if owned(state) and effect is None:effect=state;capture(label+"-effect")
                    settled=settled+1 if effect is not None and ((state["dude"]["fid"]>>16)&255)==0 else 0
                    if settled>=8:break
                after=command();capture(label+"-final")
                frames[0].save(out/(label+".gif"),save_all=True,append_images=frames[1:],duration=[max(20,b-a) for a,b in zip(times,times[1:])]+[700],loop=0)
                assert effect is not None and owned(after),"Pickup did not transfer item"
                return dict(effect=effect,after=after,samples=samples,frame_times_ms=times)
            ground=command(-5);assert ground["watched_item"] is not None and ground["watched_portable"] and ground["watched_on_map"] and ground["watched_owner"] is None
            cases.append(dict(label="original-ground-item-fixture",initial=ground,map_name="DENBUS1.MAP",map_start_tile=13292))
            # Normal camera keys expose the original item without moving or teleporting the actor.
            key("Left");key("Left");key("Left")
            selected,before=select_watched();capture("ground-item-selected")
            assert before["watched_on_map"] and before["watched_owner"] is None
            def verify_owned(state):
                slots=[x for x in state["actor_inventory"] if x["object"]["pid"]==args.locker_pid]
                return owned(state) and not state["watched_on_map"] and state["watched_item"]["tile"]==-1 and len(slots)==1 and slots[0]["quantity"]==1
            def wait_for(label,predicate,seconds=8):
                deadline=time.monotonic()+seconds;samples=[]
                while time.monotonic()<deadline:
                    state=command();samples.append(state)
                    if predicate(state):return state,samples
                    time.sleep(.015)
                raise RuntimeError("Missing trigger: "+label)
            def save_and_load(label,state):
                # Clear lab's observed pointer before native load destroys/recreates objects.
                # This is not a gameplay write.
                key("F6");time.sleep(.5);capture(label+"-save-ui")
                files=[p for p in (work/"data").rglob("*") if p.is_file() and p.name.lower()=="save.dat"]
                if not files:
                    key("Return");time.sleep(.5);capture(label+"-save-confirm")
                    key("Return");time.sleep(.6)
                files=[p for p in (work/"data").rglob("*") if p.is_file() and p.name.lower()=="save.dat"]
                if not files:files=[]
                if not files:raise RuntimeError("Native save was not created; inspect private UI capture")
                saved=dict(label=label+"-saved",files={str(p.relative_to(work)):sha(p) for p in (work/"data").rglob("*") if p.is_file()},before=state,after=command())
                cases.append(saved)
                # Create a demonstrably different state before loading the native save.
                if not owned(state):
                    selected,_=select_watched();click();result=await_pickup(label+"-altered");cases.append(dict(label=label+"-altered",**result))
                else:
                    mode(0);target=command(12479);time.sleep(.08);actual=command();assert actual["cursor_tile_before"]==12479;click();time.sleep(1)
                altered=command();cases.append(dict(label=label+"-before-load",state=altered))
                command(-6);key("F7");time.sleep(1);capture(label+"-load-ui")
                # Initial quicksave selects a slot, subsequent quickload may still need confirmation.
                for _ in range(2):
                    key("Return");time.sleep(.4)
                rebound=command(-7);capture(label+"-loaded")
                cases.append(dict(label=label+"-loaded",state=rebound))
                assert rebound["dude"]["tile"]==saved["after"]["dude"]["tile"],"Native loaded tile differs from saved state"
                assert bool(owned(rebound))==bool(owned(saved["after"])),"Native loaded ownership differs"
                return rebound
            if args.scenario=="save-before":
                restored=save_and_load("before-effect",before)
                assert restored["watched_on_map"] and restored["watched_owner"] is None and not restored["actor_inventory"]
                selected,before=select_watched()
            command(buttons=1);time.sleep(.12);release=command()
            if args.scenario=="cancel-gesture":
                mode(0);prearm_target=command(12479);time.sleep(.04);prearm_verified=command();assert prearm_verified["cursor_tile_before"]==12479
            if args.scenario in ("cancel-gesture","repeat-gesture","save-gesture"):
                trigger,samples=wait_for("ground gesture before effect",lambda q:((q["dude"]["fid"]>>16)&255)==10 and q["dude"]["frame"]<=2 and not owned(q))
                capture("gesture-trigger")
                if args.scenario=="save-gesture":
                    key("F6");time.sleep(.5);capture("save-during-gesture-ui")
                    cases.append(dict(label="save-during-gesture-request",trigger=trigger,samples=samples,after=command()))
                    key("Escape");time.sleep(.2)
                elif args.scenario=="repeat-gesture":
                    command(-3,xy=selected);time.sleep(.03);repeat_verified=command();repeat_release=click();time.sleep(1.5);after=command()
                    cases.append(dict(label="repeat-gesture",trigger=trigger,trigger_samples=samples,verified=repeat_verified,release=repeat_release,after=after))
                else:
                    target=prearm_target;verified=prearm_verified
                    press=command(buttons=1);time.sleep(.025);stop_release=command();time.sleep(1.5);after=command();capture(args.scenario+"-after")
                    cases.append(dict(label=args.scenario,trigger=trigger,trigger_samples=samples,target=target,verified=verified,press=press,release=stop_release,after=after))
                    if not owned(after):
                        assert after["watched_on_map"] and not after["actor_inventory"]
                        selected,before=select_watched();click();time.sleep(.15);retry_extra=click()
                        cases.append(dict(label="gesture-retry-extra-click",receipt=retry_extra))
            if args.scenario=="cancel-after":
                mode(0);target=command(12479);time.sleep(.04);verified=command();assert verified["cursor_tile_before"]==12479
                trigger,samples=wait_for("owned during unfinished gesture",lambda q:verify_owned(q) and ((q["dude"]["fid"]>>16)&255)==10)
                movement_release=click()
                cases.append(dict(label="cancel-after-effect-request",target=target,verified=verified,trigger=trigger,trigger_samples=samples,release=movement_release))
            result=await_pickup("pickup-complete");result.update(label="pickup-complete",before=before,release=release,selected_pixel=selected);cases.append(result)
            assert verify_owned(result["after"]),"Ownership not unique"
            command(-3,xy=selected);time.sleep(.15);repeat_before=command();repeat_release=click();time.sleep(.7);repeat_after=command()
            if repeat_after["inventory_visible"]:key("Escape");repeat_after=command()
            assert verify_owned(repeat_after)
            cases.append(dict(label="former-pixel-repeat",before=repeat_before,release=repeat_release,after=repeat_after,pixel=selected,scope="Normal UI second click; not replay of an action receipt or target-ID"))
            if args.scenario=="save-after":
                restored=save_and_load("after-effect",repeat_after)
                assert verify_owned(restored)
            (out/"final-census.json").write_text(json.dumps(command(-2),indent=2)+"\n")
        finally:
            if game and game.poll() is None: game.terminate();game.wait(timeout=5)
            x.terminate();x.wait(timeout=5)
            unchanged={name:sha(inputs/name)==expected for name,expected in INPUTS.items()}
            result=dict(kind="CE_NATIVE_PICKUP_CYCLE_EXPERIMENT",layout=layout,layout_source_sha256=sha(layout_source),configs=configs,configs_sha256={name:sha(work/name) for name in configs},scenario=args.scenario,locker_identity=[args.locker_id,args.locker_pid,args.locker_tile,0],binary_sha256=sha(binary),ce_revision=CE_REVISION,
                        input_hashes=INPUTS, original_inputs_unchanged=unchanged,
                        adapter_source_sha256=sha(adapter_source),adapter_binary_sha256=sha(adapter),
                        controller_sha256=sha(Path(__file__)),native_symbol_offsets=offsets,
                        intervention="Controlled SDL relative mouse only; native projection/unprojection/neighbor/blocker queries. No authoritative gameplay state writes.",
                        cases=cases,trace=trace,
                        native_pose_changes=[json.loads(line) for line in (out/"motion.jsonl").read_text().splitlines()] if (out/"motion.jsonl").exists() else [],
                        captures={p.name:sha(p) for p in out.iterdir() if p.suffix in (".png", ".gif")},
                        limitations=["Native pose-change log and unsuspended receipt samples; no atomic contact or exact simulation duration claim", "CE Linux DAT-only reference, not Windows original or Vampiro acceptance", "Random seed remains default; NPCs can move during experiments"])
            (out/"evidence.json").write_text(json.dumps(result,indent=2)+"\n")
            assert all(unchanged.values())


if __name__ == "__main__": main()
