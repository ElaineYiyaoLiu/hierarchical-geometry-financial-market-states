# Draft Geometry Card — correlation_distance

Status: draft; not frozen.

- Role: proposed comparison geometry.
- Input: observable 12-feature profiles only.
- Native dissimilarity family: Pearson-correlation-based distance.
- Preprocessing: none. Use the released 12-feature profile directly; do not standardize coordinates before computing Pearson correlation.
- Native distance primitive: `Delta_ij = 1 - corr(x_i, x_j)` for profiles on which Pearson correlation is numerically defined.
- Exactly constant profile: Pearson correlation is mathematically undefined; record an explicit `DEGENERATE_DISTANCE` rather than inventing a correlation.
- Confirmatory eligibility: conditional on a separately prespecified quantitative admissibility/near-constant rule.
- Near-constant/admissibility construction: pending explicit Branch B meeting. No robust-spread statistic, quantile levels, thresholds, interpolation rule, numerical tolerance, or deterministic near-constant handling is frozen at present.
- Hidden information: prohibited.
- Common post-geometry normalization: divide by the maximum finite off-diagonal native dissimilarity; if that maximum is `<= 1e-12`, return `DEGENERATE_DISTANCE`.
