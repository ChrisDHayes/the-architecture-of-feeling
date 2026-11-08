#!/usr/bin/env python3
"""Build V3.0 research preview from locked V2.9 and verified GitHub Actions evidence.

Source values are candidate-level AcousticBrainz CC0 descriptors, NOT verified masters.
Never substitute synthetic psychological axes or claim measured similarity.
"""
import csv, io, json, math, re, hashlib, zipfile, argparse, collections
from pathlib import Path

FEATURES={
 'rhythm.tempo':('Estimated tempo','BPM','rhythm.bpm'),
 'rhythm.onset_density':('Onset rate','onsets/sec','rhythm.onset_rate'),
 'rhythm.beat_histogram_peak_spread':('Beat histogram spread','source units','rhythm.bpm_histogram_first_peak_spread.mean'),
 'timbre.spectral_centroid':('Spectral centroid','Hz','lowlevel.spectral_centroid.mean'),
 'timbre.spectral_flux':('Spectral flux','source units','lowlevel.spectral_flux.mean'),
 'timbre.barkbands_flatness_db':('Bark-band flatness','source units','lowlevel.barkbands_flatness_db.mean'),
 'harmony.hpcp_entropy':('Pitch-class entropy','source units','tonal.hpcp_entropy.mean'),
 'harmony.tonal_change_candidate_proxy':('Chord change rate (proxy)','source units','tonal.chords_changes_rate'),
 'dynamics.loudness':('Algorithmic average loudness','source units','lowlevel.average_loudness'),
 'dynamics.dynamic_complexity':('Algorithmic dynamic complexity','source units','lowlevel.dynamic_complexity'),
}

STYLES=r"""
/* V3.0 evidence integration -- separate from the archived original V2.9 */
.v3-banner{border:1px solid var(--accent);padding:13px 19px;margin:12px 0 23px;background:var(--raised);color:var(--ink);font:13px/1.7 inherit}
.v3-banner strong{color:var(--accent)}.v3-banner a,.v3-evidence a{color:var(--accent);text-underline-offset:4px}
.v3-evidence{padding:45px clamp(20px,5vw,75px) 70px;border-block:1px solid var(--border);background:var(--bg);color:var(--ink)}
.v3-width{max-width:1200px;margin:auto}.v3-kicker{color:var(--accent);letter-spacing:.17em;text-transform:uppercase;font-size:11px;font-weight:750}
.v3-evidence h2{font-size:clamp(35px,6vw,69px);line-height:1.08;letter-spacing:-.05em;font-weight:540;margin:15px 0}
.v3-evidence p{color:var(--muted);line-height:1.7;font-size:14px;max-width:940px}.v3-stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:28px 0}
.v3-stat{border:1px solid var(--border);background:var(--raised);padding:18px 12px}.v3-stat strong{font-size:clamp(21px,3vw,33px);display:block;line-height:1.2}.v3-stat span{font-size:11px;color:var(--muted)}
.v3-controls{display:grid;grid-template-columns:minmax(140px,1.15fr) minmax(150px,.8fr) minmax(175px,1fr) minmax(140px,.7fr);gap:12px;margin:25px 0}
.v3-controls label{display:grid;gap:7px;font-size:12px;color:var(--muted)}.v3-controls select{border:1px solid var(--border);background:var(--raised);color:var(--ink);min-width:0;width:100%;padding:10px;min-height:43px;font:inherit}
.v3-checkboxes{display:flex;flex-wrap:wrap;gap:15px;margin:0 0 20px}.v3-checkboxes label{font:12px/1.5 inherit;color:var(--ink)}.v3-checkboxes input{accent-color:var(--accent)}
.v3-layout{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(250px,.85fr);gap:15px}
.v3-plotbox,.v3-inspect{border:1px solid var(--border);padding:14px;background:var(--raised);min-width:0}.v3-plotbox svg{display:block;width:100%;height:auto;max-height:660px;overflow:visible}
.v3-inspect h3{font-size:22px;font-weight:550;margin:4px 0 10px;line-height:1.2}.v3-inspect dl{display:grid;grid-template-columns:1fr 1.3fr;gap:7px 12px;font-size:12px}
.v3-inspect dt{color:var(--muted)}.v3-inspect dd{margin:0;overflow-wrap:anywhere}.v3-readings{margin-top:18px}.v3-reading{display:grid;grid-template-columns:1fr auto;gap:8px;border-bottom:1px solid var(--border);font-size:11px;padding:7px 0}
.v3-reading span{color:var(--muted)}.v3-reading strong{font-weight:700;font-variant-numeric:tabular-nums}.v3-key{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0 0;font-size:11px;color:var(--muted)}
.v3-key b{border:1px solid var(--border);padding:4px 9px;font-weight:500}.v3-evidence-bars{font-size:12px;line-height:1.55;display:grid;gap:7px}
.v3-evidence-bars>div{border-bottom:1px solid var(--border);padding-bottom:6px}.v3-evidence-bars b{display:block;font-weight:660;color:var(--ink)}.v3-evidence-bars small{color:var(--muted);display:block;font-size:11px}
.v3-unavailable{font-size:12px;color:var(--muted)}
@media(max-width:950px){.v3-layout{grid-template-columns:1fr}.v3-controls{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:650px){.v3-stats{grid-template-columns:repeat(2,1fr)}.v3-controls{grid-template-columns:1fr}.v3-evidence{padding:28px 17px 45px}}
"""

