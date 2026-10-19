"""Synthetic split-role validation regressions; Python 3.14 CI only."""
import pytest

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.preprocessing import validate_split_roles


def test_disjoint_roles_are_accepted():
    validate_split_roles(["train_a", "train_b"], ["validation_a"], ["test_a"])


@pytest.mark.parametrize(
    "train,validation,test",
    [
        (["same"], ["same"], ["test"]),
        (["same"], ["validation"], ["same"]),
        (["train"], ["same"], ["same"]),
        ([], ["validation"], ["test"]),
        (["train"], [], ["test"]),
        (["train"], ["validation"], []),
    ],
)
def test_overlapping_or_empty_roles_fail_closed(train, validation, test):
    with pytest.raises(BranchBFailure) as exc:
        validate_split_roles(train, validation, test)
    assert exc.value.code == FailureCode.INPUT_SCHEMA
