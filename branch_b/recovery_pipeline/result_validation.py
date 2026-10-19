"""Structural result checks; no numerical tolerance or scientific approval.

These checks are necessary, not sufficient, for scientific integration. They
intentionally do not choose symmetry, ultrametric, or height-tie tolerances.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

import numpy as np
from jsonschema import Draft202012Validator

from branch_b.failures import BranchBFailure, FailureCode
from branch_b.fitters.base import FitResult
from branch_b.serialization.tree import validate_tree_edge_list


class IdentityAwareFitter(Protocol):
    fitter_id: str

    def fit_with_sample_order(
        self, dissimilarity: object, *, sample_order: list[str],
        random_seed: int | None = None,
    ) -> FitResult:
        """Return matrices and named leaves in the supplied row order."""
        ...


def checked_sample_order(sample_order: object, *, size: int | None = None) -> list[str]:
    """Snapshot caller-supplied identities; never infer them from a returned tree."""
    if not isinstance(sample_order, list) or not sample_order:
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "canonical sample order must be a non-empty list")
    if not all(isinstance(name, str) and name for name in sample_order):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "canonical sample identifiers must be non-empty strings")
    order = sample_order.copy()
    if len(set(order)) != len(order) or (size is not None and len(order) != size):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "canonical sample order must be unique and match the row count")
    return order


def validate_finite_square(matrix: object, *, size: int) -> None:
    """Check real numeric shape and finiteness without coercion or repair."""
    try:
        values = np.asarray(matrix)
    except (TypeError, ValueError, OverflowError) as exc:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "fitted matrix must be numeric and rectangular") from exc
    if values.shape != (size, size) or values.dtype.kind not in "iuf":
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "fitted matrix must be real numeric and match canonical sample order")
    if not np.isfinite(values).all():
        raise BranchBFailure(FailureCode.NUMERICAL_FIT, "fitted matrix contains non-finite values")


def validate_bound_tree(tree: object, *, sample_order: list[str]) -> None:
    """Use the existing shared tree schema plus structural/order validation."""
    order = checked_sample_order(sample_order)
    schema_path = Path(__file__).resolve().parents[2] / "interface_package" / "branch_b_output.schema.json"
    # The shared schema is authoritative; do not duplicate or amend its rules.
    with schema_path.open(encoding="utf-8") as handle:
        schema = json.load(handle)
    validator = Draft202012Validator({"$ref": "#/$defs/tree", "$defs": schema["$defs"]})
    if next(validator.iter_errors(tree), None) is not None:
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "recovered tree violates the shared tree schema")
    validate_tree_edge_list(tree, order)


def validate_fit_result(fit: object, *, sample_order: list[str]) -> None:
    """Reject malformed fits before selection or checked-bootstrap return.

    Passing does not establish matrix symmetry, the ultrametric inequality,
    tree/matrix numerical consistency, support reliability, or authorization.
    """
    order = checked_sample_order(sample_order)
    if not isinstance(fit, FitResult):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "fitter must return FitResult")
    validate_finite_square(fit.ultrametric_matrix, size=len(order))
    if not isinstance(fit.diagnostics, dict):
        raise BranchBFailure(FailureCode.OUTPUT_SCHEMA, "fitter diagnostics must be an object")
    validate_bound_tree(fit.tree, sample_order=order)
