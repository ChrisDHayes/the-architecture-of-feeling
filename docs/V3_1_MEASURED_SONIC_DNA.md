# The Architecture of Feeling — V3.1 Measured Sonic DNA

**Author:** Christopher Hayes · 9 November 2026

## What changed

V3.1 reuses the complete V3.0 *Home* finale, personal prologue, 167-entry catalogue and **148** AcousticBrainz source observations. It replaces the displayed fictional analysis visualizations with exploratory, source-derived exhibits:

- A radial **measured dendrogram** using average-linkage agglomerative clustering. Default comparison cohort: **147** title/album-tag-aligned archival submitted files (103 lossless-tagged + 44 lossy-tagged); switch to the 103 lossless-tagged cohort to assess sensitivity.
- An interactive **acoustic field** showing two actual source descriptors as selectable axes, rather than inferred listener mood. Display positions are bounded to the 5th–95th observed feature percentiles; tooltips show original source values.
- A ten-descriptor **acoustic signature** for the selected song. Each bar shows its value relative to the source cohort’s 5th–95th percentile range, with a median marker. It is **not** a waveform or time-varying audio trace.
- A measured **album-level overview** of median onset rate per album, using only available source observations.
- Updated evidence-contract text and a small coverage note near the end of the investigation, before the personal *Home* finale.

**All 148 original source observations remain unchanged.** The exceptional source with a documented song/album tag mismatch is retained in the evidence register but excluded from the provisional clustering cohort. Seven historical catalogue entries lack aligned candidate sources; twelve entries released in 2023 fall outside the archival submission window. No features are fabricated to fill these gaps.

## Analytical choices

For each of ten source descriptors, the available 147 source-aligned recordings are standardized with a robust z-score: `(value - median) / (1.4826 × median absolute deviation)`; standard deviation is used only when MAD is zero. Values are capped at ±3 robust SD to prevent extreme points dominating a single feature. The ten descriptors are grouped into rhythm (3), timbre (3), harmony (2), and dynamics (2). Each group contributes its mean squared feature difference weighted by the user's adjustable family weight; distances are the square root of the normalized weighted total. The tree uses **UPGMA / average linkage** to merge source recordings into a provisional descriptor-similarity hierarchy.

This technique produces an **exploratory model**, not a canonical family tree. Relative distances and nearby songs can change with the cohort, feature weights, extractor version, codec and choice of studio master. A lossless codec flag does **not** independently certify a recording master. The acoustic field does **not** measure emotion, and the source summary metrics cannot reconstruct actual audio waveforms or song structure over time.

## What remains untouched

- The SHA-locked V2.9 edition is not modified.
- The original V3.0 *Home* finale and full measured-data payload are preserved. V3.1 is a **separate edition**.
- No commercial sound recording, music video or copyrighted lyrics are hosted. The finale links to the band's official *Home* video on YouTube.

## Open the experience

Open `index.html` or `The_Architecture_of_Feeling_V3_1_Measured_Sonic_DNA.html` in Chrome, Edge, Firefox or Safari. The file contains all required CSS, JavaScript, editorial writing, and measured source observations, and runs offline.

## Quality checks

Chromium desktop and mobile browser tests checked 147/103 candidate cohort switching, slider recalculation, 147 source-linked scatter points, ten measured signatures, album medians, the *Home* finale, keyboard operability and absence of JS exceptions and document-level horizontal overflow. Those checks are not formal accessibility certification or independent master-identity verification.

## Source provenance

- Existing 25-song AcousticBrainz audit (24 retrieved): GitHub Actions run `42452474436`.
- Five-batch catalogue acquisition (124 new retrieved): run `42454571883`.
- Full catalogue source review: run `42455739480`.
- Original V3.0 source file Git blob SHA: `dbb79ca5ed1727c79fa39d0a9ec205149250b389`.
- V3.1 evidence payload is byte-for-byte unchanged from V3.0.
