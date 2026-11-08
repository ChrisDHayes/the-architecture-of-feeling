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
