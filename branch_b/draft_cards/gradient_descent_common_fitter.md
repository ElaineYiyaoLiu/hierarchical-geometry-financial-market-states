# Draft Common Fitter Card — gradient_descent_ultrametric

Status: candidate; not selected; project-specific development settings approved; not frozen for pilot exchange.

## Source and role

- Fitter identifier: `gradient_descent_ultrametric`
- Source: Chierchia & Perret, *Ultrametric Fitting by Gradient Descent* (NeurIPS 2019 / arXiv:1905.10566v3).
- Registered objective: Dasgupta soft-cardinal relaxation.
- Ultrametric parameterization: min-max/subdominant-ultrametric operator.
- Initialization: working edge weights equal the input edge weights.
- Common application: the same fitter configuration applies to every registered primary geometry.

## D01 objective decision (2026-11-08; approved direction, not complete fitter freeze)

Branch B approves retaining the registered **Dasgupta-only soft-cardinality relaxation**. No separate cluster-size penalty or nonzero cluster-size lambda term is added to this candidate. This is a method choice, not an inference from scientific performance.

For ordinary, unweighted observations with the complete undirected edge set E={(i,j): i<j}, M=|E|, commonly normalized fixed input dissimilarity Delta, working weights w>=0, and u=Phi_G(w), the approved baseline structure is:

    J_D01(w; Delta, beta) =
        (1/M) * sum_{i<j} [S_i(u_ij;u,beta) + S_j(u_ij;u,beta)] / (2*Delta_ij).

The reciprocal denominator is the **fixed input** Delta_ij (never the fitted u_ij); soft cardinalities are symmetrically averaged across endpoints; contributions are averaged over undirected edges. The existing input admissibility/near-zero-denominator convention remains in force pending D06 reconciliation. No additional regularization is implied by the source paper's discussion of other objectives.

The exact executable definition of S_i (including sigmoid and self-contribution conventions), beta-selection rule (now fixed at beta=5 by the 2026-11-08 team decision), D06 bootstrap multiplicities and zero-distance behavior, and complete tied-gradient derivation remain open. Do not silently fix them from this baseline formula. The registered candidate is not selected or frozen, and the complete Python 3.14 scientific fitter remains unimplemented.

## D02 sigmoid beta decision (2026-11-08)

- Branch B team-selected and fixed soft-cardinality sigmoid parameter: **beta = 5**.
- This is the candidate's fixed method parameter, not a calibration search starting point. Do not manually retune beta using development, pilot, hierarchy-support calibration, blind-validation, independent-null, or locked-test performance without an authorized protocol revision.
- The team decision is frozen for this candidate's development specification. The full Common Fitter Card, implementation, and applicable project-level freeze gate remain pending; this record does not claim that the complete fitter is formally frozen or selected.
- Exact sigmoid/self-contribution and bootstrap soft-mass implementation details remain open and require consistency with beta = 5.

## Input and graph

- Input: the commonly normalized pairwise dissimilarity matrix.
- Graph rule: complete graph over all observations, with one edge for every pair `i < j`.
- Common normalization: divide the native dissimilarity matrix by its maximum finite off-diagonal entry.
- Normalization degeneracy: if the maximum off-diagonal native dissimilarity is `<= 1e-12`, return `DEGENERATE_DISTANCE`.

## Optimizer and stopping

- Optimizer: AMSGrad.
- Learning rate: `0.01`.
- Relative objective improvement:
  `r_t = |J_(t-1) - J_t| / max(|J_(t-1)|, epsilon_J)`.
- Convergence tolerance: `1e-8`.
- Convergence patience: require the tolerance condition for 10 consecutive iterations.
- Maximum iterations: 1000.
- Non-finite objective/optimizer state: `NUMERICAL_FIT`.
- Iteration-limit behavior: record nonconvergence as a numerical fit failure unless the later pilot/freeze record explicitly revises that convention.
- Global optimum guarantee: none.

## Reciprocal-weight safety

The Dasgupta objective uses reciprocal input weights.

- Registered normalized near-zero tolerance: `1e-12`.
- If any required normalized off-diagonal weight is `<= 1e-12`, return `DEGENERATE_DISTANCE`.
- Do not silently floor or regularize the denominator.

## Tree extraction conventions

- Equal-height ties: preserve as unresolved multifurcations; do not arbitrarily binary-resolve them.
- Zero-length branches: preserve branch length 0 and treat the associated relation as unresolved for rooted-topology comparisons.
- `DEGENERATE_TREE`: reserve for structural invalidity (for example cycle, disconnected node, multiple parents, missing root, invalid leaf set, or an optimizer output that cannot be represented as a valid rooted tree).
- Multifurcations, ties, zero-length branches, and a fully unresolved but structurally valid star are not by themselves `DEGENERATE_TREE`.

## Randomness and reproducibility

- Primary candidate execution is deterministic where the dependency stack permits deterministic behavior.
- No random restarts.
- Record a Branch B-owned run seed field for provenance even when the optimizer consumes no stochastic randomness.
- Generator-owned or hidden seeds are prohibited.

## Timeout

Timeout remains pilot-dependent under the controlling protocol and is not numerically fixed here. A pilot-fixed timeout failure must be recorded as `TIMEOUT`.

## Remaining implementation item

The project-specific settings already approved remain unchanged. A source-conformance review found that the authors' public reference implementation uses a Dasgupta soft-area sigmoid parameter with default value 5, while its default optimizer initialization differs from paper Algorithm 1 and it also applies an explicit non-negativity projection. These findings are recorded in `branch_b/decision_proposals/common_fitter_source_conformance_2026-10-02.md`. The sigmoid value, initialization choice, and positivity parameterization remain subject to explicit project review before executable freeze. The remaining engineering task is an executable Python 3.14 implementation of the approved Dasgupta soft-cardinal/min-max optimizer kernel, followed by source-conformance and golden testing.

The final Common-Fitter selection remains geometry-neutral, ground-truth-free, and subject to its later protocol freeze.
