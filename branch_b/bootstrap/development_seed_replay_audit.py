"""Development-only replay verifier for existing bootstrap engine draw records.

This independently reconstructs the CURRENT development engine's stream using
the explicitly supplied Branch B-owned base seed and per-split sizes. It does
not define the pending D14 namespaced production seed derivation, prescribe
D12 thresholds, or relabel missing seeds as recorded. Python 3.14 only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from branch_b.bootstrap.engine import BootstrapReplicate
from branch_b.bootstrap.development_reliability_audit import (
    DevelopmentReliabilityAudit,
    audit_development_attempts,
)


@dataclass(frozen=True)
class DevelopmentSeedReplayAudit:
    audited: DevelopmentReliabilityAudit
    base_seed: int
    exact_replay_attempts: int
    engine_stream: str = "development SeedSequence.spawn and default_rng, not frozen D14"


def audit_development_seed_replay(
    records: list[BootstrapReplicate],
    *,
    base_seed: int,
    train_size: int,
    validation_size: int,
    test_size: int,
) -> DevelopmentSeedReplayAudit:
    """Validate stored draws and recorded evaluator seeds, without changing them.

    This is intentionally independent of run_full_pipeline_bootstrap() to detect
    drift between recorded inputs and a freshly derived development stream.
    The complete audit checks success/failure records before replay.
    """
    if type(base_seed) is not int or base_seed < 0:
        raise ValueError("development base seed must be a nonnegative integer")
    audit = audit_development_attempts(
        records, train_size=train_size, validation_size=validation_size,
        test_size=test_size,
    )
    streams = np.random.SeedSequence(base_seed).spawn(audit.attempted)
    for index, (record, child) in enumerate(zip(records, streams, strict=True)):
        rng = np.random.default_rng(child)
        expected = (
            rng.integers(0, train_size, size=train_size, endpoint=False),
            rng.integers(0, validation_size, size=validation_size, endpoint=False),
            rng.integers(0, test_size, size=test_size, endpoint=False),
        )
        for label, observed, theoretical in zip(
            ("train", "validation", "test"),
            (record.train_indices, record.validation_indices, record.test_indices),
            expected, strict=True,
        ):
            if not np.array_equal(observed, theoretical):
                raise ValueError(f"attempt {index}: {label} draw differs from seed replay")
        expected_seed = int(rng.integers(0, 2**63 - 1))
        if record.replicate_seed != expected_seed:
            raise ValueError(f"attempt {index}: evaluator seed differs from seed replay")
    return DevelopmentSeedReplayAudit(
        audited=audit,
        base_seed=base_seed,
        exact_replay_attempts=audit.attempted,
    )
