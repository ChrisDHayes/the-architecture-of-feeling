# The Architecture of Feeling — Full-Catalogue Acoustic Evidence, November 8, 2026

**Author:** Christopher Hayes  
**Evidence state:** Preliminary, source-linked candidate retrieval. **No album master verified. No catalogue-wide sonic similarity or affective inference approved.**

## What was actually completed

The five-batch [catalogue acquisition run](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42454571883) finished successfully. Its combined output reconciles the **167 V2.9 catalogue entries** (166 core studio tracks and one edition-specific extension) to **25 earlier research-registry entries** and **142 additional entries**.

| Population or evidence state | Count | Interpretation |
|---|---:|---|
| Historical candidates newly searched | 130 | Released before AcousticBrainz submission cutoff |
| New provisional source observations retrieved | 124 | Available archive measurements, not independently verified master recordings |
| New eligible searches unresolved | 6 | No suitable album-aligned candidate selected; not proof of archive absence |
| Post-2022 archive window | 12 | 2023 *Memento Mori* tracks require a separate, appropriately licensed method |
| Older 25-song research registry | 25 | Acquired and validated separately; this full-catalogue run does not re-query them |
| Older 25-song recordings retrieved in its last confirmed run | 24 | Provisional candidate data, including outstanding identity/quality concerns |
| Provisional observations from both non-overlapping acquisition runs | 148 | **Not** a combined, master-verified or harmonized 148-song feature dataset |
| Approved for musicological comparison | **0** | Master identity and comparability remain open |

## What the additional 124 source receipts reveal

- **87** retrieved source files are tagged lossless, with matching song/album/recording-ID metadata and ten reconciled source descriptors. This is encouraging source quality, **not master certification**.
- **37** source files are lossy. Of these, **19** trigger the low-bitrate quality rule (reported bit rate below 192 kbps).
- The extractor metadata spans **Essentia 2.1-beta1 (100)** and **Essentia 2.1-beta2 (24)**. Treat any apparent sonic differences as confounded until extraction-version sensitivity is studied.
- All **124** selected new candidates reconcile ten raw descriptor values to the original source JSON and raw-file SHA-256 hashes. That proves reported-value integrity within the submitted source, not edition equivalence.
- The complete acquisition has been reviewed in a separate [automatic GitHub evidence-atlas run](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/workflows/catalogue-evidence-review.yml). That workflow reuses the archived batch files and does not re-query the music archives.

## Six unresolved historical tracks

| Song | Intended studio album | Current obstacle |
|---|---|---|
| New Life | Speak & Spell | Submitted source album identity incompatible |
| Just Can't Get Enough | Speak & Spell | Submitted source album identity incompatible |
| The Meaning of Love | A Broken Frame | Submitted source album identity incompatible |
| Freelove | Exciter | Submitted source album identity incompatible |
| Wrong | Sounds of the Universe | Submitted source album identity incompatible |
| Miles Away / The Truth Is | Sounds of the Universe | No exact album-linked recording candidate in current MusicBrainz search |

None should be represented with invented features or substituted live/compilation audio. The prior 25-song research set also has unresolved master and version issues. These form a separate review queue and must not be conflated with the six new misses.

## Research implications

**1. Coverage is not validity.** We have substantially improved our ability to *observe* songs acoustically. That does not establish that different files are technically or scientifically comparable.

**2. Production and provenance can masquerade as artistic evolution.** Mastering, reissues, codec and extractor differences could affect relationships across the 15 albums. The next model must use sensitivity analyses and cannot treat observed sonic clustering as an intrinsic fact about the music without those controls.

**3. A missing observation is an analytical state, not a zero.** The six unresolved historical tracks and the 12 post-archive songs should remain visually explicit. They should not collapse into a synthetic average or an undifferentiated category.

**4. The 25/142 boundary is an explicit integration gate.** The older 25-song workbench and the 142-entry extension share a research intent but have separate audit artifacts. Crosswalk, source selection and extraction comparability must be audited before creating one 167-row measured feature matrix.

**5. The human dimension remains a different layer of evidence.** Acoustic descriptors cannot establish whether a track is emotionally dark, profound, comforting or culturally enduring. Those claims require appropriately designed interpretive/qualitative evidence.

## Reproducibility and next gates

- [Completed five-batch acquisition](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42454571883) — original low/high-level precomputed files retained in Actions batch artifacts, currently configured for 30-day retention.
- [Postprocessing workflow](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/workflows/catalogue-evidence-review.yml) — produces `Catalogue_Evidence_Atlas.html`, `catalogue_source_review.csv` and `catalogue_evidence_atlas.json`, with 90-day artifact retention.
- [Research source and methodological contract](https://github.com/ChrisDHayes/the-architecture-of-feeling/blob/main/docs/CATALOGUE_EVIDENCE_ATLAS.md).

**Recommended next steps:** resolve the six new identity gaps and older pilot source exceptions; prioritize 19 low-bitrate submissions for alternatives; document per-source extractor and edition provenance; pre-register a normalization/sensitivity plan; and design a rights-cleared extraction path for 2023 recordings. Keep V2.9 as the locked synthetic creative edition; V3 data-driven interpretations remain separate until they pass these gates.

**Rights note:** No Depeche Mode sound recordings or protected lyrics are provided by this research artifact. Historical AcousticBrainz precomputed descriptors are used subject to their source terms; submitted recordings themselves are not redistributed.
