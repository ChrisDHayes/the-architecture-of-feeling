# Automated research-preview publication — GitHub Actions

## What is already in the repository
- A reproducible, single-run collector and candidate resolver under `research/acousticbrainz/`.
- A fail-closed evidence QA stage and standalone Measured Evidence Lab builder.
- An existing `main` workflow at `.github/workflows/acousticbrainz-25-audit.yml`.

## What this addition does
After a successful **all-25** run, GitHub Actions runs `tools/stage_research_preview.py`. The script requires:
1. A complete 25-song identity registry with no duplicate IDs.
2. At least **20** successfully retrieved and source-parity-checked low-level submissions (a minimum-coverage protection, not an evidence-validity finding).
3. A QA summary reporting **zero approved masters or similarity claims**.
4. A standalone HTML containing the `EXPLORATORY_UNAPPROVED` research status.
5. All source files needed for staging to exist and be readable.

Only then does the workflow commit two files:
- `docs/research/acousticbrainz/Measured_Evidence_Lab.html`
- `docs/research/acousticbrainz/preview_manifest.json`

The HTML contains exploratory source descriptor values already present in the research workbench. No raw AcousticBrainz JSON, song audio, lyrics, commercial artwork, or full unreviewed data dump is copied. The GitHub Actions artifact retains the underlying QA reports for **30 days** as currently configured.

## Trigger and update rules
- Any merged source change under `research/acousticbrainz/**` on `main` triggers one automatic audit and preview refresh.
- A manual `workflow_dispatch` run with scope `all_25` on `main` also refreshes the preview; a debug `pilot_6` run never overwrites the permanent all-25 snapshot.
- When retrieval fails, coverage drops below the guardrail, a parity check fails, or the HTML lacks its unapproved status, the workflow fails rather than replacing the last good preview.
- Generated files live under `docs/`, outside the collector's `push.paths` filter. The workflow's own bot commit does **not** recursively trigger a new audit.
- The workflow uses `GITHUB_TOKEN` with `contents: write` for a bot commit. If branch protection or repository Actions permissions prohibit the write, the job fails; an owner must adjust the relevant rule or use a reviewed PR-based alternative.

## Viewing and optional Pages publishing
- Immediately after a successful run, visit the HTML file inside GitHub at `docs/research/acousticbrainz/Measured_Evidence_Lab.html`, or download it from the raw-file view. GitHub's code browser is not a guaranteed interactive HTML host.
- `docs/index.html` is a landing page ready for an optional GitHub Pages site.
- **Do not assume GitHub Pages is enabled**. The owner can examine **Settings → Pages** and, if appropriate, configure a publishing source. Availability depends on account/repo settings; a Pages site may be **public even for a private repository**.
- **Critical deployment gap:** GitHub documents that a commit pushed using the Actions `GITHUB_TOKEN` **will not trigger a GitHub Pages build**. Our existing automated preview commit therefore keeps `docs/research/acousticbrainz/Measured_Evidence_Lab.html` up to date in the repository but does **not automatically refresh a live Pages site**. For true hands-off live publishing, use an explicit Pages deployment workflow (after separately authorizing website visibility) or a carefully reviewed alternate trigger.
- To open the experience **now**, download the HTML file from GitHub's source view and open it locally. GitHub `blob/main/` links show source code, not a running app.
- For an eventual public research exhibit, retain the explicit unapproved label and revisit intellectual property, master comparability, methodology, accessibility and editorial review before presenting measured relationships as findings.

## Reproduce locally
```sh
python research/acousticbrainz/tools/test_stage_research_preview.py
python research/acousticbrainz/tools/stage_research_preview.py \
  --qa-dir research/acousticbrainz/results/github_run/evidence_qa \
  --destination docs/research/acousticbrainz \
  --min-retrieved 20
```

The script copies only a generated HTML and a small research manifest; it never makes a licensing determination.

## Research boundary
All 15 studio albums remain the ultimate analytical population. The current 25-song audit is a curated **editorial research sample**, and the six-song pilot is a feasibility test. The locked creative V2.9 experience is neither modified nor automatically published by this workflow.
