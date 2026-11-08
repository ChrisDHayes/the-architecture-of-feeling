# The Architecture of Feeling
### Depeche Mode, Decoded · Christopher Hayes

An interactive investigation into Depeche Mode's sonic identity, the patterns we can measure, and what music means to human listeners.

## Open the interactive experiences

**[Open V3.0 — measured research beta](https://chrisdhayes.github.io/the-architecture-of-feeling/previews/v3-measured-beta/)** — hosted interactive version. This link opens the experience directly when GitHub Pages is enabled and its deployment has completed. If it is not live yet, follow the [one-time Pages setup guide](docs/GITHUB_PAGES_SETUP.md) (Settings → Pages → set the source to **GitHub Actions**, then run the publish workflow).

[Open V2.9 — locked creative baseline](https://chrisdhayes.github.io/the-architecture-of-feeling/archive/v2-9/) · [Open the Measured Evidence Lab](https://chrisdhayes.github.io/the-architecture-of-feeling/research/acousticbrainz/Measured_Evidence_Lab.html)

GitHub's file viewer displays HTML source rather than running the interactive page. If Pages is not available, download the [V3.0 HTML file](docs/previews/v3-measured-beta/index.html) and open it locally in a browser.

## Editions and research status

**V2.9 — locked creative baseline.** The original interactive experience is preserved unchanged at [V2.9 HTML](docs/archive/v2-9/index.html). Its sonic tree, acoustic descriptors, and emotional relationships are illustrative.

**V3.0 — measured research beta.** The beta adds source-linked acoustic observations for 148 of 167 catalogue entries, with missingness, codec/extractor filters, and recording receipts. It does **not** claim that the synthetic tree is measured or that archived recordings are independently verified studio masters. V3.0 remains exploratory and is not approved for acoustic clustering, mood inference, or catalogue-wide claims.

[Read V3 methods and publication gates](docs/V3_MEASURED_BETA_README.md) · [Evidence provenance manifest](docs/research/acousticbrainz/preview_manifest.json)

**Research state:** V2.9 remains locked and unchanged. The acoustic workbench is a separate research preview. AcousticBrainz submitted-file descriptors are not validated studio-master measurements and are not approved for similarity or mood claims.

## Catalogue-wide acoustic evidence

The separate catalogue acquisition identified 124 provisional source recordings among 130 additional eligible songs, plus six unresolved recordings and 12 post-archive tracks. These observations are not certified exact studio masters or approved for sonic-similarity claims.

- [Verified catalogue findings and unresolved recordings](docs/CATALOGUE_EVIDENCE_FINDINGS_2026-11-08.md)
- [Catalogue Evidence Atlas workflow](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/workflows/catalogue-evidence-review.yml) — open a successful run and download its atlas artifact.
- [Catalogue evidence methods and scientific controls](docs/CATALOGUE_EVIDENCE_ATLAS.md)

## Research tools and methods

- [Measured Evidence Lab](docs/research/acousticbrainz/Measured_Evidence_Lab.html) — GitHub shows the HTML source; use the hosted link above or download and open locally.
- [Methods and scientific limits](research/acousticbrainz/docs/MEASURED_EVIDENCE_LAB.md)
- [Automated research publishing guide](docs/AUTOMATED_RESEARCH_PUBLISHING.md)
- [AcousticBrainz 25-song audit workflow](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/workflows/acousticbrainz-25-audit.yml)

Changes to `research/acousticbrainz/**` on `main` run the research workflow, which validates source observations and generates an offline HTML workbench. Workflow artifacts and generated files in the repository are not, by themselves, a hosted website. The separate [GitHub Pages workflow](.github/workflows/publish-interactive-pages.yml) deploys an allowlisted static site when Pages has been enabled by the repository owner.

**Publishing note:** GitHub Pages may make the site publicly accessible, even if the repository is private. Confirm the repository's visibility and the deployment URL before enabling publication. A successful deployment does not constitute scientific publication clearance.

No copyrighted audio or protected lyrics are hosted. The project is independent and is not affiliated with Depeche Mode, the band, or its rights holders.
