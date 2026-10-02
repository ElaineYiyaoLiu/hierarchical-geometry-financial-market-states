from __future__ import annotations

from collections import Counter

import numpy as np

from branch_b.bootstrap.engine import BootstrapReplicate, run_full_pipeline_bootstrap
from branch_b.recovery_pipeline import RecoveryPipeline


def draw_multiplicities(indices: np.ndarray) -> dict[int, int]:
    """Return original-row multiplicities; duplicate draws do not become new identities."""
    return dict(sorted(Counter(int(i) for i in np.asarray(indices, dtype=int)).items()))


def distinct_original_indices(indices: np.ndarray) -> list[int]:
    """Original observations represented at least once in a bootstrap draw."""
    return sorted(draw_multiplicities(indices))


def run_recovery_pipeline_bootstrap(
    *,
    pipeline: RecoveryPipeline,
    train_values: object,
    validation_values: object,
    test_values: object,
    n_replicates: int,
    base_seed: int,
) -> list[BootstrapReplicate]:
    """Run the full recovery pipeline inside each independently resampled split.

    Preprocessing is therefore refit on bootstrap training, validation selection is
    rerun on bootstrap validation, and the selected parameters are applied to
    bootstrap test within every replicate.
    """
    train = np.asarray(train_values, dtype=float)
    validation = np.asarray(validation_values, dtype=float)
    test = np.asarray(test_values, dtype=float)

    def evaluate(train_idx, validation_idx, test_idx, seed):
        result = pipeline.run(
            train[train_idx],
            validation[validation_idx],
            test[test_idx],
            random_seed=seed,
        )
        result["bootstrap_draws"] = {
            "train_multiplicity": draw_multiplicities(train_idx),
            "validation_multiplicity": draw_multiplicities(validation_idx),
            "test_multiplicity": draw_multiplicities(test_idx),
            "test_distinct_original_indices": distinct_original_indices(test_idx),
        }
        return result

    return run_full_pipeline_bootstrap(
        n_replicates=n_replicates,
        train_size=len(train),
        validation_size=len(validation),
        test_size=len(test),
        base_seed=base_seed,
        evaluate_replicate=evaluate,
    )
