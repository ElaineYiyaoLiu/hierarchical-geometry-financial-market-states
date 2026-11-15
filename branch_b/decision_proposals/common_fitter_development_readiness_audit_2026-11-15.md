# Branch B Common Fitter — development readiness audit (2026-11-15)

**Status:** source-level review of the development branch; not a method freeze,
scientific certificate, production release, official pilot authorization, or
permission for locked-test processing or unblinding.

**Scope:** Branch B-visible code and approved candidate decisions D01–D06.
No generating materials, hidden conditions, sealed truth, or restricted
evaluation information were consulted. No project method or schema is changed.

## Evidence boundary

The Branch B team reported that the targeted development suites and the most
recent full regression suite passed under local Python 3.14. This reviewer
inspected the sources remotely but did **not** execute those tests or verify
the underlying JUnit XML, exact interpreter/dependency snapshot, Git tree
status, or file checksums. The user-reported result is not represented as an
independently reproduced execution.

## Source findings

| Area | Current code | Status and review needed |
| --- | --- | --- |
| D01/D02/D06 objective | `fitters/d01_d06_objective.py` computes the fixed-Delta reciprocal objective, beta=5 soft masses, multiplicity-product weights, and independent-pair gradient | Development implementation and synthetic tests exist; final paper/code source-conformance review outstanding |
| D03 | `fitters/d03_amsgrad.py` uses projected nonnegative AMSGrad with raw v-max then bias correction, unmasked gradients, and approved constants | Development tests reported passing; final component-to-interface review outstanding |
| D04 | `fitters/exact_tie_dp.py` and `fitters/d04_gradient_adapter.py` implement hierarchy-balanced exact ties and Jacobian transpose | Small synthetic oracles reported passing; full combinatorial proof and feasible larger-tie runtime/memory remain critical |
| D05 | `fitters/d05_stopping.py` implements 1e-6/5-update convergence and 1,000 completed-update cap | Correct development settings; production class still advertises historical 1e-8/10 |
| D06 | `fitters/development_d06_fitter.py`, `recovery_pipeline/d06_checked_handoff.py` and `d06_development_splits.py` bind original identities, positive masses, and repeat-row training preprocessing | Development path only; old `bootstrap/checked.py` still uses occurrence-labeled `RecoveryPipeline.run_checked` |
| Tree export | `fitters/development_tree_extraction.py` produces exact-height multifurcations and zero-length branches; `development_tree_fit.py` returns a checked FitResult | Candidate parent-minus-child height interpretation remains subject to review |
| Tree consistency | `fitters/development_tree_consistency.py` reconstructs candidate cophenetic heights | Exact equality is justified for chosen synthetic binary-exact fixtures only; no general numeric acceptance policy approved |
| Failure accounting | `fitters/development_optimizer.py` separates optimizer deadline from D04 deadline; `bootstrap/development_attempt_diagnostics.py` records detail in a sidecar | Scientific code mapping and shared-schema integration remain open |
| Production entry point | `fitters/gradient_descent.py` `fit()` raises `ConfigurationRequired` | Deliberately fail-closed; has not been activated or reconciled with development D05 defaults |

## Prioritized engineering and scientific checks

**E1 — Numerical interface reconciliation (engineering plus any necessary
protocol approval).** The registered `validate_normalized_input` accepts
symmetry/diagonal residuals up to 1e-12, but the D06 development adapter
subsequently takes only canonical upper-triangle values and reconstructs exact
symmetric working matrices. Record what happens to admitted near-symmetric
inputs and cover it with synthetic boundary tests. Do not silently select
another comparison tolerance or reinterpret the canonical geometry rule.

**E2 — Independent numerical tree check (engineering; tolerance pending).**
Structural output checks alone do not establish numeric agreement with the
ultrametric. The independent candidate reconstruction checks chosen exact
synthetic cases, but parent-minus-child subtraction and floating summation can
differ in general real-valued outputs. Preserve exact tests and do not apply
exact equality universally without an approved numerical comparison policy.

**E3 — Complete D06 production integration (engineering dependent on
protocol).** Existing checked bootstrap execution still uses occurrence-row
labels and cannot be treated as the approved distinct-original-identity D06
fit. Reconcile validation/test identity-bound trees and the existing bootstrap
hierarchy-support statistic under the governing protocol; do not invent a
replacement statistic or change its thresholds.

**E4 — Failure mapping/provenance (engineering dependent on registry).**
Maintain the distinction between actual optimizer deadline expiry, D04 expiry,
iteration-cap nonconvergence, numerical errors and actual memory exhaustion.
The development sidecar does not alter the shared failure export schema. Apply
only authorized codes and diagnostics in the eventual scientific entry point;
retain all attempts, including failures.

**E5 — Feasibility (required evidence, no method change).** D04 exact DP can be
memory/time intensive. Prior team-reported six-vertex fully tied development
benchmark reached a real 60-second development deadline with about 3.17 GB
peak memory; seven-vertex worst-case completion remains unverified. This is
not an approved pilot timeout, not an early complexity cutoff, and not grounds
for approximate tie averaging.

**E6 — Reproducibility/freeze gate.** Capture and inspect actual CPython 3.14
version, dependency lock/freeze, commit and dirty-tree state, relevant source
hashes, full JUnit result including failures and skipped tests, and
representative failure records. A verbal 'all passed' is not a complete
provenance archive. Finish project-lead conformance and freeze review before
activating the registered Common Fitter.

## Decisions and approvals still outside this audit

- Pilot-dependent actual timeout duration.
- The W=0 and inadequate-distinct-observation outcome and approved
  bootstrap reliability/success thresholds.
- Outstanding correlation near-constant admissibility and general numerical
  tree-comparison convention, insofar as not already resolved by controlling
  protocol/freeze records.
- Complete Common Fitter selection, pilot configuration freeze and any
  applicable source-conformance sign-off.
- Locked-test processing and unblinding: **not authorized**.

## Recommended next action

First add **synthetic tests** documenting current near-symmetry / upper-triangle
behavior without changing acceptance rules. Then prepare a conformance matrix
and inspect the actual Python 3.14 evidence artifact bundle. Keep the official
production fitter fail-closed throughout this development review.

**Public disclosure check:** This document contains Branch B-permitted
observable-side design, development code references, team-reported synthetic
tests and engineering risk analysis only. No restricted generating information,
generator-owned seeds, hidden labels, true hierarchy, sealed truth, hidden
conditions, or protected side-channel material is included.
