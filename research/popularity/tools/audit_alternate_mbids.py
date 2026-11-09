#!/usr/bin/env python3
"""Research alternate MusicBrainz recording IDs; never overwrite selected-MBID nulls."""
import csv,json,time,datetime,urllib.parse,urllib.request,re,argparse
from pathlib import Path
SONGS={'Home':'Ultra','Personal Jesus':'Violator','The Bottom Line':'Ultra'}
AGENT='ArchitectureOfFeelingResearch/1.4 (https://github.com/ChrisDHayes/the-architecture-of-feeling)'
def norm(x):return re.sub('[^a-z0-9]','',str(x).lower())
def fetch(title):
 q=urllib.parse.urlencode({'query':f'recording:"{title}" AND artist:"Depeche Mode"','fmt':'json','limit':100})
 req=urllib.request.Request('https://musicbrainz.org/ws/2/recording/?'+q,headers={'User-Agent':AGENT,'Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=35) as r:return json.load(r)
def popularity(ids):
 req=urllib.request.Request('https://api.listenbrainz.org/1/popularity/recording',data=json.dumps({'recording_mbids':ids}).encode(),headers={'User-Agent':AGENT,'Accept':'application/json','Content-Type':'application/json'},method='POST')
 with urllib.request.urlopen(req,timeout=30) as r:body=json.load(r)
 if len(body)!=len(ids) or {x['recording_mbid'] for x in body}!=set(ids):raise ValueError('ListenBrainz identity mismatch')
 return {x['recording_mbid']:x for x in body}
def run(data):
 out={'schema':'aof.alternate-recording-audit.v1','acquired_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'musicbrainz_source':'https://musicbrainz.org/ws/2/recording/','listenbrainz_source':'https://api.listenbrainz.org/1/popularity/recording','disclaimer':'Alternative recording IDs are not measured counts for selected acoustic-source MBIDs','targets':[]}
 for title,album in SONGS.items():
  row=next(x for x in data if x['title']==title)
  results=fetch(title);options=[]
  for x in results.get('recordings',[]):
   if norm(x.get('title'))!=norm(title):continue
   names=[a.get('artist',{}).get('name','') for a in x.get('artist-credit',[]) if isinstance(a,dict)]
   if 'Depeche Mode' not in names:continue
   albums=[a.get('title','') for a in x.get('releases',[])]
   options.append({'mbid':x['id'],'title':x.get('title'),'musicbrainz_score':x.get('score'),'disambiguation':x.get('disambiguation',''),'duration_ms':x.get('length'),'releases':albums[:24],'on_target_album':album in albums,'selected_original':x['id']==row['recording_mbid']})
  if not any(x['selected_original'] for x in options):
   options.append({'mbid':row['recording_mbid'],'title':title,'musicbrainz_score':None,'disambiguation':'Original source recording (not found in search result)','duration_ms':None,'releases':[],'on_target_album':False,'selected_original':True})
  options=sorted(options,key=lambda x:(not x['selected_original'],not x['on_target_album'],-int(x['musicbrainz_score'] or 0),x['mbid']))[:100]
  for i in range(0,len(options),40):
   matches=popularity([x['mbid'] for x in options[i:i+40]])
   for x in options[i:i+40]:
    found=matches[x['mbid']];x['listeners']=found.get('total_user_count');x['listens']=found.get('total_listen_count')
  out['targets'].append({'title':title,'album':album,'selected_mbid':row['recording_mbid'],'candidates':options,'reported_alt':sum(x['listeners'] is not None and not x['selected_original'] for x in options)})
  print(title,'candidate recording IDs',len(options),'reported alternate IDs',out['targets'][-1]['reported_alt'])
  time.sleep(1.2)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--crosswalk',required=True);p.add_argument('--out',required=True)
 a=p.parse_args()
 with open(a.crosswalk,encoding='utf8',newline='') as f:data=list(csv.DictReader(f))
 assert len(data)==147
 result=run(data)
 dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 for t in result['targets']:
  print('TOP ALTERNATIVES FOR',t['title'])
  for x in sorted(t['candidates'],key=lambda z:z['listeners'] or -1,reverse=True)[:7]:print(x['mbid'],x['listeners'],x['listens'],x['on_target_album'],x['disambiguation'][:50])
