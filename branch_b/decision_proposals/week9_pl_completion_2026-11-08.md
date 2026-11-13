# Week 9 PL Completion and Implementation Handoff

Reviewed baseline: `2df4551`. Meeting: November 8, 2026; PL review and execution: November 9. This supplement reconciles existing team decisions and supplies analytic and development checks. It does not freeze the candidate, certify the scientific fitter, or authorize data exchange.

## Goal Reconciliation

| November 8 goal | Current evidence | Remaining requirement |
| --- | --- | --- |
| Objective, initialization, projection, update order | D01/D02/D03 card; full objective and derivative in the golden specification; sequence below | Executable optimizer, reviewed AMSGrad arithmetic, source-conformance evidence |
| General D04 tied gradient and averaging | All-size exact DP decision, standalone engine and small-graph oracle; invariant proof below | Larger-case and source-conformance review; practical runtime/memory measurements. Small-graph oracle, relabeling and reference full-objective checks passed under Python 3.14 |
| D06 multiplicity and identity | Product pair weights, weighted soft mass including self-mass, distinct-original leaves, no same-ID reciprocal edge | Dual occurrence/distinct pipeline integration; approved low-distinct-count outcome; end-to-end tests |
| Beta, lambda, graph and zero handling | Fixed beta=5; no separate lambda penalty; complete graph; existing distinct-input near-zero rejection | Source/card conformance and upstream bootstrap normalization checks |
| Convergence, limits, timeout and failures | Five consecutive relative changes below 1e-6; 1000 complete updates; iteration cap NUMERICAL_FIT; actual deadline TIMEOUT | Code still uses historical 1e-8/10 settings; timeout duration and remaining failure mappings pending |
| Formulas, pseudocode, examples | Golden specification G1-G4; sequence and exact DP proof here; executable analytic-reference tests added | 25 targeted reference checks passed under Python 3.14; production optimizer certification remains pending |

The meeting's complete executable-method goal remains **partially complete**. Decisions already recorded in the card should not continue to appear as unmade choices. Their implementation, scientific validation and project freeze remain separate gates.

## Mathematical References and Zero Cases

Use the formulas and symmetric-coordinate derivative in [the golden specification](week9_objective_gradient_golden_spec_2026-11-08.md). Delta is fixed input; u is optimized output. Set m_i=1 for ordinary fitting. The independent gradient coordinate for u_ab represents both symmetric matrix entries, once.

| Situation | Existing rule |
| --- | --- |
| Native maximum off-diagonal distance <=1e-12 | DEGENERATE_DISTANCE at common normalization |
| Required distinct-ID normalized Delta_ij <=1e-12 | DEGENERATE_DISTANCE; retain all distinct pairs and complete graph, without flooring, jitter or edge deletion |
| Repeated draw of one original ID | One active vertex; occurrence multiplicity enters q_ij and S_i; no same-ID reciprocal edge |
| Optimized w_ij=0 or u_ij=0 | Permitted nonnegative working/output value; denominator remains fixed positive Delta_ij |
| Exactly equal working edge weights | D04 exact hierarchy-balanced average; no approximate sampling or new tie tolerance |
| Unequal near-equal working weights | Preserve strict order for the D04 engine; general numerical/tree comparison tolerances require their own reconciliation |
| W=0 or inadequate distinct observations | Formula undefined or reliability unresolved; obtain the approved outcome before production integration |

The isolated positive-edge graph proposal in PR #14 does not supersede the registered complete-graph candidate. A zero optimized weight and a zero input reciprocal denominator have different roles.

## Optimizer Sequence

This is specification pseudocode. `AMSGradUpdate` still requires an equation-level implementation review, including the running maximum's bias correction, epsilon placement, floating-point precision and state ordering. The card names bias-corrected AMSGrad and its constants but does not supply that complete arithmetic. Do not silently select a library default.

```text
validate fixed normalized Delta and canonical distinct-ID order
validate positive integer active multiplicities; require approved low-count rules
construct the complete undirected graph; W = sum_{i<j} m_i*m_j
w = upper_triangle(Delta); initialize AMSGrad states to zero
u = Phi_G(w); J0 = J(u; Delta, m); previous = J0; consecutive = 0
retain initial objective and provenance
for t = 1,...,1000:
    check actual applicable runtime deadline
    u = Phi_G(w)
    H = derivative of full smooth J in independent symmetric u coordinates
    Pbar = exact D04 mean Jacobian at w, preserving unequal-weight order
    g = transpose(Pbar) * H
    check objective, gradient and optimizer state for finite values
    candidate, next_states = AMSGradUpdate(w, g, states, t)
    w = elementwise_max(0, candidate); states = next_states
    u = Phi_G(w); current = J(u; Delta, m)
    require finite current; record this complete projected update
    r = abs(current-previous) / max(abs(previous), abs(J0), 1e-12)
    consecutive = consecutive+1 if r < 1e-6 else 0
    previous = current
    check actual deadline before accepting output
    if consecutive >= 5:
        extract and validate the tree from this u
        preserve multifurcations and zero-length branches
        return this converged iterate with full diagnostics
record NUMERICAL_FIT with iteration-cap/nonconvergence diagnostic
```

