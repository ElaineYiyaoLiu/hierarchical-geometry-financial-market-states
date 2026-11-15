"""D06 dual occurrence/distinct-identity boundary (development-only).

Uses caller-supplied canonical original IDs and draw indices. Retains every
occurrence for upstream resampled preprocessing; provides a separately aligned,
distinct-original representation for *later* fitter integration.

Does not modify the pipeline, normalize a geometry, bind a tree, select an
outcome for fewer than two identities, or define failure-code mappings.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from branch_b.bootstrap.checked import bind_bootstrap_draw
from branch_b.recovery_pipeline.result_validation import checked_sample_order


@dataclass(frozen=True)
class D06DrawBoundary:
    original_sample_order: tuple[str, ...]
    fit_sample_order: tuple[str, ...]
    draw_indices: tuple[int, ...]
    occurrence_original_ids: tuple[str, ...]
    distinct_original_ids: tuple[str, ...]
    multiplicities: tuple[int, ...]
    # For every distinct original ID, where it first appears in drawn rows.
    first_occurrence_positions: tuple[int, ...]

    def pair_weights(self) -> tuple[int, ...]:
        return tuple(
            self.multiplicities[i] * self.multiplicities[j]
            for i in range(len(self.multiplicities))
            for j in range(i + 1, len(self.multiplicities))
        )

    def total_pair_weight(self) -> int:
        return sum(self.pair_weights())


def build_d06_draw_boundary(
    indices: object,
    *,
    original_sample_order: list[str],
    fit_sample_order: list[str],
) -> D06DrawBoundary:
    """Preserve draw-order occurrences and canonical-order active identities.

    Zero-count originals are absent from distinct identities. No minimum-active
    threshold or reliability/failure decision is made here.
    """
    originals = checked_sample_order(original_sample_order)
    labels = checked_sample_order(fit_sample_order)
    bindings = bind_bootstrap_draw(
        indices, original_sample_order=originals, fit_sample_order=labels
    )
    # Bindings have been validated against the authoritative input order.
    index_by_id = {identity: i for i, identity in enumerate(originals)}
    counts = [0] * len(originals)
    first = {}
    occurrences = []
    positions = []
    for position, binding in enumerate(bindings):
        original_id = binding["original_sample_id"]
        original_index = index_by_id[original_id]
        positions.append(original_index)
        occurrences.append(original_id)
        counts[original_index] += 1
        first.setdefault(original_index, position)

    active_indices = [i for i, count in enumerate(counts) if count > 0]
    return D06DrawBoundary(
        original_sample_order=tuple(originals),
        fit_sample_order=tuple(labels),
        draw_indices=tuple(positions),
        occurrence_original_ids=tuple(occurrences),
        distinct_original_ids=tuple(originals[i] for i in active_indices),
        multiplicities=tuple(counts[i] for i in active_indices),
        first_occurrence_positions=tuple(first[i] for i in active_indices),
    )


def aligned_distinct_rows(
    transformed_occurrence_rows: object,
    boundary: D06DrawBoundary,
) -> np.ndarray:
    """Project pointwise transformed occurrence rows into canonical ID order.

    Call only after a separately approved transformation has been applied
    to the full resampled multiset. Checks exact equality for duplicate rows;
    no equivalence claim for arbitrary stateful transformations is made.
    """
    if np.ma.isMaskedArray(transformed_occurrence_rows):
        raise ValueError("transformed rows cannot be masked")
    raw = np.asarray(transformed_occurrence_rows)
    if raw.ndim != 2 or raw.dtype.kind not in "iuf":
        raise ValueError("transformed occurrence rows must be a real matrix")
    values = raw.astype(np.float64, copy=True)
    if values.shape[0] != len(boundary.draw_indices) or not np.all(np.isfinite(values)):
        raise ValueError("transformed rows must match draw occurrences and be finite")
    first_by_original = {}
    for position, original_index in enumerate(boundary.draw_indices):
        if original_index in first_by_original:
            first_value = values[first_by_original[original_index]]
            if not np.array_equal(values[position], first_value):
                raise ValueError("same-original transformed rows disagree; cannot collapse")
        else:
            first_by_original[original_index] = position
    return values[list(boundary.first_occurrence_positions)].copy()
