#!/usr/bin/env python3
"""Bounded second-stage candidate survey for the same AcousticBrainz Actions run.

Reads the first-stage report and its MusicBrainz candidate list. Searches no
more than a small capped set of *album-linked* candidates for ambiguous songs,
checks submitted audio tags and retains their provenance. Never treats a
MusicBrainz release association as proof that an AcousticBrainz upload used
that release. No audio, no 0..1 normalization, no automatic exhibit activation.
"""
import argparse
import csv
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from audit25 import FEATURES, MBID, find_candidates, get, inspect_submission, normal, value_at

ROOT = pathlib.Path(__file__).resolve().parents[1]


def quality_score(q):
    """Rank provisional candidates; none are master-certified."""
    if not q:
        return -1000
    flags = set(q.get("flags") or [])
    if flags & {"source_album_mismatch", "source_title_or_version_mismatch",
                "source_mbid_mismatch"}:
        return -200
    if "insufficient_source_tags" in flags or "file_name_version_qualifier" in flags:
        return -80
    score = 100
    if q.get("lossless") is True:
        score += 15
    if "lossy_low_bitrate" in flags:
        score -= 40
    if q.get("lossless") is False and q.get("bit_rate") is None:
        score -= 10
    return score


def refresh_summaries(report, registry):
    rows = report["records"]
    pilots = {r["track_id"] for r in registry if r["is_pilot"].lower() == "true"}
    pr = [r for r in rows if r["track_id"] in pilots]
    assert len(pilots) == 6, "Six pilot flags required"
    report["summary"] = {
        "songs_checked": len(rows),
        "lowlevel_retrieved": sum(r["lowlevel_status"] == "retrieved" for r in rows),
        "highlevel_retrieved": sum(r["highlevel_status"] == "retrieved" for r in rows),
        "outside_archive_window": sum(not r["archive_eligible_by_release_year"] for r in rows),
        "needs_recording_review": sum(
            r["selected_mbid"] is None for r in rows if r["archive_eligible_by_release_year"]),
        "retrieved_with_source_mismatch": sum(
            r.get("submission_quality", {}).get("verdict") == "source_mismatch_needs_replacement" for r in rows),
        "retrieved_with_quality_flags": sum(
            bool(r.get("submission_quality", {}).get("flags")) for r in rows),
    }
    report["pilot_summary"] = {
        "songs_in_pilot": len(pilots),
        "songs_in_current_result": len(pr),
        "lowlevel_retrieved": sum(r["lowlevel_status"] == "retrieved" for r in pr),
        "highlevel_retrieved": sum(r["highlevel_status"] == "retrieved" for r in pr),
        "unresolved_recording_identity": sum(r["selected_mbid"] is None for r in pr),
        "source_mismatches": sum(
            r.get("submission_quality", {}).get("verdict") == "source_mismatch_needs_replacement" for r in pr),
        "quality_flagged": sum(bool(r.get("submission_quality", {}).get("flags")) for r in pr),
    }


