from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode


def as_finite_matrix(values: object, *, expected_features: int = 12) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if x.ndim != 2:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "observable data must be a 2D matrix")
    if x.shape[1] != expected_features:
        raise BranchBFailure(
            FailureCode.INPUT_SCHEMA,
            f"expected {expected_features} observable features, got {x.shape[1]}",
        )
    if x.shape[0] < 2:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "at least two observations are required")
    if not np.isfinite(x).all():
        raise BranchBFailure(FailureCode.NONFINITE_INPUT, "observable data contain non-finite values")
    return x


def validate_split_roles(train_ids: Iterable[str], validation_ids: Iterable[str], test_ids: Iterable[str]) -> None:
    train = set(train_ids)
    validation = set(validation_ids)
    test = set(test_ids)
    if not train or not validation or not test:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "train/validation/test splits must all be non-empty")
    if train & validation or train & test or validation & test:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "train/validation/test sample IDs must be disjoint")
