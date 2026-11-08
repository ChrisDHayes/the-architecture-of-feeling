#!/usr/bin/env python3
"""Merge per-batch discovery receipts with the 25-song baseline registry (not its measurements)."""
import argparse
import csv
import datetime as dt
import json
from collections import Counter
from pathlib import Path
from catalogue_coverage import BATCHES, registry

def merge(artifacts_dir,output):
    artifacts_dir=Path(artifacts_dir)
    output=Path(output)
    master=registry()
    by_id={}
    summaries={}
    for batch in BATCHES:
        matches=list(artifacts_dir.glob(f'**/catalogue-expansion-batch-{batch}/coverage_report.json'))
        # Also accept direct batch folder on a local test run.
        if not matches:
            matches=list(artifacts_dir.glob(f'catalogue-expansion-batch-{batch}/coverage_report.json'))
        if len(matches)!=1: raise ValueError(f'Expected exactly one report for batch {batch}, found {len(matches)}')
        report=json.loads(matches[0].read_text(encoding='utf-8'))
        if report.get('schema')!='architecture-of-feeling.catalogue-expansion.v1':
            raise ValueError(f'Unexpected schema for batch {batch}')
        if report['summary']['batch']!=batch:
            raise ValueError(f'Batch ID mismatch {batch}')
        summaries[batch]=report['summary']
        for row in report['records']:
            if row['track_id'] in by_id:raise ValueError('Duplicate song across batches: '+row['track_id'])
            if row['batch']!=batch:raise ValueError('Record outside batch: '+row['track_id'])
            if row.get('approved_for_similarity') or row.get('master_identity_verified'):
                raise ValueError('Unexpected scientific approval in expansion report')
            by_id[row['track_id']]=row
    new_ids={r['track_id'] for r in master if r['in_existing_25_registry']=='false'}
    if set(by_id)!=new_ids:
        raise ValueError('Batch coverage not exhaustive; refusing partial catalogue report')
    merged=[]
    for row in master:
        old=row['in_existing_25_registry']=='true'
        observation=by_id.get(row['track_id'])
        entry={k:row[k] for k in ('track_id','title','album','year','scope','batch','official_archive_url','in_existing_25_registry')}
        entry['acoustic_coverage_status']=('EXISTING_25_RESEARCH_SEPARATE_PIPELINE' if old else observation['status'])
        entry['selected_mbid']=None if old else observation.get('selected_mbid')
        entry['raw_source_available_in_batch_artifact']=bool(not old and observation.get('selected_mbid'))
        entry['master_identity_verified']=False
        entry['approved_for_similarity']=False
        merged.append(entry)
    source_retrieved=sum(bool(z.get('selected_mbid')) for z in by_id.values())
    summary={'schema':'architecture-of-feeling.full-catalogue-expansion-summary.v1',
             'generated_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
             'catalogue_entries':167,'studio_core':166,'edition_extension':1,
             'existing_25_registry_entries_not_requeried':25,
             'additional_entries_checked':len(by_id),
             'additional_pre_2023_eligible':130,
             'additional_post_2022_ineligible':12,
             'additional_source_observations_selected_unapproved':source_retrieved,
             'additional_missing_or_rejected':130-source_retrieved,
             'per_batch':summaries,
             'by_album':dict(Counter(z['album'] for z in merged)),
             'approved_for_similarity':0,
             'warning':'This merges registries and candidate availability, NOT 167 measured masters. The existing 25-song data are in a separate prior workflow. All new sources require independent edition/master and extractor comparability review.'}
    output.mkdir(parents=True,exist_ok=True)
    (output/'catalogue_coverage_index.json').write_text(json.dumps({'summary':summary,'records':merged},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    fields=list(merged[0])
    with (output/'catalogue_coverage_index.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(merged)
    (output/'catalogue_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('per_batch','by_album')},indent=2))
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifacts-dir',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    merge(args.artifacts_dir,args.output)
