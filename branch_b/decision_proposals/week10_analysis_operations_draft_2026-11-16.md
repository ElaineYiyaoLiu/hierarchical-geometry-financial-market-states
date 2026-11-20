# Analysis and Operational Decision Drafts

Prepared for PL review, November 16, 2026. These are concrete review proposals, not adopted scientific rules. No frozen parameter, seed rule, schema or evaluation definition changes. The labels below do not recover or replace the missing D16/D17 questions.

## Paired Recovery Reporting

Carry the packet's primary estimand into the analysis specification: for each prespecified valuation/comparator contrast and reporting cell, use the same scheduled Monte Carlo realizations and `D_r = A_val,r - A_comparator,r`. Apply the packet-prescribed accuracy-zero failure convention before calculating D. Retain all scheduled replicates in the primary denominator. Missing submissions must be reconciled with the inventory/failure rules rather than removed as complete-case selection.

Report mean(D), scheduled count, each geometry's failures, interval/level/method, and a separately labeled common-success-only sensitivity with its actual denominator. Observations, pairs and triplets are not independent Monte Carlo replicates. A successful-only contrast does not replace the primary failure-inclusive contrast.

### Proposed Interval Decision for Explicit Approval

For an implementation-ready candidate, use a two-sided 95% paired Monte Carlo t interval `mean(D) +/- t_(R-1,0.975)*s_D/sqrt(R)` for each prespecified cell/contrast, with sample standard deviation using R-1. The source of uncertainty is independent Monte Carlo realizations of the frozen procedure. This is an approximate interval for general bounded contrasts, not an exact finite-sample guarantee. R<2, incomplete scheduled inventories and undefined summaries require an explicit ineligible/incomplete result, not a fabricated interval. A zero sample variance is reported explicitly and is not evidence of universal certainty.

This proposal is separate from D13's within-dataset support interval. It needs an explicit protocol decision, numerical implementation/edge-case review and freeze before locked-test generation. It cannot be selected using pilot recovery-effect direction or magnitude. No t-interval computation or production adoption occurred here.

### Claim Scope and Multiplicity

The default packet interpretation remains per-comparison reporting. Best-comparator, family-wide and confirmatory region claims require a separately approved procedure. A ready conservative candidate for broader claims is simultaneous Bonferroni t intervals over the entire prespecified set of M cell/contrast hypotheses, with critical value `t_(R-1,1-0.05/(2*M))` for each interval. Its simultaneous interpretation inherits the marginal intervals' assumptions/approximation; it is not a distribution-free guarantee. M, the full inventory, missing-cell behavior and the claim family must be fixed in advance. Do not reduce M after observing failures or unfavorable results.

For a prespecified region or deterministic region-selection rule, state its inventory reference and the packet-defined adjacency without publishing hidden mappings. A candidate conservative sufficient rule is: all required member cells satisfy the approved adjusted interval criterion excluding zero in the advantage direction, all meet the already justified prior minimum-effect criterion, and the prespecified sensitivity condition holds. Any alternative region aggregate or selection procedure requires its own complete definition. The intended rule and family remain proposed until approved. Regions discovered after viewing locked cellwise effects are exploratory.

Do not retrofit the historical minimum effect or choose a new effect value here. The old 0.05 proposal needs original rationale/approval/inspection chronology.

## Independent Null-Validation Specification

Separate threshold construction from independent decision-level validation. Preserve all scheduled outcomes and report supported, not-supported, indeterminate, failure and incomplete counts for each required geometry and family, plus the overall summaries. State the denominator for every rate and do not exclude indeterminate outcomes to improve apparent false-support performance.

The approval artifact must name the quantitative target error quantity, confidence-bound construction, level, tolerance, overall and family-specific conditions, family inventory and response to incomplete execution. Every required condition must pass. A failed acceptance rule keeps the affected support procedure reported but ineligible for confirmatory support claims; it does not authorize recalibration, method replacement or a new null family. This review supplies the executable decision structure; it does not invent missing numerical targets or tolerances. The exact D16/D17 source could address these or other questions, so its wording still needs verification.

