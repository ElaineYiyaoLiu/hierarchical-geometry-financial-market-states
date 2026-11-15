# Branch B D07 team confirmation — November 15, 2026

**Team response:** Branch B confirmed D07 after approving D08 and D15. This records acceptance, at the **Branch B proposal level**, of the existing general numerical-comparison candidate in `week3_numerical_rules_proposal.md`.

**Status:** Team-selected proposal, **not** project-lead authorization, scientific freeze, production implementation, or change to the public `governance/freeze_registry.csv`. The numerical-tolerances registry entry remains pending.

## Confirmed candidate comparisons

Proposed common absolute tolerance: `tau_num = 1e-12`, for normalized matrix/ultrametric numerical validity and the unresolved-tree **output-height** comparison convention.

- Symmetry validity: `abs(D[i,j] - D[j,i]) <= tau_num`.
- Zero-diagonal validity: `abs(D[i,i]) <= tau_num`.
- Ultrametric inequality validity: `D[i,j] <= max(D[i,k], D[k,j]) + tau_num`.
- Candidate extracted-height tie comparison: `abs(h_a - h_b) <= tau_num`.

These are **comparison predicates**, not instructions to project, round, edit or silently repair inputs. Invalid required comparisons retain their applicable registered failure handling.

## Critical distinction from D04

D04's approved averaged min-max Jacobian is defined using **exactly equal working edge weights** at a tied level. The D07 candidate tolerance for **extracted output tree heights** is a separate numerical-convention proposal. This team confirmation **does not authorize** grouping near-equal D04 working weights into exact ties, replacing the exact D04 averaging measure, or changing the approved D04 algorithm. The relationship between near-equal output heights and unresolved-tree serialization still requires explicit source-conformance and project-lead review.

## Remaining unresolved interface interpretation

Existing shared validator and registered fitter matrix checks both default to `1e-12`. Nevertheless, the currently tested implementation can accept nearly asymmetric matrices and inspect only upper-triangle elements as optimizer denominators, making eligibility near `1e-12` orientation dependent. D07 team confirmation alone does **not** approve choosing upper-only, lower-only, arithmetic-average or another canonicalization policy, nor does it approve a new reciprocal-denominator or near-zero rule. These remain implementation/scientific reconciliation questions for project-lead sign-off.

## Next approval and evidence gates

1. Confirm with project lead that D07's numerical predicates and output-height comparison convention are consistent with controlling protocol, existing approved freeze records and required timing.
2. Resolve accepted matrix residuals, reciprocal-denominator eligibility and candidate output-tree height treatment; do not invent an answer in implementation.
3. After authorization, update the corresponding numbered numerical-rule/Common-Fitter record and registry with actual approval, version and checksum.
4. Verify exact boundary, below-boundary and above-boundary behavior in the required Python 3.14 environment, retaining JUnit and environment evidence.

D08 and D15 remain separately team-approved proposed selections; D01–D06 are unchanged. The production Common Fitter remains fail-closed. No calibration, locked-test processing or unblinding is authorized.

**Public shared-repository content check:** This record contains only Branch B-permitted observable-side candidate numerical specifications, the user-confirmed team decision, public validator behavior and procedural review gates. It contains no hidden generator implementation, restricted configuration, generator-owned seeds, latent labels, true hierarchy, sealed evaluation information or side-channel inference. It is safe for public disclosure.
