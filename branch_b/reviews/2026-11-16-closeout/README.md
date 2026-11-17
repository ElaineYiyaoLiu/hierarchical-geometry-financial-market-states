# Week 10 PL Closeout Evidence

New execution: November 16, 2026 America/New_York; November 17 UTC. Source commit `ef9e8515e3c4cfc98d4cc0f6b40dfdfa5c128225`. The scientific application code is unchanged from `74954ae5126e5967e700234a8ccd8d5379a8e9f6`.

- Actual CPython 3.14.10, NumPy 2.5.3, pytest 8.4.2. Full distribution versions and observed platform are in `environment.json` and `pip-freeze.txt`.
- Full regression: **833 passed, zero failures/errors/skips**, 6.97 seconds. `full-junit.xml` and `full-pytest.log` are the new original outputs. This run occurred once after dependency preparation; no test failure/retry was concealed.
- `reference-checks.json` verifies all 20 prior evidence bindings, deterministic candidate namespace vectors, invalid-input guards for the public candidate root, simple support-bound sensitivity arithmetic and a height-closeness counterexample. It is separate from the 833-test count.
- `study-audit.json` and `study-recount.json` are new read-only verifications of existing 2,400/600 journals. The studies themselves were not rerun. Their original source/design/environment records remain in `../2026-11-16-pl/`.
- `pre-pilot.json`, `freezes.json`, `queue.json` and `minimum-effect.json` are new current-record audits. Their BLOCKED outcomes are substantive missing-input results, not test failures or authorizations.
- `reference-sources.json` binds the retrieved paper and authors' source files to exact hashes. The authors' software was inspected, not executed. Original paper bytes are not copied into the shared repository.
- `source-sha256.json` fingerprints 173 tracked code/configuration/register files from the tested checkout. The newly added review reference utility and all new documents/evidence are bound by `checksums.json`.

The fresh environment intentionally records its real versions. Existing reproduction used NumPy 2.5.5; original team/CI records used other pytest versions. No environment record is relabeled to make them identical. Dependency compatibility checks are separate from source/protocol approval.

## Reproduction

Use actual Python 3.14, the exact dependency versions recorded here, the source commit above, and a fresh evidence destination for a new regression run. From the repository root:

```bash
python -m pytest -q --basetemp=<fresh-temporary-directory> --junitxml=<fresh-output>/full-junit.xml
python branch_b/reviews/2026-11-16-closeout/reference_checks.py
python branch_b/reviews/2026-11-16-pl/recount.py
python -m branch_b.tools.d13_evidence_audit --expanded-dir branch_b/reviews/2026-11-16-pl/expanded --sensitivity-dir branch_b/reviews/2026-11-16-pl/sensitivity
```

The candidate seed vectors use public arithmetic root 17 and a public fixture identity. They do not choose the proposed production root 36, alter the current engine or authorize a production seed contract. Preserve the recorded NumPy/PCG64 version when comparing vectors.

The [completion record](../../decision_proposals/week10_pl_closeout_2026-11-16.md) records review conclusions and remaining inputs. No production fitter, seed rule, statistical definition, schema or approval register changed. Actual evidence contents were inspected for Branch B/public disclosure before publication.
