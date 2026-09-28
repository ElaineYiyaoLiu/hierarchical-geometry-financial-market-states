import pytest

from branch_b.paired import paired_replicate_contrasts


def test_paired_replicate_contrast_is_valuation_minus_comparator():
    result = paired_replicate_contrasts(
        {"r1": 0.8, "r2": 0.5},
        {"r1": 0.6, "r2": 0.7},
    )
    assert result["r1"] == pytest.approx(0.2)
    assert result["r2"] == pytest.approx(-0.2)
