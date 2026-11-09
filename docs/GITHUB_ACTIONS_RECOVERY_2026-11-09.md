# GitHub Actions startup restriction — isolated and mitigated

**Date:** 2026-11-09  
**Repository:** [ChrisDHayes/the-architecture-of-feeling](https://github.com/ChrisDHayes/the-architecture-of-feeling)

## Verified diagnosis

The repository experienced `startup_failure` on several workflows with **zero jobs created**, even before Python, API calls or action logs existed.

The following controlled tests isolated the failure:

| Run | Single change | GitHub conclusion |
|---|---|---|
| [42716990006](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42716990006) | Runner and shell only, no `uses:` | **success** |
| [42717417834](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42717417834) | Add `uses: actions/checkout@v4` | **startup_failure**, zero jobs |
| [42717614281](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42717614281) | Pin checkout to a full commit SHA | **startup_failure**, zero jobs |
| [42717878909](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42717878909) | Git clone + Python tests using ordinary shell steps, no `uses:` | **success** |
| [42718066788](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42718066788) | Full 147-recording ListenBrainz audit without reusable actions | **success** |

### Research workflow recovery

The current `.github/workflows/listener-reach-audit.yml` uses shell-native Git and Python rather than blocked reusable actions, and the validated audit completed successfully.

Verified [run #42718066788](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42718066788):
- 8 offline crosswalk/rights tests passed.
- 147 recording MBIDs requested from ListenBrainz.
- 144 returned listener/listen counts; 3 had no reported counts.
- 97.96% recording-level coverage (not song-wide or world-wide popularity).
- Counts are **not** automatically promoted to a public acoustic tree.
- **Known limitation:** Source-level CSV is produced in the job workspace but not retained as a downloadable Actions artifact while the `actions/upload-artifact` reusable action is blocked. The run summary/logs preserve audit coverage results.

This is a validated **workaround**, not proof that the underlying GitHub Actions setting has been changed.

## Additional integrity workflow recovery

- [V3.1 measured Sonic DNA validation — run 42718550749](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42718550749): **success** with shell-native Git checkout, verified V2.9/V3.0 provenance and V3.1 data integrity.
- [V3.0 and Home finale validation — run 42718557423](https://github.com/ChrisDHayes/the-architecture-of-feeling/actions/runs/42718557423): **success** with shell-native Git checkout, both regression suites.
- Both validation workflows retain exact-event checkout semantics for push and pull requests, without reusable `uses:` actions.
- Workflows that still rely on GitHub-authored reusable actions—including the **Pages deployer** and historical acquisition/atlas pipelines—remain at risk of startup failure until the repository Actions permission is corrected.


## Owner action: restore GitHub-authored reusable actions

Our GitHub connector permits file/PR changes but does not expose the repository's Actions security policy or an administration-write endpoint. GitHub's [official configuration instructions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository) explain the owner-only controls.

1. Open [Settings → Actions → General](https://github.com/ChrisDHayes/the-architecture-of-feeling/settings/actions).
2. In **Actions permissions**, verify GitHub-authored actions are allowed. A narrowly scoped choice is **Allow ChrisDHayes, and select non-ChrisDHayes, actions and reusable workflows** with **Allow actions created by GitHub** selected. Alternatively select **Allow all actions and reusable workflows** only if that broad policy is acceptable.
3. Click **Save**. Requiring full-length SHA alone did not fix this restriction.
4. Re-run an existing validator that uses `actions/checkout` or a small checkout-only smoke test. Confirm that a job is created and the action runs successfully.
5. After validation, restore the artifact-upload step to the listener audit. Before making GitHub Pages live, also check [Settings → Pages](https://github.com/ChrisDHayes/the-architecture-of-feeling/settings/pages) and set its build source to **GitHub Actions**.

**Unconfirmed:** The repository's exact `Actions permissions` value is not readable through the connected GitHub app. A GitHub-side action-resolution incident or a more specific account restriction could also produce a similar symptom. If the policy already allows GitHub-authored actions, collect the failed run URLs and contact GitHub Support rather than broadening permissions blindly.

## Security

Do not place a personal access token in workflow YAML or logs, and do not weaken branch controls to fix a reusable-action startup failure. The acoustic source records, locked V2.9 and V3.1 public exhibit were unchanged by the workaround.
