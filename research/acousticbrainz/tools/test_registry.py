#!/usr/bin/env python3
"""Offline smoke tests. Fail rather than imply any recording was verified."""
import csv
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "data/target_25_recordings.csv").open(encoding="utf-8")))
assert len(rows) == 25, len(rows)
assert len({r["track_id"] for r in rows}) == 25
assert len([r for r in rows if int(r["year"]) > 2022]) == 1
spec = importlib.util.spec_from_file_location("audit25", ROOT / "tools/audit25.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
assert len(mod.PILOT) == 6
assert mod.normal("Depeche Mode") == "depechemode"
assert mod.value_at({"rhythm":{"bpm":123}}, "rhythm.bpm") == 123
assert mod.value_at({"rhythm":{}}, "rhythm.bpm") is None
assert mod.value_at({"rhythm":{"bpm":"unknown"}}, "rhythm.bpm") is None
assert len(mod.UNRESOLVED) == 6
print("PASS: 25 identifiers, six pilot tracks, 2022 cutoff, no fabricated descriptors")
