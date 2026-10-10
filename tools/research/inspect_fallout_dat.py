#!/usr/bin/env python3
"""Read-only DAT2/FRM structural audit. Outputs metadata, never original resources.

Format reference: rotators/fallout2-docs at fa5b3a90b342975998f10e270c5cd7f5293af9e9.
This is an independently written inspection utility, not a game resource loader.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import zlib


class InvalidResource(ValueError):
    pass


def index_dat(blob):
    if len(blob) < 12:
        raise InvalidResource("DAT footer/tree missing")
    tree_size, archive_size = struct.unpack_from("<II", blob, len(blob) - 8)
    if archive_size > len(blob) or tree_size < 4 or tree_size + 8 > archive_size:
        raise InvalidResource("DAT footer bounds")
    base, tree = len(blob) - archive_size, len(blob) - tree_size - 8
    count = struct.unpack_from("<I", blob, tree)[0]
    pos, end, entries = tree + 4, len(blob) - 8, []
    if count > (tree_size - 4) // 18:
        raise InvalidResource("DAT entry count exceeds tree")
    for _ in range(count):
        if pos + 4 > end:
            raise InvalidResource("DAT truncated path length")
        n = struct.unpack_from("<I", blob, pos)[0]
        pos += 4
        if not n or pos + n + 13 > end:
            raise InvalidResource("DAT path/record bounds")
        name = blob[pos:pos + n].decode("ascii")
        parts = name.replace("\\", "/").split("/")
        if any(x in ("", ".", "..") for x in parts) or ":" in name or "\0" in name:
            raise InvalidResource("DAT unsafe resource path")
        pos += n
        compressed, real, stored, offset = struct.unpack_from("<BIII", blob, pos)
        pos += 13
        if compressed not in (0, 1) or base + offset + stored > tree:
            raise InvalidResource("DAT data range/flag")
        if not compressed and real != stored:
            raise InvalidResource("DAT plain size mismatch")
        entries.append(dict(path=name, compressed=compressed, size=real,
                            stored_size=stored, offset=base + offset))
    if pos != end:
        raise InvalidResource("DAT unexplained tree bytes")
    names = [e["path"].lower() for e in entries]
    if len(set(names)) != len(names):
        raise InvalidResource("DAT duplicate case-insensitive paths")
    return entries, dict(tree_size=tree_size, archive_size=archive_size,
                         data_base=base, sorted_case_insensitive=names == sorted(names))


def read_entry(blob, entry, max_size=64 * 1024 * 1024):
    if entry["size"] > max_size:
        raise InvalidResource("Entry exceeds inspection output bound")
    start = entry["offset"]
    raw = blob[start:start + entry["stored_size"]]
    if entry["compressed"]:
        inflater = zlib.decompressobj()
        try:
            raw = inflater.decompress(raw, entry["size"] + 1)
        except zlib.error as exc:
            raise InvalidResource("Invalid zlib stream") from exc
        if not inflater.eof or inflater.unused_data or inflater.unconsumed_tail:
            raise InvalidResource("Zlib stream incomplete/trailing/overlong")
    if len(raw) != entry["size"]:
        raise InvalidResource("Entry inflated size mismatch")
    return raw


def inspect_frm(raw):
    if len(raw) < 62:
        raise InvalidResource("FRM header missing")
    version, fps, action, count = struct.unpack_from(">IHHH", raw)
    xs = struct.unpack_from(">6h", raw, 10)
    ys = struct.unpack_from(">6h", raw, 22)
    offsets = struct.unpack_from(">6I", raw, 34)
    area = struct.unpack_from(">I", raw, 58)[0]
    if version != 4 or not count:
        raise InvalidResource("FRM version/count mismatch")
    directions = []
    for offset in dict.fromkeys(offsets):
        pos, frames = 62 + offset, []
        for _ in range(count):
            if pos + 12 > len(raw):
                raise InvalidResource("FRM truncated frame")
            w, h, size, x, y = struct.unpack_from(">HHIhh", raw, pos)
            if size != w * h or pos + 12 + size > len(raw):
                raise InvalidResource("FRM pixels/dimensions mismatch")
            frames.append(dict(width=w, height=h, x=x, y=y))
            pos += 12 + size
        directions.append(dict(offset=offset, frames=frames))
    return dict(version=version, fps=fps, action_frame=action,
                action_in_frame_range=action < count, frames_per_direction=count,
                direction_offsets=list(offsets), x_offsets=list(xs), y_offsets=list(ys),
                stored_direction_blocks=len(directions), declared_frame_area=area,
                physical_frame_area=len(raw) - 62,
                area_matches_physical=area == len(raw) - 62, directions=directions)


def audit(path):
    blob = path.read_bytes()
    entries, footer = index_dat(blob)
    extensions, roots, errors, frame_counts = Counter(), Counter(), [], Counter()
    samples, checked, pixel_records, area_mismatches = [], 0, 0, 0
    map_headers, proto_headers = [], []
    marker_outside_range = []
    for e in entries:
        ext = Path(e["path"]).suffix.lower()
        extensions[ext] += 1
        roots[e["path"].split("\\")[0].lower()] += 1
        try:
            raw = read_entry(blob, e)
            checked += 1
            if ext == ".map":
                if len(raw) < 236:
                    raise InvalidResource("MAP header missing")
                version = struct.unpack_from(">i", raw)[0]
                if version not in (19, 20):
                    raise InvalidResource("MAP version unsupported")
                fields = ("entering_tile", "entering_elevation", "entering_rotation",
                          "local_vars_count", "script_index", "flags", "darkness",
                          "global_vars_count", "map_index", "last_visit_time")
                values = struct.unpack_from(">10i", raw, 20)
                map_headers.append(dict(path=e["path"], bytes=len(raw), version=version,
                                        header_only=True, **dict(zip(fields, values))))
            if ext == ".pro":
                if len(raw) < 12:
                    raise InvalidResource("PRO common header missing")
                pid, message, fid = struct.unpack_from(">III", raw)
                proto_headers.append(dict(path=e["path"], bytes=len(raw), pid=pid,
                                          object_type=pid >> 24, message_num=message,
                                          fid=fid, header_only=True))
            if ext in (".frm", ".fr0", ".fr1", ".fr2", ".fr3", ".fr4", ".fr5"):
                info = inspect_frm(raw)
                frame_counts[str(info["frames_per_direction"])] += 1
                pixel_records += info["frames_per_direction"] * info["stored_direction_blocks"]
                area_mismatches += not info["area_matches_physical"]
                if not info["action_in_frame_range"]:
                    marker_outside_range.append(e["path"])
                if len(samples) < 5 or e["path"].lower().endswith(("hmjmpsaa.frm", "hmjmpsab.frm", "hmjmpsal.frm", "hmjmpsat.frm", "hmjmpsdd.frm")):
                    samples.append(dict(path=e["path"], sha256=hashlib.sha256(raw).hexdigest(), **info))
        except (InvalidResource, UnicodeError) as exc:
            errors.append(dict(path=e["path"], error=str(exc)))
    return dict(file=path.name, bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                footer=footer, entry_count=len(entries), entries_content_checked=checked,
                extensions=dict(sorted(extensions.items())), roots=dict(sorted(roots.items())),
                frm_frame_counts=dict(sorted(frame_counts.items())),
                frm_frame_records_checked=pixel_records, frm_area_mismatch_count=area_mismatches,
                frm_marker_outside_range=marker_outside_range, errors=errors, frm_samples=samples,
                map_headers=map_headers, proto_headers=proto_headers,
                resource_paths=[e["path"] for e in entries])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reports = [audit(p) for p in args.archives]
    args.output.write_text(json.dumps(dict(schema="fallout-private-resource-audit-1",
                                          archives=reports), indent=2) + "\n")
    for r in reports:
        summary = {k: r[k] for k in ("file", "bytes", "entry_count", "entries_content_checked", "extensions", "frm_frame_records_checked", "frm_area_mismatch_count")}
        summary["error_count"] = len(r["errors"])
        summary["first_errors"] = r["errors"][:3]
        print(json.dumps(summary))
    return int(any(r["errors"] for r in reports))


if __name__ == "__main__":
    raise SystemExit(main())
