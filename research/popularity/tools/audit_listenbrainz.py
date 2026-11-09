#!/usr/bin/env python3
"""Recording-level ListenBrainz audit. Missing counts remain NULL. No setlist.fm access."""
import argparse,csv,datetime,json,re,time,urllib.request
from pathlib import Path
URL="https://api.listenbrainz.org/1/popularity/recording"
MBID=re.compile(r"^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$")
def load(path):
    with Path(path).open(encoding="utf8",newline="") as fh: rows=list(csv.DictReader(fh))
    if len(rows)!=147 or len({r["track_id"] for r in rows})!=147 or len({r["recording_mbid"] for r in rows})!=147:
        raise ValueError("Expected 147 unique source recordings")
    if any(not MBID.fullmatch(r["recording_mbid"]) for r in rows):raise ValueError("Invalid MusicBrainz recording ID")
    if any(r["live_performance_count_status"]!="NOT_QUERIED_RIGHTS_GATE" for r in rows):
        raise ValueError("Live-performance rights gate absent")
    return rows
def fetch(mbids):
    req=urllib.request.Request(URL,data=json.dumps({"recording_mbids":mbids}).encode("utf8"),method="POST",headers={
        "Content-Type":"application/json","Accept":"application/json",
        "User-Agent":"ArchitectureOfFeelingResearch/1.1 (github.com/ChrisDHayes/the-architecture-of-feeling)"})
    with urllib.request.urlopen(req,timeout=25) as response:
        if response.status!=200:raise ValueError("Unexpected response status")
        return json.load(response)
def reconcile(ids,body):
    if not isinstance(body,list) or len(body)!=len(ids):raise ValueError("API response length mismatch")
    result={}
    for row in body:
        mbid=row.get("recording_mbid")
        if mbid not in ids or mbid in result:raise ValueError("Unknown or duplicated recording MBID")
        l,u=row.get("total_listen_count"),row.get("total_user_count")
        if l is None and u is None:state="NOT_REPORTED"
        elif type(l)==int and type(u)==int and l>=u>=0:state="REPORTED"
        else:raise ValueError("Invalid, partial or negative counts")
        result[mbid]=dict(total_listens=l,unique_listeners=u,listenbrainz_status=state)
    if set(result)!=set(ids):raise ValueError("Requested recording ID missing")
    return result
def run(rows,api=fetch,batch_size=40,pause=1.5):
    if not 1<=batch_size<=100:raise ValueError("Batch size out of range")
    cache={}
    for i in range(0,len(rows),batch_size):
        ids=[r["recording_mbid"] for r in rows[i:i+batch_size]]
        cache.update(reconcile(ids,api(ids)))
        if i+batch_size<len(rows):time.sleep(pause)
    if len(cache)!=len(rows):raise ValueError("Partial coverage response")
    return [{k:r[k] for k in ("track_id","title","album","year","recording_mbid","source_category","live_identity_review")} | cache[r["recording_mbid"]] for r in rows]
def save(rows,dest):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    fields=["track_id","title","album","year","recording_mbid","source_category","live_identity_review","unique_listeners","total_listens","listenbrainz_status"]
    with (dest/"recording_popularity.csv").open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    reported=sum(r["listenbrainz_status"]=="REPORTED" for r in rows)
    report={"schema":"aof.listenbrainz.recording-popularity.v1",
        "acquired_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "population":"147 selected recording MBIDs, not all editions of each song",
        "source_api":URL,"recordings_checked":len(rows),"reported":reported,
        "null_not_reported":len(rows)-reported,"coverage_percent":round(100*reported/len(rows),2),
        "semantics":"ListenBrainz site recording-level users/listens, not worldwide streaming popularity",
        "setlist_live_performances":"BLOCKED_PENDING_AUTHORIZATION_FOR_PUBLIC_STATIC_COUNTS",
        "promotion_to_public_site":False}
    (dest/"coverage_summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--crosswalk",required=True);p.add_argument("--output",required=True)
    p.add_argument("--batch-size",type=int,default=40);p.add_argument("--dry-run",action="store_true")
    a=p.parse_args();data=load(a.crosswalk)
    if a.dry_run:
        out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
        report={"dry_run":True,"recordings":len(data),"source_api":URL,"counts_acquired":False}
        (out/"dry_run.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    else:report=save(run(data,batch_size=a.batch_size),a.output)
    print(json.dumps(report,indent=2))
