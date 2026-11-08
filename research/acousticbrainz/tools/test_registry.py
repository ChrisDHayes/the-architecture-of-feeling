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
assert len([r for r in rows if int(r["year"]) > 2022]) == 0
spec = importlib.util.spec_from_file_location("audit25", ROOT / "tools/audit25.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
pilots = {r["title"] for r in rows if r["is_pilot"].strip().lower() == "true"}
assert len(pilots) == 6
assert pilots == {"Everything Counts", "Never Let Me Down Again", "Enjoy the Silence",
                  "In Your Room", "It's No Good", "World in My Eyes"}
assert "Wagging Tongue" not in pilots
assert not any(r["title"] == "Wagging Tongue" for r in rows)
barrel = next(r for r in rows if r["title"] == "Barrel of a Gun")
assert barrel["track_id"] == "a09_t01" and barrel["album"] == "Ultra" and barrel["year"] == "1997"
assert not any(r["title"] == "Barrel of a Gun" and r["is_pilot"] == "True" for r in rows)
focus_names = {"Barrel of a Gun", "Mercy in You", "Higher Love"}
assert all(len([r for r in rows if r["title"] == name]) == 1 for name in focus_names)
with (ROOT / "data/focus_tracks.csv").open(encoding="utf-8", newline="") as fh:
    focus_rows = list(csv.DictReader(fh))
assert len(focus_rows) == 3
assert {r["track_id"] for r in focus_rows} == {"a09_t01", "a08_t04", "a08_t10"}
assert {r["title"] for r in focus_rows} == focus_names
assert all(int(r["year"]) <= 2022 for r in rows if r["title"] in pilots)
world = next(r for r in rows if r["title"] == "World in My Eyes")
assert world["legacy_candidate_mbid"] == "26f7bb0d-133d-4811-a8bf-0ff930c5a11a"
assert world["candidate_identity_status"].endswith("submission_unverified")
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


# Bounded candidate resolver must preserve quality ordering; no source is
# certified as the intended master purely because its tags match.
sys.path.insert(0, str(ROOT / "tools"))
from resolve_candidates import quality_score
q_good = {"flags": [], "lossless": True, "bit_rate": 0}
q_320 = {"flags": [], "lossless": False, "bit_rate": 320000}
q_128 = {"flags": ["lossy_low_bitrate"], "lossless": False, "bit_rate": 128000}
q_bad_album = {"flags": ["source_album_mismatch"], "lossless": True}
q_missing = {"flags": ["insufficient_source_tags"], "lossless": False}
assert quality_score(q_good) == 115
assert quality_score(q_320) == 100
assert quality_score(q_128) == 60
assert quality_score(q_bad_album) < 0
assert quality_score(q_missing) < 0
assert quality_score(q_good) > quality_score(q_320) > quality_score(q_128)
assert quality_score(None) < quality_score(q_bad_album)
print("PASS: bounded candidate survey prioritizes evidence and flags wrong editions")
