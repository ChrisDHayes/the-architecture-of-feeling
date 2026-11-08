# V3 research staging — The Architecture of Feeling Catalogue Evidence Atlas

**Purpose:** Transform the five-batch, 142-song historical MusicBrainz/AcousticBrainz acquisition into a **167-entry research coverage and source-quality inspection**. Do **not** turn the available acoustic values into a verified sonic-family dendrogram, album-evolution narrative, or emotion model without separate source/master and extractor sensitivity review.

## Flow, without a second network sweep

1. GitHub Action `Depeche Mode full-catalogue acoustic evidence discovery` runs its five album batches once and archives each batch's raw precomputed JSON, source receipts, and candidate statuses.
2. A **separate** `Build full-catalogue evidence atlas from completed acquisition` workflow triggers after successful completed main-branch acquisition. It also runs on updates to its own science-review scripts and template, using the latest **already successful** acquisition artifact, and may be dispatched manually with an optional completed run ID.
3. It downloads those **existing** batch artifacts using the short-lived workflow token and re-runs the 167-entry registry reconciliation. No additional MusicBrainz or AcousticBrainz calls are made.
4. For every selected additional source, the builder checks the exact raw JSON file SHA-256 against its acquisition receipt, source recording MBID, track and album tags, source codec, source length and Essentia version. Each of ten named raw-descriptor paths must reconcile to the acquisition report. Missing values and quality warnings are retained; no imputation or default master approval is permitted.
5. The workflow writes an offline interactive atlas and source-quality CSV, plus a complete 167-entry status index, into **one downloadable GitHub Actions artifact**. It does not commit raw JSON or the atlas into the public research site.

## Information design

The atlas starts with the evidence question, then offers a 15-album coverage view with four unambiguous categories:

- **New provisional acoustic candidates** from the 142-entry extension.
- **Existing 25-song research** — separately acquired; not silently merged into the extension.
- **Unresolved** historical recording candidates (including unavailable API data, wrong album versions and out-of-scope source files).
- **Outside the 2022 archive submission window** — all twelve 2023 *Memento Mori* tracks.

A filterable 167-song inventory allows an interested reader to inspect source receipts and the ten observed raw descriptor values. The numeric fields are original-source measurements, **not** a normalized or causally interpretable 12-feature contract. No phonographic audio or lyrics are hosted.

## Evidence boundaries and review gates

- The 167-entry catalogue is **166 core studio album tracks and one edition-specific extension**. These source entries are metadata, not a complete 167-song measured dataset.
- Title/album tags, a lossless codec and source MBID are useful screening evidence, but are **not proof of a particular studio master, edition, or track boundary**.
- AcousticBrainz extractor-version and codec differences may introduce nonmusical differences. Repeated source submissions and version alternatives must be tested before computing distances.
- The 2023 recordings cannot have historic AcousticBrainz submissions after the 2022 closure. A future rights-cleared, reproducible audio-feature extractor is a separate data source and should not be mixed into this archive without a formal comparability plan.
- A six-song pilot cannot justify conclusions about 15 albums. V2.9 remains the locked creative/synthetic exhibit; V3 measured semantics are developed separately.
- The generated atlas is research-only. Before promoting it into GitHub Pages, review the source-quality results, coverage/missingness, accessible interactions and all output claims.

## Offline tests

`python research/catalogue/tools/test_catalogue_evidence_atlas.py` uses synthetic **test fixtures**, never representative musical data. It checks 167-registry integrity, source parity, safe file paths, hash mismatch protection, scientific approval gates and complete-batch requirements. The builder was also tested locally on the **actual first-batch GitHub Actions artifact**, which contained 26 provisional low-level candidates from 29 additions, with complete source-descriptor parity for those 26. That first-batch outcome is not a complete catalogue result.

The postprocessing workflow has a narrow `push` trigger for its own scripts and template and reuses the latest successful acquisition run; it **never** re-queries the archive. The separate acquisition workflow's push filter must remain scoped to changes in the 167-song registry and actual collector, not downstream visualization files. The original five-batch collection remains the authoritative acquisition source.
