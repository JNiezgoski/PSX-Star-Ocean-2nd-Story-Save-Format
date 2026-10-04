# Star Ocean: The Second Story (PS1) — Save File Format Reference

Complete byte-level reference for the decoded 7,048-byte save state (100.00% mapped, 7,048/7,048 bytes).

A save block on the memory card is 8,192 bytes: a 512-byte PS1 directory header, an uncompressed pre-header (title signature, checksums, Voice Collection bitfield), and a zero-run-compressed body. `scripts/so2_codec.py`'s `state()` function decodes that compressed body into the flat 7,048-byte structure documented below. See `tools/so2_save_map.py` for the machine-readable version of this same map.

## Chunk Overview

| Chunk | Decoded Offset | Size | Live Pointer | Contents |
|---|---|---|---|---|
| 1 | `0x0000..0x01A0` | 416 B | `[0x80075270]` | Button bitmasks, Game clock, Fol, Battles won counter, Options, Window colors, Friendship & Romance 12x12 matrices, HP/MP multipliers |
| 2 | `0x01A0..0x04A0` | 768 B | `[0x8007527C]` | Signed ID, status conditions, 10 elemental resistances, status protection mask, EXP, HP/MP triplets, Level, STR/CON/AGL/DEX/INT/GUTS triplets, Attribute triplets A/B, CRT bonus, Weapon element mask, Combat state flags |
| 3 | `0x04A0..0x0B20` | 1,664 B | `[0x80075280]` | LUC/STM triplets, 7 equipment slots (weapon/armor/shield/helm/greaves/acc1/acc2), SP, Talents, Names (16B), Combat stance/LC flags, 32 known ability flags, 46 specialty skill levels, 32 ability proficiencies/spell counters (64B), 4 equipped KM shortcuts |
| 4 | `0x0B20..0x1748` | 3,112 B | `[0x80075278]` | 1,024 x 16-bit item slots, 16 recent item IDs, 1,024 hash/integrity bytes |
| 5 | `0x1748..0x1B88` | 1,088 B | `Resource 0xE (F=[0x80075710] + G=[0x80075704])` | Saved XYZ coordinates, Area ID, 12x20B Name Table, Message speed, 48 Clock snapshots, 10 Pending items, Psynard coordinates, 2,944 Global story flags (including 338 treasure chests at 0x1B14..0x1B3D) |

## Chunk 1: Options / Fol / Affection (Resource 2)

Decoded offset `0x0000..0x01A0` (416 bytes). Live pointer: `[0x80075270]`.

| Offset | Size | Field | Description |
|---|---|---|---|
| `0x0000..0x0010` | 16 B | Controller Button Bitmasks | 8 x uint16 button assignments (Cross, Circle, Triangle, Square, Down, Left, Select, Start) |
| `0x0010..0x0014` | 4 B | Game Clock Time Word | Cumulative playtime counter word derived from hardware timer |
| `0x0014..0x0018` | 4 B | Operational Counter A | Runtime operational event counter |
| `0x0018..0x001C` | 4 B | Fol | Party currency (uint32 little-endian, max 999,999,999) |
| `0x001C..0x0020` | 4 B | Total Battles Won Counter | uint32 cumulative battles won counter (read via resident script getter 0x80067788) |
| `0x0020..0x0024` | 4 B | Save Counter A | Total in-game save action counter |
| `0x0024..0x0028` | 4 B | Save Preparation Counter | Incremented each time the save screen is invoked |
| `0x0028..0x002B` | 3 B | Save Counter B | Secondary save confirmation counter |
| `0x002B..0x002C` | 1 B | Companion Counter Delimiter Byte | Null delimiter byte (0x00) following menu operation counter |
| `0x002C..0x0030` | 4 B | Specialty Secondary Operation Counter | uint32 secondary companion operation counter (read via resident script getter 0x80067870) |
| `0x0030..0x0040` | 16 B | Window Corner Colors | 4 x uint32 window gradient corners (UL, UR, LL, LR; 0x00BBGGRR) |
| `0x0040..0x0042` | 2 B | Party Selector Flags | Active party member selection flags |
| `0x0042..0x0044` | 2 B | Non-Default Name Booleans | Booleans for Claude (0x42) and Rena (0x43) indicating custom player-assigned names |
| `0x0044..0x004D` | 9 B | Audio / Video / Gameplay Options | Sound mode (0x44), Route selector (0x45), Vibration (0x46), Window style (0x47..0x48), Targeting (0x49), Camera (0x4A), Motion (0x4B), Disc ID (0x4C) |
| `0x004D..0x004E` | 1 B | Global Link Combo Mode Active Flag | Boolean flag indicating Link Combo mode active on any party member (written at resident.asm 0x8003197C) |
| `0x004E..0x004F` | 1 B | Scripted System Milestone Flag | Boolean milestone flag written by script VM opcode 279 (written at resident.asm 0x80067B34) |
| `0x004F..0x0050` | 1 B | Natural Word Alignment Zero Pad | Alignment zero padding (0x00) aligning structure to 4-byte boundary before 32-bit timestamp word |
| `0x0050..0x0054` | 4 B | Voice Collection 64-Word Rolling Integrity Hash | 32-bit rolling integrity hash over the 64 words (256 bytes) of the Voice Collection buffer at S+0x01A0..0x02A0. Formula: v1 = (~v1 + word) mod 2^32 across all 64 words, little-endian. Written via `sw $v1, 0x50($v0)` at 0x8007F604 inside the boss-combat overlay (Disc 2 Archive 1984). Recomputed and verified whenever a new voice line is unlocked. |
| `0x0054..0x0058` | 4 B | Clock Throttle / Timer Word | Frame/timing sync word |
| `0x0058..0x00E8` | 144 B | Friendship Relationship Matrix | 12 x 12 character emotional level matrix (friendship values 0..15 per pair) |
| `0x00E8..0x0178` | 144 B | Romance / Affection Relationship Matrix | 12 x 12 character emotional level matrix (romance/affection values 0..15 per pair) |
| `0x0178..0x017C` | 4 B | Game Completion Code | Cleared game / voice collection unlocked marker word |
| `0x017C..0x0184` | 8 B | Modifier Prefix Alignment Pad | 8-byte structural zero padding flanking game completion code and stat multipliers; 100% verified zeroes across all saves |
| `0x0184..0x0188` | 4 B | HP / MP Skill Scaling Modifiers | uint16 HP percentage bonus (0x184) and uint16 MP percentage bonus (0x186) |
| `0x0188..0x0198` | 16 B | Modifier Trailing Alignment Pad | 16-byte structural zero padding flanking stat multipliers and save menu selection words; 100% verified zeroes across all saves |
| `0x0198..0x01A0` | 8 B | Save Menu Selection State | Last selected slot indices and UI cursor positions |

## Chunk 2: Party Primary Record Array (8 Slots x 96B)

Decoded offset `0x01A0..0x04A0` (768 bytes). Live pointer: `[0x8007527C]`.

