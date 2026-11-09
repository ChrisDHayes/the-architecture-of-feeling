#!/usr/bin/env python3
"""Offline identity, missingness, and rights-gate regression checks."""
import csv,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_listenbrainz as a
REGISTRY=Path(__file__).resolve().parents[1]/"data/sonic_dna_147_crosswalk.csv"
class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows=a.load(REGISTRY)
    def test_147_unique_rec_id(self):
        self.assertEqual(len(self.rows),147)
        self.assertEqual(len({r["recording_mbid"] for r in self.rows}),147)
    def test_scope_103_lossless_44_lossy(self):
        self.assertEqual(sum(r["source_category"]=="matched" for r in self.rows),103)
        self.assertEqual(sum(r["source_category"]=="lossy" for r in self.rows),44)
    def test_no_verified_live_matches_or_public_counts(self):
        self.assertEqual(sum(r["live_identity_review"]=="TITLE_CANDIDATE_UNVERIFIED" for r in self.rows),143)
        self.assertEqual(sum(r["live_identity_review"]=="ALIAS_PROPOSAL_NEEDS_REVIEW" for r in self.rows),2)
        self.assertEqual(sum(r["live_identity_review"]=="VERSION_OR_MEDLEY_NEEDS_REVIEW" for r in self.rows),2)
        self.assertTrue(all(r["live_performance_count_status"]=="NOT_QUERIED_RIGHTS_GATE" for r in self.rows))
    def test_null_remains_not_reported(self):
        m=self.rows[0]["recording_mbid"]
        got=a.reconcile([m],[{"recording_mbid":m,"total_listen_count":None,"total_user_count":None}])
        self.assertIsNone(got[m]["unique_listeners"])
        self.assertEqual(got[m]["listenbrainz_status"],"NOT_REPORTED")
    def test_reject_partial_and_invalid(self):
        m=self.rows[0]["recording_mbid"];n=self.rows[1]["recording_mbid"]
        with self.assertRaises(ValueError):a.reconcile([m,n],[{"recording_mbid":m}])
        for l,u in [(0,1),(-1,0),(3,None),("3",2)]:
            with self.assertRaises(ValueError):a.reconcile([m],[{"recording_mbid":m,"total_listen_count":l,"total_user_count":u}])
    def test_reject_duplicate_response_id(self):
        m=self.rows[0]["recording_mbid"];n=self.rows[1]["recording_mbid"]
        with self.assertRaises(ValueError):a.reconcile([m,n],[{"recording_mbid":m},{"recording_mbid":m}])
    def test_fake_147_source_audit_no_network(self):
        def mock(ids):return [{"recording_mbid":m,"total_listen_count":42,"total_user_count":7} for m in ids]
        rows=a.run(self.rows,api=mock,pause=0)
        self.assertEqual(len(rows),147)
        with tempfile.TemporaryDirectory() as p:
            report=a.save(rows,p)
            self.assertEqual(report["reported"],147)
            self.assertFalse(report["promotion_to_public_site"])
    def test_no_public_setlist_data_in_crosswalk(self):
        with REGISTRY.open(encoding="utf8") as f:
            data=list(csv.DictReader(f))
        self.assertNotIn("live_performance_count",data[0])
        self.assertTrue(all(r["unique_listeners_status"]=="NOT_QUERIED" for r in data))
if __name__=="__main__":unittest.main(verbosity=2)
