# GitHub Actions & Pages recovery — 9 November 2026

**Status: the GitHub-authored action restriction has been resolved.** The owner adjusted **Settings → Actions → General** to allow GitHub-authored actions. The successful checkout smoke test and subsequent full workflows verify that the setting takes effect.

## Diagnosis and definitive verification

Earlier in the day, multiple workflows failed with `startup_failure` **before creating any job**. Controlled tests isolated the source:

| Workflow run | Test | Result |
|---|---|---|
| [42716990006](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42716990006) | Bare Ubuntu shell, no `uses:` steps | Passed |
| [42717417834](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42717417834) | Add `actions/checkout@v4` before owner setting change | Startup failure |
| [42717614281](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42717614281) | Pin checkout to full SHA before setting change | Startup failure |
| [42717878909](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42717878909) | Shell-native Git clone + Python regression tests | Passed |
| [42719289682](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42719289682) | `actions/checkout@v4` **after** owner setting change | **Passed**, including post-checkout cleanup |

The underlying GitHub setting cannot be read from the connected app, so the exact radio selection isn't independently auditable; **effective permission is demonstrated by the actual action passing**.

## V3.2 listener-reach data pipeline restored

**[Run 42719376842](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42719376842) — success.** Uses GitHub-authored `actions/checkout@v4`, `actions/setup-python@v5` and `actions/upload-artifact@v4` again.

- All 8 source identity, missingness and rights tests passed.
- The live ListenBrainz audit checked **147** selected recording MusicBrainz IDs, with **144** reporting both unique listener and total listen counts and **3** missing (97.96% recording-level coverage).
- A dated GitHub Actions artifact is available: **`listenbrainz-147-recording-popularity-4`**, artifact ID **13718044402**, containing `recording_popularity.csv` and `coverage_summary.json` (60-day retention).
- Recording-level user counts do not measure worldwide song popularity; no cross-edition aggregation or public dashboard promotion was approved.
- Live-performance counts from setlist.fm remain behind the separate authorization gate; setting changes did **not** grant data redistribution rights.

## Other successful validations

- [V3.1 measured Sonic DNA validation, run 42718550749](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42718550749): **passed**.
- [V3.0 and Home finale validation, run 42718557423](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42718557423): **passed**.
- These validators currently use the previously established shell-native checkout workaround, which is functioning. They do not need urgent modifications just because the first-party actions restriction has been removed.

## GitHub Pages publication

**[V3.1 publication run 42719641582](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42719641582) — success.** The workflow's checks, Pages configuration, artifact upload and deployment steps all passed.

The publishing workflow now stages the repository's **V3.1 source-derived Sonic DNA experience**, its **Home finale**, the preserved V3.0 and V2.9 experiences, and the research evidence-lab documents using an **explicit six-file allowlist**. The V3.1 source's embedded measurements must match the V3.0 research payload, and an unverified-master label remains required.

GitHub's deployment step reports:
- Landing page: **https://chrisdhayes.github.io/the-architecture-of-feeling/**
- V3.1: **https://chrisdhayes.github.io/the-architecture-of-feeling/previews/v3-1-measured-dna/index.html**
- Home finale: append `#home-finale` to the V3.1 URL

The deployment was verified using GitHub's completed Actions job and its reported environment URL; **independent unauthenticated HTTP retrieval was not available from this runtime**.

## Security and scope

Owner-level repository Actions permissions were adjusted in the GitHub UI; no personal access tokens, secrets, broad default write permissions or branch protection changes were required. Popularity counts are **not** embedded in the public exhibit; live performance reuse remains separately gated. All existing measured catalogue values and the original V2.9 archive remain preserved.
