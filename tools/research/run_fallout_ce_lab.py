#!/usr/bin/env python3
"""Private, isolated CE startup/movement smoke test. Never changes CE or DATs.

Linux x86-64 reference only; requires an unstripped CE binary, Xvfb, xdotool,
Pillow and permission to read the child process's /proc/PID/mem. Captures and
saves are private outputs, not files to commit. This is not A2 acceptance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import time

from PIL import ImageGrab

CE_REVISION = "e97087b9582f37075db347a89898887320753f8b"
INPUTS = {
    "master.dat": "9b096d3035edafd4077deeb8ee7877a803b9db98497aa4596624b5c058a84711",
    "critter.dat": "da83d615967c0bac41fbc50e6b86b3088401ff69ed9d8b2e5be1d6ac0c125bcd",
    "patch000.dat": "d24788cf50294a27713a368f06cedb9b30c00ba709c2f1e0662ca2f6dddf2fc1",
}
CONFIGS = {
    "fallout2.cfg": """[system]
master_dat=master.dat
critter_dat=critter.dat
master_patches=data
critter_patches=data
language=english
art_cache_size=32
interrupt_walk=1
[sound]
initialize=0
sounds=0
music=0
speech=0
[preferences]
combat_speed=0
player_speedup=0
running=0
""",
    "f2_res.ini": "[MAIN]\nSCR_WIDTH=800\nSCR_HEIGHT=600\nWINDOWED=1\nSCALE_2X=0\n",
    "ddraw.ini": "[Misc]\nSkipOpeningMovies=1\nStartingMap=NCR1.MAP\n",
}


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def symbols(binary):
    wanted = {"fallout::gMapHeader", "fallout::gDude", "fallout::gElevation"}
    found = {}
    for line in subprocess.check_output(["nm", "-C", str(binary)], text=True).splitlines():
        fields = line.split(maxsplit=2)
        if len(fields) == 3 and fields[2] in wanted:
            found[fields[2]] = int(fields[0], 16)
    if set(found) != wanted:
        raise ValueError("Required unstripped CE symbols unavailable")
    return found


def read_state(pid, binary, offsets):
    """Read-only native state; offsets resolved from this exact executable.

    MapHeader and first 11 Object ints are from CE map.h/obj_types.h at pin.
    No pointer, field or function is written or invoked by this probe.
    """
    # Some containers mount proc from an ancestor PID namespace. Resolve only
    # our direct child with this exact executable, rather than attaching to an
    # unrelated process or assuming Popen's namespace PID equals proc's PID.
    candidates = []
    parent = os.readlink("/proc/self")
    for child in Path("/proc").iterdir():
        if not child.name.isdecimal():
            continue
        try:
            status = dict(line.split(":", 1) for line in
                          (child/"status").read_text().splitlines() if ":" in line)
            if (status.get("PPid", "").strip() == parent
                    and status.get("NSpid", "").split()[-1] == str(pid)
                    and (child/"exe").resolve() == binary):
                candidates.append(int(child.name))
        except (OSError, IndexError):
            pass
    if len(candidates) != 1:
        raise RuntimeError("Cannot uniquely resolve the direct CE child in proc")
    pid = candidates[0]
    mappings = Path(f"/proc/{pid}/maps").read_text().splitlines()
    base = next(int(l.split()[0].split("-")[0], 16) for l in mappings
                if l.split()[2] == "00000000" and l.endswith(str(binary)))
    with open(f"/proc/{pid}/mem", "rb", buffering=0) as mem:
        def read(address, size):
            mem.seek(address)
            data = mem.read(size)
            if len(data) != size:
                raise ValueError("Incomplete native state read")
            return data
        header = read(base + offsets["fallout::gMapHeader"], 60)
        dude = struct.unpack("<Q", read(base + offsets["fallout::gDude"], 8))[0]
        obj = struct.unpack("<11i", read(dude, 44))
        return {
            "map_version": struct.unpack_from("<i", header)[0],
            "map_name": header[4:20].split(b"\0")[0].decode("ascii"),
            "map_index": struct.unpack_from("<i", header, 52)[0],
            "elevation": struct.unpack("<i", read(base + offsets["fallout::gElevation"], 4))[0],
            "actor": dict(zip(["id", "tile", "x", "y", "sx", "sy", "frame",
                               "rotation", "fid", "flags", "elevation"], obj)),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--ce-source", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--display", type=int, default=27875,
                        help="X display number; TCP port is 6000 + this number")
    parser.add_argument("--move-smoke", action="store_true")
    args = parser.parse_args()
    binary, inputs, output = args.binary.resolve(), args.inputs.resolve(), args.output.resolve()
    revision = subprocess.check_output(["git", "-C", str(args.ce_source), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(args.ce_source), "status", "--porcelain"], text=True)
    if revision != CE_REVISION or dirty:
        raise ValueError("CE source must be the clean pinned reference")
    for name, expected in INPUTS.items():
        if sha(inputs / name) != expected:
            raise ValueError("Wrong private input identity: " + name)
    offsets = symbols(binary)
    output.mkdir(parents=True, exist_ok=False)
    work = output / "work"
    work.mkdir()
    (work / "data").mkdir()
    for name in INPUTS:
        (work / name).symlink_to(inputs / name)
    (work / "fallout2-ce").symlink_to(binary)
    for name, text in CONFIGS.items():
        (work / name).write_text(text)
    env = os.environ.copy()
    env.update(DISPLAY=f"127.0.0.1:{args.display}", SDL_AUDIODRIVER="dummy", DEBUGACTIVE="log",
               SDL_MOUSE_RELATIVE_MODE_WARP="1")
    trace = []
    start = time.monotonic()
    def mark(event, **extra):
        trace.append(dict(elapsed_ms=round((time.monotonic() - start)*1000), event=event, **extra))
    def capture(name):
        ImageGrab.grab(xdisplay=env["DISPLAY"]).save(output / (name + ".png"))
        mark("capture", file=name + ".png", state=read_state(game.pid, binary, offsets))
        print(name, trace[-1]["state"]["map_name"], flush=True)
    def key(value):
        subprocess.run(["xdotool", "key", value], env=env, check=True)
        mark("key", key=value)
    with (output / "xvfb.log").open("w") as xl, (output / "runtime.log").open("w") as rl:
        x = subprocess.Popen(["Xvfb", f":{args.display}", "-screen", "0", "800x600x24",
                              "-nolisten", "unix", "-nolisten", "local", "-listen", "tcp", "-ac"], stdout=xl, stderr=xl)
        game = None
        try:
            # Server and clients must share this execution's network namespace.
            for _ in range(40):
                if x.poll() is not None:
                    raise RuntimeError("Xvfb exited before startup")
                try:
                    with socket.create_connection(("127.0.0.1", 6000+args.display), timeout=.1):
                        break
                except OSError:
                    time.sleep(.1)
            else:
                raise RuntimeError("Local X display unavailable")
            game = subprocess.Popen(["./fallout2-ce"], cwd=work, env=env, stdout=rl, stderr=rl)
            mark("launch", binary_sha256=sha(binary))
            time.sleep(5)
            capture("menu")
            key("n")
            time.sleep(2)
            capture("character")
            key("t")
            time.sleep(2)
            key("Escape")  # Skip elder movie, not a game-mechanics intervention.
            time.sleep(5)
            capture("ncr")
            if trace[-1]["state"]["map_name"] != "NCR1.MAP":
                raise RuntimeError("Expected NCR1 not loaded")
            if args.move_smoke:
                before_tile = trace[-1]["state"]["actor"]["tile"]
                # CE samples button state via SDL_GetRelativeMouseState. A
                # zero-duration XTEST click can fall between polls and vanish.
                subprocess.run(["xdotool", "mousemove", "320", "295"], env=env, check=True)
                time.sleep(.2)
                subprocess.run(["xdotool", "mousedown", "1"], env=env, check=True)
                mark("mouse_down", x=320, y=295, button=1)
                time.sleep(.2)
                subprocess.run(["xdotool", "mouseup", "1"], env=env, check=True)
                mark("mouse_up", button=1)
                time.sleep(4)
                capture("ncr-after-move")
                if trace[-1]["state"]["actor"]["tile"] == before_tile:
                    raise RuntimeError("Movement smoke did not change the native actor tile")
            mark("process_alive", alive=game.poll() is None)
            if game.poll() is not None:
                raise RuntimeError("CE exited during observation")
        finally:
            if game is not None and game.poll() is None:
                game.terminate()
                game.wait(timeout=5)
            x.terminate()
            x.wait(timeout=5)
            unchanged = {name: sha(inputs / name) == expected for name, expected in INPUTS.items()}
            evidence = dict(kind="CE_STARTUP_SMOKE_NOT_A2_ACCEPTANCE", ce_revision=revision,
                            status="PASS" if trace and trace[-1].get("event") == "process_alive" and trace[-1].get("alive") else "INCOMPLETE",
                            binary_sha256=sha(binary), inputs=INPUTS, configs=CONFIGS,
                            environment_overrides={k: env[k] for k in ("DISPLAY", "SDL_AUDIODRIVER", "DEBUGACTIVE", "SDL_MOUSE_RELATIVE_MODE_WARP")},
                            configs_sha256={name: sha(work/name) for name in CONFIGS},
                            input_archives_unchanged=unchanged, trace=trace,
                            captures={p.name: sha(p) for p in output.glob("*.png")},
                            stop_policy="SIGTERM after observation; clean game exit/save not tested",
                            limitations=["Silent isolated DAT-only reference; no original loose overrides, sfall DLL or HiRes DAT",
                                         "Random seed is CE default; timing trace is measured wall time",
                                         "Fixed waits are smoke-test scheduling, not action-phase measurements"])
            (output/"evidence.json").write_text(json.dumps(evidence, indent=2)+"\n")
    if not all(unchanged.values()):
        raise RuntimeError("Private archive identity changed")


if __name__ == "__main__":
    main()