SECTION=r"""
<section class="v3-evidence" id="v3-measured" aria-labelledby="v3-title">
<div class="v3-width">
  <div class="v3-kicker">Act IX · The measured catalogue / exploratory source evidence</div>
  <h2 id="v3-title">What changes when we stop imagining the data?</h2>
  <p>We can measure an acoustic descriptor in an archived submission. We cannot yet conclude that every source file represents the same album edition, mastering, extractor, or listening experience. This exhibit exposes what we retrieved, what remains missing, and the limits of comparison—without turning unverified measurements into emotional claims.</p>
  <div class="v3-stats" aria-label="Catalogue acquisition status"><div class="v3-stat"><strong id="v3SourceCount">148</strong><span>Retrieved source observations</span></div><div class="v3-stat"><strong id="v3Coverage">167</strong><span>Catalogue entries considered</span></div><div class="v3-stat"><strong id="v3Unresolved">19</strong><span>Missing or outside archive window</span></div><div class="v3-stat"><strong>0</strong><span>Independently approved masters</span></div></div>
  <div class="v3-controls">
    <label>Measured descriptor<select id="v3Feature" aria-label="Choose measured descriptor"></select></label>
    <label>Album<select id="v3Album" aria-label="Filter by album"></select></label>
    <label>Submitted-file quality<select id="v3Quality" aria-label="Filter by source quality"><option value="clean">Tag-aligned · lossless</option><option value="all">All retrieved, including flagged</option><option value="lossy">Lossy sources only</option></select></label>
    <label>Feature extractor<select id="v3Extractor" aria-label="Filter extractor version"></select></label>
  </div>
  <div class="v3-layout">
    <div class="v3-plotbox"><svg id="v3Plot" viewBox="0 0 900 555" role="img" aria-labelledby="v3PlotTitle v3PlotDesc"><title id="v3PlotTitle">Source measurements by album</title><desc id="v3PlotDesc">A filtered scatter plot of one original-unit acoustic descriptor, with albums on the vertical axis. These records are not certified comparable masters.</desc></svg><div id="v3PlotCaption" class="v3-key" aria-live="polite"></div><p style="font-size:11px">Horizontal position is an archived descriptor in its original source units, not a normalized emotional score. Vertical groupings identify albums; no evolution, similarity or causal relationship is inferred.</p></div>
    <div class="v3-inspect" aria-live="polite" id="v3Inspector"></div>
  </div>
  <p><strong>What remains illustrative:</strong> The inherited similarity dendrogram, emotional axes, generated waveforms and the 12-feature family model remain synthetic V2.9 demonstrations. They are not derived from the retrieved acoustic evidence. Explore the <a href="../research/acousticbrainz/Measured_Evidence_Lab.html">25-song source laboratory</a> and the <a href="https://github.com/ChrisDHayes/the-architecture-of-feeling/blob/main/docs/CATALOGUE_EVIDENCE_ATLAS.md">catalogue evidence methods</a> for the full acquisition trail.</p>
</div></section>
"""

