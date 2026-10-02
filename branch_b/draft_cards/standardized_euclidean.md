# Draft Geometry Card — standardized_euclidean

Status: draft; not frozen.

- Role: proposed primary comparison geometry.
- Input: 12 observable features.
- Preprocessing: coordinate-wise z-score standardization.
- Preprocessing fit scope: for each coordinate, estimate the mean and standard deviation from the training split only.
- Preprocessing application: apply the frozen training mean and standard deviation unchanged to validation and test.
- Standard-deviation convention: `ddof=0` (population-form training-split standard deviation) for the registered preprocessing rule.
- Standardized coordinate: `z_ik = (x_ik - mu_k_train) / sigma_k_train`.
- Native dissimilarity: Euclidean distance on standardized coordinates, `Delta_ij = sqrt(sum_k (z_ik - z_jk)^2)`.
- Zero training coordinate scale: explicit degeneracy/failure; do not silently regularize or use validation/test information.
- Hidden information: prohibited.
- Geometry-specific selection rule: none currently specified for the native standardized Euclidean mapping.
- Common post-geometry normalization: divide by the maximum finite off-diagonal native dissimilarity; if that maximum is `<= 1e-12`, return `DEGENERATE_DISTANCE`.
