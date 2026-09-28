import numpy as np

from branch_b.preprocessing import Standardizer


def test_standardizer_uses_training_statistics_only():
    train = np.vstack([np.zeros(12), np.full(12, 2.0)])
    validation = np.full((2, 12), 100.0)
    standardizer = Standardizer.fit(train)
    transformed = standardizer.transform(validation)
    assert np.allclose(standardizer.mean_, 1.0)
    assert np.allclose(standardizer.scale_, 1.0)
    assert np.allclose(transformed, 99.0)
