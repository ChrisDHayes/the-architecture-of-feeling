#!/usr/bin/env python3
"""Research-only, fail-closed MusicBrainz / AcousticBrainz availability audit.
No audio, no imputation, no automatic publication of song fingerprints.
"""
import argparse
import csv
import datetime as dt
import json
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
MBID = re.compile(r"^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")
# The six-song pilot is defined solely by the CSV is_pilot column.
# These are direct source descriptors. They are NOT normalized V2.9 features.
# Names with proxy/candidate deliberately do not assert exact semantic equivalence.
FEATURES = {
    "rhythm.tempo": "rhythm.bpm",
    "rhythm.onset_density": "rhythm.onset_rate",
    "rhythm.beat_histogram_peak_spread": "rhythm.bpm_histogram_first_peak_spread.mean",
    "timbre.spectral_centroid": "lowlevel.spectral_centroid.mean",
    "timbre.spectral_flux": "lowlevel.spectral_flux.mean",
    "timbre.barkbands_flatness_db": "lowlevel.barkbands_flatness_db.mean",
    "harmony.hpcp_entropy": "tonal.hpcp_entropy.mean",
    "harmony.tonal_change_candidate_proxy": "tonal.chords_changes_rate",
    "dynamics.loudness": "lowlevel.average_loudness",
    "dynamics.dynamic_complexity": "lowlevel.dynamic_complexity",
}
UNRESOLVED = ["rhythm.pulse_regularity", "timbre.mfcc_dispersion", "harmony.chroma_entropy",
              "harmony.pitch_class_contrast", "dynamics.crest_factor", "dynamics.structural_novelty"]

def normal(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())

