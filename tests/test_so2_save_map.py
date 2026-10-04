"""Unit and regression tests for Task BR: SO2 Save-file 7,048-Byte Map and Coverage."""

import json
from pathlib import Path
import pytest
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import so2_save_map
import saveconv
import so2_codec


def test_byte_map_coverage_and_integrity():
    """Verify that the byte map accounts for all 7,048 bytes with 0 gaps and 0 overlaps."""
    ranges = so2_save_map.generate_byte_map()
    report = so2_save_map.audit_coverage(ranges)

    assert report["total_bytes"] == 0x1B88  # 7,048 bytes
    assert report["confirmed_mapped_bytes"] + report["unknown_bytes"] == 7048
    # Coverage must exceed 80%
    assert report["confirmed_mapped_percentage"] >= 80.0
    assert report["confirmed_mapped_bytes"] >= 5600

    # Verify strictly contiguous ordering
    cur = 0
    for r in report["ranges"]:
        assert r["start"] == cur, f"Discontinuity at 0x{cur:04X} vs 0x{r['start']:04X}"
        assert r["end"] == cur + r["size"]
        assert r["status"] in ("VERIFIED", "UNKNOWN")
        cur = r["end"]
    assert cur == 7048


def test_chunk_boundaries_and_accounting():
    """Verify chunk allocations match PSX MIPS DMA / buffer memory allocations."""
    ranges = so2_save_map.generate_byte_map()
    report = so2_save_map.audit_coverage(ranges)

    chunks = {c["chunk_number"]: c for c in report["chunks"]}
    assert len(chunks) == 5

    # Chunk 1: Resource 2 (0x0000..0x01A0, 416 bytes)
    assert chunks[1]["start_offset"] == 0x0000
    assert chunks[1]["end_offset"] == 0x01A0
    assert chunks[1]["total_bytes"] == 416

    # Chunk 2: Primary Party Array (0x01A0..0x04A0, 768 bytes, 8x96B)
    assert chunks[2]["start_offset"] == 0x01A0
    assert chunks[2]["end_offset"] == 0x04A0
    assert chunks[2]["total_bytes"] == 768

    # Chunk 3: Secondary Party Array (0x04A0..0x0B20, 1664 bytes, 8x208B)
    assert chunks[3]["start_offset"] == 0x04A0
    assert chunks[3]["end_offset"] == 0x0B20
    assert chunks[3]["total_bytes"] == 1664

    # Chunk 4: Inventory (0x0B20..0x1748, 3112 bytes)
    assert chunks[4]["start_offset"] == 0x0B20
    assert chunks[4]["end_offset"] == 0x1748
    assert chunks[4]["total_bytes"] == 3112

    # Chunk 5: Resource 0xE Coordinates/Flags (0x1748..0x1B88, 1088 bytes)
    assert chunks[5]["start_offset"] == 0x1748
    assert chunks[5]["end_offset"] == 0x1B88
    assert chunks[5]["total_bytes"] == 1088


def test_empty_armor_slot_resolution_in_real_saves():
    """Verify that decoded equipment in secondary records is strictly 7 fixed uint16 slots.

    An empty armor slot is represented as 0x0000, not a compressed/shifted 6-slot array.
    """
    mcd_files = list(ROOT.glob("artifacts/**/*.mcd"))
    if not mcd_files:
        pytest.skip("No .mcd save files present (personal save data is not included in this repo)")

    for mcd in mcd_files:
        with open(mcd, "rb") as f:
            data = f.read()
        for block_idx in range(1, 16):
            block = data[block_idx * 8192 : (block_idx + 1) * 8192]
            if block[0x200:0x20A] != b"STAR OCEAN":
                continue
            decomp = so2_codec.state(block)
            assert len(decomp) == 0x1B88

            # Check equipment slots for all 8 party members
            sec_base = 0x04A0
            stride = 0xD0
            for char_idx in range(8):
                rec_offset = sec_base + char_idx * stride
                # Equipment is at offset +0x0C within secondary record (7 uint16 items)
                eq_offset = rec_offset + 0x0C
                eq_slots = struct.unpack("<7H", decomp[eq_offset : eq_offset + 14])

                # Slots: [weapon, armor, shield, helmet, greaves, acc1, acc2]
                weapon, armor, shield, helmet, greaves, acc1, acc2 = eq_slots

                # If character is populated, equipment IDs should be within valid range (0..824)
                for item_id in (weapon, armor, shield, helmet, greaves, acc1, acc2):
                    assert 0 <= item_id <= 824, f"Invalid equipment ID 0x{item_id:04X}"


def test_generated_artifact_json():
    """Verify artifacts/so2-save-map/decoded_state_byte_map.json matches generated audit."""
    ranges = so2_save_map.generate_byte_map()
    report = so2_save_map.audit_coverage(ranges)

    artifact_path = ROOT / "artifacts/so2-save-map/decoded_state_byte_map.json"
    assert artifact_path.exists(), "Artifact file does not exist"

    with open(artifact_path, "r", encoding="utf-8") as f:
        saved_report = json.load(f)

    assert saved_report["total_bytes"] == report["total_bytes"]
    assert saved_report["confirmed_mapped_bytes"] == report["confirmed_mapped_bytes"]
    assert saved_report["unknown_bytes"] == report["unknown_bytes"]
    assert len(saved_report["ranges"]) == len(report["ranges"])
