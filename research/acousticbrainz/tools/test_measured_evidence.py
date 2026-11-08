#!/usr/bin/env python3
"""Offline regression tests for measured evidence QA."""
import json
import tempfile
import unittest
from pathlib import Path
from validate_measured_evidence import FEATURES, audit, path_get, write_outputs

def fixture(root, *, altered=None):
    altered=altered or {}
    low={'metadata':{'tags':{'title':['Test Track'],'album':['Test Album'],'artist':['Depeche Mode'],'musicbrainz_recordingid':['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa']},
      'audio_properties':{'codec':'flac','lossless':True,'bit_rate':0,'length':200,'md5_encoded':'x'},
      'version':{'essentia':'2.1-beta1','extractor':'music 1.0'}},'rhythm':{},'lowlevel':{},'tonal':{}}
    measurements={}
    for i,(label,(path,unit)) in enumerate(FEATURES.items()):
        parts=path.split('.');cursor=low
        for part in parts[:-1]:cursor=cursor.setdefault(part,{})
        cursor[parts[-1]]=float(i+1)
        measurements[label]={'source_path':path,'source_value':float(i+1)}
    if altered.get('tag_mbid'):low['metadata']['tags']['musicbrainz_recordingid']=['different']
    if altered.get('codec'):low['metadata']['audio_properties'].update({'codec':'mp3','lossless':False,'bit_rate':128000})
    if altered.get('alter_feature'):measurements['rhythm.tempo']['source_value']=999.0
    raw=root/'raw';raw.mkdir()
    (raw/'one.json').write_text(json.dumps(low),encoding='utf-8')
    (raw/'two.json').write_text(json.dumps({'metadata':low['metadata'],'highlevel':{}}),encoding='utf-8')
    report={'generated_at_utc':'fixture','pilot_track_ids':['test1'],'records':[{'track_id':'test1','title':'Test Track','album':'Test Album','selected_mbid':'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','lowlevel_file':'raw/one.json','highlevel_file':'raw/two.json','measurement_values':measurements}]}
    if altered.get('missing_raw'):(raw/'one.json').unlink()
    (root/'coverage_report.json').write_text(json.dumps(report),encoding='utf-8')
    return root

class ValidationTests(unittest.TestCase):
    def test_source_path_nested(self):
        self.assertEqual(path_get({'x':{'y':2}},'x.y'),2)
    def test_valid_fixture_is_still_unapproved(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(fixture(Path(d)))
            self.assertEqual(r['summary']['full_ten_feature_parity'],1)
            self.assertEqual(r['summary']['approved_for_similarity'],0)
            self.assertTrue(r['receipts'][0]['provisional_research_observation'])
            self.assertFalse(r['receipts'][0]['master_identity_verified'])
    def test_recording_mismatch_flags(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(fixture(Path(d),altered={'tag_mbid':True}))
            self.assertIn('recording_id_mismatch_or_missing_tag',r['receipts'][0]['qa_flags'])
            self.assertFalse(r['receipts'][0]['provisional_research_observation'])
    def test_lossy_source_does_not_imply_master_clearance(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(fixture(Path(d),altered={'codec':True}))
            self.assertIn('low_bitrate_source',r['receipts'][0]['qa_flags'])
            self.assertIn('lossy_source',r['receipts'][0]['qa_flags'])
            self.assertEqual(r['summary']['approved_for_similarity'],0)
    def test_feature_parity_mismatch_blocks_provisional(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(fixture(Path(d),altered={'alter_feature':True}))
            self.assertIn('feature_parity:rhythm.tempo',r['receipts'][0]['qa_flags'])
            self.assertEqual(r['receipts'][0]['feature_count_parity_passed'],9)
            self.assertFalse(r['receipts'][0]['provisional_research_observation'])
    def test_missing_json_is_not_zero_observation(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(fixture(Path(d),altered={'missing_raw':True}))
            self.assertEqual(r['summary']['lowlevel_raw_readable'],0)
            self.assertEqual(r['summary']['full_ten_feature_parity'],0)
            self.assertIn('lowlevel_missing_or_invalid_json',r['receipts'][0]['qa_flags'])
    def test_no_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(Path(d));j=json.loads((p/'coverage_report.json').read_text())
            j['records'][0]['lowlevel_file']='../elsewhere.json'
            (p/'coverage_report.json').write_text(json.dumps(j))
            self.assertIn('lowlevel_unsafe_path',audit(p)['receipts'][0]['qa_flags'])
    def test_duplicate_id_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(Path(d));j=json.loads((p/'coverage_report.json').read_text())
            j['records'].append(j['records'][0]);(p/'coverage_report.json').write_text(json.dumps(j))
            with self.assertRaisesRegex(ValueError,'Duplicate track ID'):audit(p)
    def test_output_files(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(Path(d));out=p/'qa';write_outputs(audit(p),out)
            self.assertEqual(len(list(out.iterdir())),4)
            self.assertIn('UNAPPROVED',(out/'measured_descriptor_observations.csv').read_text())

if __name__=='__main__':unittest.main(verbosity=2)
