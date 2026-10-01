# Draft Geometry Card — correlation_distance

Status: draft; not frozen.

- Role: proposed comparison geometry.
- Input: observable 12-feature profiles only.
- Native dissimilarity family: Pearson-correlation-based distance.
- Confirmatory eligibility: conditional on the prespecified quantitative admissibility rule.
- Robust spread definition: `R(z) = Q_0.95(z) - Q_0.05(z)`.
- Relative robust spread: `R_rel(z) = R(z) / max(median(|z|), s_min)`.
- Quantile levels: lower `0.05`, upper `0.95`; adopted by Branch B on 2026-09-30 from the near-constant specification supplied by the branch.
- Near-constant classification: `R_rel(z) <= tau_nc`.
- Near-constant degeneracy classification: `R_rel(z) <= tau_deg`, with `0 <= tau_deg < tau_nc`.
- Ordinary variation: `R_rel(z) > tau_nc`.
- Diagnostic-only near-constant region: `tau_deg < R_rel(z) <= tau_nc`.
- Still to freeze: `tau_nc`, `tau_deg`, `s_min`, quantile interpolation method, numerical tolerance, and deterministic degeneracy handling.
- Hidden information: prohibited.
- Common post-geometry normalization: project-level rule, exact formula pending confirmation.
