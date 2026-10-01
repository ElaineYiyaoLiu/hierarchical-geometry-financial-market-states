# Formula audit

## Branch A / Project Lead

Branch A primary implementation has been checked against the Admin Packet for the balanced K=3 hierarchy, layer strengths (2, 1, 0.5), adjacent-level elementwise leakage construction, normalized leakage vector, Gaussian observation noise, and complete structural-realization regeneration when the leakage norm is degenerate.

H1-H6 are frozen for pilot use. The structural-retry implementation was repaired without changing the frozen scientific specification, and the regression, feasibility, drift, and control-calibration workflows pass.

## Branch B

Branch B observable-geometry and support formulas have now been audited against the controlling Branch B Packet and approved shared-source records.

Verified implementation/specification points:
- standardized Euclidean uses coordinate-wise training-fit standardization, applied unchanged to validation/test, followed by Euclidean distance;
- valuation Chebyshev uses the same coordinate-wise training-fit standardization, followed by Chebyshev distance;
- correlation uses the released 12-feature profiles directly with no coordinate standardization before Pearson-correlation distance;
- hierarchy-support distortion and Q = S - min(D, 1) follow the controlling packet;
- bootstrap train/validation/test resampling and failed-fit retention are implemented as separate stages;
- LCA-depth stability uses the same contracted resolved topology as rooted-triplet evaluation;
- rooted-triplet evaluation uses resolved topological depth after contracting zero-length/unresolved edges; positive branch-length magnitudes do not affect topology, and unresolved estimated relations count as incorrect;
- the registered gradient-descent candidate is source-backed by Chierchia & Perret, *Ultrametric Fitting by Gradient Descent*.

Source-backed Common-Fitter details:
- optimization variable is mapped through the min-max/subdominant-ultrametric operator;
- the registered objective is the paper's Dasgupta soft-cardinal relaxation;
- Algorithm 1 initializes working weights from the input edge weights;
- the paper reports AMSGrad;
- the paper reports step size 0.01 for framework-validation experiments and 0.1 for illustrative clustering experiments, so it does not define one project learning rate;
- the paper reports convergence usually in a little over 100 iterations in one experiment, which is empirical evidence rather than a stopping rule;
- the paper does not guarantee a global optimum.

The following Branch B scientific/project-specific choices are still not formula-auditable because they remain unresolved:
- common post-geometry normalization formula;
- correlation admissibility values tau_nc, tau_deg, s_min, quantile interpolation convention, numerical tolerance, and deterministic degeneracy handling;
- gradient-descent graph-construction rule from the full pairwise matrix;
- learning-rate rule, convergence tolerance, maximum iterations, near-zero reciprocal-weight handling, tie/zero-branch/degenerate-tree conventions, and timeout;
- valuation favorable-feature sanity invariant and minimum criterion at its later gate.

The 0.95/0.05 quantiles used in the current near-constant robust-spread draft are a profile-spread construction and must not be conflated with a 95% confidence level or the packet's empirical 95th-percentile support calibration threshold.


### 2026-09-30 structural-depth correction

A Week 2 audit found that rooted-triplet evaluation had been using cumulative positive branch lengths as an effective depth. That was corrected because rooted-triplet recovery is topological: positive branch-length magnitudes must not change which pair has the strictly deeper common ancestor. The implementation now counts resolved structural levels, assigning zero increment to zero-length or explicitly unresolved edges. LCA-depth stability uses the same convention.

Python 3.14 CI after this correction:
- shared validator: 15 passed;
- Branch B tests: 34 passed;
- workflow run: 36808137703;
- conclusion: success.
