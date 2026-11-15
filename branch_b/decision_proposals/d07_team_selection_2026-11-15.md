# Branch B D07 team confirmation — November 15, 2026

**Team response:** Branch B confirmed D07 after approving D08 and D15. This records acceptance, at the **Branch B proposal level**, of the existing general numerical-comparison candidate in `week3_numerical_rules_proposal.md`.

**Status:** Team-selected proposal, **not** project-lead authorization, scientific freeze, production implementation, or change to the public `governance/freeze_registry.csv`. The numerical-tolerances registry entry remains pending.

## Confirmed candidate comparisons

Proposed common absolute tolerance: `tau_num = 1e-12`, for normalized matrix/ultrametric numerical validity and the unresolved-tree **output-height** comparison convention.

- Symmetry validity: `abs(D[i,j] - D[j,i]) <= tau_num`.
- Zero-diagonal validity: `abs(D[i,i]) <= tau_num`.
- Ultrametric inequality validity: `D[i,j] <= max(D[i,k], D[k,j]) + tau_num`.
- Candidate extracted-height tie comparison: `abs(h_a - h_b) <= tau_num`.

These are **comparison predicates**, not permission to repair invalid inputs. The separately team-approved, explicitly specified Option B canonicalization below applies **only after** an input passes the required validity predicates. Invalid inputs retain their applicable registered failure handling.

## Critical distinction from D04

D04's approved averaged min-max Jacobian is defined using **exactly equal working edge weights** at a tied level. The D07 candidate tolerance for **extracted output tree heights** is a separate numerical-convention proposal. This team confirmation **does not authorize** grouping near-equal D04 working weights into exact ties, replacing the exact D04 averaging measure, or changing the approved D04 algorithm. The relationship between near-equal output heights and unresolved-tree serialization still requires explicit source-conformance and project-lead review.

## D07 Option B — additional team-approved proposed canonicalization (2026-11-15)

**Branch B approved Option B at team-proposal level, subject to Project Lead source-conformance review, not a freeze.**

For a normalized input dissimilarity matrix `D`, first apply the existing required numerical validity checks, including the proposed symmetry predicate `abs(D[i,j]-D[j,i]) <= tau_num` and diagonal predicate `abs(D[i,i]) <= tau_num`, with `tau_num=1e-12`. Never canonicalize a matrix that fails a required validity check as a means of rescuing it.

Only after those checks pass, construct the **computational** matrix `Dcanon` by:

- For each distinct pair `i != j`, set `Dcanon[i,j] = Dcanon[j,i] = (D[i,j] + D[j,i]) / 2`.
- Set `Dcanon[i,i] = 0` exactly.
- Apply the **existing distinct-pair positive reciprocal-denominator/near-zero rule** to the resulting canonical off-diagonal entries, not to an arbitrarily chosen original triangle. In current development conventions, a required canonical distinct-pair denominator `<= 1e-12` is rejected as `DEGENERATE_DISTANCE`; this numerical threshold is not newly chosen here.
- Do not floor a denominator, inject jitter, discard a distinct original pair, or substitute one triangle.
- The canonicalization must preserve the approved geometry, common-normalization role and processing order; its implementation placement relative to existing normalization requires Project Lead/source-conformance verification rather than an unreviewed pipeline rearrangement.

**D04 remains unchanged:** exact tie averaging uses precisely equal optimized working edge weights. The `1e-12` numerical comparison tolerance does not group near-equal D04 working weights.

**Remaining scientific interface review:** Project Lead must determine the applicable validator/fitter conformance, numerical rounding/boundary behavior, and the already-proposed extracted output-height comparison/serialization convention. This team decision does not activate production code or assert a final tree-height policy.

**Synthetic verification required under actual Python 3.14:** cases with symmetry and diagonal residuals below, equal to, and above `tau_num`; canonical denominators just below/at/above the established minimum; transposition and joint row/column relabeling invariance; no perturbation of D04 exact working-weight tie behavior. Archive environment, tests and failure provenance.

## Next approval and evidence gates

1. Confirm with the Project Lead that the team-approved Option B input canonicalization, numerical predicates and candidate output-height comparison convention comply with the controlling protocol, existing freezes, registered normalization, and required timing.
2. Resolve the remaining precise implementation placement, floating-point boundary behavior, and output-tree height/serialization conformance; do not invent a new scientific rule during implementation.
3. After authorization, update the corresponding numbered numerical-rule/Common-Fitter record and registry with actual approval, version and checksum.
4. Verify exact boundary, below-boundary and above-boundary behavior in the required Python 3.14 environment, retaining JUnit and environment evidence.

D08 and D15 remain separately team-approved proposed selections; D01–D06 are unchanged. The production Common Fitter remains fail-closed. No calibration, locked-test processing or unblinding is authorized.

**Public shared-repository content check:** This record contains only Branch B-permitted observable-side candidate numerical specifications, the user-confirmed team decision, public validator behavior and procedural review gates. It contains no hidden generator implementation, restricted configuration, generator-owned seeds, latent labels, true hierarchy, sealed evaluation information or side-channel inference. It is safe for public disclosure.
