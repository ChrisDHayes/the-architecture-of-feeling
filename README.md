# The Architecture of Feeling
### Depeche Mode, Decoded · Christopher Hayes

An interactive investigation into Depeche Mode's sonic identity, the patterns we can measure, and the limits of what measurements can tell us about emotion and meaning. This project pairs a locked creative edition with a separate research beta that uses source-linked acoustic evidence to test how far audio descriptors can support claims about musical connection.

The repository is both an artistic exploration and a research archive: it preserves the original V2.9 interactive experience as a fixed creative work, while the V3.0 beta explores how historical acoustic measurements, provenance, and uncertainty can be surfaced without presenting those results as verified scientific claims.

## Public interactive website — owner activation required

The repository includes a [GitHub Pages Actions deployment workflow](.github/workflows/publish-interactive-pages.yml) and a [one-time setup guide](docs/GITHUB_PAGES_SETUP.md). After enabling Pages in the repository settings, the site will publish a public landing page and the interactive editions below.

**The website is not yet confirmed live.** In **Settings → Pages**, select **GitHub Actions** as the deployment source, then run **Actions → Publish The Architecture of Feeling interactive research website**.

## Editions and research progress

**V2.9 — locked creative baseline.** An unchanged, SHA-256 verified copy lives at [V2.9 archived HTML](docs/archive/v2-9/index.html). Its sonic tree, fictional acoustic descriptors, and emotional relationships remain illustrative.

**V3.0 — measured research beta.** [Open the V3.0 HTML experience](docs/previews/v3-measured-beta/index.html) to begin with the source-linked evidence chapter. This preserves the original story while adding measured acoustic descriptors for 148 of 167 catalogue entries, with missingness, codec/extractor filters, and recording receipts. It does not claim that the synthetic tree is measured, nor that archived recordings are independently verified masters.

[Read V3 methods and publication gates](docs/V3_MEASURED_BETA_README.md). V3 is deliberately kept separate from the public homepage until scientific and editorial QA is complete. GitHub's file browser shows HTML source, not the running interactive experience; a Pages deployment is required for a one-click website.

**Research state:** Creative experience **V2.9 is locked and unchanged**. The acoustic workbench is an independent research preview. Real AcousticBrainz submitted-file descriptors are **not validated as studio-master evidence**, and no measured relationship should be treated as publication-grade until further review.

## Open the interactive experience

**The HTML is in GitHub, but it is not yet a hosted website.** Clicking a file link in GitHub's README opens the **source-code viewer**, not the JavaScript application.

**Fastest route to the V3.0 experience:**
1. Open the [V3.0 measured research beta](docs/previews/v3-measured-beta/index.html).
2. Use GitHub's **Download raw file** control in the file toolbar (you may need to open the `...` menu).
3. Save `index.html` locally and open it in Chrome, Edge, Firefox, or Safari.

**Run the evidence lab immediately (no hosting required):**
1. Open the [Measured Evidence Lab HTML file](docs/research/acousticbrainz/Measured_Evidence_Lab.html).
2. Use GitHub's **Download raw file** control in the file toolbar (you may need to open the `...` menu).
3. Save `Measured_Evidence_Lab.html` locally and open it in Chrome, Edge, Firefox, or Safari. It is self-contained and runs offline.

Alternatively, download the `acousticbrainz-25-song-coverage-...` artifact from the [latest successful audit run](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/workflows/acousticbrainz-25-audit.yml) and open `evidence_qa/Measured_Evidence_Lab.html` from the extracted archive.

**A one-click live website requires a hosting deployment.** The [landing-page HTML](docs/index.html) and the generated [Evidence Lab HTML](docs/research/acousticbrainz/Measured_Evidence_Lab.html) are Pages-ready source files, **not confirmed live website URLs**. Do not mistake a GitHub `blob/main/` link for a hosted preview.

To consider GitHub Pages, see [Publishing and access notes](docs/AUTOMATED_RESEARCH_PUBLISHING.md#viewing-and-optional-pages-publishing). Publishing may make the site publicly accessible, including if the repository itself remains private. It requires an explicit visibility decision.

## Other research materials

- [Evidence provenance manifest](docs/research/acousticbrainz/preview_manifest.json) — links the generated HTML to the verified run and evidence checksums.
- [Methods and scientific limits](research/acousticbrainz/docs/MEASURED_EVIDENCE_LAB.md)
- [Automated publication guide](docs/AUTOMATED_RESEARCH_PUBLISHING.md)
- [GitHub Actions acoustic audit](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/workflows/acousticbrainz-25-audit.yml)

## Catalogue-wide acoustic evidence (167 entries)

The separate five-batch MusicBrainz/AcousticBrainz acquisition has now completed. It identified **124 provisional source recordings among 130 additional eligible songs**, plus six unresolved and 12 ineligible entries after source-eligibility checks.

- [Verified full-catalogue findings and six unresolved recordings](docs/CATALOGUE_EVIDENCE_FINDINGS_2026-11-08.md)
- [Run the interactive Catalogue Evidence Atlas](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/workflows/catalogue-evidence-review.yml) — open the latest successful run and download the generated evidence archive.
- [Catalogue evidence methods and scientific controls](docs/CATALOGUE_EVIDENCE_ATLAS.md)

The catalogue atlas is a separate research-only study, not a replacement for locked V2.9 or a live GitHub Pages URL.

## Automatic publishing

Changes to `research/acousticbrainz/**` on `main` run GitHub Actions. The workflow collects and validates 25-song AcousticBrainz source observations, generates one offline HTML workbench, and **stores the result in the repository**.

The GitHub automation **stores the HTML in the repository**; that alone does not host it as a website. GitHub Pages (if enabled by the owner) may expose content publicly even from a private repository. The research registry is distinct from the locked V2.9 editorial collection. No audio or protected lyrics are hosted. Exact versions, master identity, and cross-extractor comparability remain active research questions rather than settled facts.
