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

# Regression: MusicBrainz album links do not establish uploaded source identity.
def fake(title, album, file_name, lossless=True, bit_rate=1000000):
    return {"metadata": {"tags": {"title": [title], "album": [album],
                                  "file_name": [file_name],
                                  "musicbrainz_recordingid": ["1234"]},
                         "audio_properties": {"lossless": lossless,
                                              "bit_rate": bit_rate,
                                              "codec": "flac" if lossless else "mp3",
                                              "length": 260}}}
mismatch = mod.inspect_submission(fake("Enjoy the Silence (7\"\" version)", "Singles 19-24",
                                            "01 - Enjoy the Silence (7in version).m4a"),
                                  "Enjoy the Silence", "Violator", "1234")
assert mismatch["verdict"] == "source_mismatch_needs_replacement"
assert "source_album_mismatch" in mismatch["flags"]
good = mod.inspect_submission(fake("Everything Counts", "Construction Time Again",
                                 "04 Everything Counts.flac"),
                              "Everything Counts", "Construction Time Again", "1234")
assert good["verdict"] == "album_track_candidate_not_master_verified"
lossy = mod.inspect_submission(fake("It's No Good", "Ultra", "It's No Good.mp3",
                                  lossless=False, bit_rate=128000),
                               "It's No Good", "Ultra", "1234")
assert "lossy_low_bitrate" in lossy["flags"]
assert mod.FEATURES["harmony.hpcp_entropy"] == "tonal.hpcp_entropy.mean"
print("PASS: source album mismatch, recording quality flag and descriptor paths")