JS=r"""
(function(){
const D=window.AOF_V3_EVIDENCE;
if(!D || D.status!=='EXPLORATORY_UNAPPROVED')return;
const byId=new Map(D.records.map(r=>[r.track_id,r]));
const byAlbum=new Map(D.albums.map((a,i)=>[a,i]));
const fsel=document.getElementById('v3Feature'),album=document.getElementById('v3Album'),quality=document.getElementById('v3Quality'),extractor=document.getElementById('v3Extractor');
const plot=document.getElementById('v3Plot'),caption=document.getElementById('v3PlotCaption'),inspect=document.getElementById('v3Inspector');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const format=x=>typeof x!=='number'||!Number.isFinite(x)?'Not available':Math.abs(x)>=100?x.toLocaleString('en-CA',{maximumFractionDigits:1}):Math.abs(x)>=1?x.toLocaleString('en-CA',{maximumFractionDigits:3}):x.toPrecision(4);
let focus='a07_t01';
if(!byId.has(focus))focus=D.records[0]?.track_id;
const refs={matched:'Tag-aligned · lossless',lossy:'Lossy · investigate source quality',identity_flagged:'Identity flagged · not comparable',missing:'No accepted archival observation',ineligible:'Archive stopped submissions before this release'};
function selected(){return byId.get(focus)||D.records[0]}
function renderInspector(){
 const r=selected();if(!r)return;
 const hasData=!!r.selected_mbid && r.feature_parity===true;
 const mid=r.selected_mbid;
 inspect.innerHTML='<div class="v3-kicker">Source-linked receipt / '+esc(r.track_id)+'</div><h3>'+esc(r.title)+'</h3><p>'+esc(r.album)+' · '+esc(r.year)+'</p><dl><dt>Evidence category</dt><dd>'+esc(refs[r.category]||r.category)+'</dd><dt>Selected recording</dt><dd>'+(mid?'<a href="https://musicbrainz.org/recording/'+encodeURIComponent(mid)+'" target="_blank" rel="noopener noreferrer">MusicBrainz ID ↗</a>':'Unresolved')+'</dd><dt>Submitted audio</dt><dd>'+esc(r.codec||'Not known')+(r.lossless===true?' · lossless':r.lossless===false?' · lossy':'')+'</dd><dt>Extractor</dt><dd>'+esc(r.extractor||'Not available')+'</dd><dt>Source descriptor parity</dt><dd>'+(r.feature_parity===true?'10/10 checked':r.feature_parity===false?'Not approved for source comparisons':'No source')+'</dd><dt>Master verified</dt><dd>NO</dd></dl>'+
 (r.flags.length?'<p style="color:var(--accent)"><strong>Review flags:</strong> '+esc(r.flags.join(' · '))+'</p>':'<p>Source metadata is tag-aligned; recording master still requires independent review.</p>')+
 '<div class="v3-readings">'+D.features.map(f=>'<div class="v3-reading"><span>'+esc(f.label)+'</span><strong>'+(hasData?format(r.values[f.key])+' '+esc(f.unit):'No accepted observation')+'</strong></div>').join('')+'</div>'+
 '<p style="font-size:11px">The table displays original-unit values from submitted audio. Neither this receipt nor a MusicBrainz association establishes exact studio-master identity or cross-song scientific comparability.</p>';
}
function v3Fill(){
 fsel.innerHTML=D.features.map(f=>'<option value="'+esc(f.key)+'">'+esc(f.label)+'</option>').join('');
 album.innerHTML='<option value="all">All 15 studio albums</option>'+D.albums.map(a=>'<option value="'+esc(a)+'">'+esc(a)+'</option>').join('');
 extractor.innerHTML='<option value="2.1-beta1">Essentia 2.1-beta1 (default)</option><option value="all">All versions (descriptive only)</option><option value="2.1-beta2">Essentia 2.1-beta2</option>';
 fsel.value='rhythm.tempo';
}
function plotIt(){
 const F=D.features.find(f=>f.key===fsel.value)||D.features[0];
 const items=D.records.filter(r=>r.selected_mbid&&r.feature_parity===true&&typeof r.values[F.key]==='number'&&Number.isFinite(r.values[F.key])&&
   (album.value==='all'||r.album===album.value)&&
   (extractor.value==='all'||r.extractor===extractor.value)&&
   (quality.value==='all'||(quality.value==='clean'&&r.category==='matched')||(quality.value==='lossy'&&r.category==='lossy')));
 const xvals=items.map(r=>r.values[F.key]), lo=xvals.length?Math.min(...xvals):0,hi=xvals.length?Math.max(...xvals):1,range=hi-lo||1;
 const ax=255,bx=853,top=68,bottom=492;
 const plotX=v=>ax+(v-lo)/range*(bx-ax);
 let out='<rect width="900" height="555" fill="transparent"/>';
 out+='<text x="24" y="28" fill="currentColor" font-size="14">'+esc(F.label)+' · '+esc(F.unit)+'</text>';
 for(let n=0;n<=4;n++){let t=lo+range*n/4,xx=plotX(t);out+='<line x1="'+xx+'" y1="43" x2="'+xx+'" y2="510" stroke="currentColor" stroke-opacity=".17"/><text x="'+xx+'" y="534" text-anchor="middle" font-size="11" fill="currentColor">'+esc(format(t))+'</text>'}
 const albums=album.value==='all'?D.albums:[album.value];
 albums.forEach((name,i)=>{
    const yy=top+(i+.5)*(bottom-top)/Math.max(albums.length,1);
    out+='<text x="245" y="'+(yy+4)+'" font-size="11" text-anchor="end" fill="currentColor" opacity=".75">'+esc(name.length>27?name.slice(0,26)+'…':name)+'</text>';
    out+='<line x1="255" x2="850" y1="'+yy+'" y2="'+yy+'" stroke="currentColor" stroke-opacity=".06"/>';
    const rows=items.filter(r=>r.album===name).sort((a,b)=>a.track_id.localeCompare(b.track_id));
    rows.forEach((r,j)=>{const x=plotX(r.values[F.key]),cy=yy+(j-(rows.length-1)/2)*Math.min(4.5,20/Math.max(1,rows.length)),color=r.category==='matched'?'var(--ink)':r.category==='lossy'?'var(--accent)':'var(--muted)';
      out+='<circle tabindex="0" role="button" data-v3-id="'+esc(r.track_id)+'" aria-label="Inspect '+esc(r.title)+'" cx="'+x+'" cy="'+cy+'" r="'+(r.track_id===focus?7:4.2)+'" fill="'+color+'" stroke="'+(r.track_id===focus?'var(--accent)':'none')+'" stroke-width="2"><title>'+esc(r.title)+' · '+esc(format(r.values[F.key]))+' '+esc(F.unit)+'</title></circle>';});
 });
 if(!items.length)out+='<text x="510" y="280" text-anchor="middle" fill="currentColor" font-size="17">No observations match these evidence filters.</text>';
 plot.innerHTML=out;
 caption.innerHTML='<b>'+items.length+' source candidates shown</b><b>'+D.records.length+' registered catalogue entries</b><b>Single descriptor · original units</b><b>No master-level similarity approved</b>';
 plot.querySelectorAll('[data-v3-id]').forEach(circle=>{
   const choose=()=>{focus=circle.getAttribute('data-v3-id');renderInspector();plotIt()};
   circle.addEventListener('click',choose);circle.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();choose()}})
 });
 renderInspector();
}
for(const el of [fsel,album,quality,extractor])el.addEventListener('change',plotIt);
window.AOF_V3_FOCUS=function(track_id){if(byId.has(track_id)){focus=track_id;renderInspector();plotIt();}};
v3Fill();plotIt();
})();
"""

