#!/usr/bin/env python3
"""Fail-closed V3.1 source-data and publishing invariants (offline)."""
import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/previews/v3-measured-beta/index.html"
NEW = ROOT / "docs/previews/v3-1-measured-dna/index.html"
LOCKED = ROOT / "docs/archive/v2-9/index.html"
SHA_V29 = "3ba59e0030951051bcc4842fb2471b08a306dcb1aa838cdf1a9d06a8166eac21"
SHA_V30_BLOB = "dbb79ca5ed1727c79fa39d0a9ec205149250b389"

def payload(html):
    m = re.search(r'window\.AOF_V3_EVIDENCE\s*=\s*(\{.*?\});\s*const DATA\s*=', html, re.S)
    if not m:
        raise AssertionError("Original acoustic source payload missing")
    return json.loads(m.group(1)), m.group(1)

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

class V31MeasuredDNA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = BASE.read_text(encoding="utf8")
        cls.html = NEW.read_text(encoding="utf8")
        cls.evidence, cls.raw = payload(cls.html)

    def test_original_editions_unchanged(self):
        self.assertEqual(hashlib.sha256(LOCKED.read_bytes()).hexdigest(), SHA_V29)
        self.assertEqual(git_blob(BASE.read_bytes()), SHA_V30_BLOB)

    def test_original_148_measurement_values_unchanged(self):
        _, source = payload(self.old)
        self.assertEqual(source, self.raw)
        self.assertEqual(len(self.evidence["records"]), 167)
        self.assertEqual(sum(bool(x["selected_mbid"]) for x in self.evidence["records"]), 148)
        self.assertEqual(self.evidence["summary"]["approved_master"], 0)

    def test_unapproved_quality_classes_not_hidden_from_data(self):
        counts = Counter(x["category"] for x in self.evidence["records"])
        self.assertEqual(counts, {"matched":103,"lossy":44,"identity_flagged":1,"missing":7,"ineligible":12})
        self.assertEqual(sum(x["feature_parity"] for x in self.evidence["records"]),148)

    def test_actual_measured_engine_not_the_old_synthetic_one(self):
        for name in ["const numericDistance=","function cluster(items)","function drawTree(","function drawScatter()","function drawSignature()","function drawAlbums()","median absolute deviation","AVERAGE"]:
            if name in ("median absolute deviation","AVERAGE"):
                continue
            self.assertIn(name, self.html)
        self.assertIn("source.length!==147", self.html)
        self.assertIn("cohortLossless.length!==103", self.html)
        self.assertIn("clamp((r.values[k]-allStats[k].median)", self.html)
        self.assertIn("Source tags aligned", self.html)
        self.assertIn("family weights", self.html.lower())

    def test_not_claiming_emotions_or_waveforms_are_measured(self):
        self.assertIn("Not mood.", self.html)
        self.assertIn("not a time-domain waveform", self.html)
        self.assertIn("provisional recording identities", self.html.lower())
        self.assertIn("Missing values have not been imputed", self.html)

    def test_personal_home_ending_and_video_preserved(self):
        self.assertIn('id="home-finale"', self.html)
        self.assertIn('href="https://www.youtube.com/watch?v=DZHs-SRJbzU"', self.html)

if __name__ == "__main__":
    unittest.main(verbosity=2)