def save_report(report, output):
    (output / "coverage_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "pilot_summary.json").write_text(
        json.dumps({
            "schema": "architecture-of-feeling.acousticbrainz-pilot-summary.v1",
            "summary": report["pilot_summary"],
            "records": [r for r in report["records"] if r["track_id"] in report["pilot_track_ids"]],
            "notice": "Pilot subset of same audit; no additional full-catalogue run."
        }, indent=2, ensure_ascii=False), encoding="utf-8")
    # Focus songs are an editorial review subset of this same 25-song run.
    # No extra API calls or new analysis features are invented here.
    with (ROOT / "data/focus_tracks.csv").open(encoding="utf-8", newline="") as fh:
        focus_registry = list(csv.DictReader(fh))
    assert len(focus_registry) == 3 and len({x["track_id"] for x in focus_registry}) == 3
    by_id = {x["track_id"]: x for x in report["records"]}
    focus_evidence = []
    for target in focus_registry:
        row = by_id.get(target["track_id"])
        focus_evidence.append({
            "track_id": target["track_id"],
            "title": target["title"], "album": target["album"],
            "priority_group": target["priority_group"],
            "reason": target["reason"],
            "checked_in_scope": row is not None,
            "selected_mbid": row.get("selected_mbid") if row else None,
            "lowlevel_status": row.get("lowlevel_status") if row else "not_checked",
            "highlevel_status": row.get("highlevel_status") if row else "not_checked",
            "source_quality": row.get("submission_quality") if row else None,
            "measurement_values": row.get("measurement_values") if row else {},
            "identity_gate": "requires_independent_studio_master_review",
        })
    (output / "focus_tracks_review.json").write_text(json.dumps({
        "schema": "architecture-of-feeling.focus-acoustic-review.v1",
        "source": "Same retrieval as coverage_report.json. No extra audio or API calls.",
        "normalization_status": "not_started",
        "records": focus_evidence
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    columns = ["track_id", "title", "album", "year", "selected_mbid",
               "selected_identity_status", "musicbrainz_status", "candidate_count",
               "lowlevel_status", "highlevel_status", "source_album", "source_title",
               "source_quality_verdict", "source_quality_flags"]
    with (output / "coverage_report.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for r in report["records"]:
            d = {k: r.get(k, "") for k in columns}
            quality = r.get("submission_quality") or {}
            d.update(source_album=quality.get("source_album", ""),
                     source_title=quality.get("source_title", ""),
                     source_quality_verdict=quality.get("verdict", ""),
                     source_quality_flags=";".join(quality.get("flags", [])))
            w.writerow(d)


def resolve(output, timeout=10, max_candidates=4):
    output = pathlib.Path(output)
    raw = output / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    report = json.loads((output / "coverage_report.json").read_text(encoding="utf-8"))
    source_candidates = json.loads(
        (output / "musicbrainz_candidates.json").read_text(encoding="utf-8"))
    candidate_index = {x["track_id"]: x for x in source_candidates}
    with (ROOT / "data/target_25_recordings.csv").open(encoding="utf-8", newline="") as f:
        registry = list(csv.DictReader(f))
    assert len(registry) == 25
    by_track = {r["track_id"]: r for r in registry}
    report["pilot_track_ids"] = [
        r["track_id"] for r in registry if r["is_pilot"].strip().lower() == "true"]
    assert len(report["pilot_track_ids"]) == 6
    probes, candidates_examined, selected_or_improved, attempted = [], 0, 0, 0
    for r in report["records"]:
        if not r["archive_eligible_by_release_year"]:
            continue
        initial_score = quality_score(r.get("submission_quality")) if (
            r["lowlevel_status"] == "retrieved") else -1000
        # Do not needlessly probe records whose submitted source identity and
        # basic quality are already plausible.
        if initial_score >= 100:
            continue
        entry = candidate_index.get(r["track_id"], {
            "track_id": r["track_id"], "title": r["title"],
            "musicbrainz_status": r["musicbrainz_status"], "candidates": []})
        if entry["musicbrainz_status"] != "ok":
            for n in range(3):
                if n:
                    time.sleep(2 * n)
                fresh, status = find_candidates(by_track[r["track_id"]], timeout)
                entry["musicbrainz_status"] = status
                entry["candidates"] = fresh
                if status == "ok":
                    break
            candidate_index[r["track_id"]] = entry
            r["musicbrainz_status"] = entry["musicbrainz_status"]
            r["candidate_count"] = len(entry["candidates"]) if (
                entry["musicbrainz_status"] == "ok") else None
        all_album = [c for c in entry["candidates"]
                     if c.get("exact_album_in_search")
                     and MBID.fullmatch(c.get("mbid") or "")]
        # Prioritize flagged current MBID only for historical recordkeeping;
        # do not fetch an already-downloaded, known-bad source again.
        pool = sorted(all_album,
                      key=lambda c: (c["mbid"] != by_track[r["track_id"]].get(
                          "legacy_candidate_mbid"), -(c.get("search_score") or 0)))
        seen = set()
        for c in pool:
            if len(seen) >= max_candidates:
                break
            mbid = c["mbid"]
            if mbid in seen or mbid == r.get("selected_mbid"):
                continue
            seen.add(mbid)
            attempted += 1
            time.sleep(0.28)
            url = f"https://acousticbrainz.org/api/v1/{mbid}/low-level"
            doc, status = get(url, timeout)
            row = {"track_id": r["track_id"], "title": r["title"],
                   "mbid": mbid, "api_status": status,
                   "source_url": url, "quality_score": None}
            if doc is None:
                probes.append(row)
                continue
            candidates_examined += 1
            q = inspect_submission(doc, r["title"], r["album"], mbid)
            score = quality_score(q)
            row.update(submission_quality=q, quality_score=score)
            raw_path = raw / f'{r["track_id"]}_{mbid}_lowlevel.json'
            raw_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False),
                                encoding="utf-8")
            row["raw_file"] = str(raw_path.relative_to(output))
            probes.append(row)
            if score > initial_score and score >= 60:
                high, high_status = get(
                    f"https://acousticbrainz.org/api/v1/{mbid}/high-level", timeout)
                high_path = None
                if high is not None:
                    high_path = raw / f'{r["track_id"]}_{mbid}_highlevel.json'
                    high_path.write_text(
                        json.dumps(high, indent=2, ensure_ascii=False),
                        encoding="utf-8")
                r.update(selected_mbid=mbid, selected_identity_status=(
                    "album_tag_matched_candidate_requires_master_review"
                    if score >= 100 else "quality_flagged_candidate_requires_review"),
                    lowlevel_status="retrieved",
                    highlevel_status=("retrieved" if high is not None else high_status),
                    submission_quality=q,
                    lowlevel_file=str(raw_path.relative_to(output)),
                    measurement_values={
                        name: {"source_path": feature, "source_value": value_at(doc, feature)}
                        for name, feature in FEATURES.items()},
                    candidate_resolution="replaced_or_filled_from_candidate_survey")
                if high_path:
                    r["highlevel_file"] = str(high_path.relative_to(output))
                else:
                    r.pop("highlevel_file", None)
                initial_score = score
                selected_or_improved += 1
                # A source-tag-matched, lossless file is sufficient for *candidate*
                # selection; no need to fetch additional album-linked candidates.
                if score >= 115:
                    break
        if not r.get("selected_mbid"):
            r["selected_identity_status"] = "multiple_or_unavailable_candidate_sources"
    report["candidate_resolution_summary"] = {
        "candidate_lowlevel_requests": attempted,
        "candidate_lowlevel_documents_retrieved": candidates_examined,
        "records_added_or_improved": selected_or_improved,
        "candidate_limit_per_song": max_candidates,
        "all_selected_candidates_require_master_review": True,
    }
    refresh_summaries(report, registry)
    (output / "candidate_probes.json").write_text(
        json.dumps({"schema": "architecture-of-feeling.candidate-probes.v1",
                    "summary": report["candidate_resolution_summary"],
                    "probes": probes}, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "musicbrainz_candidates.json").write_text(
        json.dumps(list(candidate_index.values()), indent=2, ensure_ascii=False),
        encoding="utf-8")
    save_report(report, output)
    print("After bounded candidate survey:")
    print(json.dumps({"all_25": report["summary"], "pilot": report["pilot_summary"],
                      "survey": report["candidate_resolution_summary"]}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--max-candidates", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.max_candidates <= 5:
        parser.error("--max-candidates must be between 1 and 5")
    resolve(args.output, args.timeout, args.max_candidates)
