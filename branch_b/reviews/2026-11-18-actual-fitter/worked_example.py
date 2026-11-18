"""Fixed public arithmetic actual-fitter exercise. Python 3.14 only.

Run against an explicitly checked out Branch B source with --source-root.
No seed search, input search, rule changes or production activation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic


def main():
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Actual Python 3.14 required")
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a fresh output; preserve previous runs")
    source = args.source_root.resolve()
    sys.path.insert(0, str(source))
    import numpy as np
    from branch_b.fitters.development_d06_fitter import D06DevelopmentFitter
    from branch_b.preprocessing import Standardizer
    from branch_b.geometries.distances import chebyshev_dissimilarity
    from branch_b.normalization import normalize_dissimilarity
    from branch_b.bootstrap.development_d06_runner import run_development_d06_bootstrap

    values = np.repeat(np.array([[1.], [2.], [4.]]), 12, axis=1)
    identities = ["PUBLIC-A", "PUBLIC-B", "PUBLIC-C"]
    calls = []

    class ActualFitter:
        def fit_with_original_multiplicities(self, matrix, **kwargs):
            call = {"matrix": np.asarray(matrix).tolist(), **kwargs}
            calls.append(call)
            try:
                fit = D06DevelopmentFitter(deadline_monotonic=monotonic()+30.0).fit_with_original_multiplicities(matrix, **kwargs)
                call.update({"tree": fit.tree, "ultrametric": fit.ultrametric_matrix.tolist(), "diagnostics": fit.diagnostics})
                return fit
            except Exception as error:
                call["exception"] = {"type": type(error).__name__, "message": str(error)}
                raise

    fitter = ActualFitter()
    reference_input = normalize_dissimilarity(chebyshev_dissimilarity(Standardizer.fit(values).transform(values)))
    reference = fitter.fit_with_original_multiplicities(reference_input, original_sample_order=identities, multiplicities=[1, 1, 1])
    records = run_development_d06_bootstrap(
        train_values=values, validation_values=values.copy(), test_values=values.copy(),
        train_original_sample_order=identities, validation_original_sample_order=identities,
        test_original_sample_order=identities, n_replicates=8, base_seed=17,
        fit_preprocessor=Standardizer.fit,
        geometry_factory=lambda rows, parameters: chebyshev_dissimilarity(rows),
        geometry_parameter_candidates=lambda train: [{}],
        select_validation_candidate=lambda candidates: 0,
        fitter=fitter, full_test_tree=reference.tree,
    )
    attempts = [{"index": r.replicate_index, "seed": r.replicate_seed,
                 "train_indices": r.train_indices.tolist(), "validation_indices": r.validation_indices.tolist(),
                 "test_indices": r.test_indices.tolist(), "result": r.result, "failure": r.failure} for r in records]
    assert len(attempts) == 8 and [x["index"] for x in attempts] == list(range(8))
    assert all((x["result"] is None) != (x["failure"] is None) for x in attempts)
    files = ["branch_b/fitters/development_d06_fitter.py", "branch_b/fitters/development_optimizer.py",
             "branch_b/bootstrap/development_d06_runner.py", "branch_b/bootstrap/development_distinct_stability.py"]
    output = {"python": sys.version, "versions": {n: metadata.version(n) for n in ["numpy", "pytest", "jsonschema"]},
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip(),
              "source_diff": subprocess.check_output(["git", "diff", "HEAD"], cwd=source, text=True),
              "source_sha256": {p: hashlib.sha256((source/p).read_bytes()).hexdigest() for p in files},
              "scope": "public arithmetic development example, no scientific-bank result or approval",
              "input": values.tolist(), "input_ids": identities, "root_seed": 17, "attempt_budget": 8,
              "development_per_fit_budget_seconds": 30.0, "pilot_timeout_selected": False,
              "reference_matrix": reference.ultrametric_matrix.tolist(), "reference_tree": reference.tree,
              "calls": calls, "attempts": attempts,
              "successes": sum(x["failure"] is None for x in attempts),
              "failure_types": dict(Counter(x["failure"]["exception_type"] for x in attempts if x["failure"])),
              "scientific_approval": False}

    def convert(value):
        if isinstance(value, np.ndarray): return value.tolist()
        if isinstance(value, np.generic): return value.item()
        raise TypeError(type(value).__name__)
    args.output.write_text(json.dumps(output, indent=2, default=convert, allow_nan=False)+'\n')
    print(json.dumps({"attempts": len(attempts), "successes": output["successes"], "failure_types": output["failure_types"]}))


if __name__ == "__main__":
    main()
