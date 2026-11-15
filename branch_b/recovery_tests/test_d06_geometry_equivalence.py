"""Synthetic D06 pairwise-geometry equivalence checks (Python 3.14 only).

These check existing geometry primitives on one controlled duplicated draw;
they do not certify every admissibility/degeneracy case or authorize pilot use.
"""

import numpy as np
import pytest

from branch_b.bootstrap.d06_identity_boundary import (
    aligned_distinct_rows,
    build_d06_draw_boundary,
)
from branch_b.failures import BranchBFailure, FailureCode
from branch_b.geometries import (
    chebyshev_dissimilarity,
    correlation_dissimilarity,
    euclidean_dissimilarity,
)
from branch_b.normalization import normalize_dissimilarity
from branch_b.preprocessing import IdentityPreprocessor, Standardizer


def _fixture():
    """Twelve released-shape synthetic coordinates, not project observations."""
    base = np.arange(1.0, 13.0)
    originals = np.vstack((
        base,
        base[::-1] + 0.2 * base,
        np.roll(base, 4) + 0.1 * base,
        np.roll(base, 8) + 0.3 * base,
    ))
    # Training preprocessing sees the entire bootstrap multiset.
    train = originals[[0, 1, 1, 2, 1]].copy()
    draw = np.asarray([2, 1, 2, 0, 1, 0], dtype=int)
    occurrence_rows = originals[draw].copy()
    boundary = build_d06_draw_boundary(
        draw, original_sample_order=["A", "B", "C", "D"],
        fit_sample_order=[f"occ-{i}" for i in range(len(draw))],
    )
    return train, occurrence_rows, boundary


@pytest.mark.parametrize(
    "geometry,preprocessor_type",
    [
        (euclidean_dissimilarity, Standardizer),
        (chebyshev_dissimilarity, Standardizer),
        (correlation_dissimilarity, IdentityPreprocessor),
    ],
)
def test_d06_distinct_pairs_equal_occurrence_pairs_and_normalization(
    geometry, preprocessor_type
):
    train, occurrences, boundary = _fixture()
    if preprocessor_type is Standardizer:
        fitted = Standardizer.fit(train)
        assert fitted.ddof == 0
    else:
        fitted = IdentityPreprocessor()

    # Only the occurrence multiset is used to estimate standardization.
    x_occ = fitted.transform(occurrences)
    x_unique = aligned_distinct_rows(x_occ, boundary)
    occurrence_d = geometry(x_occ)
    unique_d = geometry(x_unique)
    positions = boundary.first_occurrence_positions

    # Same original identity maps to the same transformed row.
    for i, original_id in enumerate(boundary.occurrence_original_ids):
        unique_position = boundary.distinct_original_ids.index(original_id)
        np.testing.assert_array_equal(x_occ[i], x_unique[unique_position])

    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            np.testing.assert_allclose(
                occurrence_d[positions[i], positions[j]],
                unique_d[i, j], rtol=0.0, atol=1e-12,
            )

    # The registered max-offdiagonal scale is unaffected by extra
    # same-identity pairs in this nondegenerate synthetic draw.
    occurrence_normalized = normalize_dissimilarity(occurrence_d)
    distinct_normalized = normalize_dissimilarity(unique_d)
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            np.testing.assert_allclose(
                occurrence_normalized[positions[i], positions[j]],
                distinct_normalized[i, j], rtol=0.0, atol=1e-12,
            )
    assert boundary.multiplicities == (2, 2, 2)
    assert boundary.total_pair_weight() == 12


@pytest.mark.parametrize(
    "geometry",
    [euclidean_dissimilarity, chebyshev_dissimilarity, correlation_dissimilarity],
)
def test_all_identical_profiles_cannot_produce_valid_normalized_geometry(geometry):
    rows = np.tile(np.arange(12.0, dtype=float), (3, 1))
    # For correlation, identical profiles have zero distance; Euclidean and
    # Chebyshev also have zero distance. Normalization must fail closed.
    d = geometry(rows)
    with pytest.raises(BranchBFailure) as captured:
        normalize_dissimilarity(d)
    assert captured.value.code == FailureCode.DEGENERATE_DISTANCE


def test_constant_correlation_profile_fails_before_normalization():
    rows = np.vstack((
        np.ones(12, dtype=float),
        np.arange(12, dtype=float),
    ))
    with pytest.raises(BranchBFailure) as captured:
        correlation_dissimilarity(rows)
    assert captured.value.code == FailureCode.DEGENERATE_DISTANCE


def test_duplicate_occurrence_does_not_change_registered_train_standardizer():
    train, _, boundary = _fixture()
    fitted = Standardizer.fit(train)
    # Independent ddof=0 reference of the actual resampled training multiset.
    np.testing.assert_allclose(fitted.mean_, np.mean(train, axis=0), atol=0, rtol=0)
    np.testing.assert_allclose(fitted.scale_, np.std(train, axis=0, ddof=0), atol=0, rtol=0)
    distinct_train_rows = train[[0, 1, 3]]
    # Weighted original-identity arithmetic gives equivalent train moments.
    masses = np.asarray([1, 3, 1], dtype=float)
    mean = np.average(distinct_train_rows, axis=0, weights=masses)
    variance = np.average((distinct_train_rows - mean) ** 2, axis=0, weights=masses)
    np.testing.assert_allclose(fitted.mean_, mean, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(fitted.scale_, np.sqrt(variance), rtol=1e-12, atol=1e-12)
    assert boundary.distinct_original_ids == ("A", "B", "C")
