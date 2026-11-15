# D12 — Branch B team-approved bootstrap reliability framework

**Team decision (November 15, 2026):** Branch B approves the proposed **fixed-attempt bootstrap reliability framework**: explicitly preserve unsuccessful attempts, enforce minimum successful attempts, minimum distinct common observations, and a maximum failure fraction. Numerical thresholds remain reserved to the **authorized pilot-dependent freeze**.

**Status:** Team-approved proposed **structure only**. No numeric reliability thresholds, failure-code mapping changes, D13 production integration, pilot authorization, project-level approval, or scientific freeze is implied.

## Confirmed framework

For a prespecified fixed attempted-bootstrap budget `B`, let `B_s` be the number of successful attempts under the eventually approved success/failure predicates and `B_f = B - B_s`. Preserve the complete attempt ledger including seeds, original resampling identities, success status, failure codes, and diagnostics. The reported failure fraction is `B_f / B`; never replace `B` with `B_s` in its denominator.

Require all of the following for an eligible support decision:

1. `B_s >= B_min`, where the **numeric** minimum successful-attempt count is pending.
2. The applicable distinct-original-identity common-observation requirement `n_common >= n_min` is satisfied in the precise protocol-defined comparison scope, with its **numeric** minimum and any across-replicate aggregation semantics still subject to authorized specification.
3. `B_f/B <= f_max`, where the **numeric** maximum failure fraction is pending.

If any required reliability condition fails or cannot be evaluated under the approved rules, the support decision is **indeterminate**, never automatically supported or not supported. Computation of an interval alone cannot override this outcome. Report failures and required failed-fit sensitivity separately, without reclassifying unsuccessful attempts as successes.

## Relationship to already selected D13

D13's team-selected calculation uses successful `Q_b = S_b - min(D_b,1)` scores, secondary resampled means, 10,000 resamples and the 250th/9750th nearest-rank endpoints for a nominal 95% interval. These computational choices do not define `B_min`, `n_min`, `f_max`, establish interval coverage, or bypass the D12 reliability gate.

## Pending scientific and operational decisions

- Pilot-authorized thresholds `B_min`, `n_min`, `f_max` and their permitted evidence/justification.
- Exact common-observation scope, boundary/equality behavior for any per-replicate eligibility check not yet prescribed, and failure-code handling under the governing registry.
- Approved failure-penalized sensitivity score and statistical reporting details; do not silently assign a penalty value.
- Final project-lead review and registered bounded/pilot freeze with version, checksum, and provenance before confirmatory use.

The current production Common Fitter stays fail-closed; no pilot processing, calibration, locked test, unblinding, or protocol revision is authorized.

**Public Branch B pre-write check:** The actual text consists solely of the user-confirmed Branch B D12 choice, public observable-side reliability definitions and unresolved approval gates. It contains no hidden generator, hidden conditions, generator-owned seeds, latent labels or true hierarchy, sealed results, or side-channel inference. This note is permitted for Branch B and safe for public repository disclosure.
