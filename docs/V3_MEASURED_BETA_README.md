# The Architecture of Feeling — V3.0 measured research beta

**Status:** exploratory research preview, not a publication-approved acoustic similarity model.  
**Creative baseline:** V2.9, preserved byte-for-byte separately (SHA-256 `3ba59e0030951051bcc4842fb2471b08a306dcb1aa838cdf1a9d06a8166eac21`).

## What is new

The V2.9 narrative, sonic tree and 15-album journey remain intact, while a new chapter introduces actual **AcousticBrainz low-level acoustic descriptors** for selected archival submissions. The six individual-song feature cards now show source-linked acoustic readings where a candidate source passes field-level extraction checks; flagged recording-identity mismatches are withheld there. The full catalogue chapter provides source status, filters by album, basic source quality and extractor version, and shows a recording-level evidence receipt.

## Source coverage and scientific limits

- **167** V2.9 catalogue entries; **148** retrieved source observations, **7** unresolved historical entries, **12** tracks released in 2023 after the AcousticBrainz submission cutoff.
- Among retrieved sources: **103 tag-aligned lossless** candidates; **44 lossy** candidates; **1 identity-flagged** candidate.
- Ten original-unit descriptor values per retrieved recording were checked against the corresponding raw source JSON and acquisition report. This checks **source-data transcription**, not mastering or measurement comparability.
- Essentia extractor versions include 2.1-beta1 and 2.1-beta2. Audio length, track/master identity, lossy compression and feature-extractor version are confounds requiring sensitivity analysis before comparing sonic distances.
- **Zero** masters independently approved. The inherited similarity dendrogram, emotional axes, generated waveforms and other relationships remain **synthetic and illustrative**; do not use them as evidence of sound, emotions, or catalogue evolution.
- Missing or mismatched tracks are not imputed and all recorded MBIDs lead to source identities rather than claiming master certification.

## Source provenance

- Existing 25-song acoustic source audit, [GitHub Actions run #7](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42452474436) — 24 retrieved recordings, 25 registered.
- Five-batch full-catalogue expansion, [GitHub Actions acquisition run](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42454571883) — 124 new historical recordings retrieved for 130 eligible tracks.
- [Full-catalogue evidence review](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42455739480) — provenance and source-quality reporting.
- Reproducible generator: `research/catalogue/tools/build_v3_measured_beta.py`. It expects the original V2.9 HTML, 167-entry registry and the six original GitHub Actions artifacts (one 25-song baseline plus five album batches). The generator refuses missing records, ID overlap, value parity failures, and source-hash mismatches. It does not download or host commercial audio.

## GitHub layout

- `docs/archive/v2-9/index.html`: locked V2.9 baseline. **Do not edit as part of V3 research.**
- `docs/previews/v3-measured-beta/index.html`: distinct V3 research preview.
- `research/catalogue/tools/build_v3_measured_beta.py`: reproducible evidence join/build logic.

This beta is **not** intended to silently replace the public homepage. Promote it only after independent recording/feature quality assessment and an editorial usability review. The repository's current `docs/index.html` is maintained separately.

## Next gates

1. Review flagged and lossy submissions and the seven unresolved historical tracks; 2023 tracks require a separately authorized, comparable feature-extraction process.
2. Compare alternate editions of the same recording, quantify variation from version, codec and Essentia build; decide comparable-analysis cohorts explicitly.
3. Preregister normalization, feature weighting, distance/sensitivity analysis and musical interpretation boundaries. Replace synthetic dendrogram only after passing those gates.
4. Assess visual accessibility (including contrast, keyboard and reduced-motion) and evidence comprehension before calling V3 publication-ready.
