"""Development-only D13 team-selected arithmetic: synthetic Python 3.14 tests."""

from math import fsum

import numpy as np
import pytest

from branch_b.bootstrap.development_d13_interval import (
    SECONDARY_RESAMPLES,
    development_d13_resampled_mean_interval,
)


def test_constant_successful_scores_give_degenerate_interval():
    result = development_d13_resampled_mean_interval(
        [0.25, 0.25, 0.25], rng=np.random.default_rng(314)
    )
    assert result.point_estimate == result.lower_endpoint == result.upper_endpoint == 0.25
    assert result.successful_score_count == 3
    assert result.secondary_resample_count == 10_000
    assert (result.lower_one_based_rank, result.upper_one_based_rank) == (250, 9750)


def test_replay_with_explicit_development_seed_is_exact():
    data = [0.1, -0.2, 0.5, 0.9, 0.3]
    first = development_d13_resampled_mean_interval(
        data, rng=np.random.default_rng(314)
    )
    second = development_d13_resampled_mean_interval(
        data, rng=np.random.default_rng(314)
    )
    assert first == second
    assert first.lower_endpoint <= first.upper_endpoint
    assert first.point_estimate == pytest.approx(fsum(data) / len(data))


def test_order_statistic_matches_independent_synthetic_replay():
    values = [0.0, 0.5, 1.0]
    result = development_d13_resampled_mean_interval(
        values, rng=np.random.default_rng(71)
    )
    independent_rng = np.random.default_rng(71)
    reference_means = []
    for _ in range(SECONDARY_RESAMPLES):
        draw = independent_rng.integers(0, len(values), size=len(values), endpoint=False)
        reference_means.append(fsum(values[int(j)] for j in draw) / len(values))
    reference_means.sort()
    assert result.lower_endpoint == reference_means[249]
    assert result.upper_endpoint == reference_means[9749]


def test_original_inputs_are_not_modified():
    values = [1.0, 2.0, 3.0, 4.0]
    saved = values.copy()
    result = development_d13_resampled_mean_interval(
        values, rng=np.random.default_rng(10)
    )
    assert values == saved
    assert result.successful_score_count == 4


@pytest.mark.parametrize(
    "values",
    [[], [float("nan")], [float("inf")], [-float("inf")], [True], ["0.5"]],
)
def test_invalid_scores_fail_closed(values):
    with pytest.raises(ValueError):
        development_d13_resampled_mean_interval(
            values, rng=np.random.default_rng(5)
        )


def test_explicit_rng_is_required():
    with pytest.raises(TypeError):
        development_d13_resampled_mean_interval([0.1, 0.2])
    with pytest.raises(TypeError):
        development_d13_resampled_mean_interval([0.1, 0.2], rng=42)


def test_one_success_is_only_arithmetic_not_reliability_certification():
    # A singleton is calculable but cannot override D12's pending minimum count.
    result = development_d13_resampled_mean_interval(
        [0.75], rng=np.random.default_rng(7)
    )
    assert result.point_estimate == result.lower_endpoint == result.upper_endpoint == 0.75
    assert result.successful_score_count == 1
