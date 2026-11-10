#!/usr/bin/env python3
"""V3.2: source-MBID missingness and alternative album-version join stay distinct."""
import csv,hashlib,json,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
V30=ROOT/"docs/previews/v3-measured-beta/index.html"
V31=ROOT/"docs/previews/v3-1-measured-dna/index.html"
V32=ROOT/"docs/previews/v3-2-listener-reach/index.html"
CSV=ROOT/"research/popularity/data/v32_listener_reach_147_provenance.csv"
V31_GIT_BLOB="b9524507b1c076108f6a17a6ea86d6b2b18f6192"

def git_blob(data):
 return hashlib.sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()

def decoded_block(html,header):
 tail=html.split(header,1)[1].lstrip()
 return json.JSONDecoder().raw_decode(tail)[0]

class Integration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.html=V32.read_text(encoding="utf8")
  cls.aud=decoded_block(cls.html,"const REACH32 = ")
  cls.proxy=decoded_block(cls.html,"const ALBUM_PROXY32 = ")
  with CSV.open(encoding="utf8",newline="") as fh:
   cls.rows=list(csv.DictReader(fh))
 def test_acoustic_data_unchanged(self):
  self.assertEqual(git_blob(V31.read_bytes()),V31_GIT_BLOB)
  old=decoded_block(V30.read_text(encoding="utf8"),"window.AOF_V3_EVIDENCE = ")
  new=decoded_block(self.html,"window.AOF_V3_EVIDENCE = ")
  self.assertEqual(old,new)
  self.assertIn('id="home-finale"',self.html)
  self.assertIn('https://www.youtube.com/watch?v=DZHs-SRJbzU',self.html)
 def test_selected_mbid_counts_remain_missing(self):
  self.assertEqual(len(self.aud["rows"]),147)
  self.assertEqual(self.aud["reported"],144)
  missing=[r for r in self.aud["rows"] if r[2] is None]
  self.assertEqual(len(missing),3)
  self.assertTrue(all(r[3] is None for r in missing))
 def test_alternate_album_mbid_proxies_use_observed_counts(self):
  self.assertEqual(len(self.proxy["proxy_rows"]),3)
  selected={r[0]:r for r in self.aud["rows"]}
  expected={"Home":(47782,406949),"Personal Jesus":(133918,1232780),"The Bottom Line":(25049,146706)}
  for r in self.proxy["proxy_rows"]:
   self.assertEqual((r["unique_listeners"],r["total_listens"]),expected[r["title"]])
   self.assertEqual(selected[r["track_id"]][1],r["acoustic_recording_mbid"])
   self.assertNotEqual(r["acoustic_recording_mbid"],r["listening_recording_mbid"])
   self.assertIsNone(selected[r["track_id"]][2])
 def test_opening_has_no_notice_boxes_even_before_javascript(self):
  opening=self.html.split('<section id="opening">',1)[1]
  self.assertTrue(opening.lstrip().startswith('<svg class="hero-deco"'))
  hero=opening.split('</section>',1)[0]
  self.assertNotIn('<div class="v3-banner">',hero)
  self.assertNotIn('<div class="warn">',hero)
  self.assertNotIn('V3.1 · measured sonic evidence:',self.html)
  self.assertNotIn('What is measured, and what remains personal?',self.html)
  self.assertIn('THE<br>ARCHITECTURE<br>OF',hero)
  self.assertIn('class="hero-meta"',hero)
 def test_album_median_reference_is_source_based_and_common_scale(self):
  from statistics import median
  evidence=decoded_block(self.html,"window.AOF_V3_EVIDENCE = ")
  records=[r for r in evidence["records"] if r["category"] in ("matched","lossy") and r["feature_parity"]]
  by_album={}
  for r in records:
   by_album.setdefault(r["album"],[]).append(r["values"]["rhythm.onset_density"])
  medians=[median(values) for values in by_album.values()]
  self.assertEqual(len(medians),14)
  self.assertAlmostEqual(median(medians),3.5363948941225,places=7)
  self.assertEqual(max(medians).__ceil__(),5)
  self.assertIn('id="v31AlbumReference"',self.html)
  self.assertIn('class="v31-album-median-tick"',self.html)
  self.assertIn('const reference=median(albumMedians);',self.html)
  self.assertIn('const scaleMax=Math.ceil(Math.max(...albumMedians));',self.html)
  self.assertIn('g.med.toFixed(2)',self.html)
  self.assertIn('No archival measurement available',self.html)
 def test_crosswalk_and_visual_disclosure(self):
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
  self.assertIn('data-proxy=',self.html)
if __name__=="__main__":
 unittest.main(verbosity=2)
