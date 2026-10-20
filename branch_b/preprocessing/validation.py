from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from branch_b.failures import BranchBFailure, FailureCode


def _real_numeric_matrix(values: object, *, context: str) -> np.ndarray:
    """Reject lossy representations before converting an observable matrix."""
    if np.ma.isMaskedArray(values) or np.ma.is_masked(values):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, f"{context} cannot contain masked values")

    def inspect(item: object) -> None:
        if np.ma.is_masked(item) or isinstance(item, (bool, np.bool_)):
            raise BranchBFailure(FailureCode.INPUT_SCHEMA, f"{context} cannot contain Boolean or masked values")
        if isinstance(item, (list, tuple)):
            for child in item:
                inspect(child)
        elif isinstance(item, np.ndarray) and item.dtype.kind == "O":
            for child in item.flat:
                inspect(child)

    inspect(values)
    try:
        raw = np.asarray(values)
    except (TypeError, ValueError, OverflowError) as exc:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, f"{context} must be a regular numeric matrix") from exc
    if raw.dtype.kind not in "iuf":
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, f"{context} must contain real numeric values")
    try:
        return raw.astype(float, copy=True)
    except (TypeError, ValueError, OverflowError) as exc:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, f"{context} values cannot be converted to floats") from exc


def as_finite_matrix(values: object, *, expected_features: int = 12) -> np.ndarray:
    x = _real_numeric_matrix(values, context="observable data")
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
