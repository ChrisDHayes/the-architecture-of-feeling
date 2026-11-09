# V3.2 — Live Endurance and Listener Reach data contract

**Status: research acquisition / rights review. No live-performance counts are published or hosted.**

## Intended visualization

Keep the existing 147-source measured acoustic dendrogram unchanged. Draw small radial bars outside the song leaves for **Live Endurance** (documented performances); clicking or hovering on a song reveals the reported count, source and date. A secondary lens switches to ListenBrainz *recording-level* unique listeners or total listens, when source coverage is sufficient. Unknown, unmatched or unlicensed metrics remain **missing**, never zero. Popularity must not determine acoustic branching.

For legibility, bars may be transformed using `log1p(count)` and scaled to a common ring length, with **exact untransformed counts** in the details panel. Any normalization is presentation-only and must be labelled. Bars can use a neutral gray and highlight the selected song. The choice of time basis matters: lifetime performance count advantages early songs; a secondary 'eligible concert frequency' would need a documented concert denominator, not just years since release.

## Identity and 147-song source scope

`data/sonic_dna_147_crosswalk.csv` is derived exclusively from the **V3.1 embedded 147-recording cohort**, not scraped or obtained from setlist.fm. It includes track ID, studio album, release year, the existing MusicBrainz recording MBID, sound-source quality, normalized title, and a *proposed* setlist.fm title.

- 143 titles are uncomplicated textual candidates, **not verified live-database matches**.
- Two names need alias review: **Any Second Now (Voices) → Any Second Now** and **Fly on the Windscreen (Final) → Fly on the Windscreen**. These are proposals only.
- Two additional titles with version/medley syntax remain manual-review items: **No More (This Is the Last Time)** and **Soft Touch / Raw Nerve**.
- The older preliminary **117/147** title-match estimate is *not* carried into the dataset as confirmed evidence. It requires a source-authorized reconciliation, and negative hits require review rather than a zero.

## Three measures: availability, rights, semantics

| Measure | Source | Join key | Acquisition status | Meaning |
|---|---|---|---|---|
| Unique listeners | ListenBrainz popularity API | Recording MBID | Auditable via GitHub Actions; results pending run | Number of ListenBrainz users associated with one selected recording MBID |
| Total listens | ListenBrainz popularity API | Recording MBID | Same API and audit | Number of submitted ListenBrainz listens for one selected recording MBID |
| Documented live song performances | setlist.fm | Human-reviewed artist/song identity | **Blocked on reuse rights** | Count of documented performances, not necessarily unique concerts or all performances |

ListenBrainz user listen data are made available under CC0, but those recording-level counts are **not** cross-version song popularity, and they are not a census of all listening services. Null response values stay null. The `recording_popularity.csv` artifact remains separate from the public web edition until source coverage and semantics are reviewed.

setlist.fm [Terms of Use](https://www.setlist.fm/help/terms) restrict automated extraction, storage/retention and redistribution of API data; the standard API requires an issued key, as-is display and attribution. Do **not** scrape the statistics page or embed a static copied song-count table into GitHub Pages based on default terms. Its official [API documentation](https://api.setlist.fm/docs/1.0/index.html) provides registration and key instructions. An approved key **alone does not confer permission to permanently store counts in static HTML**. Public embedding requires a written grant authorizing an aggregated, durable snapshot (or an expressly permitted live server-side integration), plus specified attribution, refresh schedule and commercial/non-commercial scope. A GitHub Actions secret is not a substitute for those rights.

## Authorization request (not sent)

> Subject: Permission to visualize Depeche Mode song-level live-performance counts
>
> I'm creating The Architecture of Feeling, an independent public, non-commercial interactive research exhibit about Depeche Mode's studio recordings. I would like to compare measured acoustic similarity with documented live-performance frequency for approximately 147 songs. May I retrieve song-level performance totals through an approved source and display attributed counts as an interactive radial-bar overlay on a GitHub Pages site? Specifically, do your terms permit retaining a dated, publicly distributed static snapshot of these aggregate counts, refreshing it periodically, and publishing it with a visible setlist.fm credit/link? If not, is there an approved server-side or separately licensed method? Please let me know any applicable attribution, caching, access, commercial-use, or publication limitations. No recorded audio or lyrics would be hosted.

## GitHub integration and validation

- `tools/build_crosswalk.py` regenerates the 147-song source from the V3.1 HTML. The committed CSV is immutable input for the popularity audit until a reviewed schema change.
- `tools/test_popularity.py` runs eight offline regression tests (coverage, uniqueness, aliases, null semantics, response IDs and fail-closed behaviour).
- `tools/audit_listenbrainz.py` calls the official **POST** `/1/popularity/recording` endpoint in four requests of at most 40 MBIDs, with checks for returned ID correspondence and count consistency. It emits a 147-row CSV, a snapshot timestamp and source coverage summary, in a GitHub Actions artifact. It does not connect to setlist.fm or modify the public site.
- Never interpret API failure as zero listening. If the GitHub Actions job cannot start, counts remain **unverified**, even if the code and local tests pass.

## Proposed publication gates

1. Audit percentage of verified, song-aligned live-performance counts; no unreliable zeroes.
2. Obtain the relevant written display/retention rights and archive scope of authorization outside the public repository.
3. Confirm final alias and version mappings and clarify covers, medleys and concert duplicates.
4. Publish a dated count-source receipt next to every bar.
5. Sensitivity-check apparent sonic/popularity relationships across release eras and tree subsets; make no causal claim.
6. Only then update `docs/previews/v3-1-measured-dna/` as a new V3.2 release, keeping V3.1 and the *Home* finale intact.
