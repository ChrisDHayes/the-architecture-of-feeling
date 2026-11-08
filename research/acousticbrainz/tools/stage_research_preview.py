#!/usr/bin/env python3
"""Stage a permanent research-only HTML preview from a validated Actions audit.

Only the labelled, self-contained HTML and a small provenance manifest are copied.
Raw source JSON, commercial audio, lyrics, and master claims never enter docs/.
A failed or partial acquisition cannot overwrite the previous published snapshot.
"""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(qa_dir, destination, min_retrieved=20):
    qa_dir = Path(qa_dir)
    destination = Path(destination)
    summary_path = qa_dir / "evidence_qa_summary.json"
    receipts_path = qa_dir / "evidence_receipts.json"
    observations_path = qa_dir / "measured_descriptor_observations.csv"
    html_path = qa_dir / "Measured_Evidence_Lab.html"
    required = [summary_path, receipts_path, observations_path, html_path]
    for file in required:
        if not file.is_file() or file.stat().st_size == 0:
            raise ValueError("Missing or empty required QA artifact: " + file.name)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    receipt_data = json.loads(receipts_path.read_text(encoding="utf-8"))
    records = receipt_data.get("records", [])
    html = html_path.read_text(encoding="utf-8")
    expected_count = 25
    if summary.get("song_count") != expected_count or len(records) != expected_count:
        raise ValueError("Only a complete 25-song registry may refresh the persistent preview")
    if len({r.get("track_id") for r in records}) != expected_count:
        raise ValueError("Missing or duplicate song identities")
    if summary.get("approved_for_similarity") != 0:
        raise ValueError("This preview accepts only unapproved research observations")
    if any(r.get("approved_for_similarity") or r.get("master_identity_verified") for r in records):
        raise ValueError("Unexpected master or similarity approval; requires a separate publication workflow")
    actual = sum(bool(r.get("raw_lowlevel_sha256")) for r in records)
    retrieved = summary.get("lowlevel_raw_readable")
    parity = summary.get("full_ten_feature_parity")
    if (not isinstance(retrieved, int) or not isinstance(parity, int)
            or retrieved != actual or parity != actual or actual < min_retrieved):
        raise ValueError("QA parity or minimum-coverage gate failed; retain previous snapshot")
    if "EXPLORATORY_UNAPPROVED" not in html or "Measured Evidence Lab" not in html:
        raise ValueError("Unapproved research label missing from the standalone HTML")
    if "<script" not in html.lower() or len(html) < 1000:
        raise ValueError("HTML preview appears incomplete")

    # Validate and prepare everything BEFORE writing any destination file.
    manifest = {
        "schema": "architecture-of-feeling.research-preview.v1",
        "status": "EXPLORATORY_UNAPPROVED",
        "approval": "NOT_APPROVED_FOR_SONIC_SIMILARITY_OR_PUBLICATION",
        "source": "AcousticBrainz historical precomputed submitted-file descriptors",
        "git_source_commit": os.environ.get("GITHUB_SHA", "local-development"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID", "local-development"),
        "source_run_utc": summary.get("source_run"),
        "songs_registered": expected_count,
        "records_retrieved": retrieved,
        "records_feature_parity_checked": parity,
        "lossless_recordings_tagged": summary.get("lossless_observations"),
        "lossy_recordings_tagged": summary.get("lossy_observations"),
        "essentia_versions": summary.get("essentia_versions"),
        "html_sha256": sha256(html_path),
        "evidence_qa_summary_sha256": sha256(summary_path),
        "evidence_receipts_sha256": sha256(receipts_path),
        "source_observations_sha256": sha256(observations_path),
        "notes": [
            "All 25 songs are represented; missing sources remain explicitly missing.",
            "Neither recording/master identity nor cross-extractor comparability has been independently approved.",
            "Values remain original-source descriptors; no measured sonic-family clustering claims.",
            "No raw AcousticBrainz JSON, recordings, lyrics, or images are copied by this step.",
            "V2.9 interactive creative edition is not modified."
        ]
    }
    destination.mkdir(parents=True, exist_ok=True)
    staged_html = destination / "Measured_Evidence_Lab.html"
    staged_manifest = destination / "preview_manifest.json"
    shutil.copyfile(html_path, staged_html)
    staged_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-dir", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--min-retrieved", type=int, default=20)
    args = parser.parse_args()
    if args.min_retrieved < 1 or args.min_retrieved > 25:
        parser.error("--min-retrieved must be within 1–25")
    print(json.dumps(prepare(args.qa_dir, args.destination, args.min_retrieved), indent=2))

if __name__ == "__main__":
    main()
