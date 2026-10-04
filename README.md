# Star Ocean 2 Save Format

A complete, byte-level reverse-engineered reference for the *Star Ocean: The Second Story* (PS1, `SCUS-94422`) memory card save format.

## What's here

- **`scripts/so2_codec.py`** — decodes/encodes the zero-run compression the game uses inside each save block, and `state()` pulls the full decoded 7,048-byte structure out of a raw 8,192-byte memory card block.
- **`tools/so2_save_map.py`** — the machine-readable byte map: every offset, field name, size, and description for the entire decoded structure. Generates `artifacts/so2-save-map/decoded_state_byte_map.json`.
- **`docs/SAVE-FORMAT.md`** — the human-readable reference, generated from the same data.
- **`tests/`** — verifies the codec and byte map stay internally consistent.

## Status

**100% mapped.** All 7,048 bytes of the decoded save structure have a confirmed, evidence-backed identity — every field, flag, and counter in the format is documented.

## Usage

```python
import sys
sys.path.insert(0, ".")
import saveconv
sys.path.insert(0, "scripts")
import so2_codec

with open("memcard.mcd", "rb") as f:
    data = f.read()

block = data[1 * 8192 : 2 * 8192]  # memory card slot 1
decoded = so2_codec.state(block)   # 7,048-byte decoded structure
```

See `docs/SAVE-FORMAT.md` for the full field-by-field layout.

## Running tests

```
pip install pytest
pytest tests/
```
