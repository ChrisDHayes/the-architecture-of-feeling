#!/usr/bin/env python3
"""Network-free tests for the historical Depeche Mode full-catalogue expansion."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import catalogue_coverage as c
from merge_catalogue_coverage import merge

class Tests(unittest.TestCase):
    def test_167_registry_identity(self):
        rows=c.registry()
        self.assertEqual(len(rows),167)
        self.assertEqual(sum(r['scope']=='studio_core' for r in rows),166)
        self.assertEqual(sum(r['in_existing_25_registry']=='false' for r in rows),142)
        self.assertEqual(sum(r['archive_lookup_policy']=='ELIGIBLE_UNCHECKED' for r in rows),130)
        self.assertEqual(sum(r['archive_lookup_policy']=='OUTSIDE_2022_SUBMISSION_WINDOW' for r in rows),12)
    def test_25_baseline_not_requeried(self):
        rows=c.registry()
        for batch in c.BATCHES:
            active=[r for r in rows if r['in_existing_25_registry']=='false' and r['batch']==batch]
            self.assertFalse(any(r['in_existing_25_registry']=='true' for r in active))
    def test_all_2023_expansion_rows_outside_archive(self):
        rows=c.registry()
        post=[r for r in rows if r['year']=='2023' and r['in_existing_25_registry']=='false']
        self.assertEqual(len(post),12)
        self.assertTrue(all(r['archive_lookup_policy']=='OUTSIDE_2022_SUBMISSION_WINDOW' for r in post))
    def test_no_measured_synthetic_values_in_registry(self):
        rows=c.registry()
        self.assertNotIn('energy',rows[0]);self.assertNotIn('darkness',rows[0]);self.assertNotIn('f',rows[0])
        self.assertEqual(rows[0]['audio_measured_by_extension'],'false')
    def test_transient_error_not_absence(self):
        self.assertTrue(c.is_transient('http_503'))
        self.assertFalse(c.is_transient('http_404'))
    def test_provisional_source_selected_but_unapproved(self):
        row=next(r for r in c.registry() if r['track_id']=='a01_t01')
        mbid='01234567-89ab-cdef-0123-456789abcdef'
        def search(q,timeout):
            return [{'mbid':mbid,'search_score':95,'exact_album_in_search':True,'title':q['title']}],'ok'
        def fetch(url,timeout):
            info={'metadata':{'tags':{'title':[row['title']],'album':[row['album']],'musicbrainz_recordingid':[mbid]},'audio_properties':{'codec':'flac','lossless':True,'length':220,'bit_rate':750000},'version':{'essentia':'2.1-beta1'}},'rhythm':{},'lowlevel':{},'tonal':{}}
            for name,path in c.FEATURES.items():
                cur=info
                for part in path.split('.')[:-1]:cur=cur.setdefault(part,{})
                cur[path.split('.')[-1]]=7.0
            return info,'ok'
        with tempfile.TemporaryDirectory() as d, patch.object(c,'registry',lambda:[row]):
            report=c.run('01',Path(d)/'batch',sleep_fn=lambda _:None,search=search,fetch=fetch)
            o=report['records'][0]
            self.assertEqual(o['selected_mbid'],mbid)
            self.assertFalse(o['master_identity_verified'])
            self.assertFalse(o['approved_for_similarity'])
            self.assertEqual(report['summary']['lowlevel_selected_unapproved'],1)
            self.assertEqual(len(o['observed_features']),10)
    def test_post2022_never_calls_apis(self):
        row=next(r for r in c.registry() if r['track_id']=='a15_t01')
        def fail(*args):raise AssertionError('2023 audio must not query closed archive')
        with tempfile.TemporaryDirectory() as d,patch.object(c,'registry',lambda:[row]):
            report=c.run('05',Path(d)/'batch',sleep_fn=lambda _:None,search=fail,fetch=fail)
            self.assertEqual(report['records'][0]['status'],'post_2022_submission_window')
            self.assertIsNone(report['records'][0]['selected_mbid'])
    def test_album_mismatch_never_approved(self):
        row=next(r for r in c.registry() if r['track_id']=='a01_t01')
        mbid='01234567-89ab-cdef-0123-456789abcdef'
        def search(q,timeout):return [{'mbid':mbid,'search_score':99,'exact_album_in_search':True}],'ok'
        def fetch(url,timeout):return {'metadata':{'tags':{'title':[row['title']],'album':['The Singles 86>98']},'audio_properties':{'codec':'flac','lossless':True}}},'ok'
        with tempfile.TemporaryDirectory() as d,patch.object(c,'registry',lambda:[row]):
            report=c.run('01',Path(d),sleep_fn=lambda _:None,search=search,fetch=fetch)
            self.assertIsNone(report['records'][0]['selected_mbid'])
            self.assertEqual(report['records'][0]['status'],'retrieved_source_but_album_identity_incompatible')
    def test_merge_complete_registry_keeps_old_25_separate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); rows=c.registry()
            for batch in c.BATCHES:
                selected=[r for r in rows if r['in_existing_25_registry']=='false' and r['batch']==batch]
                directory=root/f'catalogue-expansion-batch-{batch}'
                directory.mkdir()
                report={'schema':'architecture-of-feeling.catalogue-expansion.v1',
                    'summary':{'batch':batch},
                    'records':[{'track_id':r['track_id'],'title':r['title'],'album':r['album'],
                                'batch':batch,'status':'post_2022_submission_window' if int(r['year'])>2022 else 'no_exact_album_candidate_in_search_not_proof_of_absence',
                                'selected_mbid':None,'approved_for_similarity':False,
                                'master_identity_verified':False} for r in selected]}
                (directory/'coverage_report.json').write_text(json.dumps(report))
            summary=merge(root,root/'merged')
            self.assertEqual(summary['catalogue_entries'],167)
            self.assertEqual(summary['existing_25_registry_entries_not_requeried'],25)
            self.assertEqual(summary['additional_entries_checked'],142)
            output=json.loads((root/'merged'/'catalogue_coverage_index.json').read_text())
            self.assertEqual(sum(r['acoustic_coverage_status']=='EXISTING_25_RESEARCH_SEPARATE_PIPELINE' for r in output['records']),25)
            self.assertEqual(sum(r['acoustic_coverage_status']=='post_2022_submission_window' for r in output['records']),12)
            self.assertEqual(sum(r['approved_for_similarity'] for r in output['records']),0)
    def test_no_exact_album_recording_is_unresolved(self):
        row=next(r for r in c.registry() if r['track_id']=='a01_t01')
        def search(q,timeout):return [{'mbid':'01234567-89ab-cdef-0123-456789abcdef','exact_album_in_search':False}],'ok'
        def fail(*args):raise AssertionError('Do not retrieve compilation-only candidate')
        with tempfile.TemporaryDirectory() as d,patch.object(c,'registry',lambda:[row]):
            report=c.run('01',Path(d),sleep_fn=lambda _:None,search=search,fetch=fail)
            self.assertIsNone(report['records'][0]['selected_mbid'])
            self.assertEqual(report['records'][0]['status'],'no_exact_album_candidate_in_search_not_proof_of_absence')
    def test_merge_rejects_missing_batch(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'Expected exactly one report'):
                merge(Path(d),Path(d)/'result')

if __name__=='__main__': unittest.main(verbosity=2)