def safe_norm(x):return re.sub(r'[^a-z0-9]+','',str(x).lower())
def get_path(doc,path):
    for part in path.split('.'):
        if not isinstance(doc,dict):return None
        doc=doc.get(part)
    return doc

def parse_values(doc,report_vals):
    out={}
    for name,(_,__,path) in FEATURES.items():
        actual=get_path(doc,path)
        recorded=(report_vals.get(name) or {}).get('source_value')
        rpath=(report_vals.get(name) or {}).get('source_path')
        if (not isinstance(actual,(int,float)) or not math.isfinite(actual) or
            not isinstance(recorded,(int,float)) or not math.isclose(actual,recorded,rel_tol=1e-8,abs_tol=1e-8)
            or rpath!=path):
            raise ValueError('Missing or irreconcilable field '+path)
        out[name]=float(actual)
    return out

def create_data(registry_csv,baseline_zip,batch_zips):
    with Path(registry_csv).open(encoding='utf-8',newline='') as fh:registry=list(csv.DictReader(fh))
    if len(registry)!=167 or len(set(r['track_id'] for r in registry))!=167:raise ValueError('Invalid 167 registry')
    def blank(row):
        return {'track_id':row['track_id'],'title':row['title'],'album':row['album'],'year':int(row['year']),
                'scope':row['scope'],'selected_mbid':None,'category':'ineligible' if int(row['year'])>2022 else 'missing',
                'flags':[],'codec':None,'lossless':None,'bit_rate':None,'extractor':None,
                'raw_source_sha256':None,'feature_parity':False,'values':{}}
    allr={r['track_id']:blank(r) for r in registry}
    registry_by_id={r['track_id']:r for r in registry}
    seen=set()
    with zipfile.ZipFile(baseline_zip) as z:
        ev=json.loads(z.read('evidence_qa/evidence_receipts.json'))
        report=json.loads(z.read('coverage_report.json'))
        rr={x['track_id']:x for x in report['records']}
        if ev['summary']['song_count']!=25 or len(ev['records'])!=25:raise ValueError('Missing baseline 25')
        for entry in ev['records']:
            tid=entry['track_id'];row=allr[tid]
            if registry_by_id[tid]['in_existing_25_registry']!='true':raise ValueError('Unexpected baseline track '+tid)
            flags=list(entry.get('qa_flags') or [])
            r=rr[tid];mbid=r.get('selected_mbid')
            if not mbid:row['flags']=flags;seen.add(tid);continue
            original=z.read(r['lowlevel_file']);low=json.loads(original)
            values=parse_values(low,r.get('measurement_values') or {})
            if entry['raw_lowlevel_sha256']!=hashlib.sha256(original).hexdigest():
                # The QA hashes are of the collector's JSON file bytes; ZIP carries those bytes.
                raise ValueError('Baseline raw SHA-256 mismatch '+tid)
            tags=low.get('metadata',{}).get('tags',{})
            tags_title=entry.get('source_title') or ''
            tags_album=entry.get('source_album') or ''
            if safe_norm(tags_title)!=safe_norm(row['title']) and 'title_mismatch_or_missing_tag' not in flags:flags.append('title_mismatch_or_missing_tag')
            if safe_norm(tags_album)!=safe_norm(row['album']) and 'album_mismatch_or_missing_tag' not in flags:flags.append('album_mismatch_or_missing_tag')
            identity_bad=any(k in ' '.join(flags) for k in ('mismatch','candidate_not_selected','source_mbid'))
            cat='identity_flagged' if identity_bad else 'matched' if entry.get('lossless') is True else 'lossy'
            row.update(selected_mbid=mbid,category=cat,flags=flags,codec=entry.get('codec'),lossless=entry.get('lossless'),
                bit_rate=entry.get('bit_rate'),extractor=entry.get('essentia_version'),raw_source_sha256=hashlib.sha256(original).hexdigest(),
                feature_parity=True,values=values)
            seen.add(tid)
    if len(seen)!=25:raise ValueError('Baseline 25 incomplete')
    for p in batch_zips:
        with zipfile.ZipFile(p) as z:
            report=json.loads(z.read('coverage_report.json'))
            if report['schema']!='architecture-of-feeling.catalogue-expansion.v1':raise ValueError('Unexpected batch schema')
            for entry in report['records']:
                tid=entry['track_id'];row=allr[tid]
                if tid in seen or registry_by_id[tid]['in_existing_25_registry']!='false':raise ValueError('Overlap '+tid)
                seen.add(tid)
                row['flags']=list(entry.get('quality_flags') or [])
                if not entry.get('selected_mbid'):row['flags'].append(entry.get('status','unresolved'));continue
                source=z.read(entry['lowlevel_file'])
                if hashlib.sha256(source).hexdigest()!=entry.get('lowlevel_sha256'):raise ValueError('Source SHA-256 mismatch '+tid)
                low=json.loads(source);values=parse_values(low,entry.get('observed_features') or {})
                quality=entry.get('submission_quality') or {}
                flags=row['flags'];m=quality.get('source_recording_mbid')
                if not m or m!=entry['selected_mbid']:flags.append('submitted_recording_mbid_missing_or_mismatched')
                if safe_norm(quality.get('source_title'))!=safe_norm(row['title']):flags.append('submitted_title_mismatch')
                if safe_norm(quality.get('source_album'))!=safe_norm(row['album']):flags.append('submitted_album_mismatch')
                bad=any('mismatch' in f or 'missing' in f for f in flags)
                cat='identity_flagged' if bad else 'matched' if quality.get('lossless') is True else 'lossy'
                row.update(selected_mbid=entry['selected_mbid'],category=cat,flags=sorted(set(flags)),
                     codec=quality.get('codec'),lossless=quality.get('lossless'),bit_rate=quality.get('bit_rate'),
                     extractor=quality.get('essentia_version'),raw_source_sha256=hashlib.sha256(source).hexdigest(),
                     feature_parity=True,values=values)
    if len(seen)!=167 or set(seen)!=set(allr):raise ValueError('Full registry join incomplete')
    rows=[allr[r['track_id']] for r in registry]
    cats=collections.Counter(r['category'] for r in rows)
    measured=sum(r['feature_parity'] for r in rows)
    if measured!=148 or cats['ineligible']!=12 or cats['missing']!=7:raise ValueError('Expected documented run7+batch results; got '+str((measured,cats)))
    albums=list(dict.fromkeys(r['album'] for r in registry))
    if len(albums)!=15:raise ValueError('Invalid album scope')
    return {'status':'EXPLORATORY_UNAPPROVED','schema':'architecture-of-feeling.v3.research-preview.v1',
      'source_runs':{'baseline25':42452474436,'catalogue142':42454571883,'atlas':42455739480},
      'method':'Original-unit precomputed descriptors; selected submitted-file sources; no master validation',
      'summary':{'catalogue_entries':167,'source_observations':measured,'unresolved_historical':7,'outside_archive_window':12,
                 'lossless_tag_aligned':cats['matched'],'lossy':cats['lossy'],'identity_flagged':cats['identity_flagged'],'approved_master':0,
                 'source_versions':dict(collections.Counter(r['extractor'] for r in rows if r['extractor']))},
      'albums':albums,'features':[{'key':k,'label':v[0],'unit':v[1],'source_path':v[2]} for k,v in FEATURES.items()],
      'records':rows}

