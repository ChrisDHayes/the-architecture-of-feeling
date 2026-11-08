#!/usr/bin/env python3
"""Offline regression tests of the descriptive-only evidence explorer."""
import csv, json, tempfile, unittest
from pathlib import Path
from build_evidence_explorer import build, LABELS

def fixture(root, *, approved=False, parity=True, escape=False):
    data=root/'evidence_qa'; data.mkdir()
    receipt={'track_id':'a01','song':'Sample <track>' if escape else 'Sample track',
       'album':'Album','pilot':True,'selected_mbid':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
       'source_title':'Sample track','source_album':'Album','source_duration_seconds':200,
       'codec':'flac','lossless':True,'bit_rate':0,'essentia_version':'2.1-beta1',
       'raw_lowlevel_sha256':'abc123','qa_flags':[],'approved_for_similarity':approved,'master_identity_verified':False}
    receipts={'summary':{'approved_for_similarity':1 if approved else 0,'lowlevel_raw_readable':1,'lossless_observations':1,'essentia_versions':['2.1-beta1']},'records':[receipt]}
    (data/'evidence_receipts.json').write_text(json.dumps(receipts))
    with (data/'measured_descriptor_observations.csv').open('w',newline='') as f:
        cols=['track_id','feature','source_path','unit','source_value','source_report_parity','review_state']
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for idx,key in enumerate(LABELS):writer.writerow({'track_id':'a01','feature':key,'source_path':key,'unit':'source units','source_value':idx+1,'source_report_parity':parity,'review_state':'UNAPPROVED'})
    template=root/'template.html';template.write_text('<html><script>const D=/*AUDIT_PAYLOAD*/;</script></html>')
    return data,template

class ExplorerTests(unittest.TestCase):
    def test_generated_single_file_contains_real_unapproved_descriptors(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);qa,t=fixture(p);out=p/'lab.html'
            x=build(qa,t,out)
            self.assertEqual((x['measured'],x['feature_count']),(1,10))
            self.assertIn('EXPLORATORY_UNAPPROVED',out.read_text())
            self.assertTrue((p/'source_descriptor_strata.csv').exists())
    def test_unsafe_html_source_tag_escaped_in_json(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);qa,t=fixture(p,escape=True);out=p/'lab.html';build(qa,t,out)
            self.assertNotIn('Sample <track>',out.read_text())
            self.assertIn('Sample \\u003ctrack\\u003e',out.read_text())
    def test_approved_input_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);qa,t=fixture(p,approved=True)
            with self.assertRaises(ValueError):build(qa,t,p/'lab.html')
    def test_source_parity_error_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);qa,t=fixture(p,parity=False)
            with self.assertRaisesRegex(ValueError,'parity'):build(qa,t,p/'lab.html')
    def test_duplicate_receipts_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);qa,t=fixture(p)
            f=qa/'evidence_receipts.json';obj=json.loads(f.read_text());obj['records'].append(obj['records'][0]);f.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,'duplicated'):build(qa,t,p/'lab.html')

if __name__=='__main__':unittest.main(verbosity=2)
