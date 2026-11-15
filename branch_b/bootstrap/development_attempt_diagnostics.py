"""Development-only sidecar diagnostics for bootstrap attempts.

Records exception attributes while they are still available inside the evaluator,
then re-raises unmodified to the existing bootstrap engine. The engine's
BootstrapReplicate and failure dictionaries are NOT changed. No scientific
failure-code mapping, retry, omission, or data-access policy is introduced.

Use only with Branch B-permitted observable/development inputs. The caller owns
the seed and evaluator; this wrapper does not access hidden project materials.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from branch_b.bootstrap.engine import BootstrapReplicate, run_full_pipeline_bootstrap
from branch_b.failures import BranchBFailure
from branch_b.fitters.development_optimizer import DevelopmentOptimizerDeadlineExpired
from branch_b.fitters.exact_tie_dp import ExactD04DeadlineExpired


@dataclass(frozen=True)
class DevelopmentAttemptDiagnostic:
    replicate_index: int
    replicate_seed: int
    outcome: str
    exception_type: str | None
    existing_failure_code: str | None
    detail: dict[str, int | str]


def _describe_failure(exc: Exception) -> tuple[str | None, dict[str, int | str]]:
    existing_code = str(exc.code) if isinstance(exc, BranchBFailure) else None
    if isinstance(exc, ExactD04DeadlineExpired):
        return existing_code, {
            "deadline_source": "d04",
            "processed_weight_levels": exc.processed_weight_levels,
            "maximum_stage_states": exc.maximum_stage_states,
        }
    if isinstance(exc, DevelopmentOptimizerDeadlineExpired):
        return existing_code, {"deadline_source": "optimizer"}
    return existing_code, {}


def run_development_bootstrap_with_diagnostics(
    *,
    n_replicates: int,
    train_size: int,
    validation_size: int,
    test_size: int,
    base_seed: int,
    evaluate_replicate: Callable[[np.ndarray, np.ndarray, np.ndarray, int], object],
) -> tuple[list[BootstrapReplicate], list[DevelopmentAttemptDiagnostic]]:
    """Preserve all attempts and their D04 deadline attributes in a sidecar.

    Only the standard engine draws indices and seeds. This adapter must not
    claim that the sidecar is a frozen export schema or an approved failure
    mapping. Captures a diagnostic before re-raising each exception.
    """
    diagnostics: list[DevelopmentAttemptDiagnostic] = []

    def inspect(train: np.ndarray, validation: np.ndarray,
                test: np.ndarray, seed: int) -> object:
        index = len(diagnostics)
        try:
            value = evaluate_replicate(train, validation, test, seed)
        except Exception as exc:
            code, detail = _describe_failure(exc)
            diagnostics.append(DevelopmentAttemptDiagnostic(
                replicate_index=index,
                replicate_seed=seed,
                outcome="FAILED",
                exception_type=type(exc).__name__,
                existing_failure_code=code,
                detail=detail,
            ))
            raise
        diagnostics.append(DevelopmentAttemptDiagnostic(
            replicate_index=index,
            replicate_seed=seed,
            outcome="SUCCEEDED",
            exception_type=None,
            existing_failure_code=None,
            detail={},
        ))
        return value

    records = run_full_pipeline_bootstrap(
        n_replicates=n_replicates,
        train_size=train_size,
        validation_size=validation_size,
        test_size=test_size,
        base_seed=base_seed,
        evaluate_replicate=inspect,
    )
    if len(diagnostics) != len(records):
        raise AssertionError("bootstrap sidecar must retain one record per attempt")
    for i, (record, diagnostic) in enumerate(zip(records, diagnostics, strict=True)):
        if (record.replicate_index != i or diagnostic.replicate_index != i
                or diagnostic.replicate_seed != record.replicate_seed
                or (record.failure is None) != (diagnostic.outcome == "SUCCEEDED")):
            raise AssertionError("bootstrap sidecar and attempts are misaligned")
    return records, diagnostics
