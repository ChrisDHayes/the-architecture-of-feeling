#!/usr/bin/env python3
"""Fail-closed, offline checks for the source-linked Home editorial finale."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HTML=ROOT/"docs/previews/v3-measured-beta/index.html"
LOCKED=ROOT/"docs/archive/v2-9/index.html"
ORIGINAL_V29_SHA="3ba59e0030951051bcc4842fb2471b08a306dcb1aa838cdf1a9d06a8166eac21"
SOURCE_MBIT="42f01cf7-2fdc-4f22-bf08-58e791ffdb22"

class TestHomeFinale(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=HTML.read_text(encoding="utf-8")
        match=re.search(r'window\.AOF_V3_EVIDENCE\s*=\s*(\{.*?\});\s*const DATA\s*=',cls.html,re.S)
        if not match:
            raise ValueError("Measured V3 evidence not found")
        cls.evidence=json.loads(match.group(1))

    def test_preserved_v29(self):
        self.assertEqual(hashlib.sha256(LOCKED.read_bytes()).hexdigest(),ORIGINAL_V29_SHA)

    def test_home_is_final_section_not_but_not_tonight(self):
        h=self.html
        self.assertIn('id="home-finale"',h)
        self.assertIn('href="#home-finale"',h)
        self.assertNotIn('id="but-not-tonight"',h)
        self.assertIn('<h2 id="home-heading">Home.</h2>',h)
        self.assertEqual(h.count('<section class="home-finale"'),1)

    def test_6_distinct_personal_interactions(self):
        h=self.html
        self.assertEqual(len(re.findall(r'<g class="home-node" data-memory="\d"',h)),6)
        self.assertEqual(len(re.findall(r'<button class="home-chip" data-memory="\d"',h)),6)
        self.assertIn('GATHER THE THREADS',h)
        self.assertIn('prefers-reduced-motion',h)
        self.assertIn('addEventListener(\'keydown\'',h)

    def test_not_passing_memories_off_as_measurements(self):
        h=self.html
        self.assertIn("PERSONAL INTERPRETATION · NOT AUDIO DATA",h)
        self.assertIn("no verified studio master",h)
        self.assertIn("Source recording",h)

    def test_real_home_candidate_not_mock_measurements(self):
        rows=self.evidence["records"]
        home=[r for r in rows if r.get("title")=="Home" and r.get("album")=="Ultra"]
        self.assertEqual(len(home),1)
        row=home[0]
        self.assertEqual(row["selected_mbid"],SOURCE_MBIT)
        self.assertEqual(row["codec"],"mp3")
        self.assertEqual(row["bit_rate"],320000)
        self.assertFalse(row["lossless"])
        self.assertTrue(row["feature_parity"])
        self.assertAlmostEqual(row["values"]["rhythm.tempo"],151.128799438,5)
        self.assertAlmostEqual(row["values"]["timbre.spectral_centroid"],1016.85058594,5)
        self.assertAlmostEqual(row["values"]["rhythm.onset_density"],4.22934579849,5)

    def test_original_catalogue_untouched(self):
        e=self.evidence
        self.assertEqual(e["summary"]["source_observations"],148)
        self.assertEqual(e["summary"]["catalogue_entries"],167)
        self.assertEqual(e["summary"]["approved_master"],0)
        self.assertEqual(e["status"],"EXPLORATORY_UNAPPROVED")

    def test_official_video_outbound_only(self):
        h=self.html
        self.assertIn('href="https://www.youtube.com/watch?v=DZHs-SRJbzU"',h)
        self.assertIn('target="_blank" rel="noopener noreferrer"',h)
        self.assertNotIn("<audio src=",h)
        self.assertNotIn("<video src=",h)

if __name__=="__main__":
    unittest.main(verbosity=2)
