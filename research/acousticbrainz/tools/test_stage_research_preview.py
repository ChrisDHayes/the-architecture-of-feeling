#!/usr/bin/env python3
"""Offline safeguards for the automatic permanent research-preview copy."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from stage_research_preview import prepare

def seed(folder, total=25, retrieved=23):
    qa = folder / "qa"
    qa.mkdir()
    entries = [{
        "track_id": "song_%02d" % n,
        "raw_lowlevel_sha256": ("a" * 64 if n < retrieved else None),
        "master_identity_verified": False,
        "approved_for_similarity": False,
    } for n in range(total)]
    summary = {
        "song_count": total, "lowlevel_raw_readable": retrieved,
        "full_ten_feature_parity": retrieved,
        "approved_for_similarity": 0, "essentia_versions": ["2.1-beta1", "2.1-beta2"],
        "lossless_observations": 16, "lossy_observations": 7,
        "source_run": "2026-11-08T05:00:00Z",
    }
    (qa / "evidence_qa_summary.json").write_text(json.dumps(summary))
    (qa / "evidence_receipts.json").write_text(json.dumps({"records": entries, "summary": summary}))
    (qa / "measured_descriptor_observations.csv").write_text("track_id,feature,source_value\nsong_00,bpm,120\n")
    (qa / "Measured_Evidence_Lab.html").write_text(
        "<!doctype html><title>Measured Evidence Lab</title><script>const status='EXPLORATORY_UNAPPROVED';</script>" + "." * 1200)
    return qa

class TestStage(unittest.TestCase):
    def test_stages_only_safe_preview(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); src = seed(root); dest = root / "docs" / "research" / "acousticbrainz"
            m = prepare(src, dest)
            self.assertEqual(m["records_retrieved"], 23)
            self.assertEqual(m["status"], "EXPLORATORY_UNAPPROVED")
            self.assertEqual(sorted(x.name for x in dest.iterdir()),
                ["Measured_Evidence_Lab.html", "preview_manifest.json"])
    def test_refuses_incomplete_registration_and_keeps_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); src = seed(root, total=6, retrieved=5)
            dest = root / "docs";dest.mkdir()
            (dest/"Measured_Evidence_Lab.html").write_text("old snapshot")
            with self.assertRaisesRegex(ValueError,"25-song"):
                prepare(src,dest,min_retrieved=1)
            self.assertEqual((dest/"Measured_Evidence_Lab.html").read_text(),"old snapshot")
    def test_refuses_insufficient_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); src = seed(root, retrieved=10)
            with self.assertRaisesRegex(ValueError,"minimum-coverage"):
                prepare(src,root/"docs")
            self.assertFalse((root/"docs").exists())
    def test_refuses_unreviewed_parity_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d);src = seed(root)
            p=src/"evidence_qa_summary.json";obj=json.loads(p.read_text())
            obj["full_ten_feature_parity"]=22;p.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"QA parity"):
                prepare(src,root/"docs")
    def test_refuses_approved_record(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=seed(root)
            p=src/"evidence_receipts.json";obj=json.loads(p.read_text())
            obj["records"][0]["master_identity_verified"]=True;p.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"Unexpected master"):
                prepare(src,root/"docs")
    def test_refuses_unlabelled_html(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=seed(root)
            (src/"Measured_Evidence_Lab.html").write_text("<script></script>"+"."*1200)
            with self.assertRaisesRegex(ValueError,"label missing"):
                prepare(src,root/"docs")
    def test_no_public_copy_of_source_json(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=seed(root)
            (src/"raw_source.json").write_text('{"license":"unknown"}')
            dest=root/"docs";prepare(src,dest)
            self.assertFalse((dest/"raw_source.json").exists())

if __name__ == "__main__":
    unittest.main(verbosity=2)
