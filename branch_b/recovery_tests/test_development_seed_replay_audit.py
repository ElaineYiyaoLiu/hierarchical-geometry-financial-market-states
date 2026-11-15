"""Synthetic-only D14 development seed/draw replay checks, Python 3.14."""

from dataclasses import replace

import numpy as np
import pytest

from branch_b.bootstrap.engine import run_full_pipeline_bootstrap
from branch_b.bootstrap.development_seed_replay_audit import audit_development_seed_replay


def _ledger(seed=36):
    state = {"attempt": 0}

    def evaluate(train, validation, test, replicate_seed):
        state["attempt"] += 1
        if state["attempt"] in (2, 4):
            raise ArithmeticError("synthetic failure retained")
        return {"observed_seed": replicate_seed}

    return run_full_pipeline_bootstrap(
        n_replicates=6, train_size=9, validation_size=8, test_size=7,
        base_seed=seed, evaluate_replicate=evaluate,
    )


def _audit(records, seed=36):
    return audit_development_seed_replay(
        records, base_seed=seed, train_size=9, validation_size=8, test_size=7
    )


def test_replays_every_draw_and_seed_even_after_failed_fit():
    records = _ledger()
    outcome = _audit(records)
    assert outcome.exact_replay_attempts == 6
    assert outcome.audited.attempted == 6
    assert outcome.audited.succeeded == 4
    assert outcome.audited.failed == 2
    assert outcome.base_seed == 36


def test_wrong_development_seed_rejected():
    with pytest.raises(ValueError, match="differs from seed replay"):
        _audit(_ledger(), seed=37)


@pytest.mark.parametrize("which", ["train", "validation", "test"])
def test_tampered_but_in_range_split_draw_fails_replay(which):
    records = _ledger()
    target = getattr(records[0], which + "_indices").copy()
    size = {"train": 9, "validation": 8, "test": 7}[which]
    target[0] = (int(target[0]) + 1) % size
    records[0] = replace(records[0], **{which + "_indices": target})
    with pytest.raises(ValueError, match=which + " draw differs"):
        _audit(records)


def test_tampered_but_valid_evaluator_seed_fails_replay():
    records = _ledger()
    original = records[0].replicate_seed
    records[0] = replace(records[0], replicate_seed=original + 1)
    with pytest.raises(ValueError, match="evaluator seed differs"):
        _audit(records)


def test_original_array_contents_unchanged_by_replay_audit():
    records = _ledger()
    originals = [
        (r.train_indices.copy(), r.validation_indices.copy(),
         r.test_indices.copy(), r.failure)
        for r in records
    ]
    _audit(records)
    for record, (train, validation, test, failure) in zip(records, originals, strict=True):
        np.testing.assert_array_equal(record.train_indices, train)
        np.testing.assert_array_equal(record.validation_indices, validation)
        np.testing.assert_array_equal(record.test_indices, test)
        assert record.failure == failure


@pytest.mark.parametrize("seed", [None, -1, 3.6, True])
def test_invalid_development_seeds_fail_closed(seed):
    with pytest.raises(ValueError, match="base seed"):
        _audit(_ledger(), seed=seed)
