#!/usr/bin/env python3
"""Fail-closed V3.2: preserve original acoustic sources and explicit listener ID joins."""
import csv,hashlib,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
V30=ROOT/"docs/previews/v3-measured-beta/index.html"
V31=ROOT/"docs/previews/v3-1-measured-dna/index.html"
V32=ROOT/"docs/previews/v3-2-listener-reach/index.html"
CSV=ROOT/"research/popularity/data/v32_listener_reach_147_provenance.csv"
V31_GIT_BLOB="b9524507b1c076108f6a17a6ea86d6b2b18f6192"
def git_blob(x):return hashlib.sha1(b"blob "+str(len(x)).encode()+b"\\0"+x).hexdigest()
def payload(html,name,end):
 a=html.index(name)+len(name);b=html.index(end,a);return json.loads(html[a:b].strip().removesuffix(";").strip())
def evidence(html):
 m=re.search(r'window\\.AOF_V3_EVIDENCE\\s*=\\s*(\\{.*?\\});\\s*const DATA\\s*=',html,re.S)
 if m is None:raise ValueError("Embedded acoustic evidence missing")
 return m.group(1)
class Integration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.html=V32.read_text(encoding="utf8")
  cls.aud=payload(cls.html,"const REACH32 = ","\\nconst ALBUM_PROXY32 = ")
  cls.proxy=payload(cls.html,"const ALBUM_PROXY32 = ","\\nconst cohortAll=")
  with CSV.open(encoding="utf8",newline="") as f:cls.rows=list(csv.DictReader(f))
 def test_acoustic_data_unchanged(self):
  self.assertEqual(git_blob(V31.read_bytes()),V31_GIT_BLOB)
  self.assertEqual(evidence(V30.read_text(encoding="utf8")),evidence(self.html))
  self.assertIn('id="home-finale"',self.html)
  self.assertIn('https://www.youtube.com/watch?v=DZHs-SRJbzU',self.html)
 def test_source_counts_still_missing_at_selected_mbid(self):
  self.assertEqual(len(self.aud["rows"]),147)
  self.assertEqual(self.aud["reported"],144)
  missing=[r for r in self.aud["rows"] if r[2] is None]
  self.assertEqual(len(missing),3)
  self.assertTrue(all(r[3] is None for r in missing))
 def test_proxies_are_measured_elsewhere_not_imputed(self):
  self.assertEqual(len(self.proxy["proxy_rows"]),3)
  target={r[0]:r for r in self.aud["rows"]}
  expected={"Home":(47782,406949),"Personal Jesus":(133918,1232780),"The Bottom Line":(25049,146706)}
  for r in self.proxy["proxy_rows"]:
   self.assertEqual((r["unique_listeners"],r["total_listens"]),expected[r["title"]])
   self.assertEqual(target[r["track_id"]][1],r["acoustic_recording_mbid"])
   self.assertNotEqual(r["acoustic_recording_mbid"],r["listening_recording_mbid"])
   self.assertIsNone(target[r["track_id"]][2])
 def test_crosswalk_and_source_disclosure(self):
  self.assertEqual(len(self.rows),147)
  self.assertEqual(len({r["track_id"] for r in self.rows}),147)
  self.assertEqual(sum(r["display_status"]=="ALTERNATE_ALBUM_VERSION_PROXY" for r in self.rows),3)
  self.assertEqual(sum(r["display_status"]=="OBSERVED_SAME_RECORDING" for r in self.rows),144)
  for r in self.rows:
   if r["display_status"]=="ALTERNATE_ALBUM_VERSION_PROXY":
    self.assertEqual(r["source_recording_unique_listeners"],"")
    self.assertNotEqual(r["display_recording_mbid"],r["acoustic_recording_mbid"])
   else:self.assertEqual(r["display_recording_mbid"],r["acoustic_recording_mbid"])
  self.assertIn("function renderReachRing(leaves,container)",self.html)
  self.assertIn("not estimated counts for the original IDs",self.html)
  self.assertIn('data-proxy="${proxy?1:0}"',self.html)
if __name__=="__main__":unittest.main(verbosity=2)
