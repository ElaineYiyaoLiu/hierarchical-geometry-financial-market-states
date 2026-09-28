import pytest

from branch_b.support import classify_support, summarize_successful_support


def test_support_decision_supported_only_when_lower_exceeds_threshold():
    result = classify_support(
        score=0.4,
        interval_lower=0.31,
        interval_upper=0.50,
        threshold=0.30,
        reliable_interval=True,
    )
    assert result.decision == "supported"


def test_support_decision_not_supported_only_when_upper_below_threshold():
    result = classify_support(
        score=0.1,
        interval_lower=-0.10,
        interval_upper=0.19,
        threshold=0.20,
        reliable_interval=True,
    )
    assert result.decision == "not supported"


def test_support_decision_equality_is_indeterminate():
    result = classify_support(
        score=0.2,
        interval_lower=0.20,
        interval_upper=0.40,
        threshold=0.20,
        reliable_interval=True,
    )
    assert result.decision == "indeterminate"


def test_missing_pilot_fixed_minimum_keeps_interval_unreliable():
    summary = summarize_successful_support(
        q_values=[0.1, 0.2],
        stability_values=[0.8, 0.9],
        failed_fits=1,
        minimum_successful_fits=None,
    )
    assert summary.q_hat == pytest.approx(0.15)
    assert summary.failure_rate == pytest.approx(1 / 3)
    assert summary.reliable_for_interval is False
