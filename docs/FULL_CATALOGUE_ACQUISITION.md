# Full studio catalogue — historical acoustic-data acquisition (research-only)

**Goal:** Expand *The Architecture of Feeling* from the 25-song AcousticBrainz research crosswalk to the 167 catalogue entries present in the approved V2.9 creative experience, **without carrying synthetic data into measurement**.

## What is in scope?

The canonical V2.9 source identifies 15 studio albums, **166 core tracks**, and one edition-specific extension (*But Not Tonight*). The current acoustic 25-song registry overlaps these 167 entries; **142 additional catalogue entries** remain. **130** were released before the AcousticBrainz submissions cutoff (2022), so they are candidates for historical low-level/high-level observation retrieval. The **12 *Memento Mori* tracks (2023)** are outside that historical submission window; do not invent their features or substitute remixes/live sources.

The full catalogue CSV was derived from **V2.9 track metadata only** (`id`, `title`, `album`, `year`, `scope`, `source`); the synthetic `f`, `energy`, `darkness`, `space` values have been excluded. The original source SHA-256 is recorded in `data/catalogue_registry_manifest.json`.

## Five bounded, reproducible album batches

| Batch | Studio albums | New entries | Historically eligible |
|---|---|---:|---:|
| 01 | Speak & Spell; A Broken Frame; Construction Time Again | 29 | 29 |
| 02 | Some Great Reward; Black Celebration; Music for the Masses | 25 | 25 |
| 03 | Violator; Songs of Faith and Devotion; Ultra | 15 | 15 |
| 04 | Exciter; Playing the Angel; Sounds of the Universe | 36 | 36 |
| 05 | Delta Machine; Spirit; Memento Mori | 37 | 25 |
| **Total** | **15 albums** | **142** | **130** |

The GitHub Actions workflow runs these batches serially (`max-parallel: 1`) to limit request bursts. The run is triggered once after these source files are merged into `main`, and can also be invoked manually. It is separate from the existing 25-song audit; the previous 25 are **not** queried twice by this pipeline. Network and download costs follow GitHub account limits. Files are retained as Actions artifacts for limited periods and are **not pushed into the public Pages experience**.

## What the collector does

1. Checks each official-album track candidate by title and Depeche Mode artist credit in MusicBrainz.
2. Considers **only recording MBIDs associated with the named album in returned search records**. Many candidates may share the same composition; an album-linked MBID is not the audio file's master identity.
3. Tries up to four candidate MBIDs per song against the historical AcousticBrainz low-level API. Retains each attempted status and basic source metadata.
4. If a submitted file plausibly matches song and album, retrieves its high-level document and preserves the original source fields, recording MBID, codec, bitrate, duration, quality flags and low-level checksum.
5. Treats all measurements as **provisional**, with `master_identity_verified=false` and `approved_for_similarity=false`. Wrong-album audio and missing data remain visibly unresolved.
6. Combines the 142 new rows with **registry-status references** for the existing 25, producing a 167-entry coverage/missingness inventory. The separate 25-song raw observations are not silently merged or recertified.

**What successful CI does not prove:** a full 167-song measured dataset, exact album master, consistent extractor version, high-level affect, or credible sonic similarity. The UI's synthetic family tree remains illustrative until source/master and statistical sensitivity gates pass. A MusicBrainz or AcousticBrainz HTTP error means **unknown**, not evidence of absence.

## GitHub outputs

Open **Actions → Depeche Mode full-catalogue acoustic evidence discovery**. Each batch produces an artifact named `catalogue-expansion-batch-01` through `-05` containing raw CC0 precomputed JSON and provenance records for the newly queried songs. If all five succeed, `full-catalogue-167-coverage-index` provides a source-safe CSV/JSON inventory, summary, missingness and candidate selection status.

## Sources and data rights

- [MusicBrainz recording API and query rules](https://musicbrainz.org/doc/MusicBrainz_API)
- [AcousticBrainz data and 2022 archive cutoff](https://acousticbrainz.org/download)
- [AcousticBrainz API](https://acousticbrainz.readthedocs.io/api.html)
- [Depeche Mode official album archives](https://archives.depechemode.com/discography/albums/)

AcousticBrainz publicly releases its **precomputed feature data** under CC0; that does not grant rights to redistribute underlying commercial music recordings. No audio is retrieved or committed. For the 2023 album, the alternative is a separate, documented, appropriately authorized audio-extraction process; its data must not be silently blended with the archival feature pipeline.
