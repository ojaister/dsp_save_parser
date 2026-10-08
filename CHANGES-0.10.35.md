# Changes in this fork (game build 0.10.35.29104)

This fork of Joker1718/dsp_save_parser adds support for saves that have actually been played on build 0.10.35.29104. The original spec parsed a fresh save but failed on a played one.

## What was fixed (dsp_save_parser/dsp_save_parser/save_format.txt)

- Player block: the original read a fixed 96-byte block (`playerV7Extra[96]`). In 0.10.35 it is four groups, each an int32 count followed by that many int32/int32 pairs. Counts vary per save (a fresh save had 0, 4, 1, 5), so a fixed size broke parsing at the first real save (failure showed up at GalacticTransport).
- PowerGeneratorComponent: record version bumped from 7 to 8. `fuelMask` widened from int16 to int32, plus 1 byte and 8 bytes added. The 9 extra bytes are INFERRED from measured record size (138 bytes) and were zeros in observed records, so their meaning is unknown.

## What was added

- scripts/dsp_progress.py: read-only summary of a save as JSON (game version, hours played, unlocked recipes and techs, research in progress and queue, built and planned buildings per planet). IDs are numeric; names are not looked up.
- A sanity check: the script prints nothing unless parsing ends exactly at the last byte of the file, so a layout mismatch is reported instead of silently giving wrong numbers.

Usage (from the repository root): python scripts/dsp_progress.py path/to/save.dsv > progress.json

## Caveats

- Verified on one mid-game save (about 10.8 hours, 4 planets with buildings). Later-game saves (Dyson spheres, Dark Fog, many building types) are untested and may hit other layout changes.
- Only saves from the matching build parse. Older saves (for example 0.10.30) fail by design.
- The patch fields marked inferred are not decoded; do not rely on them.
- The scripts that modify saves (such as unlock_mech_tech.py) were not touched or used; dsp_progress.py never writes to the save.
- Upstream states no license; this fork keeps upstream content unchanged apart from the above.
