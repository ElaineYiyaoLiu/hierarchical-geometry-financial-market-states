# Branch B pre-pilot source reconciliation (2026-10-18)

Scope: read-only reconciliation of the public Branch B registry against the controlling Branch B packet and weekly schedule. This note is not a protocol revision, freeze record, or approval. It contains no pilot observations or restricted generating information.

## Verified source observations

- The public `branch_b/geometry_registry.md` registers `valuation_chebyshev`, `standardized_euclidean`, and `correlation_distance`, plus `gradient_descent_ultrametric` as a candidate fitter.
- The registry says the correlation near-constant/admissibility rule is pending an explicit Branch B meeting. Prior Branch B discussion reports a decision to use 0.95 for a confidence interval, but that discussion alone does not specify or certify the complete frozen admissibility implementation.
- The registry records train-only coordinate standardization for Euclidean and valuation-Chebyshev, no coordinate transformation for correlation, and post-geometry normalization by the maximum finite off-diagonal distance.
- The registry describes the valuation-geometry favorable-feature sanity criterion as open.
- The weekly schedule requires completed executable geometry/fitter cards, golden tests, valuation-geometry sanity evidence, and the frozen geometry-neutral Common-Fitter selection rule before pilot exchange (Week 3); Week 4 pilot processing and Week 5 calibration depend on subsequent formal gates.

## Required follow-up (no automatic scientific changes)

1. Locate the approved correlation admissibility decision and implementation; reconcile the registry only against that controlling evidence. Do not assume 0.95 is the full rule.
2. Locate the valuation-geometry executable card and required sanity-gate result; if missing, flag the pilot exchange as unverified.
3. Locate the actual frozen Common-Fitter selection rule and its missing-data/failure/tie behavior. The path `branch_b/common_fitter_selection_rule.yaml` returned not found; this does not prove absence at another path.
4. Verify Python 3.14 CI logs and golden reports before asserting implementation readiness. No scientific computation or Python test was run for this note.
5. Obtain the signed pilot exchange, pilot exit, and Gate 5A evidence before official pilot/calibration processing.

## Boundaries

Do not derive scientific status from filenames or side channels. Do not inspect hidden configurations, generator-owned seeds, true hierarchy, latent labels, or sealed truth. Keep missing evidence labeled **unverified**, not **failed**. All future code changes require protocol-versus-implementation classification and a separate public-content pre-write review.
