# The Architecture of Feeling
### Depeche Mode, Decoded · Christopher Hayes

An interactive investigation into sonic identity, the patterns we can measure, and what music means to human listeners.

**Research state:** Creative experience **V2.9 is locked and unchanged**. The acoustic workbench is an independent research preview. Real AcousticBrainz submitted-file descriptors are **not validated studio masters** and are **not approved for acoustic clustering, mood inference, or catalogue-wide claims**.

## Open the research materials

- [Research landing page source](docs/index.html) — designed for an optional GitHub Pages site.
- [Latest automatically persisted Measured Evidence Lab](docs/research/acousticbrainz/Measured_Evidence_Lab.html) — once the first publishing run succeeds, this is a browsable file in the connected repository.
- [Provenance manifest](docs/research/acousticbrainz/preview_manifest.json) — links an HTML snapshot to its GitHub Actions run and SHA-256 evidence.
- [Methods and limitations](research/acousticbrainz/docs/MEASURED_EVIDENCE_LAB.md)
- [Automated preview publication guide](docs/AUTOMATED_RESEARCH_PUBLISHING.md)
- [Actions: acoustic evidence audit](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/workflows/acousticbrainz-25-audit.yml)

## Automatic publishing

Changes to `research/acousticbrainz/**` on `main` run GitHub Actions. The workflow collects and validates 25-song AcousticBrainz source observations, generates one offline HTML workbench, and **automatically commits only that HTML and its small provenance manifest** to `docs/research/acousticbrainz/`, subject to fail-closed QA gates. Raw low/high-level JSON remains in the timed GitHub Actions artifact and is **not committed into the publishing folder**.

The GitHub Pages site is **not** enabled by this automation. If the repository owner elects to publish it, GitHub Settings → Pages → **Deploy from a branch → main → /docs** may be available, depending on repository plan/settings and visibility. GitHub Pages may expose content to the public even from a private repository; review that decision and recording/evidence status before enabling.

The collector's 25-song research registry is distinct from the locked V2.9 editorial collection. No audio or protected lyrics are hosted. Exact versions, master identity and cross-extractor comparability require additional verification.
