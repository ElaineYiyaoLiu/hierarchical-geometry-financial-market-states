# Checked recovery and bootstrap integration

The checked entry points add structural result validation and explicit sample identity binding. They do not approve a method, certify an ultrametric, authorize a bank, or determine whether a bootstrap interval is reliable.

## Entry points

- `RecoveryPipeline.run_checked(...)`: requires external `validation_sample_order` and `test_sample_order` lists. Every validation fit is checked before selection; the test fit is checked before return.
- `run_checked_recovery_pipeline_bootstrap(...)` in `branch_b.bootstrap.checked`: requires canonical original sample orders for each input split and independent validation/test fit-row label orders. Every attempted fit routes through `run_checked`; there is no fallback to generic `run`.
- `bound_lca_stability(...)`: checks both trees against the externally supplied orders before invoking the existing LCA statistic.
- `bind_bootstrap_draw(...)`: maps fit-row labels to original sample IDs using an explicit integer index draw. Repeated original IDs remain repeated entries.

Generic `RecoveryPipeline.run`, the older `run_recovery_pipeline_bootstrap`, and the arbitrary-callback bootstrap engine remain available for development fixtures. Their successful returns are not evidence of scientific output validity. Do not use the generic path as a substitute when checked identity/result validation is required.

## Named fitter interface

Checked processing requires an object with the configured `fitter_id` and:

```python
def fit_with_sample_order(
    self, dissimilarity, *, sample_order, random_seed=None,
) -> FitResult:
    ...
```

The dissimilarity rows/columns and returned ultrametric use exactly this supplied order. The returned tree must name the same leaves in that order. The order passed to the fitter is a defensive copy. A reordered, missing, extra, or duplicate output identifier is rejected, not silently sorted or relabeled.

The complete scientific Common Fitter has not been implemented. The named interface is exercised with synthetic stubs. Adding this interface does not select its objective, positivity map, initialization, or weighting rules.

## Structural boundary

Checked fits must return `FitResult`, a real numeric finite matrix with the required dimensions, dictionary diagnostics, and a tree satisfying the existing shared tree schema and Branch B structural validator. A nonfinite fitted matrix raises `NUMERICAL_FIT`; schema/order errors raise `OUTPUT_SCHEMA`; existing structural-tree failures retain their existing codes. Invalid external canonical orders or index draws are input errors.

The shared tree schema is loaded from `interface_package/branch_b_output.schema.json`; it is not copied or modified. A runtime package using these checks must include that schema and its recorded provenance, as well as the existing jsonschema dependency. The older four-file packaging snapshot intentionally does not contain the complete checked pipeline.

These checks do **not** establish matrix symmetry, ultrametric inequalities, tree/matrix numerical consistency, approved comparison tolerances, a complete support statistic, or a frozen configuration. The pipeline's pre-existing normalization checks are unchanged and do not become approved scientific conventions merely because this new path uses them.

Checked internal results include `result_validation: structural_checks_only` and `scientific_authorization: false`. These are internal records, not fields to insert into a frozen shared output schema. The existing output builders and eventual exchange validator remain separate boundaries.

## Bootstrap identities and failures

Original sample orders must come from the verified input/manifest, not the fitted tree. This API validates the association against supplied orders; it does not authenticate the manifest or prove the caller supplied the correct one.

The independent fit label lists name draw positions and must match the respective resampled split lengths. They are bookkeeping labels, not new original observations. Each checked result records the explicit validation/test fit-label-to-original-ID mappings, training original IDs, and existing draw multiplicities.

Repeated rows still enter the geometry and fitter unchanged. No row, edge, or failed attempt is removed; no jitter, denominator floor, alternative weighting, or replacement draw is introduced. The audit's duplicate-bootstrap/reciprocal-weight conflict remains unresolved. A synthetic counterexample now checks that the existing fitter validator rejects the repeated-row zero distance under both Euclidean and Chebyshev mappings; the test does not prescribe a repair.

The generic engine still preserves every attempted replicate and its evaluator seed. A failed checked fit returns no result and retains its failure record, seed, and original index arrays. Canonical original orders and input/configuration provenance must be retained separately to interpret those failure indices. Structural success alone must not be counted as a protocol-valid scientific success until the remaining numerical, support, reliability, and authorization checks are implemented and approved.

## Test staging

Both pipeline entry points now convert and transform test values only after validation selection returns a valid index. Invalid indices cannot reach test conversion, transformation, geometry, or fitting through these entry points. A nonfinite test split is consequently rejected after validation selection, before test geometry. This changes staging, not the selection criterion or failure code.

This guarantee concerns calls made by the pipeline. It is not a sandbox for arbitrary callbacks with external references, proof that a preprocessor preserves row order internally, or a claim that a bootstrap adapter never reads its source test array while constructing resamples. Complete scientific isolation and authorization require the remaining runner integration.

## Verification

Run the synthetic regression suite under the required interpreter:

```sh
python3.14 -m pytest branch_b/recovery_tests/test_checked_integration.py -q
```

The cases include malformed fits, external order mismatches, forbidden unchecked fallback, delayed test access, repeated-ID mappings, preservation of the existing random draw sequence, and the unresolved duplicate-row conflict. Production seeds, bootstrap counts, interval methods, and numerical tolerances are not chosen by these fixtures.
