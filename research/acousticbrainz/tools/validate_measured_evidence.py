#!/usr/bin/env python3
"""Fail-closed, offline evidence QA for a single AcousticBrainz GitHub Actions artifact.

No network or sound files needed. All candidate observations remain UNAPPROVED
until version/master identity and comparability are independently established.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

FEATURES = {
    'rhythm.tempo': ('rhythm.bpm', 'bpm'),
    'rhythm.onset_density': ('rhythm.onset_rate', 'onsets/sec'),
    'rhythm.beat_histogram_peak_spread': ('rhythm.bpm_histogram_first_peak_spread.mean', 'source units'),
    'timbre.spectral_centroid': ('lowlevel.spectral_centroid.mean', 'Hz'),
    'timbre.spectral_flux': ('lowlevel.spectral_flux.mean', 'source units'),
    'timbre.barkbands_flatness_db': ('lowlevel.barkbands_flatness_db.mean', 'source units'),
    'harmony.hpcp_entropy': ('tonal.hpcp_entropy.mean', 'source units'),
    'harmony.tonal_change_candidate_proxy': ('tonal.chords_changes_rate', 'changes/frame'),
    'dynamics.loudness': ('lowlevel.average_loudness', 'source units'),
    'dynamics.dynamic_complexity': ('lowlevel.dynamic_complexity', 'source units'),
}

def path_get(doc, path):
    for part in path.split('.'):
        if not isinstance(doc, dict) or part not in doc:
            return None
        doc = doc[part]
    return doc

def tag(tags, name):
    value = tags.get(name)
    if isinstance(value, list):
        return str(value[0]) if value else ''
    return str(value or '')

def clean(value):
    return ' '.join(''.join(c.lower() if c.isalnum() else ' ' for c in str(value)).split())

def safe_json(directory, relative):
    if not relative:
        return None, 'missing_reference'
    root = directory.resolve()
    file = (directory / relative).resolve()
    if not file.is_relative_to(root):
        return None, 'unsafe_path'
    try:
        return json.loads(file.read_text(encoding='utf-8')), None
    except (OSError, ValueError):
        return None, 'missing_or_invalid_json'

def audit(directory):
    report, failure = safe_json(directory, 'coverage_report.json')
    if failure or not isinstance(report, dict) or not isinstance(report.get('records'), list):
        raise ValueError('Missing valid coverage_report.json')
    receipts, observations = [], []
    ids = set()
    for item in report['records']:
        tid, title, album = item['track_id'], item['title'], item['album']
        if tid in ids:
            raise ValueError('Duplicate track ID: '+tid)
        ids.add(tid)
        flags = []
        mbid = item.get('selected_mbid')
        low, error = safe_json(directory, item.get('lowlevel_file'))
        high, high_error = safe_json(directory, item.get('highlevel_file'))
        if error or not low:
            flags.append('lowlevel_'+(error or 'invalid_document'))
        if high_error or not high:
            flags.append('highlevel_'+(high_error or 'invalid_document'))
        meta = (low or {}).get('metadata') or {}
        tags = meta.get('tags') or {}
        props = meta.get('audio_properties') or {}
        version = meta.get('version') or {}
        tag_mbid = tag(tags, 'musicbrainz_recordingid')
        tag_title = tag(tags, 'title')
        tag_album = tag(tags, 'album')
        if not mbid:
            flags.append('candidate_not_selected')
        elif not tag_mbid or tag_mbid != mbid:
            flags.append('recording_id_mismatch_or_missing_tag')
        if low and (not tag_title or clean(tag_title) != clean(title)):
            flags.append('title_mismatch_or_missing_tag')
        if low and (not tag_album or clean(tag_album) != clean(album)):
            flags.append('album_mismatch_or_missing_tag')
        if low and (tag(tags, 'artist') and clean(tag(tags, 'artist')) != 'depeche mode'):
            flags.append('artist_mismatch')
        codec = str(props.get('codec') or '').lower()
        lossless = props.get('lossless')
        if low and not lossless:
            flags.append('lossy_source')
        bitrate = props.get('bit_rate')
        if low and codec in ('mp3','aac','ogg') and isinstance(bitrate,(int,float)) and bitrate < 192000:
            flags.append('low_bitrate_source')
        if low and not version.get('essentia'):
            flags.append('extractor_version_unknown')
        digest = None
        if low:
            source_path = (directory / item['lowlevel_file']).resolve()
            digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        hprops = ((high or {}).get('metadata') or {}).get('audio_properties') or {}
        if low and high and props.get('md5_encoded') and hprops.get('md5_encoded') and props['md5_encoded'] != hprops['md5_encoded']:
            flags.append('high_low_audio_fingerprint_disagrees')
        measurements = item.get('measurement_values') or {}
        counted = 0
        for label, (source_path, units) in FEATURES.items():
            v = path_get(low, source_path) if low else None
            reported = measurements.get(label, {})
            rv = reported.get('source_value') if isinstance(reported, dict) else None
            provenance_ok = isinstance(reported, dict) and reported.get('source_path') == source_path
            numeric = isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
            parity = numeric and isinstance(rv,(int,float)) and math.isclose(v,rv,rel_tol=1e-9,abs_tol=1e-9)
            if low and not (numeric and provenance_ok and parity):
                flags.append('feature_parity:'+label)
            if numeric and provenance_ok and parity:
                counted += 1
            observations.append({'track_id':tid,'song':title,'album':album,'selected_mbid':mbid or '',
                'feature':label,'source_path':source_path,'unit':units,
                'source_value':v if numeric else '',
                'source_report_parity': bool(parity and provenance_ok),
                'source_codec':codec,'essentia_version':version.get('essentia') or '',
                'review_state':'UNAPPROVED'})
        if low and not isinstance(props.get('length'),(float,int)):
            flags.append('source_duration_missing')
        receipts.append({
            'track_id':tid,'song':title,'album':album,'pilot':tid in report.get('pilot_track_ids',[]),
            'selected_mbid':mbid,'source_title':tag_title or None,'source_album':tag_album or None,
            'source_duration_seconds':props.get('length'), 'codec':codec or None,'lossless':lossless,
            'bit_rate':bitrate,'essentia_version':version.get('essentia'),'extractor':version.get('extractor'),
            'source_audio_encoded_md5':props.get('md5_encoded'), 'raw_lowlevel_sha256':digest,
            'feature_count_parity_passed':counted,'feature_count_expected':len(FEATURES),
            'qa_flags':sorted(set(flags)),
            'provisional_research_observation':bool(low and counted==len(FEATURES) and not any(
                k for k in flags if k not in ('lossy_source','low_bitrate_source'))),
            'master_identity_verified':False,'approved_for_similarity':False,
            'reason':'Matching metadata and descriptors do not prove a reference edition/master or cross-source comparability.'
        })
    summary = {
        'schema':'architecture-of-feeling.measured-evidence-qa.v1',
        'source_run':report.get('generated_at_utc'),
        'song_count':len(receipts),
        'lowlevel_raw_readable':sum(x['raw_lowlevel_sha256'] is not None for x in receipts),
        'full_ten_feature_parity':sum(x['feature_count_parity_passed']==len(FEATURES) for x in receipts),
        'lossless_observations':sum(x['lossless'] is True for x in receipts),
        'lossy_observations':sum(x['lossless'] is False for x in receipts),
        'low_bitrate_observations':sum('low_bitrate_source' in x['qa_flags'] for x in receipts),
        'unresolved_selection':sum(x['selected_mbid'] is None for x in receipts),
        'essentia_versions':sorted(set(x['essentia_version'] for x in receipts if x['essentia_version'])),
        'pilot_retrieved':sum(x['pilot'] and x['raw_lowlevel_sha256'] is not None for x in receipts),
        'pilot_size':sum(x['pilot'] for x in receipts),
        'approved_for_similarity':0,
        'warning':'Exploratory precomputed descriptors only. No studio-master identity or cross-version comparability certified.'
    }
    return {'summary':summary,'receipts':receipts,'observations':observations}

def write_outputs(result, output):
    output.mkdir(parents=True,exist_ok=True)
    (output/'evidence_receipts.json').write_text(json.dumps({'summary':result['summary'],'records':result['receipts']},indent=2,ensure_ascii=False)+'\n', encoding='utf-8')
    (output/'evidence_qa_summary.json').write_text(json.dumps(result['summary'],indent=2)+'\n',encoding='utf-8')
    columns=['track_id','song','album','selected_mbid','feature','source_path','unit','source_value','source_report_parity','source_codec','essentia_version','review_state']
    with (output/'measured_descriptor_observations.csv').open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=columns);w.writeheader();w.writerows(result['observations'])
    lines=['# Measured Evidence QA — research-only, NOT publication clearance','',
      'This is an inspection of the AcousticBrainz **submitted-file** low-level JSON in one GitHub Actions artifact.',
      'Descriptors are source values, not 0–1 V2.9 features. No recording/master has been approved.','',
      '## Overview','']
    lines.extend(f'- **{k}**: {v}' for k,v in result['summary'].items() if k!='warning')
    lines += ['', '## Priority issues', '']
    for r in result['receipts']:
        if r['qa_flags'] or r['pilot']:
            lines.append(f"- **{r['song']}** ({'pilot' if r['pilot'] else 'editorial'}): {', '.join(r['qa_flags']) if r['qa_flags'] else 'metadata parity passes; master review outstanding'}.")
    lines += ['', '## Gate before modeling', '',
     '1. Verify the exact album/studio recording and reference edition/master against release and track boundaries.',
     '2. Replace missing or wrong-version records, and assess lossy submissions and extraction-version effects.',
     '3. Document comparison eligibility and sensitivity tests; do not replace missing values or silently normalize.',
     '4. Do not claim acoustic clusters, emotional relationships, or album-level evolution from this artifact.', '']
    (output/'EVIDENCE_QA_README.md').write_text('\n'.join(lines),encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=audit(args.artifact_dir)
    write_outputs(result,args.output)
    print(json.dumps(result['summary'],indent=2))

if __name__=='__main__':
    main()
