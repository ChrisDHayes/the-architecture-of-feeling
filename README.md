# The Architecture of Feeling
### Depeche Mode, Decoded · Christopher Hayes

An interactive investigation into sonic identity, the patterns we can measure, and what music means to human listeners.

**Research state:** Creative experience **V2.9 is locked and unchanged**. The acoustic workbench is an independent research preview. Real AcousticBrainz submitted-file descriptors are **not validated studio masters** and are **not approved for acoustic clustering, mood inference, or catalogue-wide claims**.

## Open the interactive experience

**The HTML is in GitHub, but it is not yet a hosted website.** Clicking a file link in GitHub's README opens the **source-code viewer**, not the JavaScript application.

**Run it immediately (no hosting required):**
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

## Automatic publishing

Changes to `research/acousticbrainz/**` on `main` run GitHub Actions. The workflow collects and validates 25-song AcousticBrainz source observations, generates one offline HTML workbench, and **automatically commits only that HTML and its small provenance manifest** to `docs/research/acousticbrainz/`, subject to fail-closed QA gates. Raw low/high-level JSON remains in the timed GitHub Actions artifact and is **not committed into the publishing folder**.

The GitHub automation **stores the HTML in the repository**; that alone does not host it as a website. GitHub Pages (if enabled by the owner) may expose content publicly even from a private repository. **Important:** the bot commit created using the workflow's default `GITHUB_TOKEN` does not trigger a GitHub Pages build; a separate Pages deployment workflow or other approved publishing trigger is required for reliable live-site updates.

The collector's 25-song research registry is distinct from the locked V2.9 editorial collection. No audio or protected lyrics are hosted. Exact versions, master identity and cross-extractor comparability require additional verification.
