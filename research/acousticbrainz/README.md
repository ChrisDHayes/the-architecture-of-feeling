# The Architecture of Feeling — AcousticBrainz coverage audit

This is the **research-only** staging area for the 25-song Depeche Mode acoustic evidence audit. The V2.9 interactive experience is **not modified**.

## What this project does

- Registers 25 editorial songs using the project's original track IDs.
- Queries MusicBrainz for candidate recording IDs and flags ambiguous album/version matches.
- Probes AcousticBrainz's historical low-level and high-level JSON endpoints **only when a suitable exact-album candidate can be selected**.
- Stores unmodified received descriptors alongside source IDs, gaps and request statuses, including a CSV and JSON coverage report.
- Never imputes absent measurements, labels live recordings as studio recordings, or fabricates V2.9 normalized features.

## Run the audit

Once this branch is reviewed and the workflow added to `main`, open **GitHub → Actions → AcousticBrainz 25-song coverage audit → Run workflow**, choose `pilot_6` to test the six pilot tracks, and later `all_25`. Download the artifact from the workflow run. GitHub's Actions trigger must exist in the default branch to appear as a dispatchable workflow. This repository may require Actions to be enabled.

## Data readiness and interpretation

- A 2022 archive cannot contain a recording released in 2023, so *Wagging Tongue* is excluded from archival availability checks.
- MusicBrainz recording IDs are not proof of a unique edition/master; candidates must undergo independent review.
- AcousticBrainz submission availability is unknown until an actual successful network response. A network error is **not** evidence of absence.
- The acoustic descriptors are not yet V2.9's twelve 0–1 features. Normalization and methodology validation are separate research gates.
- The *Violator* MusicBrainz recording previously selected for *Enjoy the Silence* includes *Interlude #2: Crucified* and needs particular care.
- No copyrighted audio is stored or redistributed here.

## Key files

- `data/target_25_recordings.csv` — 25-song identity/candidate ledger.
- `tools/audit25.py` — no-dependency Python collector.
- `tools/test_registry.py` — offline QA.
- `.github/workflows/acousticbrainz-25-audit.yml` — on-demand CI with downloadable evidence.
- Workflow results are **artifacts**, not commits. Avoid checking raw copies into the public project until rights and quality have been reviewed.

Source documentation: [AcousticBrainz API](https://acousticbrainz.readthedocs.io/api.html) · [MusicBrainz recording search](https://musicbrainz.org/doc/MusicBrainz_API/Search/RecordingSearch)

## First real six-song run and quality gate

The first successful GitHub Actions run (2026-11-08, run #1) retrieved low- and high-level AcousticBrainz JSON for five pre-2023 pilot-song candidates. These are precomputed measurements from **submitted files** and **not verified same-master audio**. Inspection of the underlying `metadata.tags` revealed that the selected `Enjoy the Silence` submission is a 7-inch version from *Singles 19–24*, not the intended *Violator* album track; the `It's No Good` submission came from a lossy 128 kbps MP3. The v2 collector now records source-tag identity mismatches, lossiness and codec, and leaves flagged sources unapproved. Retrieved candidate descriptors must not silently activate the 12-feature V2.9 bridge. The direct `lowlevel.spectral_flatness.mean` field used in the first run does not exist in this JSON, so it has been removed in favor of source-present descriptors such as `lowlevel.barkbands_flatness_db.mean` and `tonal.hpcp_entropy.mean`; these are **not** one-for-one substitutes for the original features.

Re-run the existing workflow after merging this patch with `pilot_6`; review `coverage_report.json` and its `submission_quality` fields before expanding to `all_25`.

## Pilot update — World in My Eyes (November 2026)

The `pilot_6` scope now covers **Everything Counts, Never Let Me Down Again, Enjoy the Silence, World in My Eyes, In Your Room, and It's No Good**. *Wagging Tongue* remains one of the complete 25 editorial songs and is still outside the archive's pre-2023 acquisition range, but is **not** included in the six-song AcousticBrainz pilot. This change improves the feasibility of obtaining six historical low- and high-level records.

The selected provisional AcousticBrainz recording candidate for *World in My Eyes* is [26f7bb0d-133d-4811-a8bf-0ff930c5a11a](https://acousticbrainz.org/26f7bb0d-133d-4811-a8bf-0ff930c5a11a), listed as a 4:26 *Violator* track. Its individual submission's source file still requires the edition/codec/quality checks introduced in PR #2; **an artist/album match does not validate the master**. The pilot is driven by the `is_pilot` column of the 25-song registry to avoid maintaining two inconsistent lists.

After merging this change, run GitHub Actions → AcousticBrainz 25-song coverage audit → Run workflow → `pilot_6` on `main`. Check the `submission_quality` verdict for each retrieved low-level record. *Enjoy the Silence* from the first run remains flagged as the wrong edition until replaced. V2.9 remains unchanged.

## Consolidated acquisition — single run (V4)

The audit is now configured to **run automatically once upon merging a change to the acoustic research directory into `main`**. The default run audits all 25 registered songs and writes `coverage_report.json`, `coverage_report.csv`, `musicbrainz_candidates.json`, retrieved source JSON and an additional `pilot_summary.json` summarizing the **six acoustic pilot songs from the same run**. The pilot subset is a view into those results; it does not cause additional network requests. A manual `workflow_dispatch` remains available when deliberately needed; choose `all_25` (default) or `pilot_6` for debugging only.

**Workflow success means retrieval completed, not all recordings passed identity/quality checks.** There is no automatic merging of raw measurements into the exhibition, and the 12-feature normalized V2.9 contract remains unfilled until separately validated. GitHub Actions runs are limited by permissions and service availability; a failing network response is reported as such rather than as a missing recording.

Future research updates should be batched into one reviewed change instead of repeatedly asking for manual pull-request merging. The approved workflow change will itself be merged with the connected GitHub integration and trigger the first automatic all-25 run.

## Candidate resolution batch — after the first complete audit

The automatic 25-song audit run #2 retrieved 7/25 low- and high-level AcousticBrainz records, including 6/6 pilot candidates; the source data identified 14 songs with multiple album-linked MusicBrainz MBIDs and three searches with transient HTTP 503 responses. These are not demonstrated acoustic-archive absences. The earlier direct selection intentionally skipped ambiguous candidates.

The current workflow extends the **same GitHub Actions run** with `tools/resolve_candidates.py`. It reads the first-pass report and candidate list, checks up to four alternative album-linked AcousticBrainz submissions per unresolved or flagged song, records *all attempted candidate statuses and submitted-file metadata* in `candidate_probes.json`, and updates the aggregate report and six-song pilot summary. Temporary MusicBrainz failures get a small, bounded re-query. It does not scrape entire dumps or bulk collections.

Selection is **provisional**, not final identity confirmation. A song may get multiple candidate submissions, including wrong versions or lossy sources. Submitted-file title, album, MBID (when present), filename and basic codec quality are used to rank candidates; preference is given to matching lossless audio. Missing tags, explicit version qualifiers and incorrect albums are flagged rather than silently approved. Song-level descriptors and high-level predictions are retained only with source-identifying metadata and explicit unresolved methodological limitations.

**Publication gate:** Neither the retrieved measurements nor any visualizations should be described as comparable studio-master fingerprints until version selection, extractor comparability and feature normalization pass independent QA. No copyright-protected audio enters the repository and the V2.9 experience remains unchanged.
