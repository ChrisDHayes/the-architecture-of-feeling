#!/usr/bin/env python3
"""Create an evidence-quality atlas of 167 Depeche Mode catalogue entries.

Consumes five real MusicBrainz/AcousticBrainz batch artifacts and the merged
167-song coverage registry. NEVER certifies masters, distance, mood, or features.
Original source JSON stays in the private GitHub Actions artifacts.
"""
import argparse
import csv
import hashlib
import html
import io
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

FEATURES = {
 'rhythm.tempo': 'rhythm.bpm',
 'rhythm.onset_density': 'rhythm.onset_rate',
 'rhythm.beat_histogram_peak_spread': 'rhythm.bpm_histogram_first_peak_spread.mean',
 'timbre.spectral_centroid': 'lowlevel.spectral_centroid.mean',
 'timbre.spectral_flux': 'lowlevel.spectral_flux.mean',
 'timbre.barkbands_flatness_db': 'lowlevel.barkbands_flatness_db.mean',
 'harmony.hpcp_entropy': 'tonal.hpcp_entropy.mean',
 'harmony.tonal_change_candidate_proxy': 'tonal.chords_changes_rate',
 'dynamics.loudness': 'lowlevel.average_loudness',
 'dynamics.dynamic_complexity': 'lowlevel.dynamic_complexity',
}
EXPECTED_IDS = 167
ALLOWED_STATUSES = {'provisional_observation_requires_master_review','provisional_quality_flagged_requires_review','retrieved_source_but_album_identity_incompatible','no_exact_album_candidate_in_search_not_proof_of_absence','no_retrieved_source_for_probed_candidates','musicbrainz_unavailable_not_proof_of_absence','post_2022_submission_window'}


def norm(s):
    return ''.join(c for c in str(s).casefold() if c.isalnum())

def first_tag(tags, name):
    value = tags.get(name)
    if isinstance(value, list):
        return str(value[0]) if value else ''
    return str(value or '')

def field(doc, path):
    node = doc
    for piece in path.split('.'):
        if not isinstance(node, dict) or piece not in node:
            return None
        node = node[piece]
    return node

def safe_json(base, rel):
    if not isinstance(rel, str) or not rel:
        raise ValueError('Missing raw JSON file reference')
    src=(base/rel).resolve()
    if not src.is_relative_to(base.resolve()):
        raise ValueError('Unsafe raw JSON path: '+rel)
    return src, json.loads(src.read_text(encoding='utf8'))

def source_review(record, batch_directory):
    mbid = record.get('selected_mbid')
    if not mbid:
        raise ValueError('Cannot review record with no candidate')
    src, raw = safe_json(batch_directory, record.get('lowlevel_file'))
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    if digest != record.get('lowlevel_sha256'):
        raise ValueError('Source checksum disagreement: '+record['track_id'])
    tags=((raw.get('metadata') or {}).get('tags') or {})
    props=((raw.get('metadata') or {}).get('audio_properties') or {})
    version=((raw.get('metadata') or {}).get('version') or {})
    title=first_tag(tags,'title')
    album=first_tag(tags,'album')
    src_mbid=first_tag(tags,'musicbrainz_recordingid')
    flags=set(record.get('quality_flags') or [])
    if not title or norm(title)!=norm(record['title']):
        flags.add('source_title_mismatch_or_missing')
    if not album or norm(album)!=norm(record['album']):
        flags.add('source_album_mismatch_or_missing')
    if not src_mbid or src_mbid.casefold()!=mbid.casefold():
        flags.add('source_mbid_mismatch_or_missing')
    if props.get('lossless') is False:
        flags.add('lossy_source')
    if props.get('lossless') is not True and props.get('lossless') is not False:
        flags.add('losslessness_unknown')
    bitrate=props.get('bit_rate')
    if props.get('lossless') is False and isinstance(bitrate,(int,float)) and bitrate <192000:
        flags.add('low_bitrate')
    if not version.get('essentia'):
        flags.add('extractor_unknown')
    if not isinstance(props.get('length'),(int,float)):
        flags.add('source_duration_missing')
    observed=record.get('observed_features') or {}
    parity_count=0
    values={}
    for feature,path in FEATURES.items():
        original=field(raw,path)
        reported=(observed.get(feature) or {})
        candidate=reported.get('source_value')
        correct_path=reported.get('source_path')==path
        numeric=(type(original) in (int,float) and type(candidate) in (int,float) and
                 math.isfinite(original) and math.isfinite(candidate))
        parity=numeric and correct_path and math.isclose(original,candidate,rel_tol=1e-9,abs_tol=1e-9)
        if parity:parity_count+=1
        else:flags.add('descriptor_source_parity:'+feature)
        values[feature]=original if numeric else None
    if record.get('approved_for_similarity') or record.get('master_identity_verified'):
        raise ValueError('Unexpected master/similarity approval for '+record['track_id'])
    clean_identity=(not flags.intersection({'source_title_mismatch_or_missing','source_album_mismatch_or_missing','source_mbid_mismatch_or_missing'}))
    if parity_count<10:
        quality='source_descriptor_issue'
    elif not clean_identity:
        quality='source_identity_mismatch'
    elif flags:
        quality='source_quality_flagged'
    elif props.get('lossless') is True:
        quality='tag_aligned_lossless_candidate'
    else:
        quality='source_quality_flagged'
    return {'status':quality,'source_title':title,'source_album':album,'source_mbid':src_mbid,
            'source_codec':props.get('codec'),'lossless':props.get('lossless'),
            'bit_rate':bitrate,'essentia_version':version.get('essentia'),
            'duration_seconds':props.get('length'),'source_sha256':digest,
            'feature_parity_count':parity_count,'feature_expected':len(FEATURES),
            'flags':sorted(flags),'features':values}

