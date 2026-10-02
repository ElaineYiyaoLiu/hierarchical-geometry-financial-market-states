# Formula audit

## Branch A / Project Lead

Branch A primary implementation has been checked against the Admin Packet for the balanced K=3 hierarchy, layer strengths (2, 1, 0.5), adjacent-level elementwise leakage construction, normalized leakage vector, Gaussian observation noise, and complete structural-realization regeneration when the leakage norm is degenerate.

H1-H6 are frozen for pilot use. The structural-retry implementation was repaired without changing the frozen scientific specification, and the regression, feasibility, drift, and control-calibration workflows pass.

## Branch B — current audit state

Verified implementation/specification points:
- standardized Euclidean uses coordinate-wise training-fit z-scoring with ddof=0, applied unchanged to validation/test, followed by Euclidean distance;
- valuation Chebyshev uses the same coordinate-wise training-fit z-scoring with ddof=0, followed by Chebyshev distance;
- correlation uses the released 12-feature profiles directly with no coordinate standardization before the raw Pearson-correlation distance primitive;
- the quantitative correlation near-constant/admissibility rule is not frozen; the earlier Q0.05/Q0.95 robust-spread draft has been rolled back pending the explicit Branch B meeting;
- common post-geometry normalization is max-off-diagonal scaling with a 1e-12 normalization-degeneracy guard;
- hierarchy-support distortion and Q = S - min(D, 1) follow the controlling packet;
- bootstrap train/validation/test resampling and failed-fit retention scaffolds are implemented;
- LCA-depth stability and rooted-triplet evaluation use the same contracted resolved topology;
- zero-length/unresolved edges contribute no resolved topological depth;
- positive branch-length magnitudes do not affect rooted-triplet topology;
- the registered gradient-descent candidate is source-backed by Chierchia & Perret, *Ultrametric Fitting by Gradient Descent*.

## Approved Common-Fitter project settings

Branch B explicitly approved:
- complete graph over all normalized pairwise dissimilarities;
- Dasgupta soft-cardinal objective with min-max/subdominant-ultrametric parameterization;
- working weights initialized to input weights;
- AMSGrad;
- learning rate 0.01;
- relative objective improvement below 1e-8 for 10 consecutive iterations;
- maximum 1000 iterations;
- normalized reciprocal-weight guard <=1e-12 -> DEGENERATE_DISTANCE without silent flooring;
- equal-height ties -> unresolved multifurcations;
- zero-length branches preserved and treated as unresolved for rooted topology;
- DEGENERATE_TREE reserved for structural invalidity;
- deterministic primary execution with no random restarts;
- timeout remains pilot-fixed.

## Current unresolved items

Scientific/project decisions still unresolved:
- complete quantitative correlation admissibility/near-constant rule and deterministic handling;
- general matrix/tree numerical comparison tolerances distinct from the approved normalization and reciprocal-weight thresholds;
- valuation favorable-feature sanity invariant and minimum criterion at its later gate.

Engineering work still required:
- executable Python 3.14 Dasgupta soft-cardinal/min-max optimizer kernel and source-conformance tests;
- complete validation-selection-to-test orchestration;
- end-to-end protocol bootstrap integration;
- final Python 3.14 dependency/version record for the executable fitter;
- pilot/output provenance completion, including configuration/checksum handling at its applicable gate.

No formal pilot processing, locked-test processing, or unblinding is authorized by this audit record.
