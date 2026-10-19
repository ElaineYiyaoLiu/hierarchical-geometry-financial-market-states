# Final development audit - 2026-10-19

**Disposition: not a clean integration pass. Two admission defects, one early-validation gap, and one failure-semantics conflict were reproduced.** The ordinary regression suite still passes. Neither that result nor the term "final audit" constitutes scientific runner certification.

Audited scientific/development source: `e6f2cfb6ec53470312f8b637f50c63d7b5d7a69a`.
Audit workflow: `.github/workflows/branch-b-final-audit.yml`, commit `e1a24e99137670bc51fa2c43ec74c9c3d3d47779`.

## Scope

Reviewed the new observable loader, checked output adapter/serializer/verifier, inventory reconciliation, structural result/tree validators, relevant checked-pipeline/bootstrap interfaces, input/output tests and guide, the current fitter refusal message, and the Common-Fitter Card. Rechecked the supplied Branch B Packet Sections 2.8-2.9 (pp. 25-26), Appendices C-D (pp. 58-61), and Appendix G (pp. 66-68); the Schedule remains the execution-order source, not a substitute scientific specification.

Six literal synthetic scenarios were executed against the pinned source: one well-formed control, a terminal node incorrectly declared internal, a masked matrix, a mixed Boolean/numeric matrix, nonfinite diagnostics, and constant-rank star trees. These are deliberately constructed interface probes, not statistical samples, experimental-bank processing, or scientific fitter runs. No source or outcome was inferred from restricted materials. No new scientific settings or approval records were changed.

The audit workflow reads only Branch B code and the shared interface package from the pinned checkout. It records observations and exits nonzero when it exposes an open boundary. Its failure is retained as evidence, not suppressed with expected-failure markers. The workflow is a historical reproducer: rerunning it continues to test this pinned source, not later fixes.

## Actual executions

| Execution | Source checked out | Run | Job | Result |
| --- | --- | --- | --- | --- |
| New synthetic boundary audit | `e6f2cfb6ec53470312f8b637f50c63d7b5d7a69a` | 39331465071 | 118330433091 | Completed probes; audit exits 1 with five flagged scenarios grouped into four findings below. |
| Existing repository-wide pytest suite | `e1a24e99137670bc51fa2c43ec74c9c3d3d47779` | 39331465072 | 118330433111 | 531 passed in 1.71 s. |

Both completed job logs show **CPython 3.14.8**. The audit explicitly checks Python major/minor and the actual Git checkout. The second revision adds only the audit workflow to the audited source; it does not modify the application or test modules. The audit probes are not part of pytest discovery and must not be added to its count.

