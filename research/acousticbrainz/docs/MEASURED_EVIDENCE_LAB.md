# Measured Evidence Lab — pilot research workbench

**Research state:** exploratory source-data inspection only. **Not** a musicological conclusion, a master-approved sonic fingerprint, a mood model, or a V2.9 update.

## Why this exists
The next defensible step after retrieving AcousticBrainz candidate data is to make evidence quality, provenance and missingness legible. This workbench visualizes source observations rather than inventing normalized values or computing musical distances. Its central question is: *How comparable is the evidence before we claim that two songs sound alike?*

## Actual source run
The input for the prototype is [GitHub Actions run #5](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42450888638), produced after PR #7 was merged on November 8, 2026. The run completed successfully and produced:
- **23/25** candidate low-level and high-level source observations, each with ten reconciled low-level descriptor fields.
- **5/6** pilot source observations.
- **16** tagged lossless and **7** lossy submissions; **two 128-kbps MP3 concerns** (*Barrel of a Gun*, *It's No Good*).
- **Two** extractor versions (Essentia 2.1-beta1 and 2.1-beta2).
- Missing acceptable album-version selections for *Enjoy the Silence* and *I Feel You*. The retrieved *I Feel You* alternative is tagged to *The Singles 86>98* instead of *Songs of Faith and Devotion*.

A successful download/metadata parity check does **not** independently verify a studio master or uniform source quality.

## Generated research artifact
Run the existing GitHub Actions workflow, which now:
1. Collects and reviews candidate source JSON once.
2. Runs measured QA and its regression tests.
3. Runs the new five-case offline explorer tests.
4. Generates `evidence_qa/Measured_Evidence_Lab.html` and `evidence_qa/source_descriptor_strata.csv` inside the **same downloadable artifact**.
5. Never commits raw audio, source JSON, or measured dataset to `main`.

The HTML is standalone/offline, includes 25-song (or scoped pilot) coverage, single-descriptor dot plots, quality/extractor filters, source-ledger table, raw JSON SHA-256 receipts, and distinct missing states. The CSV provides raw descriptive medians stratified by reported losslessness, without asserting the difference is caused by compression.

### Local reproduction
```bash
python research/acousticbrainz/tools/test_evidence_explorer.py
python research/acousticbrainz/tools/build_evidence_explorer.py \
  --qa-dir research/acousticbrainz/results/github_run/evidence_qa \
  --output research/acousticbrainz/results/github_run/evidence_qa/Measured_Evidence_Lab.html
```

## Scientific contract
- Ten source descriptors retain documented original units. Visual x-axis rescaling is **only presentation geometry**, not a stored transformed measurement.
- The metadata tags and source measurements come from the *submitted file*, not an independently verified master.
- Source codec is a quality flag; lossless alone does not confirm master identity or eliminate mastering differences.
- The workbench never converts high-level classifier outputs into human emotion labels; it does not calculate distances, nearest neighbours or dendrograms.
- Earlier locked V2.9 remains untouched. The 25-song acoustic research registry currently uses *Barrel of a Gun* instead of *Wagging Tongue*; the original curated editorial set is a separate publication object.

## Next scientific gate
1. Resolve the exact album references for *Enjoy the Silence* and *I Feel You*; reject live/single/compilation variants unless explicitly modelled as distinct versions.
2. Assess source duration, mastering, lossy codec, and extractor-version effects before any cross-recording metric comparison.
3. Pre-register feature families, scaling, half-/double-tempo handling, distance metrics and sensitivity design.
4. Compare multiple authorized editions of the same recording where available. Do not infer causal effects of compression or album era from the descriptive strata.
5. Only after full-corpus validation across **all 15 studio albums** should the measured Sonic DNA tree support catalogue-wide arguments.

## Regression evidence
- 5 offline generator tests passed locally (valid source observations, duplicate IDs, unapproved-only gate, parity fail closed, HTML metadata escaping).
- Chromium desktop and mobile tests passed for the standalone HTML, including feature selection, pilot/lossless filters, selecting source receipts, theme switching, no JS exceptions and no document-level overflow. Tests used `page.set_content`; GitHub Pages and production accessibility have **not** been validated.