| Offset | Size | Field | Description |
|---|---|---|---|
| `0x01A0..0x01A4` | 4 B | Slot 0 ID & Condition Flags | Signed ID (+0, int16), Status flags (+2, uint8: Dead, Paralysis, Stone, Poison), Class byte (+3) |
| `0x01A4..0x01AE` | 10 B | Slot 0 Elemental Damage Resistances | 10 elemental damage resistances: Earth (+4), Water (+5), Fire (+6), Wind (+7), Thunder (+8), Star (+9), Void (+A), Light (+B), Dark (+C), Physical (+D); 0=Neutral, 1=Weak, 2=Resist, 3=Immune, 4=Absorb. Computed from gear via combat.asm 0x80081878..0x80081890 |
| `0x01AE..0x01B0` | 2 B | Slot 0 Status Ailment Protection Mask | uint16 status protection / immunity bitmask aggregated from equipped gear via combat.asm 0x80081878..0x80081890 |
| `0x01B0..0x01EE` | 62 B | Slot 0 EXP, Level, HP/MP & Core Stats | EXP (+10, uint32), HP triplet (+14..+1F), MP triplet (+20..+25), Derived/Base Level (+26..+29), STR/CON/AGL/DEX/INT/GUTS triplets (+2A..+4D) |
| `0x01EE..0x01FA` | 12 B | Slot 0 Attribute Triplets A & B | Attribute triplet A (+4E..+53, init 16/15) and B (+54..+59, init 9/6/8/7), scaled in combat at 0x80081824..0x8008184C |
| `0x01FA..0x01FC` | 2 B | Slot 0 Critical Hit Rate Bonus (CRT %) | int16 equipment critical hit rate bonus percentage summed from item property 0x1B via combat.asm 0x80081854..0x80081870 |
| `0x01FC..0x01FE` | 2 B | Slot 0 Weapon Elemental Attack Mask | uint16 bitmask of weapon attack elements (Water 0x02, Fire 0x04, Wind 0x08, Earth 0x10, Thunder 0x20, Star/Dark 0x40, Light 0x80) bitwise ORed via combat.asm 0x80081868..0x80081874 |
| `0x01FE..0x0200` | 2 B | Slot 0 Combat State Flags | uint16 transient combat/battle actor state flags (0x0000 in field saves) |
| `0x0200..0x0204` | 4 B | Slot 1 ID & Condition Flags | Signed ID (+0, int16), Status flags (+2, uint8: Dead, Paralysis, Stone, Poison), Class byte (+3) |
| `0x0204..0x020E` | 10 B | Slot 1 Elemental Damage Resistances | 10 elemental damage resistances: Earth (+4), Water (+5), Fire (+6), Wind (+7), Thunder (+8), Star (+9), Void (+A), Light (+B), Dark (+C), Physical (+D); 0=Neutral, 1=Weak, 2=Resist, 3=Immune, 4=Absorb. Computed from gear via combat.asm 0x80081878..0x80081890 |
| `0x020E..0x0210` | 2 B | Slot 1 Status Ailment Protection Mask | uint16 status protection / immunity bitmask aggregated from equipped gear via combat.asm 0x80081878..0x80081890 |
| `0x0210..0x024E` | 62 B | Slot 1 EXP, Level, HP/MP & Core Stats | EXP (+10, uint32), HP triplet (+14..+1F), MP triplet (+20..+25), Derived/Base Level (+26..+29), STR/CON/AGL/DEX/INT/GUTS triplets (+2A..+4D) |
| `0x024E..0x025A` | 12 B | Slot 1 Attribute Triplets A & B | Attribute triplet A (+4E..+53, init 16/15) and B (+54..+59, init 9/6/8/7), scaled in combat at 0x80081824..0x8008184C |
| `0x025A..0x025C` | 2 B | Slot 1 Critical Hit Rate Bonus (CRT %) | int16 equipment critical hit rate bonus percentage summed from item property 0x1B via combat.asm 0x80081854..0x80081870 |
| `0x025C..0x025E` | 2 B | Slot 1 Weapon Elemental Attack Mask | uint16 bitmask of weapon attack elements (Water 0x02, Fire 0x04, Wind 0x08, Earth 0x10, Thunder 0x20, Star/Dark 0x40, Light 0x80) bitwise ORed via combat.asm 0x80081868..0x80081874 |
| `0x025E..0x0260` | 2 B | Slot 1 Combat State Flags | uint16 transient combat/battle actor state flags (0x0000 in field saves) |
| `0x0260..0x0264` | 4 B | Slot 2 ID & Condition Flags | Signed ID (+0, int16), Status flags (+2, uint8: Dead, Paralysis, Stone, Poison), Class byte (+3) |
| `0x0264..0x026E` | 10 B | Slot 2 Elemental Damage Resistances | 10 elemental damage resistances: Earth (+4), Water (+5), Fire (+6), Wind (+7), Thunder (+8), Star (+9), Void (+A), Light (+B), Dark (+C), Physical (+D); 0=Neutral, 1=Weak, 2=Resist, 3=Immune, 4=Absorb. Computed from gear via combat.asm 0x80081878..0x80081890 |
| `0x026E..0x0270` | 2 B | Slot 2 Status Ailment Protection Mask | uint16 status protection / immunity bitmask aggregated from equipped gear via combat.asm 0x80081878..0x80081890 |
| `0x0270..0x02AE` | 62 B | Slot 2 EXP, Level, HP/MP & Core Stats | EXP (+10, uint32), HP triplet (+14..+1F), MP triplet (+20..+25), Derived/Base Level (+26..+29), STR/CON/AGL/DEX/INT/GUTS triplets (+2A..+4D) |
| `0x02AE..0x02BA` | 12 B | Slot 2 Attribute Triplets A & B | Attribute triplet A (+4E..+53, init 16/15) and B (+54..+59, init 9/6/8/7), scaled in combat at 0x80081824..0x8008184C |
| `0x02BA..0x02BC` | 2 B | Slot 2 Critical Hit Rate Bonus (CRT %) | int16 equipment critical hit rate bonus percentage summed from item property 0x1B via combat.asm 0x80081854..0x80081870 |
| `0x02BC..0x02BE` | 2 B | Slot 2 Weapon Elemental Attack Mask | uint16 bitmask of weapon attack elements (Water 0x02, Fire 0x04, Wind 0x08, Earth 0x10, Thunder 0x20, Star/Dark 0x40, Light 0x80) bitwise ORed via combat.asm 0x80081868..0x80081874 |
| `0x02BE..0x02C0` | 2 B | Slot 2 Combat State Flags | uint16 transient combat/battle actor state flags (0x0000 in field saves) |
| `0x02C0..0x02C4` | 4 B | Slot 3 ID & Condition Flags | Signed ID (+0, int16), Status flags (+2, uint8: Dead, Paralysis, Stone, Poison), Class byte (+3) |
| `0x02C4..0x02CE` | 10 B | Slot 3 Elemental Damage Resistances | 10 elemental damage resistances: Earth (+4), Water (+5), Fire (+6), Wind (+7), Thunder (+8), Star (+9), Void (+A), Light (+B), Dark (+C), Physical (+D); 0=Neutral, 1=Weak, 2=Resist, 3=Immune, 4=Absorb. Computed from gear via combat.asm 0x80081878..0x80081890 |
| `0x02CE..0x02D0` | 2 B | Slot 3 Status Ailment Protection Mask | uint16 status protection / immunity bitmask aggregated from equipped gear via combat.asm 0x80081878..0x80081890 |
| `0x02D0..0x030E` | 62 B | Slot 3 EXP, Level, HP/MP & Core Stats | EXP (+10, uint32), HP triplet (+14..+1F), MP triplet (+20..+25), Derived/Base Level (+26..+29), STR/CON/AGL/DEX/INT/GUTS triplets (+2A..+4D) |
| `0x030E..0x031A` | 12 B | Slot 3 Attribute Triplets A & B | Attribute triplet A (+4E..+53, init 16/15) and B (+54..+59, init 9/6/8/7), scaled in combat at 0x80081824..0x8008184C |
| `0x031A..0x031C` | 2 B | Slot 3 Critical Hit Rate Bonus (CRT %) | int16 equipment critical hit rate bonus percentage summed from item property 0x1B via combat.asm 0x80081854..0x80081870 |
| `0x031C..0x031E` | 2 B | Slot 3 Weapon Elemental Attack Mask | uint16 bitmask of weapon attack elements (Water 0x02, Fire 0x04, Wind 0x08, Earth 0x10, Thunder 0x20, Star/Dark 0x40, Light 0x80) bitwise ORed via combat.asm 0x80081868..0x80081874 |
| `0x031E..0x0320` | 2 B | Slot 3 Combat State Flags | uint16 transient combat/battle actor state flags (0x0000 in field saves) |
| `0x0320..0x0324` | 4 B | Slot 4 ID & Condition Flags | Signed ID (+0, int16), Status flags (+2, uint8: Dead, Paralysis, Stone, Poison), Class byte (+3) |
| `0x0324..0x032E` | 10 B | Slot 4 Elemental Damage Resistances | 10 elemental damage resistances: Earth (+4), Water (+5), Fire (+6), Wind (+7), Thunder (+8), Star (+9), Void (+A), Light (+B), Dark (+C), Physical (+D); 0=Neutral, 1=Weak, 2=Resist, 3=Immune, 4=Absorb. Computed from gear via combat.asm 0x80081878..0x80081890 |
| `0x032E..0x0330` | 2 B | Slot 4 Status Ailment Protection Mask | uint16 status protection / immunity bitmask aggregated from equipped gear via combat.asm 0x80081878..0x80081890 |
| `0x0330..0x036E` | 62 B | Slot 4 EXP, Level, HP/MP & Core Stats | EXP (+10, uint32), HP triplet (+14..+1F), MP triplet (+20..+25), Derived/Base Level (+26..+29), STR/CON/AGL/DEX/INT/GUTS triplets (+2A..+4D) |
| `0x036E..0x037A` | 12 B | Slot 4 Attribute Triplets A & B | Attribute triplet A (+4E..+53, init 16/15) and B (+54..+59, init 9/6/8/7), scaled in combat at 0x80081824..0x8008184C |
| `0x037A..0x037C` | 2 B | Slot 4 Critical Hit Rate Bonus (CRT %) | int16 equipment critical hit rate bonus percentage summed from item property 0x1B via combat.asm 0x80081854..0x80081870 |
| `0x037C..0x037E` | 2 B | Slot 4 Weapon Elemental Attack Mask | uint16 bitmask of weapon attack elements (Water 0x02, Fire 0x04, Wind 0x08, Earth 0x10, Thunder 0x20, Star/Dark 0x40, Light 0x80) bitwise ORed via combat.asm 0x80081868..0x80081874 |
| `0x037E..0x0380` | 2 B | Slot 4 Combat State Flags | uint16 transient combat/battle actor state flags (0x0000 in field saves) |
| `0x0380..0x0384` | 4 B | Slot 5 ID & Condition Flags | Signed ID (+0, int16), Status flags (+2, uint8: Dead, Paralysis, Stone, Poison), Class byte (+3) |
| `0x0384..0x038E` | 10 B | Slot 5 Elemental Damage Resistances | 10 elemental damage resistances: Earth (+4), Water (+5), Fire (+6), Wind (+7), Thunder (+8), Star (+9), Void (+A), Light (+B), Dark (+C), Physical (+D); 0=Neutral, 1=Weak, 2=Resist, 3=Immune, 4=Absorb. Computed from gear via combat.asm 0x80081878..0x80081890 |
| `0x038E..0x0390` | 2 B | Slot 5 Status Ailment Protection Mask | uint16 status protection / immunity bitmask aggregated from equipped gear via combat.asm 0x80081878..0x80081890 |
| `0x0390..0x03CE` | 62 B | Slot 5 EXP, Level, HP/MP & Core Stats | EXP (+10, uint32), HP triplet (+14..+1F), MP triplet (+20..+25), Derived/Base Level (+26..+29), STR/CON/AGL/DEX/INT/GUTS triplets (+2A..+4D) |
| `0x03CE..0x03DA` | 12 B | Slot 5 Attribute Triplets A & B | Attribute triplet A (+4E..+53, init 16/15) and B (+54..+59, init 9/6/8/7), scaled in combat at 0x80081824..0x8008184C |
| `0x03DA..0x03DC` | 2 B | Slot 5 Critical Hit Rate Bonus (CRT %) | int16 equipment critical hit rate bonus percentage summed from item property 0x1B via combat.asm 0x80081854..0x80081870 |
| `0x03DC..0x03DE` | 2 B | Slot 5 Weapon Elemental Attack Mask | uint16 bitmask of weapon attack elements (Water 0x02, Fire 0x04, Wind 0x08, Earth 0x10, Thunder 0x20, Star/Dark 0x40, Light 0x80) bitwise ORed via combat.asm 0x80081868..0x80081874 |
| `0x03DE..0x03E0` | 2 B | Slot 5 Combat State Flags | uint16 transient combat/battle actor state flags (0x0000 in field saves) |
| `0x03E0..0x03E4` | 4 B | Slot 6 ID & Condition Flags | Signed ID (+0, int16), Status flags (+2, uint8: Dead, Paralysis, Stone, Poison), Class byte (+3) |
| `0x03E4..0x03EE` | 10 B | Slot 6 Elemental Damage Resistances | 10 elemental damage resistances: Earth (+4), Water (+5), Fire (+6), Wind (+7), Thunder (+8), Star (+9), Void (+A), Light (+B), Dark (+C), Physical (+D); 0=Neutral, 1=Weak, 2=Resist, 3=Immune, 4=Absorb. Computed from gear via combat.asm 0x80081878..0x80081890 |
| `0x03EE..0x03F0` | 2 B | Slot 6 Status Ailment Protection Mask | uint16 status protection / immunity bitmask aggregated from equipped gear via combat.asm 0x80081878..0x80081890 |
| `0x03F0..0x042E` | 62 B | Slot 6 EXP, Level, HP/MP & Core Stats | EXP (+10, uint32), HP triplet (+14..+1F), MP triplet (+20..+25), Derived/Base Level (+26..+29), STR/CON/AGL/DEX/INT/GUTS triplets (+2A..+4D) |
| `0x042E..0x043A` | 12 B | Slot 6 Attribute Triplets A & B | Attribute triplet A (+4E..+53, init 16/15) and B (+54..+59, init 9/6/8/7), scaled in combat at 0x80081824..0x8008184C |
| `0x043A..0x043C` | 2 B | Slot 6 Critical Hit Rate Bonus (CRT %) | int16 equipment critical hit rate bonus percentage summed from item property 0x1B via combat.asm 0x80081854..0x80081870 |
| `0x043C..0x043E` | 2 B | Slot 6 Weapon Elemental Attack Mask | uint16 bitmask of weapon attack elements (Water 0x02, Fire 0x04, Wind 0x08, Earth 0x10, Thunder 0x20, Star/Dark 0x40, Light 0x80) bitwise ORed via combat.asm 0x80081868..0x80081874 |
| `0x043E..0x0440` | 2 B | Slot 6 Combat State Flags | uint16 transient combat/battle actor state flags (0x0000 in field saves) |
| `0x0440..0x0444` | 4 B | Slot 7 ID & Condition Flags | Signed ID (+0, int16), Status flags (+2, uint8: Dead, Paralysis, Stone, Poison), Class byte (+3) |
| `0x0444..0x044E` | 10 B | Slot 7 Elemental Damage Resistances | 10 elemental damage resistances: Earth (+4), Water (+5), Fire (+6), Wind (+7), Thunder (+8), Star (+9), Void (+A), Light (+B), Dark (+C), Physical (+D); 0=Neutral, 1=Weak, 2=Resist, 3=Immune, 4=Absorb. Computed from gear via combat.asm 0x80081878..0x80081890 |
| `0x044E..0x0450` | 2 B | Slot 7 Status Ailment Protection Mask | uint16 status protection / immunity bitmask aggregated from equipped gear via combat.asm 0x80081878..0x80081890 |
| `0x0450..0x048E` | 62 B | Slot 7 EXP, Level, HP/MP & Core Stats | EXP (+10, uint32), HP triplet (+14..+1F), MP triplet (+20..+25), Derived/Base Level (+26..+29), STR/CON/AGL/DEX/INT/GUTS triplets (+2A..+4D) |
| `0x048E..0x049A` | 12 B | Slot 7 Attribute Triplets A & B | Attribute triplet A (+4E..+53, init 16/15) and B (+54..+59, init 9/6/8/7), scaled in combat at 0x80081824..0x8008184C |
| `0x049A..0x049C` | 2 B | Slot 7 Critical Hit Rate Bonus (CRT %) | int16 equipment critical hit rate bonus percentage summed from item property 0x1B via combat.asm 0x80081854..0x80081870 |
| `0x049C..0x049E` | 2 B | Slot 7 Weapon Elemental Attack Mask | uint16 bitmask of weapon attack elements (Water 0x02, Fire 0x04, Wind 0x08, Earth 0x10, Thunder 0x20, Star/Dark 0x40, Light 0x80) bitwise ORed via combat.asm 0x80081868..0x80081874 |
| `0x049E..0x04A0` | 2 B | Slot 7 Combat State Flags | uint16 transient combat/battle actor state flags (0x0000 in field saves) |

