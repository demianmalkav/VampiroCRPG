#!/usr/bin/env python3
"""Static MAP dependency audit using private DAT2 inputs; never runs game scripts.

Independent reader. Format sources: rotators/fallout2-docs fa5b3a90, MAP/PRO;
CE e97087b9, scriptRead/objectRead/objectDataRead. Byte consumption, including
unused script slots, follows each slot's SID, not its enclosing list type.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from inspect_fallout_dat import index_dat, read_entry, InvalidResource

PROTO_TYPES = ["items", "critters", "scenery", "walls", "tiles", "misc"]
ART_TYPES = ["items", "critters", "scenery", "walls", "tiles", "misc", "intrface",
             "inven", "heads", "backgrnd", "skilldex"]


class DatRoots:
    """Explicit low-to-high priority roots. Does not claim to scan loose files."""
    def __init__(self, paths):
        self.roots, self.entries, self.protos = [], {}, {}
        for path in paths:
            raw = path.read_bytes()
            entries, _ = index_dat(raw)
            self.roots.append(dict(file=path.name, bytes=len(raw),
                                   sha256=hashlib.sha256(raw).hexdigest()))
            for e in entries:
                key = e["path"].replace("\\", "/").lower()
                self.entries[key] = (raw, e, path.name)

    def read(self, path):
        key = path.replace("\\", "/").lower()
        if key not in self.entries:
            raise InvalidResource("Missing dependency: " + key)
        blob, entry, source = self.entries[key]
        return read_entry(blob, entry), source

    def list(self, path):
        return self.read(path)[0].decode("latin1").splitlines()

    def proto(self, pid):
        pid &= 0xFFFFFFFF
        if pid in self.protos:
            return self.protos[pid]
        kind, line = pid >> 24, pid & 0xFFFFFF
        if kind >= len(PROTO_TYPES) or not line:
            raise InvalidResource("Unsupported PID")
        folder = "proto/" + PROTO_TYPES[kind]
        rows = self.list(folder + "/" + PROTO_TYPES[kind] + ".lst")
        if line > len(rows):
            raise InvalidResource("PID outside prototype list")
        name = rows[line - 1].split(" ")[0]
        path = folder + "/" + name
        raw, source = self.read(path)
        if len(raw) < 12 or struct.unpack_from(">I", raw)[0] != pid:
            raise InvalidResource("Prototype PID/header mismatch")
        message, fid = struct.unpack_from(">II", raw, 4)
        subtype = None
        if kind in (0, 2):
            if len(raw) < 36:
                raise InvalidResource("Prototype subtype missing")
            subtype = struct.unpack_from(">i", raw, 32)[0]
        proto = dict(path=path, source=source, pid=pid, kind=kind,
                     subtype=subtype, message_num=message, fid=fid)
        self.protos[pid] = proto
        return proto


class Cursor:
    def __init__(self, raw):
        self.raw, self.pos = raw, 0

    def take(self, size):
        if size < 0 or self.pos + size > len(self.raw):
            raise InvalidResource("MAP truncated at byte " + str(self.pos))
        start = self.pos
        self.pos += size
        return self.raw[start:self.pos]

    def ints(self, count=1):
        return struct.unpack(">" + "i" * count, self.take(4 * count))

    def count(self):
        value = self.ints()[0]
        if value < 0 or value > len(self.raw) // 4:
            raise InvalidResource("MAP invalid count")
        return value


def parse_map(raw, proto_lookup):
    c = Cursor(raw)
    header = c.take(236)
    version = struct.unpack_from(">i", header)[0]
    if version not in (19, 20):
        raise InvalidResource("MAP unsupported version")
    local, map_script, flags = struct.unpack_from(">iii", header, 32)
    global_count = struct.unpack_from(">i", header, 48)[0]
    # Negative variable counts are clamped by CE; all other counts stay strict.
    c.take(4 * (max(local, 0) + max(global_count, 0)))
    tiles, tile_ids = {}, set()
    for elevation in range(3):
        if not flags & (2 << elevation):
            tile_offset = c.pos
            values = struct.unpack(">10000I", c.take(40000))
            for v in values:
                tile_ids.update((v & 0xFFF, (v >> 16) & 0xFFF))
            tiles[elevation] = dict(offset=tile_offset, cells=10000)
    scripts, script_counts, mixed_slot_types = [], [], 0
    for list_type in range(5):
        count = c.count()
        script_counts.append(count)
        for _ in range((count + 15) // 16):
            records = []
            for _slot in range(16):
                offset = c.pos
                sid, _pointer = c.ints(2)
                sid_type = (sid >> 24) & 0xFF
                extra = 2 if sid_type == 1 else 1 if sid_type == 2 else 0
                c.ints(extra)
                tail = c.ints(14)
                mixed_slot_types += sid_type != list_type
                records.append(dict(offset=offset, sid=sid, list_type=list_type,
                                    sid_type=sid_type, script_index=tail[1],
                                    owner_id=tail[3], local_vars_offset=tail[4],
                                    local_vars_count=tail[5]))
            length, _next = c.ints(2)
            if not 0 <= length <= 16:
                raise InvalidResource("MAP invalid script extent length")
            scripts.extend(records[:length])
    if len(scripts) != sum(script_counts):
        raise InvalidResource("MAP live script count mismatch")
    objects = []

    def obj(elevation, owner_offset=None, quantity=1, depth=0):
        if depth > 32:
            raise InvalidResource("MAP inventory nesting limit")
        offset = c.pos
        base = c.ints(18)
        pid = base[11] & 0xFFFFFFFF
        proto = proto_lookup(pid)
        kind, subtype = proto["kind"], proto["subtype"]
        inventory_length = c.count()
        c.ints(2)  # capacity and pointer placeholder
        payload = c.ints(11 if kind == 1 else 1)
        extra = 0
        if kind == 0:
            if subtype not in range(7):
                raise InvalidResource("MAP unsupported item subtype")
            extra = 2 if subtype == 3 else 1 if subtype in (4, 5, 6) else 0
        elif kind == 2:
            if subtype not in range(6):
                raise InvalidResource("MAP unsupported scenery subtype")
            extra = 1 if subtype == 0 else 2 if subtype in (1, 2) else (1 if version == 19 else 2) if subtype in (3, 4) else 0
        elif kind == 5 and 0x05000010 <= pid <= 0x05000017:
            extra = 4
        extras = c.ints(extra)
        instance_flags = base[9] & 0xFFFFFFFF
        record = dict(offset=offset, id=base[0], tile=base[1], rotation=base[7],
                      fid=base[8] & 0xFFFFFFFF, flags=instance_flags,
                      stored_elevation=base[10], elevation_loop=elevation,
                      pid=pid, sid=base[16], script_index=base[17],
                      kind=kind, subtype=subtype, inventory_length=inventory_length,
                      owner_offset=owner_offset, quantity=quantity,
                      hidden=bool(instance_flags & 1), no_block=bool(instance_flags & 16),
                      multihex=bool(instance_flags & 2048),
                      door_open_flags=extras[0] if kind == 2 and subtype == 0 else None,
                      proto=proto)
        objects.append(record)
        for _ in range(inventory_length):
            amount = c.count()
            obj(elevation, offset, amount, depth + 1)

    total = c.count()
    elevation_counts = []
    for elevation in range(3):
        count = c.count()
        elevation_counts.append(count)
        for _ in range(count):
            obj(elevation)
    if total != sum(elevation_counts) or c.pos != len(raw):
        raise InvalidResource("MAP object count or final byte mismatch")
    return dict(version=version, flags=flags, map_script=map_script,
                local_vars=max(local, 0), global_vars=max(global_count, 0),
                tile_sections=tiles, tile_ids=sorted(tile_ids), scripts=scripts,
                script_counts=script_counts, mixed_script_slot_types=mixed_slot_types,
                objects=objects, top_level_objects=total,
                elevation_counts=elevation_counts, bytes_consumed=c.pos)


def audit_map(roots, path):
    raw, source = roots.read(path)
    result = parse_map(raw, roots.proto)
    scripts = roots.list("scripts/scripts.lst")
    art_lists = {}
    dependencies, missing, critter_bases = set(), set(), set()

    def art(fid):
        kind, line = (fid >> 24) & 0xF, fid & 0xFFF
        if kind >= len(ART_TYPES):
            missing.add("unsupported-fid:" + str(fid)); return
        folder = "art/" + ART_TYPES[kind]
        lst = folder + "/" + ART_TYPES[kind] + ".lst"
        dependencies.add(lst)
        if lst not in art_lists:
            art_lists[lst] = roots.list(lst)
        rows = art_lists[lst]
        if line >= len(rows):
            missing.add("fid-outside-list:" + str(fid)); return
        name = rows[line].split(" ")[0]
        if kind == 1:
            # Critter suffixes require animation/weapon/rotation resolution.
            critter_bases.add(name.split(",")[0]); return
        dependencies.add(folder + "/" + name)

    indexes = {s["script_index"] for s in result["scripts"] if s["script_index"] >= 0}
    if result["map_script"] > 0:
        indexes.add(result["map_script"] - 1)
    for o in result["objects"]:
        dependencies.add(o["proto"]["path"])
        kind = PROTO_TYPES[o["kind"]]
        dependencies.update(("proto/" + kind + "/" + kind + ".lst",
                             "text/english/game/pro_" + ["item", "crit", "scen", "wall", "tile", "misc"][o["kind"]] + ".msg"))
        if o["script_index"] >= 0:
            indexes.add(o["script_index"])
        art(o["fid"])
    for tile in result["tile_ids"]:
        art(0x04000000 | tile)
    for i in indexes:
        if i >= len(scripts):
            missing.add("script-index-outside-list:" + str(i)); continue
        name = scripts[i].split(" ")[0]
        dependencies.add("scripts/" + name)
    for dependency in dependencies:
        if dependency.lower() not in roots.entries:
            missing.add(dependency)
    top = [o for o in result["objects"] if o["owner_offset"] is None]
    doors = [o for o in top if o["kind"] == 2 and o["subtype"] == 0]
    return dict(schema="fallout-static-map-audit-1", map_path=path, map_source=source,
                bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), inputs=roots.roots,
                version=result["version"], header_flags=result["flags"],
                local_vars=result["local_vars"], global_vars=result["global_vars"],
                bytes_consumed=result["bytes_consumed"], exact_eof=True,
                top_level_objects=result["top_level_objects"],
                nested_objects=len(result["objects"]) - len(top),
                elevation_counts=result["elevation_counts"],
                kinds=dict(Counter(PROTO_TYPES[o["kind"]] for o in top)),
                script_counts=result["script_counts"],
                mixed_script_slot_types=result["mixed_script_slot_types"],
                doors=doors, dependencies=sorted(dependencies), missing_dependencies=sorted(missing),
                critter_bases=sorted(critter_bases), critter_art_resolution="BASE_ONLY_NOT_ALL_ANIMATIONS",
                runtime_executed=False, collision_paths_tested=False,
                limitation="Static DAT roots only; no scripts executed, loose overrides not scanned.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dat", type=Path, nargs="+", required=True)
    parser.add_argument("--map", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit_map(DatRoots(args.dat), args.map)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("map_path", "map_source", "top_level_objects", "nested_objects", "kinds", "script_counts", "mixed_script_slot_types", "missing_dependencies")} | {"doors": len(result["doors"])}))


if __name__ == "__main__":
    main()