Moment updates use the full gradient before projection; projection does not artificially mask boundary gradients. No random restarts or best-so-far replacement is introduced. Actual deadline expiry remains TIMEOUT. Numerical calculation errors remain distinct NUMERICAL_FIT diagnostics; structural invalidity follows DEGENERATE_TREE. Retain unsuccessful attempts and provenance. Memory failure and unspecified reliability outcomes require their approved registry treatment, never a fabricated timeout.

## D04 State-Aggregation Proof

Fix a complete finite graph, nonnegative weights and their exactly equal levels. Let Omega contain every permutation within each level, concatenated in increasing level order. Redundant edges are included. For each ordering pi, Kruskal's sequence produces a canonical labeled binary nested hierarchy T(pi) and a limiting min-max Jacobian P(pi). Hierarchies here are the canonical labeled nested trees used by the current engine, without a separate ranking of disjoint merges. A different meaning of hierarchy requires method review.

1. **Prefix invariant.** For each DP key (processed-edge subset at this level, canonical rooted forest), its integer count equals the number of ordering prefixes with that key. Its sparse matrix equals the sum of their accumulated pair-to-controller Jacobian entries. Initially the empty prefix has count one and zero matrix.
2. **Sufficient state.** The subset identifies available next edges; the forest retains all previously formed labeled nested clusters, not merely their leaf partition. Thus every shared continuation induces the same future hierarchy merges and the same Jacobian increments for all prefixes with that key. Earlier discarded edge order cannot alter those future transitions.
3. **Transition.** Each unused edge extends every prefix exactly once. An edge joining components A and B makes that edge the unique bottleneck controller for all previously disconnected pairs in A x B in its strict-order chamber. Add the predecessor count to those matrix positions. A redundant edge changes neither forest nor Jacobian, but contributes its prefix count and existing matrix sum. Summing convergent transitions preserves the invariant by distributivity.
4. **Level boundary.** Every level permutation has exhausted the same local subset. Removing its mask loses no availability information; the next level starts with a fresh empty subset. Retaining the full rooted forest preserves earlier hierarchy distinctions and accumulated derivatives.
5. **Terminal grouping.** Each complete ordering corresponds to exactly one sequence of edge choices. The connected complete graph ends with one canonical tree. Forest-key aggregation groups precisely those orders with the same T; swapping children or forest-list positions does not change that labeled nested hierarchy.
6. **Normalization.** For terminal count c_T and sum A_T, return Pbar = (1/|T|) sum_T A_T/c_T. This implements equal order weight within each hierarchy and equal total hierarchy weight. Dividing all orders by |Omega| would generally implement a different measure.
7. **Full gradient.** At fixed tied w the transformed u is common to all limiting chambers. The specified sigmoid objective is smooth there for fixed admissible positive Delta and fixed masses, so H is common. Linearity gives mean(P(pi)^T H)=Pbar^T H under the same two-level measure.

This argument establishes the combinatorial invariant of the stated finite algorithm. It supplies neither a convergence guarantee for AMSGrad nor a feasible runtime bound for large ties. Exhaustive oracle agreement, permutation tests, full-gradient checks and memory/runtime measurements remain necessary implementation evidence. Central finite differences at an exact tie do not by themselves validate the selected generalized-gradient averaging measure.

## Worked-Example Checks and Evidence

The reference tests evaluate G1 against closed forms, G2 against finite differences inside a fixed strict-order chamber, G3 against the exact Jacobian and limiting chamber gradients, and G4 against direct weighted soft masses and reduction to D01. Relabeling tests permute both output and input edge coordinates. All inputs are predetermined synthetic mathematical examples unrelated to experimental banks.

Run these under actual Python 3.14:

```text
python -m pytest -q branch_b/recovery_tests/test_exact_tie_dp.py branch_b/recovery_tests/test_week9_objective_reference.py --junitxml=week9-reference-junit.xml
python -m pytest -q
```

The existing Branch B Python 3.14 workflow collects the new tests and preserves environment/JUnit evidence. A new targeted evidence step preserves the tested commit, interpreter, exact dependency freeze and source SHA-256 values. CI results, including failures, must be inspected before recording execution success. The tests contain a mathematical reference implementation, not an alternative production fitter.

Actual local execution on CPython 3.14.9 / NumPy 2.5.3 / pytest 8.4.2: **25 targeted tests passed; 656 full-repository tests passed**. The [environment and source identity](../reviews/2026-11-09/environment.json), JUnit reports, dependency freeze and checksum index are archived together. These runs used the reviewed baseline plus the exact fingerprinted new test source, before this documentation/evidence commit. CI uses its separately recorded dependency versions; local results are not relabeled as CI results. No six/seven-vertex worst-case performance claim or end-to-end optimizer certification follows from these checks.

## Remaining Owners

- Branch B: review optimizer arithmetic; implement full objective/gradient/AMSGrad; reconcile code defaults; integrate D06 identity and masses through all split roles; provide source-conformance and benchmark evidence.
- Branch B and PL: resolve W=0/low-distinct-count outcomes against the approved failure/reliability definitions; reconcile exact ties versus numerical tree tolerances.
- PL at the applicable pilot gate: record evidence-supported timeout and other permitted pilot-dependent settings; approve completeness only after the required evidence is present.

Project Boundary: this PL supplement was inspected for Branch B/public disclosure. It contains existing observable-side method decisions, general mathematics and synthetic checks only. No restricted experimental information, hidden seeds, truth, condition mappings or private source paths are included. No frozen parameter, schema, evaluation definition, approval or freeze entry changes.