## D12 Support Sensitivity

The packet's valid scores satisfy S in [-1,1], D>=0 and Q=S-min(D,1), hence Q in [-2,1]. The mathematical lowest admissible contribution is -2. For complete B-attempt execution, the failure-penalized point summary is `(sum_success Q_b - 2*B_failure)/B`. This is a derived bound, not a newly tuned penalty.

Retain the conditional successful-score point estimate and interval separately. Their interval is not an interval for this sensitivity summary. A complete sensitivity interval/decision method remains an explicit statistical decision; the point summary cannot by itself establish whether an interval-based support conclusion changes. Missing/unexecuted attempts remain distinguishable from observed fit failures. Numeric reliability thresholds stay at the packet-designated pilot/bounded gate.

## D14 Namespace Contract Candidate

This candidate has deterministic reference vectors in the closeout evidence. It is isolated from production and does not replace the existing development stream or choose a production master seed.

1. Encode the array `["HMG-B-SEED-CANDIDATE-v1", root_seed, tier, dataset_id, attempt_index, role]` with UTF-8 JSON, `ensure_ascii=True`, no optional whitespace, the displayed order, and a final newline absent. root_seed and attempt_index are nonnegative integers excluding Booleans. tier/dataset_id/role are nonempty ASCII strings. Restrict tier and role to a registered vocabulary before adoption.
2. Hash the bytes with SHA-256. Interpret the digest as eight unsigned big-endian 32-bit words and pass that sequence to NumPy SeedSequence. Use PCG64 explicitly and freeze the NumPy/BitGenerator versions.
3. Use distinct role labels for train draw, validation draw, test draw, evaluator and D13 secondary resampling. Separate observable tiers and opaque released dataset IDs. Do not use hidden condition identifiers, generator seeds or Python's built-in hash.
4. Derive each attempt directly. Record full namespace inputs and digest; replay must be independent of execution order. Keep an explicit common-random-number policy where geometries intentionally share draws. Distinct role labels do not by themselves prove statistical independence or a mathematical absence of hash collisions.
5. Freeze the encoding, vocabulary, source, reference vectors and error behavior only after explicit approval. Retain old run provenance under the old rule.

The existing development implementation draws split streams sequentially from a spawned child. The proposed candidate changes that derivation. It requires explicit acceptance before any production use; reference-vector generation is not approval.

## Timeout and Resource Decision Package

Use an approval record with these fields: observable benchmark input/configuration digests; size variables; hardware/OS/threads/memory; interpreter/dependencies; timed operation; included setup/preprocessing/D04/extraction stages; repeat count/statistic; observations; scaling formula and coefficients; safety factor; total workload and contingency; deadline accounting; failure mapping; authority and gate.

A shared monotonic fit deadline must explicitly govern nested operations if that is the selected contract. Preserve real elapsed expiry, iteration-cap nonconvergence, numeric errors and memory exhaustion as distinct observed causes under existing registered semantics. Do not convert memory guards to scientific TIMEOUT or approximate D04 averaging.

The proposed 2x golden runtime and B=500 require permitted operational measurements. The packet's floor of at least 100 primary bootstrap repetitions does not establish sufficient successes, precision or resources for B=500. D13's 10,000 secondary samples are a different count. Test-suite runtime is not a pilot fit benchmark. No new hardware measurement, scientific workload or timeout value is fabricated by this package.

## Decision Record Fields

For each proposed decision retain: source item, exact chosen text, formula/boundaries, allowed evidence tier, source/configuration versions, worked example, statistical limitations, actual approver/date, gate, approval checksum and freeze reference. This package leaves approval/freeze fields unfilled. It is ready for explicit decisions; it is not a signed approval instrument.

Project Boundary: actual content was checked for Branch B/public disclosure. Only public mathematics, permitted proposal text and operational requirements are included. No restricted experimental information is disclosed.