def build(index, batches, template, out):
    index=Path(index);batches=Path(batches);template=Path(template);out=Path(out)
    payload=json.loads(index.read_text(encoding='utf8'))
    source_records=payload.get('records')
    if not isinstance(source_records,list) or len(source_records)!=EXPECTED_IDS:
        raise ValueError('Requires a complete 167-entry catalogue index')
    if len({r['track_id'] for r in source_records}) != EXPECTED_IDS:
        raise ValueError('Duplicate or missing source track IDs')
    if not isinstance(payload.get('summary'),dict) or payload['summary'].get('approved_for_similarity')!=0:
        raise ValueError('Source index is not an explicitly unapproved catalogue')
    by_track={}
    dirs={}
    for batch in ['01','02','03','04','05']:
        folder=batches/('catalogue-expansion-batch-'+batch)
        doc=json.loads((folder/'coverage_report.json').read_text(encoding='utf8'))
        if doc.get('schema')!='architecture-of-feeling.catalogue-expansion.v1' or doc['summary'].get('batch')!=batch:
            raise ValueError('Unexpected source batch identity: '+batch)
        dirs[batch]=folder
        for entry in doc['records']:
            id=entry['track_id']
            if id in by_track:
                raise ValueError('Repeated ID: '+id)
            if entry['batch']!=batch or entry['status'] not in ALLOWED_STATUSES:
                raise ValueError('Unexpected status/batch for '+id)
            by_track[id]=entry
    rows=[]
    for r in source_records:
        track_id=r['track_id'];baseline=r['in_existing_25_registry']=='true'
        ref=by_track.get(track_id)
        if baseline and ref or not baseline and not ref:
            raise ValueError('25 baseline/142 expansion boundary violated '+track_id)
        data={'track_id':track_id,'title':r['title'],'album':r['album'],'year':int(r['year']),
              'scope':r['scope'],'batch':r['batch'],'baseline':baseline,
              'selected_mbid':None,'candidate_status':r['acoustic_coverage_status'],
              'category':'existing_25_separate','source_quality':None,
              'approved_for_similarity':False,'master_identity_verified':False}
        if ref:
            data['selected_mbid']=ref.get('selected_mbid')
            if data['selected_mbid']:
                review=source_review(ref,dirs[ref['batch']]);data['source_quality']=review
                data['category']='provisional_observation'
            elif ref.get('status')=='post_2022_submission_window':
                data['category']='post_archive'
            else:
                data['category']='unresolved'
        rows.append(data)
    if len(by_track)!=142 or sum(r['baseline'] for r in rows)!=25:
        raise ValueError('Unexpected baseline / expansion population')
    counts=Counter(r['category'] for r in rows)
    sources=[r for r in rows if r['category']=='provisional_observation']
    family=Counter(r['source_quality']['status'] for r in sources)
    allversions=Counter(str(r['source_quality'].get('essentia_version')) for r in sources)
    by_album=[]
    for album in dict.fromkeys(r['album'] for r in rows):
        selected=[r for r in rows if r['album']==album]
        by_album.append({'album':album,'year':min(r['year'] for r in selected),'total':len(selected),
            'categories':dict(Counter(r['category'] for r in selected))})
    summary={'schema':'architecture-of-feeling.catalogue-evidence-atlas.v1',
      'population':len(rows),'baseline_separate':counts['existing_25_separate'],
      'additional_reviewed':len(by_track),'historically_ineligible':counts['post_archive'],
      'new_source_candidates':counts['provisional_observation'],
      'new_unresolved':counts['unresolved'],'source_quality':dict(family),
      'essentia_versions':dict(allversions),'approved_for_similarity':0,
      'catalogue_coverage_status':'UNAPPROVED_RESEARCH_CANDIDATES',
      'warning':'The 25-song prior audit is a separate data source. No row has master or similarity clearance.'}
    assembled={'summary':summary,'albums':by_album,'records':rows}
    out.mkdir(parents=True,exist_ok=True)
    (out/'catalogue_evidence_atlas.json').write_text(json.dumps(assembled,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    csvfields=['track_id','title','album','year','scope','batch','category','candidate_status','selected_mbid',
        'source_quality_status','codec','lossless','bit_rate','essentia_version','parity_passed','flags','approved_for_similarity']
    with (out/'catalogue_source_review.csv').open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=csvfields);w.writeheader()
        for r in rows:
            q=r['source_quality'] or {}
            w.writerow({'track_id':r['track_id'],'title':r['title'],'album':r['album'],'year':r['year'],
              'scope':r['scope'],'batch':r['batch'],'category':r['category'],
              'candidate_status':r['candidate_status'],'selected_mbid':r['selected_mbid'] or '',
              'source_quality_status':q.get('status',''),'codec':q.get('source_codec',''),
              'lossless':q.get('lossless',''),'bit_rate':q.get('bit_rate',''),
              'essentia_version':q.get('essentia_version',''),
              'parity_passed':q.get('feature_parity_count',''),
              'flags':';'.join(q.get('flags') or []),'approved_for_similarity':'false'})
    src=template.read_text(encoding='utf8')
    marker='/*CATALOGUE_ATLAS_DATA*/'
    if marker not in src:raise ValueError('Missing HTML template placeholder')
    embedded=json.dumps(assembled,separators=(',',':'),ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    (out/'Catalogue_Evidence_Atlas.html').write_text(src.replace(marker,embedded),encoding='utf8')
    readme='# The Architecture of Feeling — catalogue evidence atlas\n\n'
    readme+='**Research state: UNAPPROVED**. No catalogue-wide sonic proximity, emotion, master identity or cross-extractor comparability claims.\n\n'
    readme+=f"- {len(rows)} catalogue entries including the edition-specific extension.\n- {len(by_track)} newly searched entries; {counts['provisional_observation']} with source candidates; {counts['unresolved']} unresolved; {counts['post_archive']} post-2022 and historically ineligible.\n- The original 25-song research sample is kept separate, and neither its sources nor master identities are silently inferred here.\n\n"
    readme+='The CSV/JSON preserve source provenance and flags. The HTML is an exploratory *coverage map* without measured musical similarity. Raw AcousticBrainz JSON remains in the private Actions batch artifacts.\n'
    (out/'README.md').write_text(readme,encoding='utf8')
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--index',required=True,type=Path)
    p.add_argument('--batches',required=True,type=Path)
    p.add_argument('--template',type=Path,default=Path(__file__).resolve().parent.parent/'templates'/'catalogue_evidence_atlas.html')
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(build(a.index,a.batches,a.template,a.output),indent=2))
if __name__=='__main__':main()
