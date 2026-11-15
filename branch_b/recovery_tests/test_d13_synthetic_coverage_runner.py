"""Development-only checks for synthetic coverage diagnostics, Python 3.14."""

import pytest

from branch_b.tools.d13_synthetic_coverage import (
    synthetic_coverage_diagnostics,
    wilson_95_interval,
)


def test_wilson_coverage_uncertainty_has_valid_bounds():
    for successes in (0, 1, 5, 10):
        lower, upper = wilson_95_interval(successes, 10)
        assert 0.0 <= lower <= upper <= 1.0
        assert lower <= successes / 10 <= upper


@pytest.mark.parametrize("successes,trials", [(-1, 10), (11, 10), (1, 0)])
def test_invalid_wilson_counts_fail_closed(successes, trials):
    with pytest.raises(ValueError):
        wilson_95_interval(successes, trials)


def test_synthetic_scenarios_are_separate_and_report_known_means():
    summary = synthetic_coverage_diagnostics(trials=1, sample_size=4, seed=314159)
    assert summary["not_a_scientific_coverage_certification"] is True
    assert summary["secondary_resamples_per_interval"] == 10_000
    assert [row["scenario"] for row in summary["results"]] == [
        "symmetric_uniform", "two_point", "skewed_beta"
    ]
    assert [row["true_conditional_mean"] for row in summary["results"]] == [
        0.0, 0.25, -1.4
    ]
    for row in summary["results"]:
        assert row["outer_trials"] == 1
        assert row["successful_sample_size"] == 4
        assert row["intervals_covering_true_mean"] in (0, 1)
        assert row["mean_interval_width"] >= 0.0


@pytest.mark.parametrize("trials,sample_size,seed", [
    (0, 4, 10), (2, 0, 10), (1, 3, -1), (True, 3, 1)
])
def test_invalid_simulation_configuration_fails(trials, sample_size, seed):
    with pytest.raises(ValueError):
        synthetic_coverage_diagnostics(
            trials=trials, sample_size=sample_size, seed=seed
        )
