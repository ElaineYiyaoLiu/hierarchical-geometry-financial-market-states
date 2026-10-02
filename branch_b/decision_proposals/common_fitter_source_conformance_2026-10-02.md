# Common Fitter source-conformance review - 2026-10-02

Status: source evidence recorded; unresolved implementation choices remain unapproved.

Source basis:

- Chierchia & Perret, *Ultrametric Fitting by Gradient Descent*, NeurIPS 2019 / arXiv:1905.10566.
- Authors' public reference implementation: `PerretB/ultrametric-fitting`, files `ultrametric/optimization.py` and `ultrametric/loss.py`.

## Confirmed source-backed items

The paper's Algorithm 1 initializes the working weights with the input weights and returns the ultrametric transform of the optimized working weights.

The authors' reference implementation confirms:

- automatic differentiation with PyTorch;
- Adam with `amsgrad=True`;
- a subdominant/single-linkage ultrametric transform;
- Dasgupta dissimilarity-mode loss using soft cluster area divided by input edge weight;
- a Dasgupta soft-area sigmoid scale parameter with default value `5`.

This resolves the earlier documentation gap about whether the public reference implementation used a concrete sigmoid scale: it does, and the default is 5.

## Source discrepancy requiring an explicit project decision

The paper and the public reference implementation are not identical on initialization.

- Paper Algorithm 1: working weights start from the input weights.
- Public implementation: when no explicit initialization is supplied, the optimization variable is initialized from the subdominant ultrametric of the input edge weights.

The public implementation also applies a non-negativity map to the optimization variable, with softplus as the default when the fitting object is constructed with its default projection setting. This projection choice is not currently recorded in the project Common Fitter card.

These differences must not be silently resolved by implementation.

## Proposed review decisions

### CF-SIGMOID

Proposal: adopt `sigmoid_parameter = 5` for the Dasgupta soft-area relaxation because this is the authors' public reference-code default.

Status: proposal pending Branch B / Project Lead approval; not frozen.

### CF-INIT

Current project card follows paper Algorithm 1 and records input-weight initialization.

Proposal: retain the paper-defined input-weight initialization unless the project explicitly chooses to reproduce the authors' software default instead.

Status: decision required before executable freeze.

### CF-POSITIVITY

Proposal: explicitly choose and record the non-negativity parameterization before implementation. The authors' public code defaults to softplus; the paper-level algorithm does not by itself fix this software choice.

Status: decision required before executable freeze.

## Dependency compatibility gate

The reference software depends on PyTorch and Higra. The project requires Python 3.14 for scientific execution. Therefore the executable implementation must not be declared complete until actual Python 3.14-compatible versions are installed and tested in project CI.

Do not relabel a run from another Python version as Python 3.14 evidence.

## Next implementation sequence

1. Approve or reject CF-SIGMOID, CF-INIT, and CF-POSITIVITY.
2. Record actual Python 3.14 dependency versions.
3. Implement the min-max/subdominant-ultrametric kernel and Dasgupta soft-area objective.
4. Add source-conformance tests against small deterministic graphs.
5. Run the full Common Fitter tests in Python 3.14 CI.