## Chunk 3: Party Secondary Record Array (8 Slots x 208B)

Decoded offset `0x04A0..0x0B20` (1,664 bytes). Live pointer: `[0x80075280]`.

| Offset | Size | Field | Description |
|---|---|---|---|
| `0x04A0..0x04AC` | 12 B | Slot 0 Extended Stats (LUC & STM) | LUC triplet (+0..+5) and STM triplet (+6..+B) |
| `0x04AC..0x04BA` | 14 B | Slot 0 Equipment (7 Slots) | 7 x uint16 item IDs: weapon, armor, shield, helmet, greaves, acc1, acc2 (0x0000 = empty slot) |
| `0x04BA..0x04BC` | 2 B | Slot 0 SP Capped Value | Current available SP to spend (clamped 0..999) |
| `0x04BC..0x04C0` | 4 B | Slot 0 SP-to-Talent Alignment Padding | 4-byte structural zero padding aligning uint16 SP (+0x1A) to uint32 Talent Bitmask (+0x20); zeroed at init (0x8007A240) and verified 100% [0,0,0,0] across all saves |
| `0x04C0..0x04C4` | 4 B | Slot 0 Talent Bitmask | Low 10 bits indicate unlocked talents (Originality, Dexterity, etc.) |
| `0x04C4..0x04D4` | 16 B | Slot 0 Character Name | Null-padded ASCII character name string (max 16 characters) |
| `0x04D4..0x04DC` | 8 B | Slot 0 Combat Stance & Tactical Configuration | Combat stance (+0x34..+0x39), tactical configuration bitmask at +0x3A (bit 2 0x04 = Link Combo mode toggle 'LC ON'/'LC OFF' modified by KM menu overlay code-3004 0x80081B30..0x80081C3C, bit 0 0x01 = tactical behavior flag), and delimiter byte at +0x3B (0x00) |
| `0x04DC..0x04FC` | 32 B | Slot 0 Known / Unlocked Ability Flags | 32 x uint8 boolean flags (0x01=learned, 0x00=unlearned) for Killer Moves (fighters) and Spells (mages), indexed by 1-based ability ID |
| `0x04FC..0x04FD` | 1 B | Slot 0 Skill Table Delimiter | Single null byte (0x00) delimiting ability flag array and specialty skill levels |
| `0x04FD..0x052B` | 46 B | Slot 0 Specialty Skill Levels | 46 uint8 skill levels (0..10) corresponding to all standard IC/combat skills (Mineralogy, Cooking, Knife, etc.) |
| `0x052B..0x052C` | 1 B | Slot 0 Proficiency Table Alignment Pad | Single null byte (0x00) aligning the following uint16 proficiency array to 2-byte boundary |
| `0x052C..0x056C` | 64 B | Slot 0 Ability Proficiencies & Spell Counters | 32 x uint16 little-endian usage counters (0..999) indexed by 1-based ability ID; Killer Move proficiency for fighters, spell cast count for mages |
| `0x056C..0x0570` | 4 B | Slot 0 Equipped Killer Move Shortcuts | 4 x uint8 assigned ability IDs: Short-range L1 (+0xCC), Short-range R1 (+0xCD), Long-range L1 (+0xCE), Long-range R1 (+0xCF); all 0x00 for mages |
| `0x0570..0x057C` | 12 B | Slot 1 Extended Stats (LUC & STM) | LUC triplet (+0..+5) and STM triplet (+6..+B) |
| `0x057C..0x058A` | 14 B | Slot 1 Equipment (7 Slots) | 7 x uint16 item IDs: weapon, armor, shield, helmet, greaves, acc1, acc2 (0x0000 = empty slot) |
| `0x058A..0x058C` | 2 B | Slot 1 SP Capped Value | Current available SP to spend (clamped 0..999) |
| `0x058C..0x0590` | 4 B | Slot 1 SP-to-Talent Alignment Padding | 4-byte structural zero padding aligning uint16 SP (+0x1A) to uint32 Talent Bitmask (+0x20); zeroed at init (0x8007A240) and verified 100% [0,0,0,0] across all saves |
| `0x0590..0x0594` | 4 B | Slot 1 Talent Bitmask | Low 10 bits indicate unlocked talents (Originality, Dexterity, etc.) |
| `0x0594..0x05A4` | 16 B | Slot 1 Character Name | Null-padded ASCII character name string (max 16 characters) |
| `0x05A4..0x05AC` | 8 B | Slot 1 Combat Stance & Tactical Configuration | Combat stance (+0x34..+0x39), tactical configuration bitmask at +0x3A (bit 2 0x04 = Link Combo mode toggle 'LC ON'/'LC OFF' modified by KM menu overlay code-3004 0x80081B30..0x80081C3C, bit 0 0x01 = tactical behavior flag), and delimiter byte at +0x3B (0x00) |
| `0x05AC..0x05CC` | 32 B | Slot 1 Known / Unlocked Ability Flags | 32 x uint8 boolean flags (0x01=learned, 0x00=unlearned) for Killer Moves (fighters) and Spells (mages), indexed by 1-based ability ID |
| `0x05CC..0x05CD` | 1 B | Slot 1 Skill Table Delimiter | Single null byte (0x00) delimiting ability flag array and specialty skill levels |
| `0x05CD..0x05FB` | 46 B | Slot 1 Specialty Skill Levels | 46 uint8 skill levels (0..10) corresponding to all standard IC/combat skills (Mineralogy, Cooking, Knife, etc.) |
| `0x05FB..0x05FC` | 1 B | Slot 1 Proficiency Table Alignment Pad | Single null byte (0x00) aligning the following uint16 proficiency array to 2-byte boundary |
| `0x05FC..0x063C` | 64 B | Slot 1 Ability Proficiencies & Spell Counters | 32 x uint16 little-endian usage counters (0..999) indexed by 1-based ability ID; Killer Move proficiency for fighters, spell cast count for mages |
| `0x063C..0x0640` | 4 B | Slot 1 Equipped Killer Move Shortcuts | 4 x uint8 assigned ability IDs: Short-range L1 (+0xCC), Short-range R1 (+0xCD), Long-range L1 (+0xCE), Long-range R1 (+0xCF); all 0x00 for mages |
| `0x0640..0x064C` | 12 B | Slot 2 Extended Stats (LUC & STM) | LUC triplet (+0..+5) and STM triplet (+6..+B) |
| `0x064C..0x065A` | 14 B | Slot 2 Equipment (7 Slots) | 7 x uint16 item IDs: weapon, armor, shield, helmet, greaves, acc1, acc2 (0x0000 = empty slot) |
| `0x065A..0x065C` | 2 B | Slot 2 SP Capped Value | Current available SP to spend (clamped 0..999) |
| `0x065C..0x0660` | 4 B | Slot 2 SP-to-Talent Alignment Padding | 4-byte structural zero padding aligning uint16 SP (+0x1A) to uint32 Talent Bitmask (+0x20); zeroed at init (0x8007A240) and verified 100% [0,0,0,0] across all saves |
| `0x0660..0x0664` | 4 B | Slot 2 Talent Bitmask | Low 10 bits indicate unlocked talents (Originality, Dexterity, etc.) |
| `0x0664..0x0674` | 16 B | Slot 2 Character Name | Null-padded ASCII character name string (max 16 characters) |
| `0x0674..0x067C` | 8 B | Slot 2 Combat Stance & Tactical Configuration | Combat stance (+0x34..+0x39), tactical configuration bitmask at +0x3A (bit 2 0x04 = Link Combo mode toggle 'LC ON'/'LC OFF' modified by KM menu overlay code-3004 0x80081B30..0x80081C3C, bit 0 0x01 = tactical behavior flag), and delimiter byte at +0x3B (0x00) |
| `0x067C..0x069C` | 32 B | Slot 2 Known / Unlocked Ability Flags | 32 x uint8 boolean flags (0x01=learned, 0x00=unlearned) for Killer Moves (fighters) and Spells (mages), indexed by 1-based ability ID |
| `0x069C..0x069D` | 1 B | Slot 2 Skill Table Delimiter | Single null byte (0x00) delimiting ability flag array and specialty skill levels |
| `0x069D..0x06CB` | 46 B | Slot 2 Specialty Skill Levels | 46 uint8 skill levels (0..10) corresponding to all standard IC/combat skills (Mineralogy, Cooking, Knife, etc.) |
| `0x06CB..0x06CC` | 1 B | Slot 2 Proficiency Table Alignment Pad | Single null byte (0x00) aligning the following uint16 proficiency array to 2-byte boundary |
| `0x06CC..0x070C` | 64 B | Slot 2 Ability Proficiencies & Spell Counters | 32 x uint16 little-endian usage counters (0..999) indexed by 1-based ability ID; Killer Move proficiency for fighters, spell cast count for mages |
| `0x070C..0x0710` | 4 B | Slot 2 Equipped Killer Move Shortcuts | 4 x uint8 assigned ability IDs: Short-range L1 (+0xCC), Short-range R1 (+0xCD), Long-range L1 (+0xCE), Long-range R1 (+0xCF); all 0x00 for mages |
| `0x0710..0x071C` | 12 B | Slot 3 Extended Stats (LUC & STM) | LUC triplet (+0..+5) and STM triplet (+6..+B) |
| `0x071C..0x072A` | 14 B | Slot 3 Equipment (7 Slots) | 7 x uint16 item IDs: weapon, armor, shield, helmet, greaves, acc1, acc2 (0x0000 = empty slot) |
| `0x072A..0x072C` | 2 B | Slot 3 SP Capped Value | Current available SP to spend (clamped 0..999) |
| `0x072C..0x0730` | 4 B | Slot 3 SP-to-Talent Alignment Padding | 4-byte structural zero padding aligning uint16 SP (+0x1A) to uint32 Talent Bitmask (+0x20); zeroed at init (0x8007A240) and verified 100% [0,0,0,0] across all saves |
| `0x0730..0x0734` | 4 B | Slot 3 Talent Bitmask | Low 10 bits indicate unlocked talents (Originality, Dexterity, etc.) |
| `0x0734..0x0744` | 16 B | Slot 3 Character Name | Null-padded ASCII character name string (max 16 characters) |
| `0x0744..0x074C` | 8 B | Slot 3 Combat Stance & Tactical Configuration | Combat stance (+0x34..+0x39), tactical configuration bitmask at +0x3A (bit 2 0x04 = Link Combo mode toggle 'LC ON'/'LC OFF' modified by KM menu overlay code-3004 0x80081B30..0x80081C3C, bit 0 0x01 = tactical behavior flag), and delimiter byte at +0x3B (0x00) |
| `0x074C..0x076C` | 32 B | Slot 3 Known / Unlocked Ability Flags | 32 x uint8 boolean flags (0x01=learned, 0x00=unlearned) for Killer Moves (fighters) and Spells (mages), indexed by 1-based ability ID |
| `0x076C..0x076D` | 1 B | Slot 3 Skill Table Delimiter | Single null byte (0x00) delimiting ability flag array and specialty skill levels |
| `0x076D..0x079B` | 46 B | Slot 3 Specialty Skill Levels | 46 uint8 skill levels (0..10) corresponding to all standard IC/combat skills (Mineralogy, Cooking, Knife, etc.) |
| `0x079B..0x079C` | 1 B | Slot 3 Proficiency Table Alignment Pad | Single null byte (0x00) aligning the following uint16 proficiency array to 2-byte boundary |
| `0x079C..0x07DC` | 64 B | Slot 3 Ability Proficiencies & Spell Counters | 32 x uint16 little-endian usage counters (0..999) indexed by 1-based ability ID; Killer Move proficiency for fighters, spell cast count for mages |
| `0x07DC..0x07E0` | 4 B | Slot 3 Equipped Killer Move Shortcuts | 4 x uint8 assigned ability IDs: Short-range L1 (+0xCC), Short-range R1 (+0xCD), Long-range L1 (+0xCE), Long-range R1 (+0xCF); all 0x00 for mages |
| `0x07E0..0x07EC` | 12 B | Slot 4 Extended Stats (LUC & STM) | LUC triplet (+0..+5) and STM triplet (+6..+B) |
| `0x07EC..0x07FA` | 14 B | Slot 4 Equipment (7 Slots) | 7 x uint16 item IDs: weapon, armor, shield, helmet, greaves, acc1, acc2 (0x0000 = empty slot) |
| `0x07FA..0x07FC` | 2 B | Slot 4 SP Capped Value | Current available SP to spend (clamped 0..999) |
| `0x07FC..0x0800` | 4 B | Slot 4 SP-to-Talent Alignment Padding | 4-byte structural zero padding aligning uint16 SP (+0x1A) to uint32 Talent Bitmask (+0x20); zeroed at init (0x8007A240) and verified 100% [0,0,0,0] across all saves |
| `0x0800..0x0804` | 4 B | Slot 4 Talent Bitmask | Low 10 bits indicate unlocked talents (Originality, Dexterity, etc.) |
| `0x0804..0x0814` | 16 B | Slot 4 Character Name | Null-padded ASCII character name string (max 16 characters) |
| `0x0814..0x081C` | 8 B | Slot 4 Combat Stance & Tactical Configuration | Combat stance (+0x34..+0x39), tactical configuration bitmask at +0x3A (bit 2 0x04 = Link Combo mode toggle 'LC ON'/'LC OFF' modified by KM menu overlay code-3004 0x80081B30..0x80081C3C, bit 0 0x01 = tactical behavior flag), and delimiter byte at +0x3B (0x00) |
| `0x081C..0x083C` | 32 B | Slot 4 Known / Unlocked Ability Flags | 32 x uint8 boolean flags (0x01=learned, 0x00=unlearned) for Killer Moves (fighters) and Spells (mages), indexed by 1-based ability ID |
| `0x083C..0x083D` | 1 B | Slot 4 Skill Table Delimiter | Single null byte (0x00) delimiting ability flag array and specialty skill levels |
| `0x083D..0x086B` | 46 B | Slot 4 Specialty Skill Levels | 46 uint8 skill levels (0..10) corresponding to all standard IC/combat skills (Mineralogy, Cooking, Knife, etc.) |
| `0x086B..0x086C` | 1 B | Slot 4 Proficiency Table Alignment Pad | Single null byte (0x00) aligning the following uint16 proficiency array to 2-byte boundary |
| `0x086C..0x08AC` | 64 B | Slot 4 Ability Proficiencies & Spell Counters | 32 x uint16 little-endian usage counters (0..999) indexed by 1-based ability ID; Killer Move proficiency for fighters, spell cast count for mages |
| `0x08AC..0x08B0` | 4 B | Slot 4 Equipped Killer Move Shortcuts | 4 x uint8 assigned ability IDs: Short-range L1 (+0xCC), Short-range R1 (+0xCD), Long-range L1 (+0xCE), Long-range R1 (+0xCF); all 0x00 for mages |
| `0x08B0..0x08BC` | 12 B | Slot 5 Extended Stats (LUC & STM) | LUC triplet (+0..+5) and STM triplet (+6..+B) |
| `0x08BC..0x08CA` | 14 B | Slot 5 Equipment (7 Slots) | 7 x uint16 item IDs: weapon, armor, shield, helmet, greaves, acc1, acc2 (0x0000 = empty slot) |
| `0x08CA..0x08CC` | 2 B | Slot 5 SP Capped Value | Current available SP to spend (clamped 0..999) |
| `0x08CC..0x08D0` | 4 B | Slot 5 SP-to-Talent Alignment Padding | 4-byte structural zero padding aligning uint16 SP (+0x1A) to uint32 Talent Bitmask (+0x20); zeroed at init (0x8007A240) and verified 100% [0,0,0,0] across all saves |
| `0x08D0..0x08D4` | 4 B | Slot 5 Talent Bitmask | Low 10 bits indicate unlocked talents (Originality, Dexterity, etc.) |
| `0x08D4..0x08E4` | 16 B | Slot 5 Character Name | Null-padded ASCII character name string (max 16 characters) |
| `0x08E4..0x08EC` | 8 B | Slot 5 Combat Stance & Tactical Configuration | Combat stance (+0x34..+0x39), tactical configuration bitmask at +0x3A (bit 2 0x04 = Link Combo mode toggle 'LC ON'/'LC OFF' modified by KM menu overlay code-3004 0x80081B30..0x80081C3C, bit 0 0x01 = tactical behavior flag), and delimiter byte at +0x3B (0x00) |
| `0x08EC..0x090C` | 32 B | Slot 5 Known / Unlocked Ability Flags | 32 x uint8 boolean flags (0x01=learned, 0x00=unlearned) for Killer Moves (fighters) and Spells (mages), indexed by 1-based ability ID |
| `0x090C..0x090D` | 1 B | Slot 5 Skill Table Delimiter | Single null byte (0x00) delimiting ability flag array and specialty skill levels |
| `0x090D..0x093B` | 46 B | Slot 5 Specialty Skill Levels | 46 uint8 skill levels (0..10) corresponding to all standard IC/combat skills (Mineralogy, Cooking, Knife, etc.) |
| `0x093B..0x093C` | 1 B | Slot 5 Proficiency Table Alignment Pad | Single null byte (0x00) aligning the following uint16 proficiency array to 2-byte boundary |
| `0x093C..0x097C` | 64 B | Slot 5 Ability Proficiencies & Spell Counters | 32 x uint16 little-endian usage counters (0..999) indexed by 1-based ability ID; Killer Move proficiency for fighters, spell cast count for mages |
| `0x097C..0x0980` | 4 B | Slot 5 Equipped Killer Move Shortcuts | 4 x uint8 assigned ability IDs: Short-range L1 (+0xCC), Short-range R1 (+0xCD), Long-range L1 (+0xCE), Long-range R1 (+0xCF); all 0x00 for mages |
| `0x0980..0x098C` | 12 B | Slot 6 Extended Stats (LUC & STM) | LUC triplet (+0..+5) and STM triplet (+6..+B) |
| `0x098C..0x099A` | 14 B | Slot 6 Equipment (7 Slots) | 7 x uint16 item IDs: weapon, armor, shield, helmet, greaves, acc1, acc2 (0x0000 = empty slot) |
| `0x099A..0x099C` | 2 B | Slot 6 SP Capped Value | Current available SP to spend (clamped 0..999) |
| `0x099C..0x09A0` | 4 B | Slot 6 SP-to-Talent Alignment Padding | 4-byte structural zero padding aligning uint16 SP (+0x1A) to uint32 Talent Bitmask (+0x20); zeroed at init (0x8007A240) and verified 100% [0,0,0,0] across all saves |
| `0x09A0..0x09A4` | 4 B | Slot 6 Talent Bitmask | Low 10 bits indicate unlocked talents (Originality, Dexterity, etc.) |
| `0x09A4..0x09B4` | 16 B | Slot 6 Character Name | Null-padded ASCII character name string (max 16 characters) |
| `0x09B4..0x09BC` | 8 B | Slot 6 Combat Stance & Tactical Configuration | Combat stance (+0x34..+0x39), tactical configuration bitmask at +0x3A (bit 2 0x04 = Link Combo mode toggle 'LC ON'/'LC OFF' modified by KM menu overlay code-3004 0x80081B30..0x80081C3C, bit 0 0x01 = tactical behavior flag), and delimiter byte at +0x3B (0x00) |
| `0x09BC..0x09DC` | 32 B | Slot 6 Known / Unlocked Ability Flags | 32 x uint8 boolean flags (0x01=learned, 0x00=unlearned) for Killer Moves (fighters) and Spells (mages), indexed by 1-based ability ID |
| `0x09DC..0x09DD` | 1 B | Slot 6 Skill Table Delimiter | Single null byte (0x00) delimiting ability flag array and specialty skill levels |
| `0x09DD..0x0A0B` | 46 B | Slot 6 Specialty Skill Levels | 46 uint8 skill levels (0..10) corresponding to all standard IC/combat skills (Mineralogy, Cooking, Knife, etc.) |
| `0x0A0B..0x0A0C` | 1 B | Slot 6 Proficiency Table Alignment Pad | Single null byte (0x00) aligning the following uint16 proficiency array to 2-byte boundary |
| `0x0A0C..0x0A4C` | 64 B | Slot 6 Ability Proficiencies & Spell Counters | 32 x uint16 little-endian usage counters (0..999) indexed by 1-based ability ID; Killer Move proficiency for fighters, spell cast count for mages |
| `0x0A4C..0x0A50` | 4 B | Slot 6 Equipped Killer Move Shortcuts | 4 x uint8 assigned ability IDs: Short-range L1 (+0xCC), Short-range R1 (+0xCD), Long-range L1 (+0xCE), Long-range R1 (+0xCF); all 0x00 for mages |
| `0x0A50..0x0A5C` | 12 B | Slot 7 Extended Stats (LUC & STM) | LUC triplet (+0..+5) and STM triplet (+6..+B) |
| `0x0A5C..0x0A6A` | 14 B | Slot 7 Equipment (7 Slots) | 7 x uint16 item IDs: weapon, armor, shield, helmet, greaves, acc1, acc2 (0x0000 = empty slot) |
| `0x0A6A..0x0A6C` | 2 B | Slot 7 SP Capped Value | Current available SP to spend (clamped 0..999) |
| `0x0A6C..0x0A70` | 4 B | Slot 7 SP-to-Talent Alignment Padding | 4-byte structural zero padding aligning uint16 SP (+0x1A) to uint32 Talent Bitmask (+0x20); zeroed at init (0x8007A240) and verified 100% [0,0,0,0] across all saves |
| `0x0A70..0x0A74` | 4 B | Slot 7 Talent Bitmask | Low 10 bits indicate unlocked talents (Originality, Dexterity, etc.) |
| `0x0A74..0x0A84` | 16 B | Slot 7 Character Name | Null-padded ASCII character name string (max 16 characters) |
| `0x0A84..0x0A8C` | 8 B | Slot 7 Combat Stance & Tactical Configuration | Combat stance (+0x34..+0x39), tactical configuration bitmask at +0x3A (bit 2 0x04 = Link Combo mode toggle 'LC ON'/'LC OFF' modified by KM menu overlay code-3004 0x80081B30..0x80081C3C, bit 0 0x01 = tactical behavior flag), and delimiter byte at +0x3B (0x00) |
| `0x0A8C..0x0AAC` | 32 B | Slot 7 Known / Unlocked Ability Flags | 32 x uint8 boolean flags (0x01=learned, 0x00=unlearned) for Killer Moves (fighters) and Spells (mages), indexed by 1-based ability ID |
| `0x0AAC..0x0AAD` | 1 B | Slot 7 Skill Table Delimiter | Single null byte (0x00) delimiting ability flag array and specialty skill levels |
| `0x0AAD..0x0ADB` | 46 B | Slot 7 Specialty Skill Levels | 46 uint8 skill levels (0..10) corresponding to all standard IC/combat skills (Mineralogy, Cooking, Knife, etc.) |
| `0x0ADB..0x0ADC` | 1 B | Slot 7 Proficiency Table Alignment Pad | Single null byte (0x00) aligning the following uint16 proficiency array to 2-byte boundary |
| `0x0ADC..0x0B1C` | 64 B | Slot 7 Ability Proficiencies & Spell Counters | 32 x uint16 little-endian usage counters (0..999) indexed by 1-based ability ID; Killer Move proficiency for fighters, spell cast count for mages |
| `0x0B1C..0x0B20` | 4 B | Slot 7 Equipped Killer Move Shortcuts | 4 x uint8 assigned ability IDs: Short-range L1 (+0xCC), Short-range R1 (+0xCD), Long-range L1 (+0xCE), Long-range R1 (+0xCF); all 0x00 for mages |

