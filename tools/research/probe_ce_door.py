#!/usr/bin/env python3
"""Private CE navigation experiment, with controlled SDL input and native queries.

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
    args = p.parse_args()
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
    for name, text in CONFIGS.items(): (work/name).write_text(text)
    nm = subprocess.check_output(["nm", "-C", str(binary)], text=True)
    addresses = {line.split(maxsplit=2)[2]: int(line.split()[0], 16)
                 for line in nm.splitlines() if len(line.split(maxsplit=2)) == 3
                 and line.split(maxsplit=2)[2] in NAMES.values()}
    offsets = {key: addresses[name] for key, name in NAMES.items()}
    (out/"ce_probe_offsets.h").write_text("\n".join(f"constexpr uintptr_t OFF_{key}=0x{v:x};" for key,v in offsets.items())+"\n")
    adapter_source = Path(__file__).with_name("ce_door_input.cc").resolve()
    adapter = out/"ce_door_input.so"
    subprocess.run(["g++", "-shared", "-fPIC", "-std=c++17", "-O2", "-I/usr/include/SDL2", "-I"+str(source/"src"), "-I"+str(out), str(adapter_source), "-o", str(adapter), "-ldl"], check=True)
    env = os.environ.copy()
    env.update(DISPLAY="127.0.0.1:27875", SDL_AUDIODRIVER="dummy", DEBUGACTIVE="log",
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
        x=subprocess.Popen(["Xvfb",":27875","-screen","0","800x600x24","-nolisten","unix","-nolisten","local","-listen","tcp","-ac"],stdout=xl,stderr=xl)
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
            deadline=time.monotonic()+40
            while time.monotonic()<deadline:
                ready=read_state(game.pid,binary,symbols_cache)
                if ready["map_name"]=="NCR1.MAP" and ready["actor"]["tile"]==13915:break
                if game.poll() is not None:raise RuntimeError("CE exited during map load")
                time.sleep(.25)
            else:raise RuntimeError("NCR1 initial actor not ready within 40 seconds")
            time.sleep(1)
            capture("initial")
            census=command(-2);(out/"initial-census.json").write_text(json.dumps(census,indent=2)+"\n")
            origin=census["dude"]["tile"]
            # A normal right click switches CE from move to arrow mode.
            command(buttons=4);time.sleep(.12);command();time.sleep(.2)
            state=command()
            assert state["mouse_mode"]==1
            rect=state["door_rect"]
            selected=None
            # Bounded scan of visible door artwork; no gameplay state writes.
            for fy in (.5,.25,.75):
                for fx in (.5,.25,.75):
                    xy=(round(rect[0]+(rect[2]-rect[0])*fx),round(rect[1]+(rect[3]-rect[1])*fy))
                    command(-3,xy=xy);time.sleep(.08);state=command()
                    o=state.get("selected_object")
                    if o and (o["id"],o["pid"],o["tile"])==(26,33555281,15710):
                        selected=xy;break
                if selected:break
            assert selected, "Door artwork not selectable through normal UI"
            capture("door-selected")
            before=command();command(buttons=1);time.sleep(.12);command()
            frames=[];times=[];event_start=time.monotonic()
            for i in range(120):
                frames.append(ImageGrab.grab(xdisplay=env["DISPLAY"]))
                times.append(round((time.monotonic()-event_start)*1000))
                time.sleep(.1)
                if i>15 and command()["door"]["flags"] & 16:break
            after=command();capture("door-after-use")
            cases.append(dict(label="normal-door-use",before=before,after=after,selected_pixel=selected,frame_times_ms=times))
            if frames:
                frames[0].save(out/"door-use.gif",save_all=True,append_images=frames[1:],duration=[max(20,b-a) for a,b in zip(times,times[1:])]+[600],loop=0)
            if after["door"]["flags"] & 16:
                # Return to move mode by normal right click, cross the now-open tile.
                command(buttons=4);time.sleep(.12);command();time.sleep(.2)
                assert command()["mouse_mode"]==0
                move(15710,"cross-open-door")
                inside=command(15709)
                if inside["blocker"] is None:move(15709,"inside-door")
                subprocess.run(["xdotool","key","Home"],env=env,check=True);note("key",key="Home");time.sleep(.5)
                capture("interior")
            (out/"final-census.json").write_text(json.dumps(command(-2),indent=2)+"\n")
        finally:
            if game and game.poll() is None: game.terminate();game.wait(timeout=5)
            x.terminate();x.wait(timeout=5)
            unchanged={name:sha(inputs/name)==expected for name,expected in INPUTS.items()}
            result=dict(kind="CE_NATIVE_DOOR_EXPERIMENT",binary_sha256=sha(binary),ce_revision=CE_REVISION,
                        input_hashes=INPUTS, original_inputs_unchanged=unchanged,
                        adapter_source_sha256=sha(adapter_source),adapter_binary_sha256=sha(adapter),
                        controller_sha256=sha(Path(__file__)),native_symbol_offsets=offsets,
                        intervention="Controlled SDL relative mouse only; native projection/unprojection/neighbor/blocker queries. No authoritative gameplay state writes.",
                        cases=cases,trace=trace,
                        native_pose_changes=[json.loads(line) for line in (out/"motion.jsonl").read_text().splitlines()] if (out/"motion.jsonl").exists() else [],
                        captures={p.name:sha(p) for p in out.iterdir() if p.suffix in (".png", ".gif")},
                        limitations=["Unsuspended memory samples, about 40ms apart; no atomic phase or duration claim", "CE Linux DAT-only reference, not Windows original or Vampiro acceptance", "Random seed remains default; NPCs can move during experiments"])
            (out/"evidence.json").write_text(json.dumps(result,indent=2)+"\n")
            assert all(unchanged.values())


if __name__ == "__main__": main()
