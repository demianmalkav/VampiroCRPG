"""Independent synthetic MAP checks, including unused SID-dependent records."""
import struct
import unittest
from inspect_fallout_map import parse_map, InvalidResource


def ints(*values):
    return struct.pack(">" + "i" * len(values), *values)


def object_record(pid, inventory=0, extra=()):
    base = [0] * 18
    base[0], base[1], base[11], base[16], base[17] = 7, 12345, pid, -1, -1
    return ints(*base) + ints(inventory, inventory, 0) + ints(0) + ints(*extra)


def proto(pid):
    kind = pid >> 24
    return dict(kind=kind, subtype={1: 1, 2: 6}.get(pid & 0xFFFFFF) if kind == 0 else None)


def map_fixture(objects=b"", top=0, total=None, spatial=False):
    header = bytearray(236)
    struct.pack_into(">i", header, 0, 20)
    struct.pack_into(">i", header, 40, 14)  # no tile sections
    scripts = ints(0)
    if spatial:
        # One spatial live record followed by fifteen unused *system* SID slots.
        scripts += ints(1, 0x01000000, 0, 12345, 3, *([0] * 14))
        scripts += ints(*([0] * (15 * 16))) + ints(1, 0)
    else:
        scripts += ints(0)
    scripts += ints(0, 0, 0)
    return bytes(header) + scripts + ints(top if total is None else total, top) + objects + ints(0, 0)


class MapTests(unittest.TestCase):
    def test_zero_map_exact_eof(self):
        raw = map_fixture()
        result = parse_map(raw, proto)
        self.assertEqual(result["bytes_consumed"], len(raw))
        self.assertEqual(result["objects"], [])

    def test_unused_script_slots_follow_own_sid_not_list_type(self):
        raw = map_fixture(spatial=True)
        result = parse_map(raw, proto)
        self.assertEqual(result["script_counts"], [0, 1, 0, 0, 0])
        self.assertEqual(result["mixed_script_slot_types"], 15)
        self.assertEqual(len(result["scripts"]), 1)

    def test_nested_key_payload_and_quantity(self):
        owner = object_record(1, inventory=1)
        child = object_record(2, extra=(42,))
        raw = map_fixture(owner + ints(3) + child, top=1)
        result = parse_map(raw, proto)
        self.assertEqual(result["top_level_objects"], 1)
        self.assertEqual(len(result["objects"]), 2)
        self.assertEqual(result["objects"][1]["quantity"], 3)
        self.assertEqual(result["objects"][1]["owner_offset"], result["objects"][0]["offset"])

    def test_top_level_count_mismatch_rejected(self):
        with self.assertRaises(InvalidResource):
            parse_map(map_fixture(total=1), proto)

    def test_truncated_and_extra_bytes_rejected(self):
        for raw in (map_fixture()[:-1], map_fixture() + b"\0"):
            with self.assertRaises(InvalidResource):
                parse_map(raw, proto)


if __name__ == "__main__":
    unittest.main()
