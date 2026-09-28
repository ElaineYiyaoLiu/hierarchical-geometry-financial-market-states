from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BootstrapReplicate:
    replicate_index: int
    train_indices: np.ndarray
    validation_indices: np.ndarray
    test_indices: np.ndarray
    result: object | None
    failure: dict | None


def bootstrap_split_indices(n: int, rng: np.random.Generator) -> np.ndarray:
    if n <= 0:
        raise ValueError("bootstrap split size must be positive")
    return rng.integers(0, n, size=n, endpoint=False)


def run_full_pipeline_bootstrap(
    *,
    n_replicates: int,
    train_size: int,
    validation_size: int,
    test_size: int,
    base_seed: int,
    evaluate_replicate: Callable[[np.ndarray, np.ndarray, np.ndarray, int], object],
) -> list[BootstrapReplicate]:
    """Resample train/validation/test independently and preserve failed replicates.

    Scientific decisions such as the minimum successful-replicate count, confidence
    interval method, and failed-fit treatment are intentionally not imposed here.
    """
    if n_replicates <= 0:
        raise ValueError("n_replicates must be positive")
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
            result = evaluate_replicate(train_idx, validation_idx, test_idx, replicate_seed)
            failure = None
        except Exception as exc:
            result = None
            failure = {
                "exception_type": type(exc).__name__,
                "message": str(exc),
            }
        out.append(
            BootstrapReplicate(
                replicate_index=b,
                train_indices=train_idx,
                validation_indices=validation_idx,
                test_indices=test_idx,
                result=result,
                failure=failure,
            )
        )
    return out
