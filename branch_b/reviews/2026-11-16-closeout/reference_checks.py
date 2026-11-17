"""Read-only review checks and proposed seed vectors; actual Python 3.14 only.

This does not change production code, adopt a seed rule or perform research fits.
The root seed and dataset identifier below are public arithmetic test fixtures.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np


def candidate_seed(root_seed: int, tier: str, dataset_id: str, attempt_index: int, role: str):
    for number in (root_seed, attempt_index):
        if type(number) is not int or number < 0:
            raise ValueError("candidate seed integers must be nonnegative and not Boolean")
    for label in (tier, dataset_id, role):
        if not isinstance(label, str) or not label or not label.isascii():
            raise ValueError("candidate labels must be nonempty ASCII strings")
    fields = ["HMG-B-SEED-CANDIDATE-v1", root_seed, tier, dataset_id, attempt_index, role]
    encoded = json.dumps(fields, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(encoded).digest()
    words = [int.from_bytes(digest[i:i + 4], "big") for i in range(0, 32, 4)]
    generator = np.random.Generator(np.random.PCG64(np.random.SeedSequence(words)))
    return {"namespace": fields, "encoded_utf8": encoded.decode(), "sha256": digest.hex(),
            "entropy_uint32_be": words,
            "first_four_raw_uint64": [int(x) for x in generator.bit_generator.random_raw(4)]}


def main():
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Actual Python 3.14 required")
    root = Path(__file__).resolve().parents[3]
    old = root / "branch_b/reviews/2026-11-16-pl/checksums.json"
    bindings = json.loads(old.read_text())
    for relative, expected in bindings.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected, relative
    roles = ["train_draw", "validation_draw", "test_draw", "evaluator", "secondary_mean"]
    vectors = [candidate_seed(17, "public_fixture", "PUBLIC-SEED-VECTOR", 3, role) for role in roles]
    assert len({x["sha256"] for x in vectors}) == len(vectors)
    assert vectors[0] == candidate_seed(17, "public_fixture", "PUBLIC-SEED-VECTOR", 3, roles[0])
    assert candidate_seed(17, "other_fixture", "PUBLIC-SEED-VECTOR", 3, roles[0])["sha256"] != vectors[0]["sha256"]
    assert candidate_seed(17, "public_fixture", "OTHER-PUBLIC-ID", 3, roles[0])["sha256"] != vectors[0]["sha256"]
    assert candidate_seed(17, "public_fixture", "PUBLIC-SEED-VECTOR", 4, roles[0])["sha256"] != vectors[0]["sha256"]
    for bad in (True, -1, 1.5):
        try:
            candidate_seed(bad, "public_fixture", "PUBLIC-SEED-VECTOR", 3, roles[0])
        except ValueError:
            pass
        else:
            raise AssertionError("invalid candidate root seed accepted")
    # Point-summary arithmetic from the already defined Q support bound.
    assert abs((sum([0.2, 0.4, 0.6]) - 2 * 2) / 5 - (-0.56)) < 1e-15
    # Numerical closeness is not an equivalence relation; no grouping is chosen.
    tau = 1e-12
    a, b, c = 0.0, 0.75 * tau, 1.5 * tau
    assert abs(a - b) <= tau and abs(b - c) <= tau and abs(a - c) > tau
    print(json.dumps({"status": "REVIEW_REFERENCE_CHECKS_PASSED", "python": sys.version,
                      "numpy": np.__version__, "existing_bundle_bindings_verified": len(bindings),
                      "seed_contract_status": "unadopted development candidate, root 17 is public fixture only",
                      "reference_vectors": vectors,
                      "scientific_approval": False, "production_rule_changed": False}, indent=2))


if __name__ == "__main__":
    main()
