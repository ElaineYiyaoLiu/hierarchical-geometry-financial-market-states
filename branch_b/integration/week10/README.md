# Week 10 Branch B implementation and integration kit

Prepared November 13 for the November 15 meeting and November 15–21 work. This is a development handoff: public arithmetic fixtures, executable interface checks and meeting examples. It contains no experimental or pilot bank. The public source baseline is `a0b2a8d60cc1e1254333913e780725c37157caad`.

## Start here

Use a Python 3.14 checkout containing this folder. From the repository root, install the pinned dependencies in `.github/workflows/branch-b-python314.yml`, then run:

```sh
python -m branch_b.integration.week10.verify
python -m pytest branch_b/recovery_tests/test_week10_integration_kit.py branch_b/recovery_tests/test_week9_objective_reference.py branch_b/recovery_tests/test_exact_tie_dp.py -q
```

The first command must report `status: pass`, nine valid observable files, seven rejected malformed or mismatched loader calls, and rejection of exactly constant correlation profiles. The second exercises the kit plus existing exact tie and full-objective mathematical references. Neither command invokes the unfinished scientific optimizer.

`catalog.json` binds every CSV/manifest pair to an external expected checksum, dataset identity and split. Keep it outside the loader input when passing the exact observable manifest. `generation_receipt.json` records actual generation under Python 3.14.7. `build_fixtures.py` reproduces the fixture bytes without randomness, external inputs or a research generator. Do not overwrite the generation receipt merely to change its Python version.

## Data and expected behavior

Each of three fixture families has train (8 rows), validation (5) and test (5), the exact 12 released-feature columns, unique sample IDs, a schema-valid observable manifest and SHA-256 bindings. Dataset IDs are fixture-local and have no experimental meaning; units are arbitrary arithmetic units, including AUX. The integer construction is fully public in `build_fixtures.py`. These sizes exercise interfaces and are not scientific sample-size recommendations.

- **regular:** varied finite values for input, preprocessing and geometry integration. Fit training preprocessing only on train; apply it unchanged to validation/test. Loading alone makes no geometric admissibility claim.
- **duplicates:** distinct IDs with identical observable values. Preserve both IDs. Bootstrap occurrences live in the separate D06 worked example; repeated occurrence IDs must not be inserted into the observable CSV.
- **constant_profiles:** each row is exactly constant across its 12 coordinates. The loader accepts finite valid input; raw Pearson correlation must return `DEGENERATE_DISTANCE`. Acceptance by a schema is not method eligibility.

The verifier constructs invalid cases in memory: external CSV hash mismatch, manifest hash mismatch, split mismatch, nonfinite cell, duplicate ID, wrong header and short row. It rebinds checksums for parser cases so the intended parser guard is actually exercised. Do not repair, sort, impute, jitter or deduplicate these examples. The numerical comparison tolerance used by an assertion is an engineering check, not a new scientific tie rule.

## Meeting and implementation coverage

The controlling meeting agenda is the shared “Branch B Meeting Goals — Weeks 9–11 — November 2026” PDF. The public November 8 reconciliation supersedes historical D01–D06 intake wording. `worked_cases.json` supplies literal inputs and mechanical expectations; fields labelled `pending` are questions to resolve, not defaults.

| November 15 goal | Ready input / reference | What Branch B still needs to decide or implement |
| --- | --- | --- |
| Core algorithm and worked examples | G2 strict chamber, D04 four-vertex exact tie, G4 weighted zero-height objective; existing 25 Week 9 reference tests | AMSGrad equation-level arithmetic, projection/update integration, D06 pipeline wiring and executable optimizer conformance |
| Correlation and valuation sanity | constant CSVs, D08 zero/near-constant profiles, D09 checklist | Near-constant threshold/equality and dataset eligibility; exact favorable-feature criterion and eligible scientific verifier |
| Parameter and Common-Fitter selection | D11 tied candidates, failed/missing stability | Parameter candidates and scale-invariant geometry-neutral ranking, missingness/failure eligibility, final ties |
| Bootstrap target and reliability | D06 six-occurrence ledger; D12–D13 four attempts including timeout | Inferential target, confidence level and percentile convention, minimum successes/common observations and sensitivity to failures |
| Calibration quantiles, seed and timeout | D15 duplicate order statistics comparing two quantile conventions; D14 resource inputs | Authorized quantile rule; namespaced B seed derivation; reference timing and size scaling; actual runtime deadline |
| Pilot-dependent settings and gates | Gate record below | Which setting may be fixed using which permitted evidence, by which deadline; no performance-driven change to already fixed beta=5 |
| Final comparisons and region claims | D16–D17 paired values, missing region pair | Estimand, CI, multiplicity family/adjustment and region-level claim criteria |
| D16–D17 / substantive revisions by Nov 18 | Explicit unresolved checklist and empty decision record below | Obtain authoritative D16–D17 definitions and record decisions by the specified deadline; do not infer option meaning from these fixture names |

## Handoff result Branch B should return

For each relevant input, retain source revision, actual Python/dependency versions, input and configuration digests, geometry/fitter identity, row order, attempt ledger and failure details. For a completed implementation, return the actual output and comparison against the reference; for an unresolved method, return the exact missing decision. Preserve failed attempts and original-ID multiplicities. Do not present a placeholder result as a production fit.

For each pending choice, record: authoritative source/item; exact formula and boundary cases; permitted data tier/evidence; approval/freeze authority and date; implementation revision; worked-case output; remaining dependencies. Leave approval fields blank until an actual decision is received. Historical minimum-effect chronology cannot be repaired by entering a new date.

## Project boundary

This kit is safe for public disclosure and contains only public formulas, arbitrary arithmetic fixtures and public Branch B method references. No Branch A implementation, hidden configurations, seeds, labels, hierarchy or sealed ground truth is included. It does not release formal pilot observations, resolve scientific choices, authorize research processing or replace protocol gates. The current public scientific optimizer and D06 integration remain incomplete.

Sources: `branch_b/geometry_registry.md`; `branch_b/decision_proposals/week9_pl_completion_2026-11-08.md`; `branch_b/decision_proposals/week9_objective_gradient_golden_spec_2026-11-08.md`; historical `branch_b/decision_proposals/branch_b_meeting_intake_2026-10-20.md`; `branch_b/tools/development_bundles.md`; observable schema and loader.
