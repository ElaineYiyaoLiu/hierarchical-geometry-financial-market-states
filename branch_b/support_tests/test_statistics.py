import numpy as np
import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.support import normalized_ultrametric_distortion, q_statistic


def test_distortion_exact_fit_is_zero():
    d = np.array([[0.0, 1.0, 2.0], [1.0, 0.0, 2.0], [2.0, 2.0, 0.0]])
    assert normalized_ultrametric_distortion(d, d) == 0.0


def test_distortion_rejects_zero_mass():
    z = np.zeros((3, 3))
    with pytest.raises(BranchBFailure) as exc:
        normalized_ultrametric_distortion(z, z)
    assert exc.value.code == FailureCode.DEGENERATE_DISTANCE


def test_q_statistic_caps_distortion_at_one():
    assert q_statistic(0.8, 1.7) == pytest.approx(-0.2)
