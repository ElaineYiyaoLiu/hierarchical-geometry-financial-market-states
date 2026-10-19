# Common Fitter paper reference map - 2026-10-19

Documentation review only. This does not approve a parameter, change the candidate, or enable the optimizer.

Source: Chierchia and Perret, *Ultrametric Fitting by Gradient Descent*, arXiv:1905.10566v3, dated 17 October 2019. Page numbers below are the printed pages of the 16-page arXiv PDF, including its supplement; they are not the Branch B Packet page numbers. The public PDF and the shared reference identify the same v3 source.

[Paper](https://arxiv.org/pdf/1905.10566) | [Version record](https://arxiv.org/abs/1905.10566v3)

| Implementation question | Exact location |
| --- | --- |
| Subdominant min-max operator and composite objective | p. 3, Section 2.1, Equations (4)-(6) |
| Input-weight initialization and final ultrametric transform | p. 4, Algorithm 1, lines 1 and 5 |
| Dasgupta reciprocal-weight objective and initial soft-cardinality motivation | p. 5, Section 2.5, Equations (12)-(13) |
| Pass-edge derivative and ambiguity at tied bottlenecks | p. 6, Section 3.1, Equations (14)-(15), Figure 3 |
| Subdominant algorithm | p. 7, Algorithm 2 |
| Averaging over pass-edge endpoints and ancestor-based soft cardinality | p. 7, Section 3.3, Equation (17) |
| Dasgupta cost accumulation | p. 11, Algorithm 5 |
| Soft-cardinality accumulation | p. 12, Algorithm 6 |
| AMSGrad with step size 0.01 in the framework-validation experiment | p. 11, Section A.2 |
| Different step size 0.1 in illustrative examples | p. 12, Section A.3 |

The project's registered learning rate remains 0.01; different experimental settings in the paper do not authorize changing it.

## Formula consistency flags for executable review

Equation (12) uses fixed input weights `w` in the denominator, whereas Algorithm 5 line 6 prints `u`. Equation (17) averages the two endpoint contributions with a factor `1/2`; Algorithm 6's printed accumulation has no final halving step. These are apparent source inconsistencies to resolve explicitly in the executable specification, not permission to silently choose a variant. The current card already describes reciprocal input weights.

## Existing decision boundary

The [current card](../draft_cards/gradient_descent_common_fitter.md) and [October 2 source-conformance review](common_fitter_source_conformance_2026-10-02.md) explicitly reserve **CF-SIGMOID**, **CF-INIT**, and **CF-POSITIVITY** for project approval. The review records reference-code sigmoid parameter 5, differing default initialization, and a softplus nonnegativity map. Those observations are not approvals.

Confirm the complete executable formula, including normalization and the meaning of initialization before/after any positivity map, when closing those decisions. Do not import additional regularizers, use labels, introduce another fitter, or select conventions from scientific performance.

The current min-max implementation and tie-free Jacobian are development references. Their successful synthetic tests do not validate a complete Dasgupta optimizer, resolve tied-gradient behavior, or establish production scalability. The full fitter remains fail-closed.
