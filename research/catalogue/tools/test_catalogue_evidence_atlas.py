#!/usr/bin/env python3
"""Network-free regression tests for the 167-entry source-quality atlas.

All fabricated data here are TEST FIXTURES, never catalogue observations.
"""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from build_catalogue_evidence_atlas import build, safe_json, source_review, FEATURES

ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/'data/full_catalogue_167.csv'
TEMPLATE=ROOT/'templates/catalogue_evidence_atlas.html'


def fixtures(path, unsafe=False, approved=False):
    with REGISTRY.open(encoding='utf8',newline='') as f: songs=list(csv.DictReader(f))
    new=[x for x in songs if x['in_existing_25_registry']=='false']
    example=new[0];mbid='01234567-89ab-cdef-0123-456789abcdef'
    raw={'metadata':{'tags':{'title':[example['title']], 'album':[example['album']],
      'musicbrainz_recordingid':[mbid]},'audio_properties':{'codec':'flac','lossless':True,
      'length':200.5,'bit_rate':900000},'version':{'essentia':'2.1-beta1'}},
      'rhythm':{},'lowlevel':{},'tonal':{}}
    observed={}
    for n,(key,rawpath) in enumerate(FEATURES.items()):
        cursor=raw
        sections=rawpath.split('.')
        for sub in sections[:-1]:cursor=cursor.setdefault(sub,{})
        cursor[sections[-1]]=float(n+1)
        observed[key]={'source_path':rawpath,'source_value':float(n+1)}
    index=[];found={}
    for row in songs:
        old=row['in_existing_25_registry']=='true'
        status='EXISTING_25_RESEARCH_SEPARATE_PIPELINE' if old else ('post_2022_submission_window' if row['year']=='2023' else 'no_exact_album_candidate_in_search_not_proof_of_absence')
        index.append({'track_id':row['track_id'],'title':row['title'],'album':row['album'],
             'scope':row['scope'],'year':row['year'],'batch':row['batch'],
             'in_existing_25_registry':row['in_existing_25_registry'],'acoustic_coverage_status':status})
        if not old:
            entry={'track_id':row['track_id'],'title':row['title'],'album':row['album'],
              'batch':row['batch'],'status':status,'selected_mbid':None,
              'master_identity_verified':False,'approved_for_similarity':False}
            if row['track_id']==example['track_id']:
                dest=path/('catalogue-expansion-batch-'+row['batch'])
                (dest/'raw').mkdir(parents=True,exist_ok=True)
                fp=dest/'raw/selected.json'
                fp.write_text(json.dumps(raw))
                entry.update(selected_mbid=mbid,status='provisional_observation_requires_master_review',
                   observed_features=observed,lowlevel_file='raw/selected.json' if not unsafe else '../../outside.json',
                   lowlevel_sha256=hashlib.sha256(fp.read_bytes()).hexdigest(),
                   quality_flags=[],approved_for_similarity=approved)
            found[entry['track_id']]=entry
    for batch in ('01','02','03','04','05'):
        entries=[row for row in found.values() if row['batch']==batch]
        folder=path/('catalogue-expansion-batch-'+batch);folder.mkdir(exist_ok=True)
        (folder/'coverage_report.json').write_text(json.dumps({'schema':'architecture-of-feeling.catalogue-expansion.v1',
           'summary':{'batch':batch},'records':entries}))
    idx=path/'index.json';idx.write_text(json.dumps({'summary':{'approved_for_similarity':0},'records':index}))
    return idx,example

class AtlasTest(unittest.TestCase):
 def test_builds_full_registry_without_promoting_fixtures(self):
    with tempfile.TemporaryDirectory() as d:
       root=Path(d);index,example=fixtures(root)
       res=build(index,root,TEMPLATE,root/'results')
       self.assertEqual(res['population'],167)
       self.assertEqual(res['baseline_separate'],25)
       self.assertEqual(res['new_source_candidates'],1)
       self.assertEqual(res['historically_ineligible'],12)
       self.assertEqual(res['approved_for_similarity'],0)
       data=json.loads((root/'results/catalogue_evidence_atlas.json').read_text())
       selected=next(r for r in data['records'] if r['track_id']==example['track_id'])
       self.assertEqual(selected['source_quality']['feature_parity_count'],10)
       self.assertFalse(selected['master_identity_verified'])
       self.assertIn('UNAPPROVED_RESEARCH_CANDIDATES',(root/'results/Catalogue_Evidence_Atlas.html').read_text())
 def test_path_traversal_blocked(self):
    with tempfile.TemporaryDirectory() as d:
       root=Path(d);idx,_=fixtures(root,unsafe=True)
       with self.assertRaisesRegex(ValueError,'Unsafe raw JSON path'):
           build(idx,root,TEMPLATE,root/'results')
 def test_approved_claim_blocked(self):
    with tempfile.TemporaryDirectory() as d:
       root=Path(d);idx,_=fixtures(root,approved=True)
       with self.assertRaisesRegex(ValueError,'Unexpected master/similarity approval'):
           build(idx,root,TEMPLATE,root/'results')
 def test_source_sha_mismatch_blocked(self):
    with tempfile.TemporaryDirectory() as d:
       root=Path(d);idx,e=fixtures(root)
       folder=root/('catalogue-expansion-batch-'+e['batch'])
       (folder/'raw/selected.json').write_text('{}')
       with self.assertRaisesRegex(ValueError,'Source checksum disagreement'):
           build(idx,root,TEMPLATE,root/'results')
 def test_missing_batch_cannot_be_partial_claim(self):
    with tempfile.TemporaryDirectory() as d:
       root=Path(d);idx,e=fixtures(root)
       (root/'catalogue-expansion-batch-05/coverage_report.json').unlink()
       with self.assertRaises(FileNotFoundError):
           build(idx,root,TEMPLATE,root/'results')

if __name__=='__main__':unittest.main(verbosity=2)
