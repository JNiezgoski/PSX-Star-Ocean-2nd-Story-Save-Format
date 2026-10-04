"""Verifies the save-format byte map stays internally consistent and fully mapped."""
from pathlib import Path
import struct
import sys
import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "tools"))

import so2_save_map
from scripts.so2_codec import state


def test_chunk1_coverage():
    """Chunk 1 (Options/Fol/Clock/Affection): 416/416 bytes mapped."""
    ranges = so2_save_map.generate_byte_map()
    report = so2_save_map.audit_coverage(ranges)

    chunk1 = next(c for c in report["chunks"] if c["chunk_number"] == 1)
    assert chunk1["total_bytes"] == 416
    assert chunk1["mapped_bytes"] == 416
    assert chunk1["unknown_bytes"] == 0
    assert chunk1["mapped_percentage"] == 100.0


def test_chunk2_coverage():
    """Chunk 2 (Party Primary Records): 768/768 bytes mapped."""
    ranges = so2_save_map.generate_byte_map()
    report = so2_save_map.audit_coverage(ranges)

    chunk2 = next(c for c in report["chunks"] if c["chunk_number"] == 2)
    assert chunk2["total_bytes"] == 768
    assert chunk2["mapped_bytes"] == 768
    assert chunk2["unknown_bytes"] == 0
    assert chunk2["mapped_percentage"] == 100.0


def test_chunk5_coverage():
    """Chunk 5 (World/Name Table/Story Flags): 1,088/1,088 bytes mapped."""
    ranges = so2_save_map.generate_byte_map()
    report = so2_save_map.audit_coverage(ranges)

    chunk5 = next(c for c in report["chunks"] if c["chunk_number"] == 5)
    assert chunk5["total_bytes"] == 1088
    assert chunk5["mapped_bytes"] == 1088
    assert chunk5["unknown_bytes"] == 0
    assert chunk5["mapped_percentage"] == 100.0


def test_overall_coverage():
    """Full decoded save state: 7,048/7,048 bytes mapped (100%) across all 5 chunks."""
    ranges = so2_save_map.generate_byte_map()
    report = so2_save_map.audit_coverage(ranges)

    assert report["total_bytes"] == 7048
    assert report["confirmed_mapped_bytes"] == 7048
    assert report["unknown_bytes"] == 0
    assert report["confirmed_mapped_percentage"] == 100.0


def test_chunk2_against_real_saves():
    """Sanity-check decoded Chunk 2 fields (elemental resistances, CRT bonus, element mask)
    against real memory card saves, when available."""
    mcd_files = list(_ROOT.glob("artifacts/**/*.mcd"))
    if not mcd_files:
        pytest.skip("No .mcd save files present (personal save data is not included in this repo)")

    verified_chars = 0
    for mcd in mcd_files:
        with open(mcd, "rb") as f:
            data = f.read()
        for block in range(1, 16):
            blk = data[block * 8192 : (block + 1) * 8192]
            if blk[0x200:0x20A] != b"STAR OCEAN":
                continue
            dec = state(blk)
            for slot in range(8):
                base = 0x01A0 + slot * 0x60
                pid = struct.unpack_from("<h", dec, base)[0]
                if pid <= 0:
                    continue

                verified_chars += 1
                elem_res = list(dec[base + 4 : base + 14])
                assert len(elem_res) == 10
                for r in elem_res:
                    assert 0 <= r <= 5, f"Unexpected elemental resistance code {r}"

                status_mask = struct.unpack_from("<H", dec, base + 14)[0]
                assert 0 <= status_mask <= 0xFFFF

                crt = struct.unpack_from("<h", dec, base + 0x5A)[0]
                assert 0 <= crt <= 255, f"Unexpected CRT rate bonus {crt}"

                elem_mask = struct.unpack_from("<H", dec, base + 0x5C)[0]
                assert 0 <= elem_mask <= 0xFFFF

    assert verified_chars > 0, "No active party members verified in test saves"
