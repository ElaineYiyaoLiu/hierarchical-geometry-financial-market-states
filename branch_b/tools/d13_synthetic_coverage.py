"""D13 synthetic conditional-mean coverage diagnostics (Python 3.14 only).

Development-only bounded simulations with known analytic means, never project
datasets, never hidden hierarchy information, and never production seed rules.
No coverage acceptance threshold or method retuning is defined here.
"""

from __future__ import annotations

import argparse
import json
from math import sqrt
from statistics import NormalDist

import numpy as np

from branch_b.bootstrap.development_d13_interval import (
    development_d13_resampled_mean_interval,
)

SCENARIOS = ("symmetric_uniform", "two_point", "skewed_beta")


def _known_conditional_mean(name: str) -> float:
    if name == "symmetric_uniform":
        return 0.0                     # Uniform[-1, 1]
    if name == "two_point":
        return 0.25                    # Bernoulli(p=0.25)
    if name == "skewed_beta":
        return -1.4                    # 3*Beta(1, 4) - 2
    raise ValueError("unknown synthetic scenario")


def _sample_synthetic(name: str, size: int, rng: np.random.Generator) -> np.ndarray:
    if name == "symmetric_uniform":
        return rng.uniform(-1.0, 1.0, size=size)
    if name == "two_point":
        return (rng.random(size) < 0.25).astype(float)
    if name == "skewed_beta":
        return 3.0 * rng.beta(1.0, 4.0, size=size) - 2.0
    raise ValueError("unknown synthetic scenario")


def wilson_95_interval(successes: int, trials: int) -> tuple[float, float]:
    """Uncertainty on empirical diagnostic coverage, not the D13 interval."""
    if type(trials) is not int or trials <= 0:
        raise ValueError("positive integer trial count required")
    if type(successes) is not int or not 0 <= successes <= trials:
        raise ValueError("coverage count outside [0,trials]")
    z = NormalDist().inv_cdf(0.975)
    p = successes / trials
    denom = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denom
    radius = z * sqrt(p * (1.0 - p) / trials + z * z / (4.0 * trials * trials)) / denom
    return center - radius, center + radius


def synthetic_coverage_diagnostics(*, trials: int, sample_size: int,
                                   seed: int) -> dict:
    """Evaluate the unchanged D13 candidate on independent toy samples."""
    if type(trials) is not int or trials <= 0:
        raise ValueError("trials must be a positive integer")
    if type(sample_size) is not int or sample_size <= 0:
        raise ValueError("sample_size must be a positive integer")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    root = np.random.SeedSequence(seed)
    scenario_sequences = root.spawn(len(SCENARIOS))
    records = []
    for name, scenario_sequence in zip(SCENARIOS, scenario_sequences, strict=True):
        sample_rng, interval_rng = (
            np.random.default_rng(s) for s in scenario_sequence.spawn(2)
        )
        mean = _known_conditional_mean(name)
        covered = 0
        widths = []
        for _ in range(trials):
            values = _sample_synthetic(name, sample_size, sample_rng)
            candidate = development_d13_resampled_mean_interval(
                values, rng=interval_rng
            )
            covered += int(candidate.lower_endpoint <= mean <= candidate.upper_endpoint)
            widths.append(candidate.upper_endpoint - candidate.lower_endpoint)
        lo, hi = wilson_95_interval(covered, trials)
        records.append({
            "scenario": name,
            "true_conditional_mean": mean,
            "successful_sample_size": sample_size,
            "outer_trials": trials,
            "intervals_covering_true_mean": covered,
            "empirical_coverage": covered / trials,
            "coverage_wilson_95_lower": lo,
            "coverage_wilson_95_upper": hi,
            "mean_interval_width": float(np.mean(widths)),
            "zero_width_intervals": sum(width == 0.0 for width in widths),
        })
    return {
        "purpose": "synthetic_development_conditional_mc_coverage_only",
        "not_a_scientific_coverage_certification": True,
        "seed_note": "synthetic development-only, NOT the frozen D14 seed policy",
        "development_seed": seed,
        "secondary_resamples_per_interval": 10_000,
        "nominal_interval_level": 0.95,
        "results": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=48)
    parser.add_argument("--sample-size", type=int, default=24)
    parser.add_argument("--seed", type=int, default=314159)
    args = parser.parse_args()
    output = synthetic_coverage_diagnostics(
        trials=args.trials, sample_size=args.sample_size, seed=args.seed
    )
    print(json.dumps(output, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
