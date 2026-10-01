# Draft Geometry Card — valuation_chebyshev

Status: draft; not frozen.

- Role: proposed primary valuation-based observable geometry.
- Input: 12 observable features only; AUX is treated as the 12th observable.
- Preprocessing: coordinate-wise z-score standardization.
- Preprocessing fit scope: for each coordinate, estimate the mean and standard deviation from the training split only.
- Preprocessing application: apply the frozen training mean and standard deviation unchanged to validation and test.
- Standard-deviation convention: degrees-of-freedom (`ddof`) remains to be explicitly fixed by Branch B; implementation fails closed if omitted.
- Standardized coordinate: `z_ik = (x_ik - mu_k_train) / sigma_k_train`.
- Native dissimilarity: Chebyshev distance on standardized coordinates, `Delta_ij = max_k |z_ik - z_jk|`.
- Zero training coordinate scale: explicit degeneracy/failure; do not silently regularize or use validation/test information.
- Hidden information: prohibited.
- Preliminary hierarchy used to define native dissimilarity: prohibited.
- Geometry-specific selection: none currently specified for the native Chebyshev mapping.
- Favorable-feature sanity invariant and minimum criterion: pending prespecification before the designated control is inspected.
- Common post-geometry normalization: project-level rule, exact formula pending confirmation.
