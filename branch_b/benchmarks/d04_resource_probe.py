"""Development-only exact-D04 resource probe; no scientific failure mapping."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from math import factorial, prod
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time


CASES = (
    {"name": "K4_all_equal", "vertices": 4, "weights": [1.0] * 6},
    {"name": "K5_seven_equal_edges", "vertices": 5, "weights": [1.0] * 7 + [2.0, 3.0, 4.0]},
    {"name": "K5_all_equal", "vertices": 5, "weights": [1.0] * 10},
    {"name": "K6_all_equal", "vertices": 6, "weights": [1.0] * 15},
    {"name": "K7_all_equal", "vertices": 7, "weights": [1.0] * 21},
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def worker(engine: Path, case: dict, seconds: float):
    spec = importlib.util.spec_from_file_location("d04_probe_engine", engine)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    start = time.monotonic()
    result = {"engine_started": True}
    try:
        answer = module.exact_average_minmax_jacobian(
            case["vertices"], case["weights"], deadline_monotonic=start + seconds)
        expected = prod(factorial(n) for n in Counter(case["weights"]).values())
        assert answer.strict_order_count == expected
        assert all(sum(row) == 1 and all(value >= 0 for value in row) for row in answer.jacobian)
        exact = [[str(v) for v in row] for row in answer.jacobian]
        result.update(outcome="COMPLETED_EXACT", hierarchy_count=answer.hierarchy_count,
                      strict_order_count=answer.strict_order_count,
                      maximum_stage_states=answer.maximum_stage_states,
                      processed_weight_levels=answer.processed_weight_levels,
                      exact_jacobian_sha256=hashlib.sha256(json.dumps(exact, separators=(",", ":")).encode()).hexdigest(),
                      row_sum_and_nonnegative_checks_passed=True)
    except module.ExactD04DeadlineExpired as error:
        result.update(outcome="ACTUAL_DEADLINE_EXPIRED",
                      maximum_stage_states=error.maximum_stage_states,
                      processed_weight_levels=error.processed_weight_levels)
    except MemoryError:
        result.update(outcome="MEMORY_ERROR")
    except Exception as error:
        result.update(outcome="ERROR", error_type=type(error).__name__, diagnostic=str(error))
    result["engine_elapsed_seconds"] = time.monotonic() - start
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result["worker_peak_rss_bytes"] = raw if sys.platform == "darwin" else raw * 1024
    if result["outcome"] == "ACTUAL_DEADLINE_EXPIRED":
        assert result["engine_elapsed_seconds"] >= seconds
    print(json.dumps(result, allow_nan=False), flush=True)


def current_rss(pid):
    measurement = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)],
                                 text=True, capture_output=True, timeout=2)
    text = measurement.stdout.strip()
    return int(text) * 1024 if measurement.returncode == 0 and text else None


def probe(engine, case, seconds, memory_bytes, watchdog_grace):
    command = [sys.executable, str(Path(__file__).resolve()), "--worker", json.dumps(case),
               "--engine", str(engine.resolve()), "--seconds", str(seconds)]
    start = time.monotonic()
    child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    maximum, samples, stopped = 0, 0, None
    try:
        while child.poll() is None:
            rss = current_rss(child.pid)
            if rss is not None:
                maximum = max(maximum, rss)
                samples += 1
            if maximum > memory_bytes:
                stopped = "DEVELOPMENT_MEMORY_GUARD"
            elif time.monotonic() - start > seconds + watchdog_grace:
                stopped = "DEVELOPMENT_WATCHDOG"
            if stopped:
                child.terminate()
                break
            time.sleep(0.05)
    except BaseException:
        if child.poll() is None:
            child.terminate()
        try:
            child.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            child.kill()
            child.communicate()
        raise
    try:
        stdout, stderr = child.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        child.kill()
        stdout, stderr = child.communicate()
    result = dict(name=case["name"], vertices=case["vertices"], edges=len(case["weights"]),
                  largest_equal_edge_group=max(Counter(case["weights"]).values()),
                  parent_elapsed_seconds=time.monotonic() - start,
                  sampled_peak_rss_bytes=maximum, rss_samples=samples,
                  returncode=child.returncode, scientific_failure_code=None)
    if stopped:
        result["outcome"] = stopped
    elif child.returncode != 0:
        result.update(outcome="WORKER_EXIT", diagnostic=stderr)
    else:
        result.update(json.loads(stdout))
    if stderr:
        result["stderr"] = stderr
    return result


def main():
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path, default=Path("branch_b/fitters/exact_tie_dp.py"))
    parser.add_argument("--seconds", type=float, default=10)
    parser.add_argument("--memory-mib", type=int, default=384)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker")
    args = parser.parse_args()
    if args.worker:
        worker(args.engine, json.loads(args.worker), args.seconds)
        return
    if args.seconds <= 0 or args.memory_mib < 64 or args.output is None:
        raise ValueError("positive development deadline, practical memory guard and output required")
    current_rss(os.getpid())  # Refuse to start if live memory monitoring is unavailable.
    before = digest(args.engine)
    results = []
    for case in CASES:
        row = probe(args.engine, case, args.seconds, args.memory_mib * 1024**2, 2)
        results.append(row)
        print(json.dumps({k: row[k] for k in ("name", "vertices", "largest_equal_edge_group", "outcome", "parent_elapsed_seconds", "sampled_peak_rss_bytes")}), flush=True)
    assert before == digest(args.engine)
    report = dict(record="synthetic_d04_resource_probe", python=platform.python_version(),
                  platform=platform.platform(), machine=platform.machine(),
                  engine_ref="branch_b/fitters/exact_tie_dp.py", engine_sha256=before,
                  probe_sha256=digest(Path(__file__)), cases=results,
                  development_limits={"actual_engine_deadline_seconds": args.seconds,
                                      "sampled_rss_guard_mib": args.memory_mib,
                                      "watchdog_grace_seconds": 2, "rss_sample_interval_seconds": 0.05},
                  scientific_timeout_selected=False, scientific_failure_registry_changed=False,
                  experimental_data_used=False, production_fitter_certified=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