## Chunk 4: Inventory Roster & Integrity Buffer

Decoded offset `0x0B20..0x1748` (3,112 bytes). Live pointer: `[0x80075278]`.

| Offset | Size | Field | Description |
|---|---|---|---|
| `0x0B20..0x1320` | 2048 B | Inventory Roster Array | 1,024 x uint16 item slots: bits 0..9 item ID, bits 10..14 count (max 20), bit 15 seen/new flag |
| `0x1320..0x1340` | 32 B | Recent Acquired Item IDs | 16 x uint16 tracking recent item acquisitions |
| `0x1340..0x1344` | 4 B | Inventory Buffer Control Word | Memory buffer allocation descriptor |
| `0x1344..0x1744` | 1024 B | Inventory Hash / Integrity Bytes | Zeroed during save, recomputed on load via 0x8003C8A0 |
| `0x1744..0x1748` | 4 B | Inventory Trailing Alignment | Padding word to complete 0xC28 allocation |

## Chunk 5: World Entrance Coordinates, Name Table & Story Flags

Decoded offset `0x1748..0x1B88` (1,088 bytes). Live pointer: `Resource 0xE (F=[0x80075710] + G=[0x80075704])`.

| Offset | Size | Field | Description |
|---|---|---|---|
| `0x1748..0x1750` | 8 B | Warp / Scene Transition Header | Scene transition dispatch and return linkage parameters |
| `0x1750..0x175C` | 12 B | Saved Location Coordinates | Signed 32-bit world/dungeon entrance coordinates: X (+0), Y (+4), Z (+8) |
| `0x175C..0x1760` | 4 B | Camera Elevation | Sub-area camera angle and elevation offset |
| `0x1760..0x1762` | 2 B | Party Facing Angle | Orientation angle (uint16) |
| `0x1762..0x1764` | 2 B | Psynard Mount Active Bank | Selects active parked mount coordinate bank (0 or 1) |
| `0x1764..0x1766` | 2 B | Resource / Sequence Selector | Field sequence and transition resource selector (signed int16, -1 sentinel) |
| `0x1766..0x1768` | 2 B | Saved Scene-View Parameter | Signed halfword scene-view angle parameter (written at resident.asm 0x80054400, 0x80063A10; read at 0x80055830) |
| `0x1768..0x1769` | 1 B | Overworld Minimap View Mode | Overworld minimap / radar / full map display mode (uint8 0..2 cyclic toggle; overworld.asm 0x800889A4..0x800889CC) |
| `0x1769..0x176A` | 1 B | Sub-Area Index | Interior sub-area room index |
| `0x176A..0x176C` | 2 B | Zero Alignment Halfword | Zero-initialized alignment halfword (0x0000) preceding actor index (initialized at resident.asm 0x8005EC60) |
| `0x176C..0x176D` | 1 B | Landmark / Area ID | Current landmark index (0..193; e.g. Area 128 = Linga) |
| `0x176D..0x176E` | 1 B | Controlled-Object / Leader Active Flag | Leader object readiness flag (0 or 1; written at resident.asm 0x800540E8, 0x80054108; read at 0x800558BC) |
| `0x176E..0x176F` | 1 B | Scene Movement Lock Flag | Cutscene / movement lock flag (written at resident.asm 0x8006378C, cleared at 0x80055878, tested at 0x8004C9D0) |
| `0x176F..0x1770` | 1 B | Pending Scene Action Trigger Flag | Interactive field transition trigger flag (written at resident.asm 0x800525EC, cleared at 0x80054334) |
| `0x1770..0x1860` | 240 B | Character Name Table | 12 characters x 20 bytes each: saved character names and status display labels |
| `0x1860..0x1861` | 1 B | Message Speed | Text display speed (uint8 0..7, displayed 1..8 in options menu) |
| `0x1861..0x1880` | 31 B | Field Scene Viewport & Camera State Registers | Field camera parameters, viewpoint angle, and viewport scroll limits (initialized at resident.asm 0x80058FC0, 0x8005904C, 0x800590E4) |
| `0x1880..0x1881` | 1 B | Area / Room Transition Target ID | Target room/landmark entrance index (uint8; written at resident.asm 0x80059078, verified across saves 0x83..0xF6) |
| `0x1881..0x1894` | 19 B | Field Environment State Registers | Field scene environment parameters and transition state scratch registers (resident.asm 0x80058FC0) |
| `0x1894..0x189E` | 10 B | Cutscene Progress & Event Dispatch Markers | 5 x uint16 scene cutscene progress IDs (written at resident.asm 0x80058FFC, 0x80059000, verified across saves) |
| `0x189E..0x18C8` | 42 B | Event Dispatch Scratch & Transition Registers | Field event dispatch countdown scratch registers and transition parameters preceding clock snapshots (resident.asm 0x80058FC0) |
| `0x18C8..0x1988` | 192 B | Game Clock Snapshots | 48 x uint32 clock snapshot timestamps recording in-game milestones |
| `0x1988..0x198C` | 4 B | Operational Milestone Parameter | uint32 milestone parameter preceding completion counter (verified in real saves; resident.asm 0x80048C14) |
| `0x198C..0x1990` | 4 B | Completion Counter | uint32 completion counter incremented when chunk-1 halfword +178 equals 1 (read/written at resident.asm 0x80048C30..0x80048C3C; script getter 0x8006776C) |
| `0x1990..0x1992` | 2 B | Script-Additive Counter | uint16 script-additive counter (read at resident.asm 0x800676A0, 0x800676C4) |
| `0x1992..0x1994` | 2 B | Script RNG Test Attempt Counter | uint16 attempt counter for script RNG tests (read/written at resident.asm 0x80066604, 0x80066614; script getter 0x800676E0) |
| `0x1994..0x1996` | 2 B | Script RNG Test Success Counter | uint16 success counter for script RNG tests (read at resident.asm 0x80066630; script getter 0x800676FC) |
| `0x1996..0x1998` | 2 B | Delivery Array Alignment Halfword | Alignment halfword preceding 10-element pending delivery array (initialized at resident.asm 0x8005ED2C) |
| `0x1998..0x19AC` | 20 B | Pending Item Deliveries | 10 x uint16 slots tracking delayed item deliveries (e.g. publication royalties, forging) |
| `0x19AC..0x19AE` | 2 B | Menu Return Request Code | Signed halfword menu request code (read at resident.asm 0x8003055C, 0x80050D0C; set at 0x80032180) |
| `0x19AE..0x19B0` | 2 B | Menu Return Modifiers | Two signed 8-bit menu modifiers (read at resident.asm 0x8004D47C, 0x8004D480) |
| `0x19B0..0x19B4` | 4 B | Object-14 Saved X Coordinate | Signed 32-bit X coordinate for persistent object 14 (written at resident.asm 0x80068320; read at 0x800557AC) |
| `0x19B4..0x19C8` | 20 B | Psynard Parked Coordinates | Two saved XYZ banks: Bank 1 at 0x19B4/0x19D4/0x19B8, Bank 2 at 0x19BC/0x19D8/0x19C0 |
| `0x19C8..0x19D0` | 8 B | Saved Active Party Character IDs | 8 x uint8 character IDs in current active party roster |
| `0x19D0..0x19D1` | 1 B | Menu Delivery Variant Selector | Delivery variant mode byte (read at resident.asm 0x8004CC24, 0x8004E2B8, 0x80050280) |
| `0x19D1..0x19D2` | 1 B | Delivery Variant Alignment Pad | Structural alignment pad byte (verified 100% all-zeroes across saves) |
| `0x19D2..0x19D4` | 2 B | Object-14 Saved Orientation | Signed halfword orientation parameter for object 14 (read at resident.asm 0x800557D0; written at 0x80068344) |
| `0x19D4..0x19DC` | 8 B | Psynard Parked Y Coordinates | Signed 32-bit Y coordinates for Psynard parking bank 1 (0x19D4) and bank 2 (0x19D8) (written at resident.asm 0x8004C774, 0x8004C7A4; read at 0x80054454, 0x80055684) |
| `0x19DC..0x19E0` | 4 B | Deferred Delivery Clock Marker | uint32 clock marker gating deferred delivery processing (written at resident.asm 0x80030580, 0x80050C20; read at 0x80030570, 0x8004CBE4) |
| `0x19E0..0x19E8` | 8 B | Object-14 Saved Y and Z Coordinates | Signed 32-bit Y (0x19E0) and Z (0x19E4) coordinates for object 14 (written at resident.asm 0x8006832C, 0x80068338; read at 0x800557B8, 0x800557C4) |
| `0x19E8..0x1B58` | 368 B | Global Story / Event Flag Bitfield | 368 bytes (2,944 flags) from live buffer G=[0x80075704]; read/set/clear via 0x80055ECC/0x80055EFC/0x80055F38. 346 individual flag bits now definitively resolved: 338 real treasure chests at flags 2400..2730 (0x1B14..0x1B3D, 42 bytes), Cross Cave altar cutscene flag 449 at 0x1A20, Precious/Key item flags 0x02B4..0x02E3 at 0x1A3E..0x1A44, and developer debug flags 0x02C8..0x02D7 at 0x1A41..0x1A42. |
| `0x1B58..0x1B88` | 48 B | Resource-E Trailing Buffer Padding | 48-byte trailing buffer padding beyond 0x410 active bytes of F and G; allocated via malloc(0x440) at resident.asm 0x800325F0; snapshot 0x80055FC8 and restore 0x8005EAA0 bounded strictly to 0x410; contains zero pad or heap residue |
