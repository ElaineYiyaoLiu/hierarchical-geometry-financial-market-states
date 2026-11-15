"""Synthetic-only D13 conditional-mean diagnostic tests for Python 3.14.

These tests check exact arithmetic support and illustrate inferential limits;
they do not estimate coverage of any project data or assert nominal coverage.
"""

from itertools import product
from math import fsum

import numpy as np
import pytest

from branch_b.bootstrap.development_d13_interval import (
    development_d13_resampled_mean_interval,
)


def _all_exact_resampled_means(values):
    """Enumerate equiprobable bootstrap index tuples for tiny synthetic input."""
    n = len(values)
    return sorted(fsum(values[j] for j in indices) / n
                  for indices in product(range(n), repeat=n))


@pytest.mark.parametrize("scores", [(0.0, 1.0), (-1.0, 0.0, 2.0)])
def test_small_synthetic_support_matches_exact_bootstrap_enumeration(scores):
    exact_means = set(_all_exact_resampled_means(scores))
    observed = development_d13_resampled_mean_interval(
        scores, rng=np.random.default_rng(20261115)
    )
    assert observed.lower_endpoint in exact_means
    assert observed.upper_endpoint in exact_means
    assert observed.point_estimate == pytest.approx(fsum(scores) / len(scores))
    assert observed.lower_endpoint <= observed.upper_endpoint


def test_conditional_on_success_target_is_not_all_attempt_mean():
    # Synthetic attempt outcomes only. Missing fits do not become Q=0.
    scores_for_successful_attempts = (0.2, 0.4, 0.8)
    attempts = (0.2, None, 0.4, None, 0.8)
    result = development_d13_resampled_mean_interval(
        scores_for_successful_attempts, rng=np.random.default_rng(314)
    )
    assert len(attempts) == 5
    assert sum(value is None for value in attempts) == 2
    assert result.successful_score_count == 3
    assert result.point_estimate == pytest.approx((0.2 + 0.4 + 0.8) / 3)


def test_degenerate_scores_do_not_prove_unconditional_coverage():
    # A zero-width conditional interval follows even if no population-level
    # sampling conclusion is warranted. This is a diagnostic, not a coverage claim.
    result = development_d13_resampled_mean_interval(
        (0.5,) * 8, rng=np.random.default_rng(17)
    )
    assert result.lower_endpoint == result.upper_endpoint == 0.5
