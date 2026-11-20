# Actual Development Fitter Worked Example

Executed November 18, 2026 with actual Python 3.14.10 against development commit `51eca3158bff46bf52c04ec592c71559cb2ad637`. Exact environment, source fingerprints, inputs, optimizer diagnostics, fitted trees, draw indices, evaluator seeds and failure records are in `run.json`.

## Fixed Example and Outcome

The public arithmetic fixture has three original identities, with scalar row values 1, 2 and 4 repeated across twelve coordinates. It uses the existing train-only `Standardizer`, Chebyshev geometry, common normalization, actual `D06DevelopmentFitter` and published D06 bootstrap runner. One fixed geometry configuration is supplied; there is no hyperparameter search. The three split roles use separate arrays with these same arbitrary values. This is not an experimental bank or a sample-size recommendation.

An initial exploratory probe and the archived repeat used the same fixture, seed 17, eight attempts and unchanged scientific source. No alternative seeds, inputs, stopping rules or methods were searched to obtain a favorable example. The initial probe found the same all-zero reference and zero successful attempts. Its summary is retained here; `run.json` is the full archived repeat, not a relabeling of that initial execution.

The full-reference actual optimizer converged in 170 completed updates to an all-zero ultrametric. Its serialized reference tree is an unresolved zero-length star. Therefore its LCA-depth ranks are constant and cannot supply a defined reference Spearman stability.

| Attempt indices | Observed outcome |
| --- | --- |
| 0, 7 | Training coordinate scales are zero: `DEGENERATE_DISTANCE` |
| 1, 3, 4, 6 | Too few common pairwise LCA-depth relations: `INSUFFICIENT_BOOTSTRAP` |
| 2 | The current distance path reports fewer than two observations: `INPUT_SCHEMA` |
| 5 | Constant-rank comparison: `UndefinedRankCorrelation` |

All eight attempts are retained. There are zero successful stability results; no support interval, reliability assertion or support classification is emitted. The observed `INPUT_SCHEMA` and uncoded rank exception are actual current outputs, not endorsements of final scientific failure mapping. The previously outstanding low-distinct-count and undefined-rank mapping still require reconciliation.

The 30-second budget is a per-fit development execution guard supplied through the existing explicit-deadline interface. It does not choose the pilot timeout. No deadline expired in this example. Multiplicity continues to reach the actual fitter; no duplicate original leaves or same-ID reciprocal edges are introduced.

## Review Meaning

The actual optimizer-to-tree-to-bootstrap failure path has now been exercised rather than represented only by a recording fitter. The fixed example exposes a limitation: it cannot satisfy the requested successful nonconstant-reference stability example. It does not show that every input collapses, establish a general optimizer defect, or justify modifying the fixed objective. Small-sample bootstrap failures also do not establish production reliability cutoffs.

Next technical review should examine the collapsed reference under the already recorded objective and its intended procedure controls, the full-fit tree eligibility/reference requirements, and complete failure mapping. Preserve this example when presenting any subsequent worked examples. Any scientific-method change requires its own explicit authorization; a success must not be manufactured by replacing the reference tree, changing the objective, adding jitter, choosing a favorable seed or dropping attempts.

## Reproduction

Use the source commit above and the recorded Python/dependency versions. From this review branch, with a separate checkout of that source:

```bash
python branch_b/reviews/2026-11-18-actual-fitter/worked_example.py --source-root <source-checkout> --output <fresh-run.json>
```

The output destination must be new. Elapsed timings can differ; compare the fixed input/draw/seed bindings, optimizer outcome, tree/matrix, attempt ledger and failures independently of machine timing. The source/configuration is not revised by this script.

Project Boundary: actual script, fixed inputs and outputs were inspected and are permitted for Branch B/public disclosure. Only public arithmetic fixtures, existing observable-side development computations and diagnostics are included. No generating implementation, hidden experimental conditions, generator-owned seeds, labels, true hierarchy, sealed truth or restricted paths appear. No scientific bank, pilot, calibration, production or unblinding execution is authorized.
