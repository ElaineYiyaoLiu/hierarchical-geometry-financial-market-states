"""Reproduce the four-point public D09 and D06 development exercise."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, is_dataclass
import hashlib
from importlib.metadata import version
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic


SOURCE = "51eca3158bff46bf52c04ec592c71559cb2ad637"
LEAVES = ["A", "B", "C", "D"]
TRIPLETS = {
    ("A", "B", "C"): ("A", "B"),
    ("A", "B", "D"): ("A", "B"),
    ("A", "C", "D"): ("C", "D"),
    ("B", "C", "D"): ("C", "D"),
}
DEVELOPMENT_FIT_SECONDS = 30.0
ATTEMPTS = 8
DEVELOPMENT_SEED = 17


def main():
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 is required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a fresh output location")
    source = args.source_root.resolve()
    commit = subprocess.check_output(["git", "-C", source, "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "-C", source, "status", "--porcelain"], text=True)
    if commit != SOURCE or status:
        raise RuntimeError("Use a clean checkout of the specified development commit")
    sys.path.insert(0, str(source))

    import numpy as np
    from branch_b.bootstrap.development_d06_runner import run_development_d06_bootstrap
    from branch_b.fitters.development_d06_fitter import D06DevelopmentFitter
    from branch_b.geometries.distances import chebyshev_dissimilarity
    from branch_b.normalization import normalize_dissimilarity
    from branch_b.preprocessing import Standardizer
    from branch_b.recovery.triplets import rooted_triplet_closest_pair

    train = np.repeat(np.array([[-1.0], [1.0]]), 12, axis=1)
    test = np.repeat(np.array([[0.0], [0.25], [2.0], [2.25]]), 12, axis=1)
    native = chebyshev_dissimilarity(Standardizer.fit(train).transform(test))
    within = max(native[0, 1], native[2, 3])
    between = min(native[i, j] for i in (0, 1) for j in (2, 3))
    matrix_ok = (
        np.isfinite(native).all() and (native >= 0).all()
        and np.array_equal(native, native.T) and np.all(native.diagonal() == 0)
    )
    assert matrix_ok and (within, between, between - within) == (0.25, 1.75, 1.50)
    assert list(TRIPLETS) == list(combinations(LEAVES, 3))
    normalized = normalize_dissimilarity(native)

    def score(tree):
        rows = []
        for triplet, expected in TRIPLETS.items():
            observed = rooted_triplet_closest_pair(tree, triplet)
            rows.append({"triplet": triplet, "expected_pair": expected, "observed_pair": observed})
        return {"correct": sum(row["expected_pair"] == row["observed_pair"] for row in rows),
                "total": len(rows), "triplets": rows}

    def toy_tree(internal, edges):
        return {"tree_format_version": "1", "root": "R", "leaves": LEAVES,
                "internal_nodes": internal,
                "edges": [{"parent": p, "child": c, "branch_length": 1.0} for p, c in edges]}

    paired = toy_tree(["R", "AB", "CD"],
                      [("R", "AB"), ("R", "CD"), ("AB", "A"), ("AB", "B"), ("CD", "C"), ("CD", "D")])
    star = toy_tree(["R"], [("R", leaf) for leaf in LEAVES])
    verifier_checks = {"declared_pair_tree": score(paired), "declared_star": score(star)}
    assert [row["correct"] for row in verifier_checks.values()] == [4, 0]

    calls = []

    class RecordedFitter:
        def fit_with_original_multiplicities(self, matrix, **kwargs):
            call = {"input": np.asarray(matrix).tolist(), **kwargs}
            calls.append(call)
            try:
                fitter = D06DevelopmentFitter(deadline_monotonic=monotonic() + DEVELOPMENT_FIT_SECONDS)
                fitted = fitter.fit_with_original_multiplicities(matrix, **kwargs)
            except Exception as error:
                call["failure"] = {"type": type(error).__name__, "message": str(error)}
                raise
            call.update(tree=fitted.tree, ultrametric=fitted.ultrametric_matrix.tolist(),
                        diagnostics=fitted.diagnostics)
            return fitted

    fitter = RecordedFitter()
    fitted = fitter.fit_with_original_multiplicities(
        normalized, original_sample_order=LEAVES, multiplicities=[1] * len(LEAVES)
    )
    actual_score = score(fitted.tree)
    ledger = run_development_d06_bootstrap(
        train_values=train, validation_values=test.copy(), test_values=test,
        train_original_sample_order=["TRAIN-A", "TRAIN-B"], validation_original_sample_order=LEAVES,
        test_original_sample_order=LEAVES, n_replicates=ATTEMPTS, base_seed=DEVELOPMENT_SEED,
        fit_preprocessor=Standardizer.fit, geometry_factory=lambda rows, _: chebyshev_dissimilarity(rows),
        geometry_parameter_candidates=lambda _: [{}], select_validation_candidate=lambda _: 0,
        fitter=fitter, full_test_tree=fitted.tree,
    )
    attempts = [{"index": row.replicate_index, "development_seed": row.replicate_seed,
                 "train_indices": row.train_indices.tolist(), "validation_indices": row.validation_indices.tolist(),
                 "test_indices": row.test_indices.tolist(), "result": row.result, "failure": row.failure}
                for row in ledger]
    assert [row["index"] for row in attempts] == list(range(ATTEMPTS))
    assert all((row["result"] is None) != (row["failure"] is None) for row in attempts)
    summary = {"correct_rooted_triplets": actual_score["correct"], "eligible_triplets": actual_score["total"],
               "bootstrap_successes": sum(row["failure"] is None for row in attempts),
               "bootstrap_failure_types": dict(Counter(row["failure"]["exception_type"]
                                                        for row in attempts if row["failure"] is not None))}
    record = {
        "source_commit": commit,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version,
        "packages": {name: version(name) for name in ("numpy", "pytest", "jsonschema")},
        "development_fit_deadline_seconds": DEVELOPMENT_FIT_SECONDS,
        "development_root_seed": DEVELOPMENT_SEED,
        "train": train.tolist(), "validation": test.tolist(), "test": test.tolist(),
        "native_matrix": native.tolist(), "within_max": float(within), "between_min": float(between),
        "native_gap": float(between - within), "verifier_checks": verifier_checks,
        "actual_fitter_score": actual_score, "fitter_calls": calls, "attempts": attempts, "summary": summary,
    }

    def serialize(value):
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, np.generic):
            return value.item()
        if is_dataclass(value):
            return asdict(value)
        raise TypeError(type(value).__name__)

    payload = json.dumps(record, indent=2, allow_nan=False, default=serialize)
    with args.output.open("x", encoding="utf-8") as target:
        target.write(payload + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
