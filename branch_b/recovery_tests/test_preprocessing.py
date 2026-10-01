import numpy as np
import pytest

from branch_b.failures import ConfigurationRequired
from branch_b.preprocessing import IdentityPreprocessor, Standardizer


def test_standardizer_requires_explicit_ddof():
    train = np.vstack([np.zeros(12), np.full(12, 2.0)])
    with pytest.raises(ConfigurationRequired):
        Standardizer.fit(train)


def test_standardizer_uses_training_statistics_only_with_explicit_ddof():
    train = np.vstack([np.zeros(12), np.full(12, 2.0)])
    validation = np.full((2, 12), 100.0)
    standardizer = Standardizer.fit(train, ddof=0)
    transformed = standardizer.transform(validation)
    assert np.allclose(standardizer.mean_, 1.0)
    assert np.allclose(standardizer.scale_, 1.0)
    assert np.allclose(transformed, 99.0)


def test_identity_preprocessor_leaves_correlation_profiles_unchanged():
    x = np.arange(24, dtype=float).reshape(2, 12)
    transformed = IdentityPreprocessor().transform(x)
    assert np.array_equal(transformed, x)
    assert transformed is not x
