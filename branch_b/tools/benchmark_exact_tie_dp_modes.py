"""Development-only D04 benchmark with explicit allocation-tracing modes.

Uses constant synthetic weights, not experimental-bank inputs.  The --seconds
argument controls only this development run, never the scientific fitter timeout.
Every case runs in an independent Python 3.14 process.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
from time import monotonic
import tracemalloc


def require_python314():
    if tuple(sys.version_info[:2]) != (3, 14):
        raise RuntimeError("D04 benchmarks require actual Python 3.14")


def peak_process_memory():
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            class Counters(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD
            ]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            record = Counters()
            record.cb = ctypes.sizeof(record)
            if not psapi.GetProcessMemoryInfo(
                kernel.GetCurrentProcess(), ctypes.byref(record), record.cb
            ):
                raise OSError("GetProcessMemoryInfo failed")
            return {"bytes": record.PeakWorkingSetSize,
                    "metric": "Windows PeakWorkingSetSize", "error_type": None}
        if sys.platform.startswith("linux") or sys.platform == "darwin":
            import resource
            value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            scale = 1 if sys.platform == "darwin" else 1024
            return {"bytes": int(value * scale),
                    "metric": "ru_maxrss", "error_type": None}
        return {"bytes": None, "metric": "unavailable", "error_type": None}
    except Exception as exc:
        return {"bytes": None, "metric": "unavailable",
                "error_type": type(exc).__name__}


def provenance():
    root = Path(__file__).resolve().parents[2]
    files = [
        "branch_b/fitters/exact_tie_dp.py",
        "branch_b/tools/benchmark_exact_tie_dp_modes.py",
    ]

    def git(*args):
        try:
            return subprocess.check_output(
                ["git", "-C", str(root), *args],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    versions = {}
    for package in ("numpy", "pytest"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    return {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_build": platform.python_build(),
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "dependency_versions": versions,
        "git_head": git("rev-parse", "HEAD"),
        "git_branch": git("branch", "--show-current"),
        "engine_head_blob": git("rev-parse", "HEAD:branch_b/fitters/exact_tie_dp.py"),
        "engine_worktree_blob": git(
            "hash-object", "--path=branch_b/fitters/exact_tie_dp.py",
            "branch_b/fitters/exact_tie_dp.py"
        ),
        "source_sha256": {
            item: (hashlib.sha256((root / item).read_bytes()).hexdigest()
                   if (root / item).is_file() else None)
            for item in files
        },
        "seed": None,
        "randomness": "none; deterministic constant synthetic weights",
    }


def measure(n, seconds, *, tracing):
    require_python314()
    from branch_b.fitters.exact_tie_dp import (
        ExactD04DeadlineExpired, exact_average_minmax_jacobian
    )

    weights = (0.5,) * (n * (n - 1) // 2)
    result = None
    status = None
    error = None
    maximum_states = None
    processed_levels = None
    if tracemalloc.is_tracing():
        raise RuntimeError("benchmark requires ownership of allocation tracing")
    if tracing:
        tracemalloc.start()

    started = monotonic()
    deadline = started + seconds
    try:
        result = exact_average_minmax_jacobian(
            n, weights, deadline_monotonic=deadline
        )
        ended = monotonic()
        status = "TIMEOUT" if ended >= deadline else "COMPLETED"
    except ExactD04DeadlineExpired as exc:
        ended = monotonic()
        status = "TIMEOUT" if ended >= deadline else "EARLY_DEADLINE_ERROR"
        error = type(exc).__name__
        maximum_states = exc.maximum_stage_states
        processed_levels = exc.processed_weight_levels
    except Exception as exc:
        ended = monotonic()
        status = "MEMORY_ERROR" if isinstance(exc, MemoryError) else "ERROR"
        error = type(exc).__name__
    finally:
        if tracing:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
        else:
            current, peak = None, None

    digest = None
    if result is not None:
        maximum_states = result.maximum_stage_states
        processed_levels = result.processed_weight_levels
        rational = [
            [[x.numerator, x.denominator] for x in row]
            for row in result.jacobian
        ]
        digest = hashlib.sha256(
            json.dumps(rational, separators=(",", ":")).encode("ascii")
        ).hexdigest()
    return {
        "vertices": n,
        "edges": len(weights),
        "weight": 0.5,
        "budget_seconds": seconds,
        "tracemalloc_enabled": tracing,
        "status": status,
        "engine_returned": result is not None,
        "hierarchy_count": result.hierarchy_count if result is not None else None,
        "strict_order_count": result.strict_order_count if result is not None else None,
        "maximum_stage_states": maximum_states,
        "processed_weight_levels": processed_levels,
        "jacobian_sha256": digest,
        "exception_type": error,
        "elapsed_seconds": ended - started,
        "deadline_elapsed": ended >= deadline,
        "deadline_overshoot_seconds": max(0.0, ended - deadline),
        "python_traced_current_bytes": current,
        "python_traced_peak_bytes": peak,
        "process_peak_memory": peak_process_memory(),
    }


def main(argv=None):
    require_python314()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vertices", nargs="+", type=int, default=[3, 4, 5])
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--tracemalloc", action="store_true",
                        help="enable Python allocation tracing (off by default)")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if any(n < 2 for n in args.vertices):
        parser.error("vertices must be >= 2")
    if not math.isfinite(args.seconds) or args.seconds <= 0:
        parser.error("seconds must be finite and positive")
    if args.worker and len(args.vertices) != 1:
        parser.error("worker accepts exactly one vertex count")

    if args.worker:
        record = {
            "schema_version": 2,
            "scope": "development-only synthetic D04 benchmark",
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "provenance": provenance(),
            "timing_scope": ("engine call with Python allocation tracing"
                             if args.tracemalloc else
                             "engine call without Python allocation tracing"),
            "state_scope": "completed-stage frontier; partial stage excluded",
            "case": measure(args.vertices[0], args.seconds,
                            tracing=args.tracemalloc),
        }
        print(json.dumps(record, allow_nan=False))
        return 0 if record["case"]["status"] == "COMPLETED" else 1

    failed = False
    for n in args.vertices:
        command = [
            sys.executable, "-B", "-m",
            "branch_b.tools.benchmark_exact_tie_dp_modes",
            "--worker", "--vertices", str(n), "--seconds", str(args.seconds),
        ]
        if args.tracemalloc:
            command.append("--tracemalloc")
        child = subprocess.run(command, text=True, capture_output=True)
        try:
            record = json.loads(child.stdout)
        except json.JSONDecodeError:
            record = {
                "schema_version": 2,
                "scope": "development-only synthetic D04 benchmark",
                "case": {
                    "vertices": n, "budget_seconds": args.seconds,
                    "tracemalloc_enabled": args.tracemalloc,
                    "status": "WORKER_ERROR",
                    "returncode": child.returncode,
                },
                "diagnostic": "worker did not produce a valid JSON record",
            }
        failed |= record["case"]["status"] != "COMPLETED"
        print(json.dumps(record, allow_nan=False), flush=True)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
