# The Architecture of Feeling — V3.2 Listener Reach / Album-Version Bridge

**Author:** Christopher Hayes · **Source snapshot:** 9 November 2026 · **Status:** source-linked exploratory public exhibit

## Why this edition exists

The measured Sonic DNA dendrogram groups 147 archival Depeche Mode recording candidates using ten acoustic descriptors. V3.2 adds a second, independent variable: how often each *MusicBrainz recording* has been heard by users who contribute listening history to ListenBrainz. **Listeners do not determine clustering.** The outer radial bars are rendered with a logarithmic presentation scale and can switch between unique listeners and total submitted listens.

## 147-song coverage, without invented counts

The [successful original 147-recording audit](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42719376842) recorded exact-source ID counts for **144** songs. Three selected acoustic recording IDs returned null for both listener metrics. A separate [MusicBrainz and ListenBrainz alternative-ID audit](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42722017809) found independently reported, album-linked alternate recordings for those songs:

| Song | Acoustic recording ID (still null in source audit) | Counted album recording ID | Unique listeners | Total listens | Album evidence |
|---|---|---|---:|---:|---|
| Personal Jesus | `bbbc7e9e-0bd8-4a12-a7a5-9a1c9bb6f52d` | `695d0c34-e5da-4f0a-b27c-67ae9ae0e8f4` | 133,918 | 1,232,780 | *Violator*; MusicBrainz 'album version' |
| Home | `42f01cf7-2fdc-4f22-bf08-58e791ffdb22` | `9dd8ea73-de16-449b-93a6-b6b775231bdb` | 47,782 | 406,949 | *Ultra*; MusicBrainz 'album version' |
| The Bottom Line | `2f42e6c7-beb9-4983-9dc9-25180e8e3e36` | `d5fe2bd9-365d-46c2-b949-91bb51d30286` | 25,049 | 146,706 | *Ultra*; MusicBrainz matching studio-album release |

**These are observed counts for different MBIDs, not imputed counts for the acoustic IDs, and not three world-wide song totals.** We deliberately retain the original three nulls in the embedded `REACH32` snapshot, then overlay a separate `ALBUM_PROXY32` crosswalk with each alternate MBID and provenance. The three alternate-ID proxy bars are **blue and dashed**; all 144 exact-ID bars are warm neutral. The song inspector links to the counted MusicBrainz recording.

The *Home* finale, personal narrative, V3.1 acoustic tree algorithm, 167-entry catalogue and all source acoustic descriptor values are preserved. A successful match to an album name is not proof that the waveform or mastering is identical to a particular audio edition.

## Data and rights

- ListenBrainz [popularity/recording API](https://listenbrainz.readthedocs.io/en/latest/users/api/popularity.html) — recording-level `total_user_count` and `total_listen_count`, with nulls for unreported recording MBIDs. Contributor-based usage data are published under CC0.
- MusicBrainz [recording search API](https://musicbrainz.org/doc/MusicBrainz_API/Search) — candidate recording IDs, titles, credits, release associations, and disambiguation notes.
- Exact-ID source: successful [GitHub Actions run 42719376842](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42719376842), artifact `listenbrainz-147-recording-popularity-4`.
- Alternate-ID audit: successful [run 42722017809](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42722017809), artifact `alternative-recording-research-1`.
- Publication crosswalk: `research/popularity/data/v32_listener_reach_147_provenance.csv` (complete 147-row audit with both source and display MBIDs).

This dataset is **not a streaming census** and cannot establish global fans, lifetime song popularity, number of unique people across versions, live-performance counts, or causation. The top songs may be affected by MusicBrainz recording splits and listen-submission behaviour. Do not sum unique listeners across alternative recording IDs: the same user may appear in more than one recording count.

**Live Endurance remains a separate, preferred future layer** only if documented performance counts can lawfully be acquired and reused. No setlist.fm data or unlicensed audio or lyrics are embedded here.

## What to test

1. In the tree's *Unique listeners* mode, all 147 songs have a bar; exactly three are dashed blue.
2. Select *Home*, *Personal Jesus*, and *The Bottom Line* and confirm the correct alternate-ID disclosure and MusicBrainz link.
3. Change to *Total listens*, switch the overlay off/on, adjust the rhythm/timbre/harmony/dynamics weights, and change from 147 to 103 lossless-only candidates. No audience metric may affect acoustic branching.
4. Check desktop and mobile layout; the *Home* ending and official video remain functional.
5. Keep V3.1 and V2.9 as separate rollback editions and do not overwrite the earlier recorded snapshot.

## Independent QA scope

Chromium headless desktop 1440px and mobile 390px validated: 147 visible radial bars, 3 alternative-ID markers, source selection and counts, mode switching, *Home* finale present, no browser JavaScript errors, and no horizontal page overflow. This is not formal WCAG evaluation or a certification of recording master identity.
