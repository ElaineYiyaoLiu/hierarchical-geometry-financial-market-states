# Draft Geometry Card — correlation_distance

Status: draft; not frozen.

- Role: proposed comparison geometry.
- Input: observable 12-feature profiles only.
- Native dissimilarity family: Pearson-correlation-based distance.
- Preprocessing: none. Use the released 12-feature profile directly; do not standardize coordinates before computing Pearson correlation.
- Native distance primitive: `Delta_ij = 1 - corr(x_i, x_j)` for profiles on which Pearson correlation is numerically defined.
- Exactly constant profile: Pearson correlation is mathematically undefined; record an explicit `DEGENERATE_DISTANCE` rather than inventing a correlation.
- Confirmatory eligibility: conditional on a separately prespecified quantitative admissibility/near-constant rule.
- Near-constant/admissibility candidate (team selection, November 15): for each finite 12-coordinate raw profile, set `c(x)=sqrt(sum_k (x_k-mean(x))^2)` and `r(x)=sqrt(sum_k x_k^2)`. Require `r(x)>0` and `c(x)/r(x)>1e-12`. Equality is inadmissible. If any required profile fails, the proposed dataset-level correlation outcome is `DEGENERATE_DISTANCE`. No jitter, row removal, denominator flooring or repair from another split is permitted.
- PL protocol-conformity review (November 17): the candidate specifies the previously missing admissibility statistic and boundaries consistently with the packet's conditional geometry eligibility. The documentary review is complete. Scientific implementation, actual boundary evidence and the applicable authorization/freeze remain required.
- Method source: [November 15 team record](../decision_proposals/d08_d15_team_selections_2026-11-15.md). This card consolidates that existing proposal; its numerical rule remains unfrozen.
- Hidden information: prohibited.
- Common post-geometry normalization: divide by the maximum finite off-diagonal native dissimilarity; if that maximum is `<= 1e-12`, return `DEGENERATE_DISTANCE`.
