from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from branch_b.failures import BranchBFailure


@dataclass(frozen=True)
class BootstrapReplicate:
    """One attempted replicate, including its original draw and evaluator seed.

    Records produced by the bootstrap engine always include replicate_seed.
    None preserves compatibility with older manually constructed records; it
    means the seed was not recorded, not that a seed may be reconstructed here.
    """

    replicate_index: int
    train_indices: np.ndarray
    validation_indices: np.ndarray
    test_indices: np.ndarray
    result: object | None
    failure: dict | None
    replicate_seed: int | None = None


def bootstrap_split_indices(n: int, rng: np.random.Generator) -> np.ndarray:
    if n <= 0:
        raise ValueError("bootstrap split size must be positive")
    return rng.integers(0, n, size=n, endpoint=False)


def _failure_record(exc: Exception) -> dict:
    record = {
        "exception_type": type(exc).__name__,
        "message": str(exc),
    }
    if isinstance(exc, BranchBFailure):
        record["failure_code"] = str(exc.code)
    return record


def run_full_pipeline_bootstrap(
    *,
    n_replicates: int,
    train_size: int,
    validation_size: int,
    test_size: int,
    base_seed: int,
    evaluate_replicate: Callable[[np.ndarray, np.ndarray, np.ndarray, int], object],
) -> list[BootstrapReplicate]:
    """Resample train/validation/test independently and preserve every failed replicate.

    Scientific decisions such as the minimum successful-replicate count, confidence
    interval method, timeout rule, and failed-fit sensitivity convention are intentionally
    not imposed here because the protocol assigns them to the bounded pilot revision.
    """
    for name, value in (
        ("n_replicates", n_replicates),
        ("train_size", train_size),
        ("validation_size", validation_size),
        ("test_size", test_size),
    ):
        if type(value) is not int or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if type(base_seed) is not int or base_seed < 0:
        raise ValueError("base_seed must be a nonnegative integer")
    if not callable(evaluate_replicate):
        raise TypeError("evaluate_replicate must be callable")
    root = np.random.SeedSequence(base_seed)
    child_sequences = root.spawn(n_replicates)
    out: list[BootstrapReplicate] = []

    for b, seq in enumerate(child_sequences):
        rng = np.random.default_rng(seq)
        train_idx = bootstrap_split_indices(train_size, rng)
        validation_idx = bootstrap_split_indices(validation_size, rng)
        test_idx = bootstrap_split_indices(test_size, rng)
        replicate_seed = int(rng.integers(0, 2**63 - 1))
        try:
            # Preserve the original draw even if an evaluator modifies its inputs.
            result = evaluate_replicate(
                train_idx.copy(), validation_idx.copy(), test_idx.copy(), replicate_seed
            )
            failure = None
        except Exception as exc:
            result = None
            failure = _failure_record(exc)
        out.append(
            BootstrapReplicate(
                replicate_index=b,
                train_indices=train_idx,
                validation_indices=validation_idx,
                test_indices=test_idx,
                result=result,
                failure=failure,
                replicate_seed=replicate_seed,
            )
        )
    return out
