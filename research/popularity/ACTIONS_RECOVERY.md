# GitHub Actions startup recovery — V3.2 listener reach

## Verified observations — 9 November 2026

- V3.2 ListenBrainz audit [run 42699983191](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42699983191) concluded `startup_failure`, with **zero created jobs**. Neither Python tests nor the ListenBrainz API were invoked in that run.
- The same no-job startup status affected independent V3.0/V3.1 checks and GitHub Pages deployments earlier on 9 November. Historical workflows in this repository had completed successfully on 8 November.
- GitHub published [Actions incident notices](https://www.githubstatus.com/) on 9 November. Those notices cannot conclusively establish why every repository-specific run failed.
- After isolating the problem, a zero-dependency Ubuntu [Actions health check, run 42716990006](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42716990006), completed **successfully** with a real job and runner.
- The GitHub connector could not retry failed jobs on the no-job startup run (GitHub returned 403: `This workflow run cannot be retried`).

## Fresh audit trigger

This documentation change under `research/popularity/**` intentionally triggers the existing [V3.2 listener reach coverage audit](../../.github/workflows/listener-reach-audit.yml) on `main`. Its 147-song MusicBrainz recording-ID crosswalk and research methodology are **not altered**.

The fresh job must be validated independently:
1. The unit tests should run on Ubuntu.
2. The ListenBrainz API stage should produce `recording_popularity.csv` with nulls where values are unreported.
3. The artifact should contain `coverage_summary.json`, reporting counts, not inventing zero listens.
4. Do not publish setlist.fm performance totals unless reuse authorization has been established.
5. Do not automatically promote any popularity metrics to the public Sonic DNA tree before source coverage and identity review.

## If another run cannot start

Check repository [Actions settings](https://github.com/ChrisDHayes/the-architecture-of-feeling/settings/actions) for disabled workflows and any policies, then GitHub account [billing and usage](https://github.com/settings/billing) for Actions budgets or payment restrictions. If the UI says Actions are disabled for the account, GitHub may need to review the restriction. See [GitHub's official Actions settings guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository).

**Scope:** operational audit only. This file does not change the V3.1 HTML, V2.9, the 147-source crosswalk, or licensing boundaries.
