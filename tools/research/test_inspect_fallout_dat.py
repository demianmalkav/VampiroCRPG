"""Synthetic parser checks; no proprietary fixtures."""
import struct
import unittest
import zlib
from inspect_fallout_dat import index_dat, read_entry, inspect_frm, InvalidResource


def archive(payload=b"hello", compressed=True, prefix=b""):
    stored = zlib.compress(payload) if compressed else payload
    name = b"art\\sample.frm"
    tree = struct.pack("<II", 1, len(name)) + name
    tree += struct.pack("<BIII", compressed, len(payload), len(stored), 0)
    data = stored + tree
    return prefix + data + struct.pack("<II", len(tree), len(data) + 8)


def frame(area=13, pixels=b"\x01"):
    return struct.pack(">IHHH6h6h6II", 4, 10, 0, 1, *([0] * 12), *([0] * 6), area) + struct.pack(">HHIhh", 1, 1, 1, 0, 0) + pixels


class ResourceTests(unittest.TestCase):
    def test_compressed_and_plain_with_leading_prefix(self):
        for compressed in [False, True]:
            blob = archive(compressed=compressed, prefix=b"prefix")
            entries, footer = index_dat(blob)
            self.assertEqual(footer["data_base"], 6)
            self.assertEqual(read_entry(blob, entries[0]), b"hello")

    def test_footer_and_entry_ranges_rejected(self):
        with self.assertRaises(InvalidResource):
            index_dat(b"bad")
        blob = bytearray(archive())
        struct.pack_into("<I", blob, len(blob) - 12, len(blob))
        with self.assertRaises(InvalidResource):
            index_dat(blob)

    def test_inflated_size_and_output_bound(self):
        blob = archive()
        entry = index_dat(blob)[0][0]
        with self.assertRaises(InvalidResource):
            read_entry(blob, entry, max_size=4)
        with self.assertRaises(InvalidResource):
            read_entry(blob, dict(entry, size=4))

    def test_trailing_zlib_bytes_rejected(self):
        blob = archive() + b"x"
        entry = index_dat(blob[:-1])[0][0]
        raw = blob[entry["offset"]:entry["offset"] + entry["stored_size"]] + b"x"
        with self.assertRaises(InvalidResource):
            read_entry(raw, dict(entry, offset=0, stored_size=len(raw)))

    def test_split_direction_area_is_metadata_not_physical_bound(self):
        info = inspect_frm(frame(area=78))
        self.assertFalse(info["area_matches_physical"])
        self.assertEqual(info["stored_direction_blocks"], 1)

    def test_truncated_pixels_rejected(self):
        with self.assertRaises(InvalidResource):
            inspect_frm(frame(pixels=b""))


if __name__ == "__main__":
    unittest.main()
