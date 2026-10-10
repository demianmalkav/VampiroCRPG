#!/usr/bin/env python3
"""Private A2-03 experiments: native input, sub-tile poses and real X frames.

No gameplay writes or upstream modifications. Escape and click-current-tile
are separate stimuli; neither is silently assumed to match Vampiro policy.
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
from probe_ce_navigation import BASELINE_BINARY, NAMES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("binary", "ce-source", "inputs", "output"):
        parser.add_argument("--"+name, type=Path, required=True)
    parser.add_argument("--scenarios", nargs="+", choices=("single", "repeated", "rapid", "escape", "stop"), default=["single"])
    args = parser.parse_args()
    binary, source, inputs, out = [p.resolve() for p in (args.binary, args.ce_source, args.inputs, args.output)]
    if sha(binary) != BASELINE_BINARY:
        raise ValueError("Wrong executable")
    if subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip() != CE_REVISION:
        raise ValueError("Wrong CE revision")
    if subprocess.check_output(["git", "-C", str(source), "status", "--porcelain"], text=True):
        raise ValueError("CE source is dirty")
    for name, expected in INPUTS.items():
        if sha(inputs/name) != expected:
            raise ValueError("Wrong DAT: " + name)
    out.mkdir(parents=True, exist_ok=False)
    work = out/"work"; work.mkdir(); (work/"data").mkdir()
    for name in INPUTS:
        (work/name).symlink_to(inputs/name)
    (work/"fallout2-ce").symlink_to(binary)
    for name, value in CONFIGS.items():
        (work/name).write_text(value)
    addresses = {}
    for line in subprocess.check_output(["nm", "-C", str(binary)], text=True).splitlines():
        parts = line.split(maxsplit=2)
        if len(parts) == 3 and parts[2] in NAMES.values():
            addresses[parts[2]] = int(parts[0], 16)
    offsets = {key: addresses[value] for key, value in NAMES.items()}
    (out/"ce_probe_offsets.h").write_text("\n".join(f"constexpr uintptr_t OFF_{key}=0x{value:x};" for key,value in offsets.items())+"\n")
    adapter_source = Path(__file__).with_name("ce_redirect_input.cc").resolve()
    adapter = out/"ce_redirect_input.so"
    subprocess.run(["g++", "-shared", "-fPIC", "-std=c++17", "-O2", "-I/usr/include/SDL2", "-I"+str(source/"src"), "-I"+str(out), str(adapter_source), "-o", str(adapter), "-ldl"], check=True)
    env = dict(os.environ, DISPLAY="127.0.0.1:27875", SDL_AUDIODRIVER="dummy", DEBUGACTIVE="log",
               LD_PRELOAD=str(adapter), CE_PROBE_COMMAND=str(out/"command"), CE_PROBE_RECEIPT=str(out/"receipt.json"), CE_PROBE_MOTION=str(out/"poses.jsonl"))
    sequence = 0; trace = []; cases = []; active = None; frames = []; frame_times = []
    start = time.monotonic(); last_frame = -1; failure = None
    def mark(event, **data):
        trace.append(dict(t_ms=round((time.monotonic()-start)*1000), event=event, **data))
    def record_frame(force=False):
        nonlocal last_frame
        if active is None:
            return
        now = round((time.monotonic()-start)*1000)
        if force or now-last_frame >= 45:
            frames.append(ImageGrab.grab(xdisplay=env["DISPLAY"]))
            frame_times.append(now); last_frame=now
    def command(tile=-1, buttons=0):
        nonlocal sequence
        sequence += 1
        tmp=out/"command.tmp"; tmp.write_text(f"{sequence} {tile} {buttons}\n"); tmp.replace(out/"command")
        for _ in range(200):
            record_frame()
            try:
                receipt=json.loads((out/"receipt.json").read_text())
                if receipt["sequence"] == sequence:
                    mark("input_receipt", **receipt)
                    return receipt
            except (OSError, json.JSONDecodeError):
                pass
            if game.poll() is not None:
                raise RuntimeError("CE exited")
            time.sleep(.005)
        raise RuntimeError("Input acknowledgement timeout")
    def wait(seconds):
        deadline=time.monotonic()+seconds
        while time.monotonic() < deadline:
            record_frame(); time.sleep(.005)
    def click(tile, label):
        projection=command(tile); wait(.02); actual=command()
        if projection["roundtrip_tile"] != tile or actual["cursor_tile_before"] != tile or actual["mouse_mode"] != 0:
            raise RuntimeError("Native movement cursor disagrees with requested tile")
        down=command(buttons=1); wait(.08); up=command(buttons=0)
        mark("click_submitted", label=label, target=tile, up_sequence=up["sequence"])
        return dict(label=label,target=tile,projection=projection,verified=actual,down=down,release_before_handling=up)
    def partial():
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            receipt=command(); dude=receipt["dude"]
            if ((dude["fid"]>>16)&0xFF) in (1,19) and (dude["x"] or dude["y"]):
                return receipt
            wait(.01)
        raise RuntimeError("No walking sub-tile pose observed")
    def settle():
        deadline=time.monotonic()+12; first=time.monotonic(); prior=None; count=0
        while time.monotonic()<deadline:
            r=command(); d=r["dude"]
            pose=(d["tile"],d["x"],d["y"],d["fid"],d["frame"],d["rotation"])
            count=count+1 if pose==prior else 0; prior=pose
            if time.monotonic()-first>.65 and count>=10 and ((d["fid"]>>16)&0xFF)==0:
                return r
            wait(.02)
        raise RuntimeError("No settled standing endpoint")
    def finish_frames(label):
        if frames:
            durations=[max(20,b-a) for a,b in zip(frame_times,frame_times[1:])]+[500]
            frames[0].save(out/(label+".gif"), save_all=True, append_images=frames[1:], duration=durations, loop=0)
    with (out/"xvfb.log").open("w") as xl, (out/"runtime.log").open("w") as rl:
        x=subprocess.Popen(["Xvfb",":27875","-screen","0","800x600x24","-nolisten","unix","-nolisten","local","-listen","tcp","-ac"],stdout=xl,stderr=xl)
        game=None
        try:
            for _ in range(50):
                if x.poll() is not None: raise RuntimeError("Xvfb exited")
                try:
                    with socket.create_connection(("127.0.0.1",33875),timeout=.1): break
                except OSError: time.sleep(.1)
            else: raise RuntimeError("Xvfb unavailable")
            game=subprocess.Popen(["./fallout2-ce"],cwd=work,env=env,stdout=rl,stderr=rl)
            time.sleep(5)
            for key,delay in (("n",2),("t",2),("Escape",5)):
                subprocess.run(["xdotool","key",key],env=env,check=True);time.sleep(delay)
            native=read_state(game.pid,binary,symbols(binary))
            if native["map_name"] != "NCR1.MAP" or native["actor"]["tile"] != 13915:
                raise RuntimeError("Unexpected reference start")
            mark("initial_state", **native); command()
            for scenario in args.scenarios:
                current=command()
                if current["dude"]["tile"] != 13915:
                    reset=click(13915,"reset_origin"); endpoint=settle()
                    if endpoint["dude"]["tile"] != 13915: raise RuntimeError("Reset origin not reached")
                    mark("reset_origin_reached", endpoint=endpoint,click=reset)
                active=scenario; frames=[];frame_times=[];last_frame=-1
                case=dict(scenario=scenario,start=command(),initial=click(13911,"initial_walk"),actions=[])
                cases.append(case)
                case["trigger"]=partial()
                record_frame(True)
                if scenario in ("single","repeated","rapid","stop"):
                    target={"single":14115,"repeated":13911,"rapid":14115,"stop":case["trigger"]["dude"]["tile"]}[scenario]
                    action=click(target,"interrupt");case["actions"].append(action)
                    pre=action["release_before_handling"]["dude"]
                    if not (pre["x"] or pre["y"]): raise RuntimeError("Interruption release did not occur during partial step")
                    case["after_first_input"]=command()
                    if scenario=="rapid":
                        case["second_trigger"]=partial()
                        action=click(13716,"second_redirect");case["actions"].append(action)
                        pre=action["release_before_handling"]["dude"]
                        if not(pre["x"] or pre["y"]): raise RuntimeError("Second redirect not during partial step")
                else:
                    case["before_escape"]=command()
                    mark("key_submit",key="Escape")
                    subprocess.run(["xdotool","key","Escape"],env=env,check=True)
                    wait(.2);case["options_open"]=command()
                    ImageGrab.grab(xdisplay=env["DISPLAY"]).save(out/"escape-options.png")
                    wait(.8);case["options_later"]=command()
                    mark("key_submit",key="Escape")
                    subprocess.run(["xdotool","key","Escape"],env=env,check=True)
                    wait(.1);case["after_options_close"]=command()
                case["endpoint"]=settle();case["frame_times_ms"]=frame_times.copy()
                case["complete"]=True;finish_frames(scenario)
                print(scenario,"end",case["endpoint"]["dude"],flush=True)
                active=None
        except Exception as error:
            failure=f"{type(error).__name__}: {error}"
            mark("failure",message=failure)
            if active: finish_frames(active+"-partial")
            raise
        finally:
            if game and game.poll() is None: game.terminate();game.wait(timeout=5)
            x.terminate();x.wait(timeout=5)
            unchanged={name:sha(inputs/name)==expected for name,expected in INPUTS.items()}
            result=dict(kind="CE_REDIRECTION_EXPERIMENT",status="OBSERVATIONS_ONLY" if failure is None else "INCOMPLETE",
                        failure=failure,ce_revision=CE_REVISION,binary_sha256=sha(binary),input_hashes=INPUTS,
                        original_inputs_unchanged=unchanged,adapter_source_sha256=sha(adapter_source),adapter_binary_sha256=sha(adapter),
                        controller_sha256=sha(Path(__file__)),native_symbol_offsets=offsets,configs=CONFIGS,cases=cases,trace=trace,
                        native_poses=[json.loads(line) for line in (out/"poses.jsonl").read_text().splitlines()] if (out/"poses.jsonl").exists() else [],
                        captures={p.name:sha(p) for p in out.iterdir() if p.suffix in (".png",".gif")},
                        intervention="SDL relative mouse/buttons substituted; keyboard through XTEST; read-only native queries and pose logging; no authoritative writes",
                        limitations=["SDL polling snapshots occur before input processing, not at every simulation phase","Native anchor is tile projection + [16,8] + Object x/y; not anatomical foot or pixel-volume proof","Wall-clock/capture load and default NPC randomness uncontrolled; no 150ms or deterministic replay claim","CE Linux DAT-only, original Windows and Vampiro unverified"])
            (out/"evidence.json").write_text(json.dumps(result,indent=2)+"\n")
            if not all(unchanged.values()): raise RuntimeError("Original DAT changed")


if __name__ == "__main__":
    main()
