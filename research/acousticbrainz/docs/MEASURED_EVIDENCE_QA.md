# Measured Sonic DNA — evidence QA gate (research branch)

This research-only stage consumes the **single-run** AcousticBrainz 25-song archive already produced by GitHub Actions. The V2.9 HTML is unchanged and **no audio, lyrics, or recording masters** enter the repository.

## What the validation checks
- Read the raw low/high-level observation JSON for each selected candidate from the exact same workflow artifact.
- Compare source MusicBrainz recording MBID, album and title tags against the track registry; capture source duration, codec, bit rate, losslessness and Essentia version.
- Recompute ten source descriptor paths from the **raw low-level JSON**, and compare them against the corresponding fields in `coverage_report.json`. Record values in original units with full field-level provenance.
- Record raw JSON SHA-256 hashes; reject path traversal, malformed JSON, duplicate track IDs and inconsistent reported features.
- Identify provenance/quality issues; mark all candidate measurements **UNAPPROVED** for cross-song similarity until exact recording/master, extractor and weighting reviews are complete.

## November 8, 2026 run #4 — observed results
[Source run](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42449701291) (all_25, successful retrieval, not scientific clearance):
- 23 of 25 low-level and high-level observations; 5 of 6 pilot candidates.
- 16 lossless-source files and 7 lossy-source files; *Barrel of a Gun* and *It's No Good* have 128-kbps MP3 flags.
- Two different Essentia versions, 2.1-beta1 and 2.1-beta2.
- *Enjoy the Silence* and *I Feel You* remain unresolved/no selected candidate in this run. Older *Enjoy the Silence* submissions included a single edit; no incorrect substitute should be treated as an album version.
- 23/23 retrieved candidate records showed exact source-path/value parity for the ten currently tracked descriptors in the locally audited artifact. This establishes **data extraction parity**, NOT source mastering, scientific comparability or equivalence with V2.9's twelve-feature visualization contract.

## Pipeline
Run `python research/acousticbrainz/tools/test_measured_evidence.py` for offline checks.
The existing audit workflow will run `validate_measured_evidence.py --artifact-dir research/acousticbrainz/results/github_run --output research/acousticbrainz/results/github_run/evidence_qa` after candidate resolution and before artifact upload.

Generated artifacts:
- `evidence_qa/evidence_qa_summary.json`
- `evidence_qa/evidence_receipts.json`
- `evidence_qa/measured_descriptor_observations.csv`
- `evidence_qa/EVIDENCE_QA_README.md`

These remain part of the temporary GitHub Actions artifact, **not** a source-committed or publication-approved feature dataset.

## Remaining gate
1. Resolve the exact *Enjoy the Silence* album-vs-single recording; investigate *I Feel You*.
2. Verify actual release/edition, track boundaries, mastering and submitted-file identity for all included songs.
3. Assess lossy compression and Essentia-build sensitivity, half/double tempo, track length and dynamic mastering confounding.
4. Define reproducible normalization, descriptive distance measures and uncertainty/sensitivity protocols before any measured clustering.
5. Keep measured acoustic descriptors, model-derived outputs, and listener/human interpretation separate. Do not generalize a six-song pilot to all 15 studio albums.

**Research decisions retained:** CORE-01, CORE-02, CORE-03 and AUD-01. The 25-song acoustic research registry currently includes *Barrel of a Gun* rather than *Wagging Tongue*; its revision is separate from the locked V2.9 editorial experience.
