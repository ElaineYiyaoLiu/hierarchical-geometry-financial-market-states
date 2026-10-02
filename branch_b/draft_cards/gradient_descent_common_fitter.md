# Draft Common Fitter Card — gradient_descent_ultrametric

Status: candidate; not selected; project-specific development settings approved; not frozen for pilot exchange.

## Source and role

- Fitter identifier: `gradient_descent_ultrametric`
- Source: Chierchia & Perret, *Ultrametric Fitting by Gradient Descent* (NeurIPS 2019 / arXiv:1905.10566v3).
- Registered objective: Dasgupta soft-cardinal relaxation.
- Ultrametric parameterization: min-max/subdominant-ultrametric operator.
- Initialization: working edge weights equal the input edge weights.
- Common application: the same fitter configuration applies to every registered primary geometry.

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

The project-specific scientific settings above are now specified. The remaining engineering task is an executable Python 3.14 implementation of the paper's Dasgupta soft-cardinal objective and min-max/subdominant-ultrametric optimization kernel, followed by source-conformance and golden testing.

The final Common-Fitter selection remains geometry-neutral, ground-truth-free, and subject to its later protocol freeze.
