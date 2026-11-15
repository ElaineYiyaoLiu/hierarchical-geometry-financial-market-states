# Numerical-interface conformance — Branch B review (2026-11-15)

Status: source-level finding and project-lead handoff. Not a method change, freeze, approved numeric policy, scientific-run result, or production activation.

## Sources inspected

- Controlling Version 2 Branch B Packet (Appendix C.2, Appendix F, Appendix H.8).
- Shared `validator/validate.py`, `interface_package/branch_b_output.schema.json`, and `golden_cases/invalid/{asymmetric_matrix,nonzero_diagonal}.json`.
- `branch_b/fitters/gradient_descent.py`, `development_d06_fitter.py`, and `recovery_tests/test_development_numerical_interface.py`.
- `governance/freeze_registry.csv` as inspected on this branch.

No restricted data or generating information was accessed.

## Findings

1. **The source packet does not imply exact-equality rejection for every small floating-point residual.** Appendix H.8 requires invalid golden cases for asymmetric matrices and nonzero diagonals. Current invalid fixtures contain off-diagonal values 1 vs 2, and a diagonal value 0.1, respectively. They establish rejection of these *large* deviations, not the exact tolerance threshold.
2. **The shared validator and development fitter currently agree on a nominal tolerance.** `validator.validate_matrix` uses the CLI default `matrix_tolerance=1e-12` for diagonal residuals and absolute symmetry gaps. `GradientDescentUltrametricFitter.validate_normalized_input` also accepts gaps/residuals up to `1e-12`. Thus previous characterization tests of accepted `5e-13` departures do not, by themselves, conflict with the current shared validator.
3. **The freeze registry does not show numerical tolerance approval.** The `numerical_tolerances` entry is a pending placeholder. An implementation default, even one shared across two modules, is not a project-level scientific freeze.
4. **Orientation-dependent near-zero denominators remain unresolved.** The registered fitter tests fixed reciprocal denominators using only `d[i,j]` for `i<j`. A close-to-symmetric matrix can pass the shared symmetry tolerance while the lower-triangle entry is `<=1e-12` and the upper entry is `>1e-12`; transposing that same matrix can reverse its eligibility. The D06 development fitter likewise sends only upper-triangle values to the optimizer. The recently reported Python 3.14 numerical-interface tests characterize this behavior; they do not approve it.
5. **Canonicalization remains an open implementation rule.** Replacing a nearly asymmetric matrix with an averaged, upper-only, lower-only, or exactly symmetric matrix changes which numerical input is optimized. Do not select a new canonicalization/admissibility rule without checking controlling approvals.
6. **Tree reconstruction numeric tolerance is separate.** Independent exact-height tests use synthetic binary-exact values. They are not a frozen general tree-to-matrix acceptance criterion; parent-child subtraction and path summation can introduce ordinary floating discrepancies.
7. **The production candidate remains inactive.** `GradientDescentUltrametricFitter.fit` still raises `ConfigurationRequired`, and its historical D05 default values do not match the approved development stopping rule.

## Recommended project-lead resolution

Confirm whether the shared `1e-12` validator default is the intended final matrix symmetry/diagonal acceptance rule; if so, explicitly record how accepted residuals are canonicalized and how the fixed positive reciprocal denominator is tested, so permutation/transpose of merely near-symmetric input cannot silently change scientific eligibility. Alternatively, apply any already-approved stronger rule if a later controlling freeze record governs. Do not silently alter the validator, fitter, normalization, shared schema, or interpretation of failure codes in this review.

The Branch B meeting-goals document for Week 10 additionally calls for completing correlation admissibility, valuation sanity, selection/failure/tie rules, bootstrap interval/reliability, timeout scaling and pilot-dependent numerical settings; this numerical issue is only one part of that broader sign-off.

## Evidence and gate

Team reported the latest local Python 3.14 targeted and full-regression suites passed, but this reviewer has not inspected the JUnit report, exact interpreter/dependency snapshot, source hashes, or working-tree state. Those are required before formal reproducibility certification. No locked-test or unblinding activity is authorized.

Public repository pre-write review: This note contains only Branch B-permitted observable-side protocol requirements, public shared validator/fixture behavior, implementation findings and team-reported test status. It contains no generator code, hidden configuration, generator-owned seeds, latent labels, sealed ground truth, hidden condition mappings or side-channel analysis. It is safe for the public review branch.
