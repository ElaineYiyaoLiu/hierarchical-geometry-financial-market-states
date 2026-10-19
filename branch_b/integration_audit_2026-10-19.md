# Branch B integration audit - 2026-10-19

Audited revision: `44f1663ad1d68bc65c1bab48f440e466b76c3f56`.

**Disposition: development evidence verified; scientific integration not ready.** This audit records material integration gaps as well as the existing scientific decision blockers. No implementation, method, threshold, shared schema, or freeze record is changed by this report.

## Scope and verification limits

Reviewed the last three documentation commits, the recovery pipeline, bootstrap engine and adapter, distance primitives, output-record builders, relevant synthetic tests, the Common-Fitter implementation/card/decision record, numerical proposals, and the reviewed-source packaging workflow. Scientific requirements were checked against the supplied Version 2 Branch B Packet, especially pp. 20, 25-26, 37-42, 58-61 and 66-68; the Schedule supplies the Weeks 1-6 execution order.

The findings below are source-level findings and logical consequences of the inspected code. No new counterexample test, scientific experiment, or benchmark was executed in this audit. Existing CI logs were independently retrieved and inspected, rather than treating earlier summaries as test evidence. No restricted generating information or experimental bank was accessed. This is not an exhaustive audit of all historical commits, dependencies, permissions, or approvals on other surfaces.

## Confirmed evidence

The comparison from `64db636725f4c96c83f2ad0dc0658a12b1e077c7` to the audited revision contains only three changed files: `branch_b/README.md`, `branch_b/branch_b_environment.txt`, and `branch_b/weeks_1_to_6_evidence_checklist.md`. The historical September 28 environment record is still present before the October 19 supplement. The last continuation therefore did not edit scientific code or an approval record.

Actual logs for the previously tested revision `8f224c2fcaa48ba9b915a2240421fc1f175cfb1c` confirm:

| Scope | Run | Job | Recorded result |
| --- | --- | --- | --- |
| Branch B support/recovery/failure tests | 39320669279 | 118293564490 | 202 passed in 0.70 s |
| Shared validator, same job | 39320669279 | 118293564490 | 15 passed in 0.10 s |
| Repository-wide pytest discovery | 39320669222 | 118293564529 | 343 passed in 1.13 s |

Both logs print CPython 3.14.8 and show checkout of the tested revision. The Branch B job explicitly checks Python major/minor. It uses pytest 9.1.1; repository-wide discovery uses pytest 8.4.2. Both install NumPy 2.5.3. Suites overlap and counts must not be summed. These are prior runs, not new executions of the newly identified counterexamples.

[Branch B run](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39320669279) and [repository-wide run](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39320669222).

Artifact metadata for `12219757568` agrees with the Branch B upload log: SHA-256 `ad4b38a7242bffdde4842cadbb8a03f2f79d4e2f6d53a66c2dda0624ee973541`, with reported expiry `2027-01-17T20:36:08Z`. This is provider-reported integrity evidence; the archive was not independently rehashed locally.

The packaging workflow still pins source revision `6975d4da8baf1e1374353466fe8420183da69152` and its four explicit reviewed files. It does not silently package newer pipeline code. Its output is not a scientific runner.

## A1 - High: duplicate bootstrap rows conflict with the fitter's input rule

Sources: `bootstrap/engine.py::bootstrap_split_indices`, `bootstrap/pipeline.py::run_recovery_pipeline_bootstrap`, `geometries/distances.py`, and `fitters/gradient_descent.py::validate_normalized_input`, all relative to `branch_b/` at the audited revision.

The engine samples indices with replacement. The adapter passes repeated rows directly into the pipeline using `train[train_idx]`, `validation[validation_idx]`, and `test[test_idx]`. With the registered Euclidean or Chebyshev mapping, two copies of one observation have pairwise distance zero. Common scalar normalization does not remove that off-diagonal zero. The Common-Fitter validator rejects any required off-diagonal weight at or below `1e-12`.

Thus, a validation or test bootstrap draw containing a duplicate is incompatible with this fitter input path, even if the optimizer kernel is subsequently completed. This is a source-level consequence, not a measured failure rate. It is not a regression introduced by the last documentation or output-copy changes.

The Packet, pp. 40 and 60, requires duplicate draws to represent multiplicities of original observations. Recording multiplicities after `pipeline.run` returns cannot resolve the zero-distance rejection that occurs before it returns. Stub-based bootstrap tests do not test this interaction with the real candidate's input validator.

**Required disposition:** reconcile the executable multiplicity representation, pair weighting, and reciprocal-weight rule with the authorized scientific specification before enabling the fitter. Do not silently drop repeated rows, add jitter, floor denominators, omit zero edges, change the resampling scheme, or substitute another fitter. Any scientifically consequential resolution needs explicit approval. A synthetic regression demonstrating the existing conflict does not itself select that resolution.

## A2 - High: bootstrap success is not yet bound to scientific output validation

Sources: `recovery_pipeline/pipeline.py::_fit_split`, `bootstrap/pipeline.py::run_recovery_pipeline_bootstrap`, `bootstrap/engine.py::run_full_pipeline_bootstrap`, `output/records.py`, and `recovery_tests/test_pipeline_output_snapshots.py`.

