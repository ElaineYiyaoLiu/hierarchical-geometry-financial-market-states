# D06 investigation: repeated bootstrap observations and the reciprocal-weight objective

Status: **mathematical alternatives for Branch B discussion; no selected weighting, no implementation authorization, no protocol revision**.

## Observable problem

For an ordinary bootstrap resample with replacement, two fit rows can refer to the same observed sample. For Euclidean or Chebyshev dissimilarities their pairwise distance is exactly zero. The currently registered Dasgupta-type objective divides by fixed normalized input pair dissimilarities, while the current fitter admission check rejects off-diagonal distances at or below its reciprocal safety threshold. The conflict is deterministic and does not depend on hidden labels or the true hierarchy.

The checked bootstrap transport already retains (a) the complete sequence of draw occurrences and (b) their original sample identities. It does **not** decide how the objective must treat the repeated occurrences. Deduplicating, dropping edges, jittering, flooring denominators, or changing the resampling scheme would each change the scientific procedure and cannot be adopted as an engineering workaround.

## Distinguish two different meanings of multiplicity

Suppose the bootstrap draw has unique observed identities indexed by `i`, with integer occurrence counts `m_i >= 1` and total `sum_i m_i = n`. Two distinct objectives are possible:

1. **Occurrence-replication target.** Every occurrence is a vertex. Distinct occurrences of the same original identity produce off-diagonal zero distances, so a reciprocal objective is not defined without an explicitly chosen zero-edge convention.
2. **Mass-on-unique-identities target.** Each unique identity is represented once, with a positive mass `m_i`. Pairwise distances between distinct identities are well defined, but both the soft-cluster-cardinality function and the pairwise loss measure need a specified mass treatment. This is a *different objective*, not a computationally harmless deduplication.

The team chose D06 Option A as the direction for investigation and explicitly stated that the weight effect should **not simply be linear in multiplicity**. This rules out assuming a naive linear multiplier. It does not uniquely determine a nonlinear objective.

## Necessary mathematical specification

A general candidate can be written schematically as

`J(w; d, m) = [sum_{i<j} a(m_i,m_j) C_beta(i,j; Phi(w),m) / d_ij] / Z(m)`,

where `d_ij > 0` is the *fixed* normalized dissimilarity between distinct original identities, `a` is an explicitly chosen pair coefficient, `C_beta` is a specified mass-aware soft-cardinality expression, and `Z` is a fixed normalization. The expression is **only a template**. In particular, setting `a=1` does not remove the need to define mass-aware `C_beta`, and a nonlinear `a` does not itself resolve within-identity zero edges.

Candidate families to investigate, not select:

| Candidate | Pair coefficient on distinct identities | Benefit | Limitation |
| --- | --- | --- | --- |
| Equal unique-pair weighting | `a=1` | Avoids direct multiplicity amplification | Resampled frequency may then affect only the soft mass or not at all; requires a defined inferential target |
| Sublinear power weighting | `a=(m_i m_j)^alpha`, `0<alpha<1` | Adjustable diminishing influence of large counts | Introduces `alpha` and a selection/freeze obligation |
| Logarithmic weighting | `a=log(1+m_i)log(1+m_j)/(log 2)^2` | Monotone but diminishing marginal influence; unit mass gives 1 | Scale and normalization must be justified; not automatically a faithful bootstrap |
| Full occurrence-pair weighting | `a=m_i m_j` | Represents the number of cross-identity occurrence pairs | **Linear in each multiplicity holding the other fixed**; does not satisfy the team's stated concern without further justification; does not resolve zero edges |

Other choices (e.g. pairwise saturation, inverse-frequency weighting) also require an explicit scientific target. The table does not endorse any choice.

## Properties to decide before coding

- **Singleton reduction:** for `m_i=1` for every identity, the objective and derivative should reduce exactly to the approved ordinary-data D01 loss, unless the team explicitly authorizes a different target.
- **Permutation invariance:** relabeling anonymous original identities or permuting draw occurrences should not change the objective for the same observable distances and multiplicities.
- **Zero-edge convention:** specify whether same-identity occurrence pairs contribute to soft cardinality, objective, both, or neither, and why. An omission is a scientific choice.
- **Mass normalization:** define the denominator `Z(m)`, effective total cluster mass, sigmoid argument units, and the endpoint-average rule; test scale and duplication behavior.
- **Fitter domain:** define whether optimization vertices are original identities or occurrences, how tree leaves and their canonical order are represented, and how results map back to the original sample set.
- **Bootstrap inference:** determine whether the resulting stability statistic still estimates the protocol's intended quantity when some original identities are absent and others repeated.
- **Failure handling:** retain each unsuccessful attempt and its actual failure code; do not quietly convert zero distances to success or discard the attempt.
- **Reproducibility:** record draw indices, original-ID counts, any mass transform and its configuration, Branch B seed, and fit diagnostics; never use generator-owned seeds.

## Safe next steps

1. Agree on the inferential target and the meaning of a bootstrap replicate: occurrence replication versus unique-identity mass.
2. Specify `a`, `C_beta`, `Z`, and same-identity treatment together. A pair-weight formula alone is insufficient.
3. Approve a tiny hand-checkable synthetic fixture with multiplicities `(2,1,1)`, a no-duplicate control `(1,1,1)`, and relabeled equivalents. Compute expected loss and directional derivatives **only after** the formula is approved.
4. Confirm the applicable pre-pilot freeze and approved observable-data role before any tuning.
5. Implement the selected method and run Python 3.14 source-conformance, gradient, reproducibility, and failure-accounting tests. Do not process official pilot data until the applicable gates are satisfied.

No hidden generator configuration, latent labels, true hierarchy, sealed ground truth, or other blinded information was used in this investigation.
