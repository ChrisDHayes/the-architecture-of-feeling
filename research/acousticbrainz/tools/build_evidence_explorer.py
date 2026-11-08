#!/usr/bin/env python3
"""Build a provenance-first, single-file source descriptor explorer.

Input is the QA stage's exported receipt JSON and observed descriptor CSV.
This is NOT master approval, a sonic similarity analysis or a mood predictor.
"""
import argparse, csv, hashlib, html, io, json, math
from pathlib import Path
from statistics import median

LABELS = {
 'rhythm.tempo':'Estimated tempo',
 'rhythm.onset_density':'Onset rate',
 'rhythm.beat_histogram_peak_spread':'Beat histogram spread',
 'timbre.spectral_centroid':'Spectral centroid',
 'timbre.spectral_flux':'Spectral flux',
 'timbre.barkbands_flatness_db':'Bark-band flatness',
 'harmony.hpcp_entropy':'Pitch-class entropy',
 'harmony.tonal_change_candidate_proxy':'Chord-change rate',
 'dynamics.loudness':'Algorithmic average loudness',
 'dynamics.dynamic_complexity':'Algorithmic dynamic complexity',
}

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def build(qa_dir, template, output):
    receipt_path=qa_dir/'evidence_receipts.json'
    csv_path=qa_dir/'measured_descriptor_observations.csv'
    if not all(p.is_file() for p in [receipt_path,csv_path,template]):
        raise ValueError('Required QA inputs or HTML template absent')
    source=json.loads(receipt_path.read_text(encoding='utf8'))
    receipts=source.get('records',[])
    if not receipts or len({r['track_id'] for r in receipts})!=len(receipts):
        raise ValueError('Receipt records missing or duplicated')
    if source['summary'].get('approved_for_similarity') != 0:
        raise ValueError('Explorer is limited to unapproved research evidence')
    values={r['track_id']:{} for r in receipts}
    feature_meta={}
    reader=csv.DictReader(io.StringIO(csv_path.read_text(encoding='utf8')))
    for row in reader:
        tid,feature=row['track_id'],row['feature']
        if tid not in values or feature not in LABELS or feature in values[tid]:
            raise ValueError('Unknown or duplicate descriptor')
        if row['review_state']!='UNAPPROVED':
            raise ValueError('Publication clearance state mismatch')
        raw=row['source_value']
        if raw:
            if row['source_report_parity'] != 'True':
                raise ValueError('Raw source / summary parity failure')
            value=float(raw)
            if not math.isfinite(value):
                raise ValueError('Nonfinite numeric descriptor')
        else:
            value=None
        values[tid][feature]=value
        md={'key':feature,'label':LABELS[feature],'source_path':row['source_path'],'unit':row['unit']}
        if feature in feature_meta and feature_meta[feature]!=md:
            raise ValueError('Feature metadata inconsistent')
        feature_meta[feature]=md
    tracks=[]
    for r in receipts:
        if set(values[r['track_id']])!=set(LABELS):
            raise ValueError('Missing feature rows for '+r['track_id'])
        if r.get('approved_for_similarity') or r.get('master_identity_verified'):
            raise ValueError('Found approved source in unapproved-only explorer')
        tracks.append({k:r.get(k) for k in ('track_id','song','album','pilot','selected_mbid','source_title','source_album','source_duration_seconds','codec','lossless','bit_rate','essentia_version','raw_lowlevel_sha256','qa_flags')} | {'values':values[r['track_id']]})
    payload={'status':'EXPLORATORY_UNAPPROVED','summary':source['summary'],'features':[feature_meta[f] for f in LABELS],
             'tracks':tracks,'provenance':{'receipts_sha256':digest(receipt_path),'observations_sha256':digest(csv_path)}}
    js=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    text=template.read_text(encoding='utf8')
    if '/*AUDIT_PAYLOAD*/' not in text:
        raise ValueError('Required template placeholder not present')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(text.replace('/*AUDIT_PAYLOAD*/',js),encoding='utf8')
    summary=[]
    for feature in LABELS:
        a=[t for t in tracks if t['values'][feature] is not None]
        by_codec=[t['values'][feature] for t in a if t['lossless'] is True]
        other=[t['values'][feature] for t in a if t['lossless'] is False]
        summary.append({'feature':feature,'observed_n':len(a),
          'median_raw':median(t['values'][feature] for t in a) if a else '',
          'lossless_n':len(by_codec),'lossless_median_raw':median(by_codec) if by_codec else '',
          'lossy_n':len(other),'lossy_median_raw':median(other) if other else ''})
    with output.with_name('source_descriptor_strata.csv').open('w',newline='',encoding='utf8') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    return {'tracks':len(tracks),'measured':sum(bool(t['selected_mbid']) for t in tracks),
        'missing':sum(not t['selected_mbid'] for t in tracks), 'feature_count':len(LABELS),
        'source_versions':source['summary'].get('essentia_versions'), 'output':str(output)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--qa-dir',required=True,type=Path)
    ap.add_argument('--template',type=Path,default=Path(__file__).resolve().parent.parent/'templates'/'evidence_explorer.html')
    ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args()
    print(json.dumps(build(a.qa_dir,a.template,a.output),indent=2))
if __name__=='__main__':main()