The pipeline snapshots a returned `FitResult` but does not validate its fitted matrix or rooted-tree schema before giving it to selection or returning it. The engine records `failure=None` whenever the callback returns without an exception. The adapter optionally computes tree-based LCA stability, but does not establish fitted-matrix conformance or a complete support result. Output-record builders also construct records; they do not validate them.

The current snapshot test explicitly returns a tree-shaped diagnostic dictionary rather than a valid recovered-tree record and still expects no bootstrap failure. That is appropriate for an ownership-only fixture, but it proves neither scientific validity nor compliance with the Packet's unsuccessful-fit criteria. A nonfinite fitted matrix can likewise pass this orchestration path if its producer returns it without raising.

**Required disposition:** add or identify a mandatory scientific result-validation boundary before a fit contributes to validation selection or a bootstrap success count. Exact shape, finiteness, identifier and structural-schema checks implement existing requirements and can be developed without choosing a new statistical method. Numerical tolerance-dependent checks must use approved conventions, not new defaults. Keep the generic callback engine's successful arbitrary return values distinct from protocol-valid scientific successes; do not redefine its general-purpose contract silently.

## A3 - High: original sample identity relies on unchecked leaf-list position

Sources: `bootstrap/pipeline.py::full_test_lca_depths_by_index`, `bootstrap_lca_depths_by_original`, and the recovery-pipeline input/output interfaces.

The full-test helper assigns original indices by enumerating the tree's own `leaves` list. The bootstrap helper zips its tree's `leaves` list with sampled row indices. It checks length and uniqueness, but has no independently supplied canonical sample order or explicit leaf-to-original mapping against which to verify that association.

The mapping is correct only if an upstream component preserves exactly the assumed order. Reordering a tree's leaf list while keeping its named topology unchanged can change the ordinal mapping; a scientific caller must reject a mismatch against the manifest or consistently reindex it. The current adapter cannot independently enforce that contract. This is an integration gap, not evidence that any actual bank was misidentified.

**Required disposition:** bind original sample identifiers and multiplicities explicitly through the adapter, enforce agreement with the external canonical order, and test misordered/missing/extra identifiers. This implements the Packet's pp. 25-26 and 60 identity requirements without selecting a new geometry or stability statistic. The scientifically consequential duplicate-weighting question remains A1, not a license to invent a different representation here.

## A4 - Medium: invalid selection prevents test fitting, not all test processing

Sources: `recovery_pipeline/pipeline.py::run` and `recovery_tests/test_pipeline_parameter_isolation.py::test_invalid_selector_index_never_processes_test_split`.

The pipeline validates all input matrices and calls `preprocessor.transform(test.copy())` before candidate generation and validation selection. The invalid-selector regression records geometry calls only. Consequently, it establishes that an invalid selector cannot reach test geometry/fitting; it does not establish that no test preprocessing occurred.

Immediate array copies address buffer reuse, not every possible component-state dependency. Pure train-fitted transformations do not by themselves establish a test-to-selection leak, and no such leak was measured in this audit. Nevertheless the earlier broader wording is unsupported, and staging or testing the transformation boundary is material integration work.

**Required disposition:** correct the test/claim scope and verify the intended test-isolation contract with an instrumented preprocessor. Deferring test transformation until selection is validated is an engineering safeguard to evaluate; it is not a new scientific selection criterion. Do not claim the existing test certifies complete split isolation.

## A5 - Medium: readiness wording and development defaults need explicit separation

Sources: `fitters/gradient_descent.py`, `draft_cards/gradient_descent_common_fitter.md`, and `decision_proposals/week3_numerical_rules_proposal.md`.

The fitter's exception says registered settings are complete except the pilot timeout, while its card and source-conformance review still reserve CF-SIGMOID, CF-INIT, and CF-POSITIVITY. The implementation also executes literal `1e-12` symmetry/diagonal checks while general comparison conventions remain proposed rather than frozen. These are pre-existing development conventions, not evidence of a new approval.

Configuration validation checks positivity for several numeric settings rather than equality to the registered values; it also does not validate every recorded tree convention. A development configuration object is therefore not proof of compliance with an approved configuration. The unconditional missing-kernel exception still prevents this fitter from returning a scientific fit.

**Required disposition:** align readiness messages with the actual pending decisions, and require approved configuration/numerical-rule evidence at the production entry point before the kernel is enabled. Do not resolve the proposed values through this audit.

## Effect on the stopping-point assessment

The statement that no substantial decision-independent work had been identified must now be qualified. This audit has identified material output-validation, sample-identity, and test-isolation work, not merely another packaging layer. Those bounded engineering repairs and their Python 3.14 regression tests can proceed where they implement existing protocol requirements. Their implementations have not been completed or tested by this audit.

The central optimizer and the scientifically consequential bootstrap/multiplicity conflict remain decision-blocked. CF-SIGMOID, CF-INIT, CF-POSITIVITY, numerical-comparison approvals, correlation admissibility, valuation sanity, selection-rule freezes, and later execution approvals are not supplied by passing CI or by this report.

No audit finding here is a measured scientific outcome. No method approval, production seed, official processing gate, or protocol freeze is changed. The prior validation reports remain historical evidence for their stated scopes; this report supplements them and narrows the stopping-point claim.
