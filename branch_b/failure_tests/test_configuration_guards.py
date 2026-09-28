import numpy as np
import pytest

from branch_b.failures import ConfigurationRequired
from branch_b.fitters import GradientDescentUltrametricFitter
from branch_b.normalization import normalize_dissimilarity


def test_normalization_fails_closed_until_rule_is_frozen():
    with pytest.raises(ConfigurationRequired):
        normalize_dissimilarity(np.eye(3), rule=None)


def test_candidate_fitter_fails_closed_until_card_is_complete():
    with pytest.raises(ConfigurationRequired):
        GradientDescentUltrametricFitter().fit(np.eye(3))
