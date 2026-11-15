"""D12/D14 threshold-free bootstrap ledger audit (development only).

No D12 pilot cutoffs, minimum common-ID rule, D14 production namespace,
or scientific support decision is chosen here. This module audits an existing
observable-side development ledger and never edits it. Python 3.14 only.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import numpy as np

from branch_b.bootstrap.engine import BootstrapReplicate


@dataclass(frozen=True)
class DevelopmentReliabilityAudit:
    attempted: int
    succeeded: int
    failed: int
    failure_fraction: float
    failure_codes: tuple[tuple[str, int], ...]
    distinct_recorded_seeds: int
    minimum_distinct_train_positions: int
    minimum_distinct_validation_positions: int
    minimum_distinct_test_positions: int


def audit_development_attempts(
    records: list[BootstrapReplicate],
    *,
    train_size: int,
    validation_size: int,
    test_size: int,
) -> DevelopmentReliabilityAudit:
    """Check all attempts and observable resampled-position bookkeeping.

    Distinct positions count sampled originals *within each split*, not an
    approved D12 inter-split common-identity statistic. This audit neither
    accepts nor rejects scientific bootstrap reliability.
    """
    if not isinstance(records, list) or not records:
        raise ValueError("nonempty attempt ledger required")
    for name, size in (
        ("train_size", train_size),
        ("validation_size", validation_size),
        ("test_size", test_size),
    ):
        if type(size) is not int or size <= 0:
            raise ValueError(f"{name} must be positive integer")
    counts = (train_size, validation_size, test_size)
    distinct_min = [None, None, None]
    seeds: set[int] = set()
    failures = Counter()
    succeeded = 0
    for expected_index, record in enumerate(records):
        if not isinstance(record, BootstrapReplicate):
            raise TypeError("all attempt records must be BootstrapReplicate")
        if record.replicate_index != expected_index:
            raise ValueError("missing, repeated or reordered attempt index")
        if (type(record.replicate_seed) is not int
                or record.replicate_seed < 0):
            raise ValueError("missing or invalid recorded attempt seed")
        if record.replicate_seed in seeds:
            raise ValueError("duplicate recorded attempt seed")
        seeds.add(record.replicate_seed)
        for which, (indices, split_size) in enumerate(zip(
            (record.train_indices, record.validation_indices, record.test_indices),
            counts, strict=True,
        )):
            if not isinstance(indices, np.ndarray):
                raise ValueError("attempt indices must be NumPy arrays")
            if indices.ndim != 1 or len(indices) != split_size or indices.dtype.kind not in "iu":
                raise ValueError("attempt indices have invalid shape, size or dtype")
            if np.any(indices >= split_size) or np.any(indices < 0):
                raise ValueError("attempt indices outside original split bounds")
            unique = int(np.unique(indices).size)
            distinct_min[which] = unique if distinct_min[which] is None else min(distinct_min[which], unique)
        if record.failure is None:
            if record.result is None:
                raise ValueError("attempt marked successful but missing result")
            succeeded += 1
        else:
            if record.result is not None:
                raise ValueError("failed attempt must not also have successful result")
            if not isinstance(record.failure, dict):
                raise ValueError("failure record must be a mapping")
            kind = record.failure.get("failure_code")
            if kind is None:
                kind = record.failure.get("exception_type")
                if type(kind) is not str or not kind:
                    raise ValueError("failure lacks both code and exception type")
                kind = "EXCEPTION:" + kind
            elif type(kind) is not str or not kind:
                raise ValueError("invalid registered failure code")
            failures[kind] += 1
    attempted = len(records)
    return DevelopmentReliabilityAudit(
        attempted=attempted,
        succeeded=succeeded,
        failed=attempted - succeeded,
        failure_fraction=(attempted - succeeded) / attempted,
        failure_codes=tuple(sorted(failures.items())),
        distinct_recorded_seeds=len(seeds),
        minimum_distinct_train_positions=distinct_min[0],
        minimum_distinct_validation_positions=distinct_min[1],
        minimum_distinct_test_positions=distinct_min[2],
    )
