import numpy as np

from branch_b.preprocessing import IdentityPreprocessor, Standardizer


def test_standardizer_defaults_to_registered_ddof_zero_and_uses_train_only():
    train = np.vstack([np.zeros(12), np.full(12, 2.0)])
    validation = np.full((2, 12), 100.0)
    standardizer = Standardizer.fit(train)
    transformed = standardizer.transform(validation)
    assert standardizer.ddof == 0
    assert np.allclose(standardizer.mean_, 1.0)
    assert np.allclose(standardizer.scale_, 1.0)
    assert np.allclose(transformed, 99.0)


def test_identity_preprocessor_leaves_correlation_profiles_unchanged():
    x = np.arange(24, dtype=float).reshape(2, 12)
    transformed = IdentityPreprocessor().transform(x)
    assert np.array_equal(transformed, x)
    assert transformed is not x
