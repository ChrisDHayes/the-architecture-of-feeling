# Publishing The Architecture of Feeling on GitHub Pages

The public **main URL** is https://chrisdhayes.github.io/the-architecture-of-feeling/ . It serves the **V3.2 interactive experience directly**, with the approved preview kept at `/previews/v3-2-listener-reach/`.

## Deployment configuration

This repository uses the GitHub Actions workflow [`publish-interactive-pages.yml`](../.github/workflows/publish-interactive-pages.yml), not GitHub Pages' branch-folder publisher. In **Settings → Pages → Build and deployment**, set **Source = GitHub Actions**. Publication is complete only after the Pages deployment succeeds and the main URL loads the updated page.

The publishing workflow checks:
- The main `docs/index.html` is byte-for-byte equivalent to the approved V3.2 preview, except for one corrected relative hyperlink to the evidence lab.
- V3.2 acoustic evidence is unchanged from V3.0, and the selected-recording audience layer preserves the 144 exact-MBID observations plus three clearly labelled alternate-album-version proxies.
- The original V2.9 creative exhibit matches its locked SHA-256 hash; V3.0 and V3.1 remain present; research status, source manifests and evidence lab have their required integrity markers.
- Only seven explicitly approved static files and `.nojekyll` are staged publicly. Raw collectors, commercial audio, unlicensed lyrics, and internal research archives are excluded.

## Public locations

- **Main exhibit:** `/` → `docs/index.html` (V3.2 interactive experience)
- **V3.2 preserved preview:** `/previews/v3-2-listener-reach/`
- **V3.1:** `/previews/v3-1-measured-dna/`
- **V3.0:** `/previews/v3-measured-beta/`
- **V2.9:** `/archive/v2-9/`
- **Evidence Lab:** `/research/acousticbrainz/Measured_Evidence_Lab.html`

## Publication verification

Open the [main experience](https://chrisdhayes.github.io/the-architecture-of-feeling/) in an incognito browser, jump to the acoustic scatterplot (`#contradiction`) and dendrogram (`#family`), check hover/tap receipts and the three audience modes, and verify the source link and `#home-finale`. In the GitHub Actions deployment log, confirm the allowlist/integrity step and Pages deployment have both passed.

**Scientific and legal caveat:** Publishing an exploratory exhibit does not validate recordings as studio masters, convert listening counts into global popularity, or license audio. The original measured/synthetic and human-interpretation distinctions remain in place.
