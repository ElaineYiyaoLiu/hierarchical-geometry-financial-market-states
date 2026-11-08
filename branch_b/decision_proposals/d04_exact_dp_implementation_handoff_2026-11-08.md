# D04 exact dynamic programming: implementation handoff

Status: source written, not executed. This is not a verified mathematical proof, a Python 3.14 test result, a Common Fitter freeze, or authority to run official pilot/locked-test data.

## Files

- `branch_b/fitters/exact_tie_dp.py`: standalone exact combinatorial D04 engine.
- `branch_b/recovery_tests/test_exact_tie_dp.py`: independently implemented exhaustive strict-ordering oracle for small complete graphs.
- `branch_b/decision_proposals/week9_objective_gradient_golden_spec_2026-11-08.md`: full-objective gradient and synthetic case definitions.

## Approved mathematics retained

At fixed nonnegative complete-graph working weights, preserve the strict order between unequal input weights. At each equal-weight level, consider every strict order of its edges, including redundant edges that do not change Kruskal's forest. Group completed orders by canonical distinct labeled rooted binary hierarchy. Average Jacobians uniformly among orders *within* each hierarchy and then uniformly over distinct hierarchies. The reported fitted tree must still preserve unresolved multifurcations; the internal binary refinements exist only for gradient averaging.

`exact_average_minmax_jacobian(n, edge_weights, deadline_monotonic=...)` returns exact rational Jacobian rows/columns indexed by canonical `(i,j)` pairs `i<j`. No minimum/maximum tied-vertex count, approximate fallback, stochastic sampling, or predicted-complexity termination appears in the function. The deadline is an absolute monotonic-clock instant provided by the caller. Only its actual expiry produces `ExactD04DeadlineExpired`; mapping this into the approved `TIMEOUT` record belongs in the still-unimplemented scientific fitter. True memory/numerical failures must not be silently reclassified as TIMEOUT.

## Exact DP invariant requiring formal review

For each state `(processed-tied-edge-mask, canonical labeled rooted forest)`, store:

- an integer count of strict-order prefixes reaching the state;
- the integer sum of all prefix min-max Jacobian contributions.

Future transitions depend on the forest and which tied edges have already appeared, not on the earlier order producing that state. If the next edge connects components with vertex sets A and B, add one Jacobian unit for each unordered cross-pair in A x B in the next edge's column; if already connected, add zero. When paths reach the same key, sum counts and Jacobian sums. At the end of each level, remove the now-exhausted mask, retaining the complete history in the forest structure and accumulated Jacobians. At the end, normalize each full-hierarchy Jacobian sum by that hierarchy's strict-order count and then average the hierarchy means equally.

The proof obligation is to show that this canonical forest retains all hierarchy distinctions needed by the approved averaging measure and that every strict ordering is represented exactly once. This is plausible from the state invariant but remains unverified by execution.

## Known constraints

- Exact subset-plus-forest DP can still use extreme memory: seven tied original vertices in a complete graph give 21 edges and potentially many distinct hierarchy states. No seven-vertex guarantee is claimed.
- The current engine stores sparse integer Jacobian sums per state and exact Fraction output. This prioritizes correctness and auditability, not verified efficiency.
- No use of generated labels, hidden hierarchy, protected conditions, generator source, or restricted side channels is necessary.
- No integration into `GradientDescentUltrametricFitter.fit` has been attempted; it remains the existing `ConfigurationRequired` stub.
- The `n` and `edge_weights` interface expects one canonical upper-triangle weight per pair. Numerical tie convention is exact equality, not a new tolerance.
- The caller must retain ordinary multibranch tree extraction and all existing D03, D05, D06 and failure rules.

## Python 3.14 validation handoff

In an actual Python 3.14 project environment, from the repository root, first record the active interpreter and exact environment. Run:

    python -V
    python -m pytest -q branch_b/recovery_tests/test_exact_tie_dp.py

If this suite succeeds, run related existing fitter and pipeline tests, then a separate scheduled development-only benchmark using permitted synthetic complete-graph tied cases at 6 and 7 vertices, with actual runtime deadline, peak memory, states, outcomes and diagnostics. Do not run the 7-vertex worst case without practical memory monitoring; if memory fails before the deadline, preserve that failure rather than inventing TIMEOUT.

For the next review: check proof/state-compression invariant; assess worst-case memory; verify exact vs independent oracle on small graphs; validate relabeling/permutation behavior; connect the averaged Jacobian transpose to the already-approved smooth D01/D06 full-objective gradient; and only then integrate into projected AMSGrad.

This document and all code referenced are development-only. Their existence does not constitute successful Python 3.14 execution.
