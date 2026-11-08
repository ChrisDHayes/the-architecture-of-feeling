#!/usr/bin/env python3
"""Acquire previously unaudited studio-catalogue candidates from MusicBrainz / AcousticBrainz.

Five album-ordered batches, 25-song baseline held separate. Fails closed: presence of
precomputed features NEVER establishes album/master identity or sonic comparability.
No audio, lyrics, fabricated values, or automatic publication is used.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import pathlib
import sys
import time

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE.parent.parent/'acousticbrainz'/'tools'))
from audit25 import FEATURES, MBID, find_candidates, get, inspect_submission, value_at
from resolve_candidates import quality_score

BATCHES=tuple(f'{i:02}' for i in range(1,6))
TRANSIENT={'http_429','http_500','http_502','http_503','http_504'}

def registry(path=None):
    path=path or ROOT/'data'/'full_catalogue_167.csv'
    with pathlib.Path(path).open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=167 or len({r['track_id'] for r in rows})!=167:
        raise ValueError('Expected 167 distinct archival catalogue entries')
    if sum(r['scope']=='studio_core' for r in rows)!=166:
        raise ValueError('Expected 166 core studio-album entries')
    if len({r['album'] for r in rows})!=15:
        raise ValueError('Expected 15 studio albums')
    old=[r for r in rows if r['in_existing_25_registry']=='true']
    new=[r for r in rows if r['in_existing_25_registry']=='false']
    if len(old)!=25 or len(new)!=142:
        raise ValueError('25-song baseline must be excluded from 142-song expansion')
    if sum(r['archive_lookup_policy']=='ELIGIBLE_UNCHECKED' for r in new)!=130:
        raise ValueError('Expected 130 pre-2023 additional candidates')
    if sum(r['archive_lookup_policy']=='OUTSIDE_2022_SUBMISSION_WINDOW' for r in new)!=12:
        raise ValueError('Expected 12 2023 entries ineligible for historical lookup')
    if {r['batch'] for r in new}!=set(BATCHES):
        raise ValueError('Expected 5 album-based batches')
    return rows

def is_transient(status):
    return status in TRANSIENT or status.startswith('network_error_')

def retry(fn, *args):
    for attempt in range(3):
        obj,status=fn(*args)
        if status=='ok' or not is_transient(status) or attempt==2:
            return obj,status
        time.sleep([1.2,2.5][attempt])
    return None,'retry_exhausted'

def run(batch,output,timeout=12,max_candidates=4,sleep_fn=time.sleep,fetch=None,search=None):
    if batch not in BATCHES: raise ValueError('Unknown batch')
    if not 1<=max_candidates<=5: raise ValueError('max_candidates must be 1..5')
    rows=[r for r in registry() if r['in_existing_25_registry']=='false' and r['batch']==batch]
    if not rows: raise ValueError('Batch empty')
    output=pathlib.Path(output);output.mkdir(parents=True,exist_ok=True)
    raw=output/'raw';raw.mkdir(exist_ok=True)
    fetch=fetch or get
    search=search or find_candidates
    entries=[];probes=[]
    last_mb=0.0
    for row in rows:
        entry={'track_id':row['track_id'],'title':row['title'],'album':row['album'],
               'year':int(row['year']),'scope':row['scope'],'batch':batch,
               'archive_eligible':row['archive_lookup_policy']=='ELIGIBLE_UNCHECKED',
               'selected_mbid':None,'master_identity_verified':False,
               'approved_for_similarity':False,'candidate_count':None,
               'musicbrainz_status':'not_checked','status':'not_checked',
               'lowlevel_status':'not_checked','highlevel_status':'not_checked',
               'observed_features':{},'candidate_evidence':[]}
        if not entry['archive_eligible']:
            entry['status']='post_2022_submission_window'
            entry['lowlevel_status']=entry['highlevel_status']='not_in_2022_archive'
            entries.append(entry)
            continue
        # Strictly respect MusicBrainz's ~1 request/second policy.
        elapsed=time.monotonic()-last_mb
        if elapsed < 1.25: sleep_fn(1.25-elapsed)
        last_mb=time.monotonic()
        cands,sstatus=retry(search,row,timeout)
        entry['musicbrainz_status']=sstatus
        if sstatus!='ok':
            entry['status']='musicbrainz_unavailable_not_proof_of_absence'
            entries.append(entry);continue
        valid=[];seen=set()
        for c in cands:
            mbid=c.get('mbid') or ''
            if c.get('exact_album_in_search') and MBID.fullmatch(mbid) and mbid not in seen:
                valid.append(c);seen.add(mbid)
        entry['candidate_count']=len(valid)
        if not valid:
            entry['status']='no_exact_album_candidate_in_search_not_proof_of_absence'
            entries.append(entry);continue
        valid=sorted(valid,key=lambda c:(-(c.get('search_score') or 0),c['mbid']))
        best=None;best_score=-1001;tried=0
        for cand in valid[:max_candidates]:
            mbid=cand['mbid'];tried+=1
            sleep_fn(0.35)
            low,status=retry(fetch,f'https://acousticbrainz.org/api/v1/{mbid}/low-level',timeout)
            probe={'mbid':mbid,'url':f'https://acousticbrainz.org/{mbid}',
                   'musicbrainz_search_score':cand.get('search_score'),
                   'lowlevel_status':status,'source_album_match_in_search':True}
            if status!='ok' or not isinstance(low,dict):
                if status=='ok':probe['lowlevel_status']='invalid_lowlevel_document'
                probes.append({'track_id':row['track_id'],**probe})
                continue
            quality=inspect_submission(low,row['title'],row['album'],mbid)
            score=quality_score(quality)
            rawp=raw/f'{row["track_id"]}_{mbid}_lowlevel.json'
            rawp.write_text(json.dumps(low,ensure_ascii=False,indent=2),encoding='utf-8')
            qflags=list(quality.get('flags') or [])
            if not quality.get('source_recording_mbid'):
                qflags.append('submitted_audio_recording_mbid_tag_missing')
            if not quality.get('source_length_seconds'):
                qflags.append('submitted_audio_duration_missing')
            probe.update({'quality_score':score,'quality':quality,'warnings':qflags,
                           'lowlevel_sha256':hashlib.sha256(rawp.read_bytes()).hexdigest(),
                           'lowlevel_file':str(rawp.relative_to(output))})
            probes.append({'track_id':row['track_id'],**probe})
            if score>best_score:
                best_score=score;best=(mbid,low,quality,probe)
            if score>=115 and not qflags:
                break
        entry['candidate_probes_count']=tried
        if best is None:
            entry['status']='no_retrieved_source_for_probed_candidates'
            entry['lowlevel_status']='unknown_or_not_found_for_tested_candidates'
        elif best_score < 60:
            entry['status']='retrieved_source_but_album_identity_incompatible'
            entry['lowlevel_status']='candidate_retrieved_but_rejected'
            entry['best_rejected_candidate_quality']=best[2]
        else:
            mbid,low,quality,probe=best
            entry['selected_mbid']=mbid
            entry['status']='provisional_observation_requires_master_review'
            entry['lowlevel_status']='retrieved_unapproved'
            entry['lowlevel_file']=probe['lowlevel_file']
            entry['lowlevel_sha256']=probe['lowlevel_sha256']
            entry['submission_quality']=quality
            entry['quality_flags']=probe['warnings']
            entry['observed_features']={name:{'source_path':path,'source_value':value_at(low,path)}
                                        for name,path in FEATURES.items()}
            sleep_fn(0.35)
            high,hstat=retry(fetch,f'https://acousticbrainz.org/api/v1/{mbid}/high-level',timeout)
            entry['highlevel_status']='retrieved_unapproved' if hstat=='ok' and isinstance(high,dict) else hstat
            if hstat=='ok' and isinstance(high,dict):
                hp=raw/f'{row["track_id"]}_{mbid}_highlevel.json'
                hp.write_text(json.dumps(high,ensure_ascii=False,indent=2),encoding='utf-8')
                entry['highlevel_file']=str(hp.relative_to(output))
            if best_score<100:
                entry['status']='provisional_quality_flagged_requires_review'
        entries.append(entry)
    summary={'batch':batch,'catalogue_entries_checked':len(entries),
             'eligible_attempted':sum(x['archive_eligible'] for x in entries),
             'outside_2022_archive':sum(not x['archive_eligible'] for x in entries),
             'lowlevel_selected_unapproved':sum(bool(x.get('selected_mbid')) for x in entries),
             'highlevel_retrieved':sum(x['highlevel_status']=='retrieved_unapproved' for x in entries),
             'identity_or_source_unresolved':sum(x['archive_eligible'] and not x.get('selected_mbid') for x in entries),
             'approved_for_similarity':0,'complete_catalogue_measured':False}
    report={'schema':'architecture-of-feeling.catalogue-expansion.v1',
            'generated_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'source':'MusicBrainz search + AcousticBrainz historical CC0 API',
            'scope':'142 additional catalogue tracks, partitioned by three studio albums',
            'warnings':['No commercial audio downloaded','MusicBrainz album affiliation does not prove the submitted audio master',
                        '2023 tracks postdate the 2022 AcousticBrainz submission window',
                        'A missing API observation is not proof that the song lacks recordings'],
            'summary':summary,'records':entries}
    (output/'coverage_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (output/'candidate_probes.json').write_text(json.dumps(probes,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    columns=['track_id','title','album','year','scope','batch','archive_eligible','musicbrainz_status',
             'candidate_count','status','selected_mbid','lowlevel_status','highlevel_status','codec',
             'lossless','bit_rate','source_album','quality_flags','approved_for_similarity']
    with (output/'coverage_report.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
        for e in entries:
            q=e.get('submission_quality') or {}
            w.writerow({k:({'codec':q.get('codec'),'lossless':q.get('lossless'),
                 'bit_rate':q.get('bit_rate'),'source_album':q.get('source_album'),
                 'quality_flags':';'.join(e.get('quality_flags') or [])}.get(k,e.get(k)))
                 for k in columns})
    print(json.dumps(summary,indent=2))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True,choices=BATCHES)
    p.add_argument('--output',required=True)
    p.add_argument('--timeout',type=int,default=12)
    p.add_argument('--max-candidates',type=int,default=4)
    a=p.parse_args()
    run(a.batch,a.output,a.timeout,a.max_candidates)