def get(url, timeout=10):
    request = urllib.request.Request(url, headers={
        "User-Agent": "ArchitectureOfFeelingResearch/1.0 (GitHub research; https://github.com/ChrisDHayes/the-architecture-of-feeling)",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response), "ok"
    except urllib.error.HTTPError as exc:
        return None, "http_" + str(exc.code)
    except Exception as exc:
        return None, "network_error_" + type(exc).__name__

def artist_name(recording):
    parts = recording.get("artist-credit", [])
    return "".join(x.get("name", "") + x.get("joinphrase", "") for x in parts if isinstance(x, dict))

def find_candidates(row, timeout):
    query = f'recording:"{row["title"]}" AND artistname:"Depeche Mode"'
    url = "https://musicbrainz.org/ws/2/recording/?" + urllib.parse.urlencode({
        "query": query, "fmt": "json", "limit": "100"
    })
    data, status = get(url, timeout)
    if not data:
        return [], status
    matches = []
    for recording in data.get("recordings", []):
        title = recording.get("title", "")
        is_title = (normal(title) == normal(row["title"])
                    or normal(title).startswith(normal(row["title"]) + "interlude"))
        is_artist = normal(artist_name(recording)) == "depechemode"
        if not (is_title and is_artist):
            continue
        is_album = any(normal(r.get("title", "")) == normal(row["album"])
                       for r in recording.get("releases", []))
        matches.append({
            "mbid": recording.get("id"), "title": title,
            "length_ms": recording.get("length"), "exact_album_in_search": is_album,
            "release_titles": [r.get("title") for r in recording.get("releases", [])[:8]],
            "search_score": recording.get("score"),
            "source": "https://musicbrainz.org/recording/" + recording.get("id", "")
        })
    return matches, status

def value_at(doc, path):
    node = doc
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if type(node) in (float, int) else None

def first_tag(tags, key):
    value = tags.get(key)
    return str(value[0]) if isinstance(value, list) and value else (str(value) if value else "")

def inspect_submission(doc, requested_title, requested_album, recording_id):
    """Assess tags from the *submitted audio*, not the many MusicBrainz releases."""
    meta = doc.get("metadata", {}) if isinstance(doc, dict) else {}
    tags = meta.get("tags", {})
    audio = meta.get("audio_properties", {})
    source_title = first_tag(tags, "title")
    source_album = first_tag(tags, "album")
    source_file = first_tag(tags, "file_name")
    source_mbid = first_tag(tags, "musicbrainz_recordingid")
    codec = audio.get("codec", "")
    bit_rate = audio.get("bit_rate")
    lossless = audio.get("lossless")
    flags = []
    if not source_title or not source_album:
        flags.append("insufficient_source_tags")
    if source_album and normal(source_album) != normal(requested_album):
        flags.append("source_album_mismatch")
    if source_title and normal(source_title) != normal(requested_title):
        flags.append("source_title_or_version_mismatch")
    if source_mbid and source_mbid != recording_id:
        flags.append("source_mbid_mismatch")
    # A matching album and song title can still be a reissue or remaster.
    # A file-name version suffix deserves human inspection.
    if re.search(r"(?i)(?:\bremix\b|\blive\b|\bdemo\b|\bacoustic\b|\bedit\b|\bextended\b|\bversion\b)", source_file):
        flags.append("file_name_version_qualifier")
    if lossless is False and isinstance(bit_rate, int) and bit_rate < 192000:
        flags.append("lossy_low_bitrate")
    if flags:
        verdict = ("source_mismatch_needs_replacement"
                   if any(f in flags for f in ("source_album_mismatch", "source_title_or_version_mismatch", "source_mbid_mismatch"))
                   else "album_track_candidate_needs_quality_review")
    else:
        verdict = "album_track_candidate_not_master_verified"
    return {
        "verdict": verdict, "flags": flags, "source_title": source_title,
        "source_album": source_album, "source_file_name": source_file,
        "source_recording_mbid": source_mbid, "source_length_seconds": audio.get("length"),
        "codec": codec, "lossless": lossless, "bit_rate": bit_rate,
        "essentia_version": meta.get("version", {}).get("essentia")
    }

def run(scope, timeout, output):
    output = pathlib.Path(output)
    output.mkdir(parents=True, exist_ok=True)
    raw = output / "raw"
    raw.mkdir(exist_ok=True)
    with (ROOT / "data" / "target_25_recordings.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 25 and len({r["track_id"] for r in rows}) == 25
    if scope == "pilot_6":
        rows = [r for r in rows if r["is_pilot"].strip().lower() == "true"]
        assert len(rows) == 6 and len({r["track_id"] for r in rows}) == 6, "Pilot registry must specify six unique songs"
    results, candidates_all = [], []
    last_mb_request = 0.0
    for row in rows:
        eligible = int(row["year"]) <= 2022
        entry = {
            "track_id": row["track_id"], "title": row["title"], "album": row["album"],
            "year": int(row["year"]), "archive_eligible_by_release_year": eligible,
            "legacy_candidate_mbid": row["legacy_candidate_mbid"],
            "selected_mbid": None, "selected_identity_status": "unresolved",
            "musicbrainz_status": "not_checked", "candidate_count": None,
            "lowlevel_status": "not_checked", "highlevel_status": "not_checked",
            "measurement_values": {}, "method_gaps": UNRESOLVED,
        }
        if not eligible:
            entry["lowlevel_status"] = entry["highlevel_status"] = "not_in_2022_submission_window"
            results.append(entry)
            continue
        wait = 1.2 - (time.monotonic() - last_mb_request)
        if wait > 0:
            time.sleep(wait)
        last_mb_request = time.monotonic()
        candidates, mb_status = find_candidates(row, timeout)
        entry["musicbrainz_status"] = mb_status
        entry["candidate_count"] = len(candidates) if mb_status == "ok" else None
        candidates_all.append({"track_id": row["track_id"], "title": row["title"],
                               "musicbrainz_status": mb_status, "candidates": candidates})
        # Restrict checks to a single exact-album search match or a previously
        # identified MBID that appears among exact-album search matches.
        exact = [c for c in candidates if c["exact_album_in_search"] and MBID.fullmatch(c["mbid"] or "")]
        legacy = next((c for c in exact if c["mbid"] == row["legacy_candidate_mbid"]), None)
        chosen = legacy if legacy else exact[0] if len(exact) == 1 else None
        if not chosen:
            entry["selected_identity_status"] = "needs_review_or_musicbrainz_unavailable"
            results.append(entry)
            continue
        mbid = chosen["mbid"]
        entry["selected_mbid"] = mbid
        entry["selected_identity_status"] = "album_linked_candidate_requires_master_review"
        for label, suffix in [("lowlevel", "low-level"), ("highlevel", "high-level")]:
            doc, status = get(f"https://acousticbrainz.org/api/v1/{mbid}/{suffix}", timeout)
            entry[label + "_status"] = "retrieved" if doc is not None else status
            if doc is None:
                continue
            path = raw / f'{row["track_id"]}_{mbid}_{label}.json'
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
            entry[label + "_file"] = str(path.relative_to(output))
            if label == "lowlevel":
                entry["submission_quality"] = inspect_submission(doc, row["title"], row["album"], mbid)
                entry["measurement_values"] = {
                    name: {"source_path": feat, "source_value": value_at(doc, feat)}
                    for name, feat in FEATURES.items()
                }
        results.append(entry)
    # Summarize the same fetched records for the six curated pilot tracks.
    # The pilot is a subset of the all-25 audit, not a second API run.
    with (ROOT / "data" / "target_25_recordings.csv").open(newline="", encoding="utf-8") as f:
        registry = list(csv.DictReader(f))
    pilot_ids = {r["track_id"] for r in registry if r["is_pilot"].strip().lower() == "true"}
    assert len(pilot_ids) == 6, "Exactly six pilot songs required"
    pilot_rows = [r for r in results if r["track_id"] in pilot_ids]
    pilot_summary = {
        "songs_in_pilot": 6,
        "songs_in_current_result": len(pilot_rows),
        "lowlevel_retrieved": sum(r["lowlevel_status"] == "retrieved" for r in pilot_rows),
        "highlevel_retrieved": sum(r["highlevel_status"] == "retrieved" for r in pilot_rows),
        "unresolved_recording_identity": sum(
            r.get("selected_mbid") is None for r in pilot_rows),
        "source_mismatches": sum(
            r.get("submission_quality", {}).get("verdict") == "source_mismatch_needs_replacement"
            for r in pilot_rows),
        "quality_flagged": sum(bool(r.get("submission_quality", {}).get("flags")) for r in pilot_rows),
    }
    report = {
        "schema": "architecture-of-feeling.acousticbrainz-25-coverage.v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "mode": "online_api", "scope": scope, "audio_processed": False,
        "normalized_v29_data_ready": False,
        "warning": "Candidate album matches are not confirmed masters; API errors mean unknown, not missing data.",
        "summary": {
            "songs_checked": len(results),
            "lowlevel_retrieved": sum(r["lowlevel_status"] == "retrieved" for r in results),
            "highlevel_retrieved": sum(r["highlevel_status"] == "retrieved" for r in results),
            "outside_archive_window": sum(not r["archive_eligible_by_release_year"] for r in results),
            "needs_recording_review": sum(r["selected_mbid"] is None for r in results if r["archive_eligible_by_release_year"]),
            "retrieved_with_source_mismatch": sum(
                r.get("submission_quality", {}).get("verdict") == "source_mismatch_needs_replacement"
                for r in results),
            "retrieved_with_quality_flags": sum(bool(r.get("submission_quality", {}).get("flags")) for r in results),
        }, "pilot_summary": pilot_summary, "records": results
    }
    (output / "coverage_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "musicbrainz_candidates.json").write_text(json.dumps(candidates_all, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "pilot_summary.json").write_text(json.dumps({
        "schema": "architecture-of-feeling.acousticbrainz-pilot-summary.v1",
        "summary": pilot_summary,
        "records": pilot_rows,
        "notice": "Pilot is a subset of the same API run. No extra fetches performed."
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    fields = ["track_id", "title", "album", "year", "selected_mbid",
              "selected_identity_status", "musicbrainz_status", "candidate_count",
              "lowlevel_status", "highlevel_status", "source_album", "source_title",
              "source_quality_verdict", "source_quality_flags"]
    with (output / "coverage_report.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            row = {k: r.get(k, "") for k in fields}
            quality = r.get("submission_quality", {})
            row.update({
                "source_album": quality.get("source_album", ""),
                "source_title": quality.get("source_title", ""),
                "source_quality_verdict": quality.get("verdict", ""),
                "source_quality_flags": ";".join(quality.get("flags", [])),
            })
            writer.writerow(row)
    print("All songs:", json.dumps(report["summary"], indent=2))
    print("Six-song pilot subset:", json.dumps(report["pilot_summary"], indent=2))
    return report

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--scope", choices=["pilot_6", "all_25"], default="pilot_6")
    p.add_argument("--timeout", type=int, default=10)
    p.add_argument("--output", default="results/github_run")
    a = p.parse_args()
    run(a.scope, a.timeout, a.output)
