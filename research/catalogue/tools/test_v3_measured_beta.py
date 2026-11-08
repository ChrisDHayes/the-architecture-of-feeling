#!/usr/bin/env python3
"""Offline integrity gates: V2.9 immutable; V3.0 measurable source status unchanged."""
import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ORIGINAL=ROOT/"docs/archive/v2-9/index.html"
PREVIEW=ROOT/"docs/previews/v3-measured-beta/index.html"
SHA_V29="3ba59e0030951051bcc4842fb2471b08a306dcb1aa838cdf1a9d06a8166eac21"

class EvidenceGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=PREVIEW.read_text(encoding="utf-8")
        found=re.search(r'window\.AOF_V3_EVIDENCE\s*=\s*(\{.*?\});\s*const DATA\s*=',cls.html,re.S)
        if not found:raise ValueError("Expected V3 source payload unavailable")
        cls.data=json.loads(found.group(1))

    def test_locked_original_unchanged(self):
        self.assertEqual(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),SHA_V29)

    def test_167_catalogue_and_148_sources(self):
        rows=self.data["records"]
        self.assertEqual(len(rows),167)
        self.assertEqual(len({r["track_id"] for r in rows}),167)
        self.assertEqual(sum(bool(r["selected_mbid"]) for r in rows),148)
        self.assertEqual(Counter(r["category"] for r in rows),
            {"matched":103,"lossy":44,"identity_flagged":1,"missing":7,"ineligible":12})

    def test_measured_fields_not_imputed(self):
        features=self.data["features"]
        self.assertEqual(len(features),10)
        self.assertTrue(all(f["unit"] and f["source_path"] for f in features))
        for r in self.data["records"]:
            if r["selected_mbid"]:
                self.assertTrue(r["feature_parity"])
                self.assertEqual(len(r["values"]),10)
                self.assertTrue(r["raw_source_sha256"])
            else:
                self.assertFalse(r["values"])

    def test_no_master_approval(self):
        self.assertEqual(self.data["status"],"EXPLORATORY_UNAPPROVED")
        self.assertEqual(self.data["summary"]["approved_master"],0)
        self.assertIn("Source version mismatch",self.html)

    def test_synthetic_boundaries_and_navigation(self):
        self.assertIn("synthetic_demonstration",self.html)
        self.assertIn("STILL SYNTHETIC",self.html)
        self.assertIn("V3.0 MIXED EVIDENCE · BETA",self.html)
        self.assertIn('id="v3-measured"',self.html)
        self.assertIn('href="#v3-measured"',self.html)

if __name__=="__main__":
    unittest.main(verbosity=2)
