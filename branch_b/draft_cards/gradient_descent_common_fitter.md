# Draft Common Fitter Card — gradient_descent_ultrametric

Status: candidate; not selected; not frozen for pilot exchange.

## Source and role

- Fitter identifier: `gradient_descent_ultrametric`
- Source: Chierchia & Perret, *Ultrametric Fitting by Gradient Descent* (NeurIPS 2019 / arXiv:1905.10566v3).
- Project meeting decision: use the paper's gradient-descent framework with the Dasgupta-based objective as a candidate Common Fitter.
- The same candidate must be applied across registered primary geometries. This card does not select the final Common Fitter.

## Input

Input is the project-level commonly normalized observable dissimilarity matrix. Geometry-specific preprocessing and native dissimilarity construction occur before the fitter.

The exact common normalization is a separate project-level rule and is not supplied by the paper.

## Ultrametric parameterization

The paper works on a connected weighted graph G=(V,E) with input weights w. It introduces working weights w_tilde and enforces ultrametricity through the min-max / subdominant-ultrametric operator Phi_G. The generic optimization is:

minimize J(Phi_G(w_tilde); w)

and Algorithm 1 returns Phi_G(w_tilde) after optimization.

The source therefore fixes the optimization framework and admissible fitted object, but not the Branch B graph-construction rule from the project's full pairwise dissimilarity matrix.

## Objective

The registered project candidate uses the paper's Dasgupta relaxation. The paper defines the Dasgupta cost as a sum over graph edges of LCA-node cardinality divided by the input edge weight. Because exact node cardinality is nondifferentiable with respect to the ultrametric, the paper replaces it with a differentiable soft-cardinal construction based on a sigmoid approximation to the Heaviside function.

Project implication:
- use the Dasgupta soft-cardinal objective;
- do not silently substitute closest-ultrametric, cluster-size, or triplet objectives under this fitter identifier;
- triplet supervision is not part of this candidate.

The reciprocal input-weight form requires an explicit project convention for zero or numerically tiny off-diagonal weights. That convention is still unresolved.

## Initialization

Paper Algorithm 1 initializes the working weights from the input weights:

w_tilde[0] = w.

This part is source-defined.

## Optimizer

The paper reports the AMSGrad variant of ADAM.

It reports step size 0.01 in the framework-validation experiments and 0.1 in illustrative clustering experiments. The paper therefore does not define one universal learning rate for this project.

## Convergence and iteration behavior

The paper reports that convergence was usually reached in a little over 100 iterations in its framework-validation experiment. This is empirical evidence, not a formal project stopping rule.

Still unresolved:
- learning rate or learning-rate rule;
- convergence tolerance;
- stopping criterion;
- maximum iteration count;
- behavior at iteration limit.

## Regularization, pruning, and depth

The paper studies optional closest-ultrametric, cluster-size, and triplet terms, but the project meeting record chose the Dasgupta objective. No extra regularizer, pruning rule, or candidate-depth rule is currently registered for this candidate.

Adding one would require an explicit card revision before the applicable freeze gate.

## Tree extraction

The paper relates the min-max/subdominant ultrametric to single-linkage / MST structure and a corresponding dendrogram. Branch B must convert the fitted ultrametric into the project's authoritative rooted JSON edge-list output.

Still unresolved:
- equal-altitude tie convention;
- zero-length branch convention;
- unresolved multifurcation convention;
- excluded degenerate-tree rule;
- deterministic internal-node identifiers.

These are project-specific and are not uniquely fixed by the paper.

## Randomness and seed rule

The source-backed initialization is deterministic given the input weights. Branch B still needs an explicit deterministic/stochastic seed rule for the actual AMSGrad implementation and dependency stack. No generator-owned seed may be used.

## Timeout

Timeout is pilot-dependent under the controlling protocol. No numerical timeout is frozen here yet. A timeout must be recorded as `TIMEOUT`.

## Numerical failures

Applicable project failure codes include:
- `NONFINITE_INPUT`
- `DEGENERATE_DISTANCE`
- `NUMERICAL_FIT`
- `TIMEOUT`
- `DEGENERATE_TREE`
- `OUTPUT_SCHEMA`

Still to specify: near-zero reciprocal-weight handling, optimizer nonfinite-state handling, nonconvergence handling, and tree degeneracy/tie behavior.

## Complexity

The paper gives O(N^2) for the Dasgupta soft-cardinal computation and uses single-linkage/MST and LCA subroutines. Actual project runtime and memory must be measured after the graph rule and Python 3.14 implementation are fixed.

## Software and reproducibility

The paper describes an automatic-differentiation implementation and cites PyTorch and Higra. The Branch B project must use actual package versions that are compatible with and tested under Python 3.14; paper-era package versions are not automatically adopted.

Record for every run:
- Python/package versions;
- graph rule;
- optimizer settings;
- seed/determinism settings;
- iterations and convergence diagnostics;
- runtime and memory;
- failure status.

## Global optimum

The paper explicitly provides no guarantee of reaching a global optimum. The returned fit is an approximate numerical solution and convergence diagnostics must be retained.

## Geometry-neutral selection

Blind validation may later select among complete registered candidate Common Fitters using the frozen geometry-neutral, ground-truth-free, scale-invariant rule. Raw distortion values from different geometries may not simply be pooled, and hidden recovery scores may not be used.

## Remaining project-specific items before this card is complete

1. graph-construction rule from the full commonly normalized dissimilarity matrix;
2. fixed learning rate or frozen learning-rate rule;
3. convergence tolerance and stopping rule;
4. maximum iteration count;
5. zero / near-zero input-weight convention for the Dasgupta reciprocal term;
6. tie, zero-branch, unresolved, and degenerate-tree conventions;
7. Branch B seed/determinism rule;
8. actual Python 3.14 dependency versions;
9. reference to the frozen common post-geometry normalization;
10. reference to the frozen geometry-neutral candidate-selection rule;
11. pilot-fixed timeout.

Until these are resolved, execution must fail closed rather than run a partially specified scientific fitter.
