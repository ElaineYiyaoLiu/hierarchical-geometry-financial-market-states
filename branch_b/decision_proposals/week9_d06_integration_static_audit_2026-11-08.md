# Week 9 D06 source-level integration audit and handoff

Status: static audit and implementation-ready contract notes only. No scientific executable code changed; no Python test or optimizer run. Uses only public Branch B source and approved observable methods. No complete fitter or pipeline certification is implied.

## Source evidence inspected

- `branch_b/bootstrap/checked.py`
- `branch_b/recovery_pipeline/pipeline.py`
- `branch_b/recovery_pipeline/checked_integration.md`
- `branch_b/fitters/gradient_descent.py`
- `branch_b/draft_cards/gradient_descent_common_fitter.md`
- `branch_b/decision_proposals/week9_objective_gradient_golden_spec_2026-11-08.md`

## Confirmed existing interfaces

1. The checked bootstrap evaluator draws train/validation/test index arrays and supplies repeated-row data to `pipeline.run_checked()`. Fit-row labels identify *draw occurrences*, not original IDs.
2. `bind_bootstrap_draw()` correctly retains the mapping from each draw-occurrence label to its canonical original ID. This is provenance, not yet the distinct-leaf scientific representation.
3. `RecoveryPipeline._run()` fits preprocessing on the resampled training rows; transforms validation/test rows; obtains geometry-parameter candidates from transformed training data; selects candidates on validation fits; and fits test only after valid validation selection.
4. `RecoveryPipeline._fit_split()` constructs a native dissimilarity, normalizes it, and calls `fitter.fit_with_sample_order(normalized, sample_order=..., random_seed=...)`; it passes no original-ID multiplicity vector.
5. The checked fit validator requires returned tree/matrix identities to match the caller-supplied sample order exactly; simply passing duplicated original IDs would not satisfy that checked contract.
6. `bound_lca_stability()` currently validates the returned bootstrap tree against draw-occurrence labels, whereas approved D06 fitting must return distinct original leaves.
7. The registered scientific fitter is still a stub; the development configuration in `branch_b/fitters/gradient_descent.py` retains superseded D05 defaults (1e-8, patience 10). The approved card specifies 1e-6 and patience 5. This document does not patch executable behavior.

## Required data-flow contract for approved D06

For each split and draw, maintain *both* representations:

- **Occurrence representation**: draw index array, independent fit-row labels, canonical original-ID mapping, repeated input values in drawn order, stochastic draw seed and attempted-fit provenance. This drives any stage whose approved behavior is defined on the actual resample, such as training preprocessing estimation.
- **Distinct-original-ID representation**: active canonical original IDs (each appears once), strictly positive integer multiplicities, and an aligned distinct-row transformed feature matrix and dissimilarity matrix. This drives the approved D06 complete-graph fitter and original-ID-labeled output tree.

The boundary between the two representations must be explicit. The original-ID order must be derived from the trusted canonical input/manifest and the draw mapping, not from a predicted tree or hidden information. A fixed ordering convention must not affect the scientific results; test permutation equivariance.

A proposed interface shape for later engineering review, not a change to frozen API:

    fit_with_original_multiplicities(
        normalized_distinct_dissimilarity,
        *,
        original_sample_order,
        multiplicities,
        random_seed=None,
    ) -> FitResult

If another interface is chosen, it must still preserve these semantics and use the checked structural validation on distinct original IDs. Do not overload the existing `sample_order` with duplicate original IDs.

## Preserve resampling effects through preprocessing/geometry

- Train preprocessing must retain exactly the effect of the resampled training multiset. An equivalent frequency-weighted estimator on distinct original train rows is acceptable only *after* equivalence is demonstrated for each preprocessor and its edge cases.
- Validation parameter selection must continue to use the approved validation objective/criterion and its frozen split roles. Do not select a candidate from duplicated-occurrence fits and silently substitute different distinct-identity fits as if selection were unchanged.
- For a geometry evaluated pointwise from transformed feature vectors, repeated transformed feature rows are identical for the same original observation; a distinct-row representation may therefore preserve each pairwise distinct dissimilarity. This is a property to verify for every registered geometry, not an assumption for all geometry factories.
- For any normalization using the maximum finite off-diagonal dissimilarity, an occurrence-level matrix can include zero duplicate distances. A correctly constructed distinct-identity matrix omits those self-duplicate edges. Prove that normalization of the intended distinct pairs remains consistent (including degenerate cases) before reusing prior scalars.
- The fitter alone uses one vertex per active distinct ID and the approved pair weights q_ij=m_i*m_j, soft masses S_i=sum_k m_k*sigma(5*(u_ij-u_ik)), and W=sum_{i<j}m_i*m_j. There are no same-original-ID reciprocal edges. Do not replace product multiplicity weights with minimum weights or leave soft masses unweighted.
- The output ultrametric and tree must be indexed only by distinct original IDs, with the original draw occurrence mapping retained separately for audit and stability comparison.

## Static blockers (not permission to invent scientific rules)

1. The current `run_checked` signature does not carry split multiplicity vectors or the dual occurrence/distinct representation.
2. The current bootstrap stability binding expects occurrence-label tree leaves; it must be adapted to distinct original tree leaves while preserving the protocol's definition of common original observations and average-rank ties.
3. There is not yet an approved executable outcome for W=0 / fewer than two distinct active observations, nor finalized bootstrap minimum-success and minimum-common-observation thresholds. Keep these gates open; do not pick a failure code by convenience.
4. The exact source-conformant soft-area construction, D04 exact tied min-max Jacobian, and Python 3.14 conformance still require validation.
5. No pilot-frozen timeout value is present here; do not construct one from performance or metadata.

## Ready-to-implement non-scientific tests once Python 3.14 is available

- A small draw such as indices [0,0,1,1,1,2] must preserve six occurrence labels, three distinct original IDs, multiplicities [2,3,1], and pair weights [6,2,3], W=11.
- Verify canonical-original-ID mapping is invariant to occurrence-label renaming; reject missing/extra/duplicate *distinct* IDs in the returned fit.
- Compare repeated-row training preprocessing with equivalent multiplicity-weighted distinct-row formulas on nondegenerate and degenerate synthetic rows.
- Verify validation selection completes before test processing; failed attempts retain input draw, seed, failure reason, and diagnostic data.
- For every geometry, compare distinct-pair dissimilarities computed on repeated rows and unique transformed rows under controlled synthetic inputs, without applying arbitrary jitter or zero-denominator flooring.
- Verify all active multiplicities equal one reduces the objective to ordinary D01.
- Verify timeouts are observed only after an actual deadline expiry, with no approximate tied-gradient fallback.
- Verify mathematical golden cases and objective derivatives against the separate Week 9 reference specification.

## Safe handoff and evidence requirements

When the Python 3.14 machine is available: implement on a reviewable branch, capture the exact interpreter version, dependency lock/freeze, commit SHA and configuration; run the targeted identity/preprocessing/geometry tests first, then D01/D06 objective and D04 gradient tests, then checked end-to-end integration. Record successes and failures with SHA-256 and provenance. Do not claim that documentation or synthetic stub tests constitute approval for official pilot, blind validation or locked-test execution.

This static audit deliberately does not change approved method choices, the failure registry, protocol gates, or repository schemas.
