# Branch B Implementation Review

Date: 2026-11-04. Scope: shared main, Kyle's PRs #12 and #14, and the Version 2 Branch B Packet, Sections 2.4 and Appendices C, D.2 and F. Status: engineering review completed; final method acceptance remains blocked.

## Sources and Findings

| Source | Inspected Revision | Finding |
| --- | --- | --- |
| Shared main | `eeeeeffc6c268328f9759ce8a7a3e22aca89de21` | `fit()` intentionally raises `ConfigurationRequired`; an executable optimizer and production termination dispatcher are absent. |
| PR #12 | `32c0167b654b0b1b36a942eb2fb661ceebd75aa9` | Correctly retains a `None` evaluator return as an unsuccessful attempt. This is a narrow accounting repair, separate from the multiplicity question. |
| PR #14 | `159bda5addcb4f316fab1ef201541fefeab49102` | Development graph and min-max/tie references, with a wrong triangle-test expectation and lossy input conversion. Additional scientific proposals remain unresolved. |

## Bootstrap: Preserve Identity, Specify the Objective

The packet requires repeated draws to remain resampling multiplicities and stability to compare distinct original observations. The checked development route already records occurrence-to-original mappings and rejects ambiguous cross-copy LCA relations. This establishes identity accounting, not an approved weighted fitting formula.

The concrete incompatibility is in `fitters/gradient_descent.py::validate_normalized_input`: duplicate observations can have zero off-diagonal distance, and the registered reciprocal-distance safety rule rejects any required distance at or below `1e-12`. Replacing zeros, dropping repeated draws, or silently selecting product weights would change the procedure.

Action for Branch B: finish D06 as one mathematical specification covering optimization vertices, preprocessing with repeated observations, pair coefficients, mass-aware soft cardinality, self-pairs, normalization, distortion and original-ID tree/stability projection. The existing investigation document is the starting point. The October 20 intake records a nonlinear-weighting concern; it does not select a formula. Branch B must provide the complete proposal for PL review before implementation/freeze.

PR #14's graph helper removes **all edges with weights <= 1e-12**, including small positive edges. Its PR description says exact-zero removal. Clarify that discrepancy explicitly before acceptance; this patch preserves its current development behavior. Removing zero edges is also not a multiplicity solution: for the synthetic matrix `[[0,0,2],[0,0,2],[2,2,0]]`, the positive-edge min-max transform gives distance 2 between the repeated occurrences. Any use of that result needs an approved treatment of identity and the objective.

## Termination: Follow the Current Card

The packet registry uses `NUMERICAL_FIT`, not `NUMERICAL_FAILURE`, and defines `TIMEOUT` by the frozen runtime limit. The current draft Fitter Card additionally states that iteration-limit nonconvergence is a numerical fit failure unless an explicit later pilot/freeze revision changes it. This is a candidate-card convention, not wording inferred from Appendix F alone.

Implementation instructions for the eventual optimizer:

1. Preserve the card's convergence tolerance, patience and iteration limit unless a separately approved revision changes them.
2. Report a nonfinite objective or optimizer state as `NUMERICAL_FIT`.
3. Report an exhausted iteration budget without convergence as `NUMERICAL_FIT` under the current card. Keep a separate diagnostic termination reason such as `iteration_limit`; use an existing schema-permitted diagnostics field.
4. Report `TIMEOUT` only when the applicable frozen runtime budget is exceeded. Use a monotonic clock; document timing scope and checks. A hard runtime guarantee needs interruptible execution or a supervising process, since a check between iterations cannot interrupt a stalled iteration.
5. Specify simultaneous-trigger precedence, exact deadline boundary, last-iteration convergence handling and cleanup before freeze. These are still review items, not choices made by this patch.
6. Exercise converged, iteration-limit-only, runtime-only, nonfinite and simultaneous-trigger cases using deterministic fake timing once the dispatcher exists. Preserve bootstrap attempts and their actual failure codes.

No matching implementation of an iteration-limit-to-`NUMERICAL_FAILURE` dispatcher was found in the inspected shared sources. If Kyle has a newer local optimizer, reconcile its exact commit before extending this review to it.

## Implemented Engineering Repairs

- Reject mixed Boolean entries and masked arrays before `np.asarray` erases their original meaning in the graph and min-max reference helpers. Seven synthetic regressions cover these boundaries; valid numeric behavior and graph thresholds are unchanged.
- Correct the three-leaf limiting-Jacobian test. Across six strict edge orderings, a pair's own edge controls its output four times and each other edge once, giving diagonal `2/3` and off-diagonal `1/6`. Existing forward finite-difference tests verify the individual strict Jacobians. This fixes the test expectation, not the unresolved general D04 averaging measure.
- Add the input regressions to the Python 3.14 workflow.

## Executed Verification

Actual environment: CPython 3.14.7, NumPy 2.5.3, pytest 9.1.1 and the existing output-development requirements. See `verification.json`, `environment.txt`, JUnit evidence and `SHA256SUMS` for exact versions, source fingerprints and artifact checksums.

| Revision | Full-Suite Result |
| --- | --- |
| Inspected main | 631 passed |
| Inspected PR #12 | 634 passed |
| Inspected PR #14 | 655 passed, 1 failed: incorrect triangle expectation |
| PR #14 plus these repairs | 663 passed |

The first environment setup omitted the existing `rfc3339-validator` requirement; those environment-related failures were resolved by installing the repository's declared requirements before the recorded verification runs. No Python version was substituted and no scientific or official bank was generated or processed.

## PL Review Prepared

The existing register audit, freeze reconciliation and eight-item A/PL closure queue were rerun. All 13 supplied evidence checksums verify; the overall 20-gate decision remains BLOCKED. These are current checks of existing public records, not a fresh verification of private Branch A execution or a signature.

| Item | Prepared Assessment | Remaining Evidence / Authority |
| --- | --- | --- |
| PR #12 accounting fix | Engineering tests passed | Maintainer review/merge; no scientific gate closure implied |
| PR #14 reference helpers | Bounded repairs provided | Review repaired code and the zero/near-zero description conflict |
| D06 multiplicity | Root cause and required formula fields identified | Complete Branch B proposal, PL review and approved freeze |
| Termination rules | Current packet/card reconciliation provided | Implement and test dispatcher; approve any proposed departure |
| General fitter acceptance | Not ready | Executable approved objective/optimizer, D04, source conformance, complete cards and scientific golden report |
| PL operational work | Current eight-item queue attached | Actual approvals, provenance and operational evidence specified in that queue |
| Final PL confirmation | Withheld pending prerequisites | Review exact final artifact versions, checksums, tests and applicable independent verification |

Suggested PL review disposition: accept these bounded engineering findings for discussion; keep scientific approval and final fitter/pilot acceptance pending. This is prepared text for Elaine's decision, not a signed approval. No approval, historical timestamp or freeze entry has been fabricated.

## Disclosure Review

The actual new patch and reports were inspected before sharing. They contain shared Branch B code, existing Branch B-visible rules, synthetic tests and permitted aggregate gate status. No hidden generator implementation, configuration, condition mapping, latent labels, true hierarchy, sealed truth, generator-owned seeds or revealing restricted paths are included. No frozen scientific parameter, evaluation definition, schema or approval record is changed.