- [Audit job and logs](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39331465071)
- [Ordinary regression run and logs](https://github.com/ElaineYiyaoLiu/hierarchical-geometry-financial-market-states/actions/runs/39331465072)

A separate comparison of the previously tested `82bef433fcbaa455e12bf4695f34ce46a34b7e96` with the audited source shows only README, transport-guide, and validation-report changes. Its historical 390 Branch B and 15 shared-validator passes remain evidence for their stated scope; this audit does not relabel those as new targeted-probe results.

### Observed probe results

| Synthetic case | Checked pipeline / structure | Outgoing transport | Interpretation |
| --- | --- | --- | --- |
| Well-formed control | Returned; selector called once | Prepared and verified | Harness and normal path operate. |
| Extra terminal node declared internal | Returned; selector called once | Prepared and verified | Structural admission defect F1. |
| Masked fitted matrix | Returned; selector called once | Prepared and verified; masked entry became ordinary float 1.0 | Representation-loss defect F2. |
| Boolean embedded among numeric matrix entries | Returned; selector called once | Prepared and verified; True became ordinary float 1.0 | Same representation-loss defect F2. |
| NaN in fitter diagnostics | Returned; selector called once | Rejected with OUTPUT_SCHEMA | Early-validation gap F3; final transport safeguard works. |
| Two structurally valid star trees | Both passed bound structural checks | Not an export probe | LCA stability raised DEGENERATE_TREE for constant ranks: F4. |

## F1 - High: declared internal nodes can be terminal nodes

Locations: `serialization/tree.py::validate_tree_edge_list`, `recovery_pipeline/result_validation.py::validate_bound_tree`, and their checked pipeline/output callers, relative to `branch_b/` at the audited source.

The synthetic tree declares three named sample leaves and two internal nodes. One declared internal node is attached to the root but has no children. All nodes are reachable and every non-root node has one parent, so the existing checks accept it. The graph actually has four terminal nodes, but only three are declared sample leaves. The shared JSON schema checks field types and lists; it does not supply the missing graph-semantic check.

The probe passed `run_checked`, reached validation selection, and passed record construction, preparation, and verification. Thus the defect is within the claimed structural scope, not one of the deliberately deferred numerical tolerances.

**Bounded repair:** require the graph's terminal-node set to equal the declared canonical leaf set and require declared internal nodes to have children. Reject an invalid representation; do not silently prune the extra node. Do not impose binary branching, a new minimum depth, or a new treatment of legitimate multifurcations or zero-length branches. Add an end-to-end rejection regression before selection and export.

## F2 - High: array coercion can erase missingness and invalid scalar types

Locations: `recovery_pipeline/result_validation.py::validate_finite_square` and `output/checked.py::complete_record_from_checked_pipeline`.

The validator calls `np.asarray(matrix)` before inspecting dtype and finiteness. The executed masked-array probe supplied a masked off-diagonal entry with finite underlying storage. The mask was not rejected. The outgoing adapter's `np.asarray(...).tolist()` then serialized the underlying value as an ordinary finite number.

A separate probe embedded Boolean True in a numeric nested matrix. Array conversion promoted it to a numeric dtype; the outgoing adapter serialized 1.0. The original invalid Boolean no longer existed by the time the shared JSON number schema saw the record.

Both cases survived the complete checked-pipeline-to-verifier path. Detached hashes correctly bound the resulting bytes, but cannot detect a representation change that happened before those bytes were prepared. Packet Section 2.9 prohibits missing/nonfinite matrix entries without documented failure; masking must not silently become an observation.

**Bounded repair:** inspect the supplied representation before coercion and reject masked/missing entries and Boolean matrix scalars under the existing real-numeric/no-repair contract. Preserve valid numeric values without choosing any tolerance, imputation, rounding, or missing-data policy. Keep the originally supplied malformed result available in failure evidence rather than relabeling its coerced value as valid.

## F3 - Medium: malformed diagnostics reach selection before the exporter rejects them

Locations: `recovery_pipeline/result_validation.py::validate_fit_result` and `output/checked.py::validate_development_output`.

The fit validator checks only that diagnostics is a dictionary. A synthetic NaN diagnostic passed the checked pipeline and reached the selector. The outgoing adapter correctly rejected it as OUTPUT_SCHEMA because the output is not finite JSON.

This is **not** a bypass of the final serializer: no prepared valid output was produced for this case. It demonstrates that a checked return is still not a guarantee of exportable diagnostics or a scientific success. The current generic callback-based bootstrap accounting must not be promoted to protocol-valid successful-fit accounting on that basis.

**Bounded repair:** validate the diagnostics intended for export against the established finite-JSON contract before they are used as checked candidate/output records, or explicitly separate internal diagnostic objects from the exchange-bound fields with an enforced adapter contract. Do not erase invalid fields, substitute a support decision, or choose a new statistical failure treatment to make export succeed.

## F4 - Medium, scientific disposition required: constant rank is reported as structural tree degeneracy

Locations: `support/stability.py::spearman_with_average_ties`, `bootstrap/checked.py::bound_lca_stability`, and `draft_cards/gradient_descent_common_fitter.md`.

Both literal star trees passed the bound structural validator with their independent expected sample orders. Their pairwise LCA-depth ranks were constant. The existing stability helper raised DEGENERATE_TREE with the message "LCA-depth ranks are constant".

The current Common-Fitter Card explicitly reserves DEGENERATE_TREE for structural invalidity and says a structurally valid unresolved star is not, by itself, DEGENERATE_TREE. Undefined rank correlation is therefore being conflated with an invalid tree. This code predates the new transport modules; the audit did not introduce or approve it.

**Required disposition:** record the undefined-stability state distinctly from structural invalidity and reconcile its code, bootstrap usability, support reliability, and interval consequences against the controlling failure rules. The audit does not choose 0 or 1 as the correlation, discard the replicate, retry it, or select a new failure category. The consequential downstream treatment requires the appropriate scientific decision or an already approved governing record.

## What the audit supports, and what it does not

The ordinary suite really passes under Python 3.14.8; that does not establish coverage of these new counterexamples. The well-formed audit control succeeds. The final outgoing path correctly rejects the nonfinite diagnostic. External checksum checking, canonical JSON, independently supplied identity expectations, and explicit inventory failure/missing/duplicate accounting remain implemented in the reviewed code. No claim is made that all their possible edge cases were exhaustively verified here.

The loader verifies its explicit input hashes/schema/row order. Receipt hashes bind a supplied manifest/configuration and declared source revision; they do not authenticate permission, prove the source was executed, or establish that the configuration and support values are scientifically correct. The guide already documents those limits and requires other run evidence. The transport is not a complete archive of train/validation/test provenance, candidate logs, or bootstrap attempts by itself.

The current scientific fitter still refuses to run with ConfigurationRequired, explicitly naming the pending CF decisions. This audit supplies neither those choices nor the duplicate-bootstrap multiplicity/pair-weighting/reciprocal-zero reconciliation. Numerical comparison conventions, correlation admissibility, valuation sanity, search/selection rules, pilot operational rules, and later approvals remain governed by their existing decision and freeze records.

## Environments and retained evidence

Audit: CPython 3.14.8, NumPy 2.5.3, jsonschema 4.26.0, rfc3339-validator 0.1.4, pytest 9.1.1; Ubuntu 24.04.5, runner 2.337.0, image `ubuntu-24.04` version `20261018.339.1`. The actual pip listing is retained with the observations. No dependency pin was changed for the audit.

Ordinary regression job: CPython 3.14.8 and pytest 8.4.2; Ubuntu 24.04.5, runner 2.337.0, image version `20261012.334.1`. It used the existing repository requirements and output-format dependency. These are not identical environments.

Audit artifact: `branch-b-final-audit-evidence`, ID `12224128943`, containing `final-audit-observations.json`, `final-audit.log`, and `final-audit-pip-freeze.txt`. Upload log and artifact metadata agree on provider-reported SHA-256:

```text
00d5991d02302f28cf81dd410495622ff47fff415be8132f9586742f5b58d645
```

Reported expiry: `2027-01-17T21:57:29Z`. The artifact has not been independently downloaded and rehashed locally. The retained failed audit is evidence, not a failed experiment. Its fixture support numbers, timestamps, labels, configuration/manifest contents, and array values are not production settings or released data. No scientific computation was performed locally under a different interpreter.

## Completion assessment

The prior stopping-point statement must be qualified again: F1-F3 identify concrete engineering work, not generic extra testing. Their bounded rejection/validation repairs can proceed without deciding the optimizer, a statistical threshold, or a new resampling scheme. F4's scientific handling and the previously documented method blockers remain reserved.

Do not close the structural integration audit, certify a scientific runner, or advance an official processing gate on the basis of the current passes. Preserve this audit and its pinned reproducer; subsequent repairs require a new reviewed source revision and Python 3.14 verification, not relabeling this run.

This audit adds only the diagnostic workflow and this report. It changes no scientific module, existing test assertion, shared schema, method card, seed assignment, approval, or freeze record. The scope is the inspected development snapshot and executed fixtures, not an exhaustive historical-access, supply-chain, all-approval-surface, or whole-program proof.