def build(base_path, registry_csv, baseline_zip, batch_zips, output, data_output=None):
    base=Path(base_path).read_text(encoding='utf-8')
    if 'V2.9 NAVIGATION' not in base or 'synthetic_demonstration' not in base or 'id="v3-measured"' in base:
        raise ValueError('Locked original V2.9 baseline not recognized')
    data=create_data(registry_csv,baseline_zip,batch_zips)
    embed=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    if base.count('const DATA = ')!=1:raise ValueError('DATA source not unique')
    base=base.replace('const DATA = ','window.AOF_V3_EVIDENCE = '+embed+';\nconst DATA = ',1)
    # Leave the V2.9 simulated tree and interpretation visibly, explicitly SYNTHETIC.
    import re
    bars=re.search(r'function bars\(t\)\{return featureMeans\(t\).*?\.join\(\'\'\)\}',base,re.S)
    if not bars:raise ValueError('Expected V2.9 feature bar renderer missing')
    bar_fn="""function bars(t){const r=window.AOF_V3_EVIDENCE.records.find(x=>x.track_id===t.id);if(!r||!r.selected_mbid||!r.feature_parity)return '<div class=\"v3-evidence-bars\"><b>Source observation unavailable</b><small>No accepted archival measurement for this catalogue entry. Other visualizations remain synthetic.</small></div>';if(r.category==='identity_flagged')return '<div class=\"v3-evidence-bars\"><b>Source version mismatch — values withheld from song card</b><small>Inspect the evidence chapter for documented source limitations.</small></div>';const keys=['rhythm.tempo','rhythm.onset_density','timbre.spectral_centroid','timbre.barkbands_flatness_db','harmony.hpcp_entropy','dynamics.dynamic_complexity'];return '<div class=\"v3-evidence-bars\">'+keys.map(k=>{const f=window.AOF_V3_EVIDENCE.features.find(y=>y.key===k);return '<div><b>'+f.label+'</b><small>'+Number(r.values[k]).toLocaleString('en-CA',{maximumFractionDigits:3})+' '+f.unit+'</small></div>'}).join('')+'<small>Original-unit AcousticBrainz descriptors · source '+(r.lossless?'lossless':'lossy')+' · '+r.extractor+' · master unverified. Dendrogram/affect views remain synthetic.</small></div>'}"""
    base=base[:bars.start()]+bar_fn+base[bars.end():]
    base=base.replace('EXISTING SYNTHETIC FEATURE FINGERPRINT','SOURCE-LINKED ACOUSTIC DESCRIPTORS · RESEARCH ONLY',1)
    base=base.replace('All audio features are synthetic.','Individual-song descriptors are sourced when available. Similarity tree and emotion charts remain synthetic.',1)
    disclosure='<br><b>Acoustic features:</b> NONE. All displayed feature profiles and clustering relationships are synthetic.'
    if disclosure not in base:raise ValueError('Original disclosure missing')
    base=base.replace(disclosure,'<br><b>Individual-song descriptors:</b> sourced from unapproved AcousticBrainz submitted-file measurements when available. The similarity tree, emotional axes and remaining derived visuals are STILL SYNTHETIC.',1)
    base=base.replace('</style>',STYLES+'\n</style>',1)
    if '<div id="uxResearchAppendix"' not in base:raise ValueError('No research appendix section')
    base=base.replace('<div id="uxResearchAppendix"',SECTION+'\n<div id="uxResearchAppendix"',1)
    # Keep original nav architecture, add dedicated deep-link in the discovery interface.
    if 'href="#album-atlas"' not in base:raise ValueError('No discovery navigation to album atlas')
    base=base.replace('href="#album-atlas"','href="#v3-measured"',1) if False else base
    banner='<div class="v3-banner"><strong>V3.0 · measured research preview:</strong> 148 archived source measurements across 167 catalogue entries. Original-unit descriptors and receipts have been added. The sonic tree, mood axes and generated waveforms are still <strong>synthetic demonstrations</strong>. No studio master has been independently verified. <a href="#v3-measured">Examine the evidence and its limitations</a>.</div>'
    base=base.replace('<section id="opening">','<section id="opening">'+banner,1)
    base=base.replace('</body>','<script>'+JS+'</script>\n</body>',1)
    base=base.replace('V2.9 NAVIGATION EDITION · SYNTHETIC DATA','V3.0 RESEARCH PREVIEW · MIXED MEASURED / SYNTHETIC',1)
    # V2.9 also rewrites its status labels dynamically. Keep the V3 evidence distinction consistent.
    statuses={
      "'V2.9 NAVIGATION EDITION · SYNTHETIC DATA'":"'V3.0 RESEARCH · MEASURED SOURCE / SYNTHETIC STORY'",
      "'V2.9 · SYNTHETIC'":"'V3.0 · MIXED EVIDENCE'",
      "'167 catalogue entries · 15 albums · 25 chosen songs. No real audio features. No copyrighted music embedded.'":"'167 catalogue entries · 148 provisional acoustic source observations. Story and similarity models remain synthetic. No copyrighted audio hosted.'",
    }
    for old,new in statuses.items():
        if old not in base:raise ValueError('Expected dynamic provenance disclosure not found: '+old)
        base=base.replace(old,new)
    base=base.replace('<span class="demo-short">V2.9 · SYNTHETIC</span>','<span class="demo-short">V3.0 · MIXED</span>',1)
    base=base.replace('SYNTHETIC DATA DEMO</span><small>','MIXED EVIDENCE · BETA</span><small>',1)
    base=base.replace('167 catalogue entries · 15 albums · 25 chosen songs. No real audio features. No copyrighted music embedded.',
        '167 catalogue entries · 148 provisional acoustic observations. Synthetic story and comparisons remain labelled. No copyrighted audio hosted.',1)
    base=base.replace("sidePill.textContent=external?'EXTERNAL INPUT · UNVERIFIED':'SYNTHETIC DATA DEMO'",
        "sidePill.textContent=external?'EXTERNAL INPUT · UNVERIFIED':'V3.0 MIXED EVIDENCE · BETA'",1)
    base=base.replace('Research and evidence tools', 'Research and evidence tools',1)
    anchor='<a href="#data-bridge" data-ux-explore="true"><span>↗</span> Data Bridge</a>'
    if anchor not in base:raise ValueError('Expected provenance navigation not found')
    base=base.replace(anchor, '<a href="#v3-measured"><span>↗</span> V3 measured catalogue</a>'+anchor,1)
    base=base.replace('The Architecture of Feeling: personal Depeche Mode scrollytelling with interactive synthetic-data music exhibits. V2.8 Pre-Data Readiness & Pilot Lab.',
        'The Architecture of Feeling V3.0: interactive Depeche Mode editorial investigation with source-linked, provisional acoustic evidence and clearly labelled synthetic storytelling.',1)
    base=base.replace('The Architecture of Feeling · V2.8 Pre-Data Readiness & Pilot Lab','The Architecture of Feeling · V3.0 Measured Research Preview',1)
    if base.count('id="v3-measured"')!=1 or 'EXPLORATORY_UNAPPROVED' not in base:raise ValueError('V3 smoke-check failed')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(base,encoding='utf-8')
    if data_output:
        data_output=Path(data_output);data_output.parent.mkdir(parents=True,exist_ok=True);data_output.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return {'output':str(output),'bytes':output.stat().st_size,'records':len(data['records']),**data['summary'],
            'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--registry',type=Path,required=True)
    p.add_argument('--baseline-zip',type=Path,required=True)
    p.add_argument('--batch-zip',type=Path,action='append',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--data-output',type=Path)
    q=p.parse_args()
    print(json.dumps(build(q.baseline,q.registry,q.baseline_zip,q.batch_zip,q.output,q.data_output),indent=2))
