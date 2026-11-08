# Publish the interactive research experience with GitHub Pages

The repository keeps the approved **V2.9 creative original** and the **V3.0 measured research beta** separate. A dedicated Actions deployment publishes only an allowlisted static site (landing page, V2.9 HTML, V3 beta HTML, 25-song Evidence Lab HTML, and lab provenance manifest). It does **not** publish raw AcousticBrainz JSON archives, commercial audio, private project files, or research collection scripts.

## One-time owner-side GitHub setting

In the connected repository, go to **Settings → Pages → Build and deployment**.

1. Verify that your GitHub plan/repository settings permit Pages for a private repository. GitHub Pages content can be **publicly accessible even when repository contents remain private**.
2. Set **Source = GitHub Actions**. **Do not** choose *Deploy from a branch*: this repository uses the dedicated upload/deploy Pages workflow.
3. Open **Actions → Publish The Architecture of Feeling interactive research website → Run workflow** if the deployment did not begin automatically. Review the first run's result and the URL GitHub displays under **Settings → Pages** or under the deployment job.
4. Verify the public landing page and all three exhibits in a private/incognito browser (not signed in to GitHub). Confirm navigation, interactive controls, and explicit source-evidence/synthetic disclaimers.

These settings cannot be switched by the current ChatGPT GitHub connector, so publication is **not confirmed until the Pages deployment completes and its site URL can be opened**.

## Layout and audience

- Landing page: `docs/index.html` — entry links to both interactive editions and the 25-song Evidence Lab.
- **V2.9**: `docs/archive/v2-9/index.html` — unchanged creative baseline (SHA-256 `3ba59e0030951051bcc4842fb2471b08a306dcb1aa838cdf1a9d06a8166eac21`).
- **V3.0 beta**: `docs/previews/v3-measured-beta/index.html` — 148 provisional source-linked observations / 167 entries; source quality and missingness visible; musical similarity and emotional tree **still synthetic**.
- Source Evidence Lab: `docs/research/acousticbrainz/Measured_Evidence_Lab.html` and corresponding provenance manifest.

## How automatic updates work

The Pages workflow `.github/workflows/publish-interactive-pages.yml` runs for:
- site-related edits to `main`;
- manual `workflow_dispatch`;
- completion of the **AcousticBrainz 25-song coverage audit** on `main`, but only when the audit succeeds.

The third trigger accounts for GitHub's rule that commits created with the default `GITHUB_TOKEN` do not trigger another Pages build. We use a workflow completion event instead of expecting the audit bot's file commit to trigger a normal push event.

The deployment checks the V2.9 SHA-256, V3 catalogue count/status and lack of scientific approvals, and the Evidence Lab's SHA-256 provenance match. Any violation fails closed. The public upload includes **only five explicitly allowed files plus a no-Jekyll marker**.

**A successful static deployment is not scientific publication clearance.** The sources remain unapproved studio masters, and the V3 beta must remain labelled provisional. Revising the sonic-family tree requires a separate measured-similarity methodology and sensitivity review.
