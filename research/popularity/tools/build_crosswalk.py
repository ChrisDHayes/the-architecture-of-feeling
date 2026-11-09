#!/usr/bin/env python3
"""Regenerate the 147-row candidate crosswalk from V3.1 source evidence, not setlists."""
import argparse,csv,json,re,unicodedata
from pathlib import Path
FIELDS=["track_id","title","album","year","recording_mbid","source_category","codec","source_lossless","setlist_title_candidate","normalized_title","live_identity_review","live_performance_count_status","unique_listeners_status","total_listens_status"]
ALIAS={"Any Second Now (Voices)":"Any Second Now","Fly on the Windscreen (Final)":"Fly on the Windscreen"}
def slug(s):
    a=unicodedata.normalize("NFKD",s).casefold()
    return re.sub("[^a-z0-9]+","", "".join(c for c in a if not unicodedata.combining(c)))
def build(source,dest):
    text=Path(source).read_text(encoding="utf8")
    m=re.search(r"window\.AOF_V3_EVIDENCE\s*=\s*(\{.*?\});\s*const DATA\s*=",text,re.S)
    if not m:raise ValueError("Embedded acoustic evidence unavailable")
    e=json.loads(m.group(1))
    if e.get("status")!="EXPLORATORY_UNAPPROVED" or len(e["records"])!=167:raise ValueError("Source evidence metadata mismatch")
    rec=[r for r in e["records"] if r["category"] in ("matched","lossy")]
    if len(rec)!=147 or len({r["selected_mbid"] for r in rec})!=147 or len({r["track_id"] for r in rec})!=147:raise ValueError("Expected 147 unique source records")
    out=[]
    for r in rec:
        if r.get("feature_parity") is not True:raise ValueError("Unreconciled source data")
        title=r["title"];proposal=ALIAS.get(title,title)
        review=("ALIAS_PROPOSAL_NEEDS_REVIEW" if title in ALIAS else
            "VERSION_OR_MEDLEY_NEEDS_REVIEW" if ("(" in title or "/" in title) else "TITLE_CANDIDATE_UNVERIFIED")
        out.append(dict(track_id=r["track_id"],title=title,album=r["album"],year=r["year"],
             recording_mbid=r["selected_mbid"],source_category=r["category"],codec=r["codec"],
             source_lossless=str(r["lossless"]).lower(),setlist_title_candidate=proposal,
             normalized_title=slug(proposal),live_identity_review=review,
             live_performance_count_status="NOT_QUERIED_RIGHTS_GATE",
             unique_listeners_status="NOT_QUERIED",total_listens_status="NOT_QUERIED"))
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("w",encoding="utf8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(out)
    return out
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",default="docs/previews/v3-1-measured-dna/index.html")
    p.add_argument("--output",default="research/popularity/data/sonic_dna_147_crosswalk.csv")
    a=p.parse_args();print("Crosswalk records:",len(build(a.source,a.output)))
