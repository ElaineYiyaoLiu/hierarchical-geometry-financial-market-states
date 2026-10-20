"""Week 3 golden-test readiness inventory, not a golden-test result.

The Schedule specifies the domains; the controlling protocol and approved
golden cases determine actual expectations. This module cannot execute a
scientific test, choose tolerances, or certify pilot readiness.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
import re

from branch_b.failures import BranchBFailure, FailureCode


GOLDEN_DOMAINS = (
    "geometry", "common_fitter", "support", "interval", "tree",
    "triplet", "bootstrap", "failure", "serialization",
)
_ALLOWED_STATUSES = frozenset({"pending", "passed", "failed", "blocked"})
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_PY314 = re.compile(r"3\.14\.\d+(?:[a-zA-Z0-9.+-]*)?\Z")


def audit_golden_readiness(cases: Sequence[dict]) -> dict:
    """Validate supplied case evidence and summarize readiness without approval.

    Every supplied case must name a Schedule domain. A passed or failed case
    must have an actual Python 3.14 version and an external evidence digest.
    Pending/blocked cases cannot claim executed evidence. Case identifiers are
    opaque, never interpreted as hints about any generating information.
    """
    if not isinstance(cases, (list, tuple)):
        raise BranchBFailure(FailureCode.INPUT_SCHEMA, "golden case inventory must be a sequence")
    counts = Counter({domain: 0 for domain in GOLDEN_DOMAINS})
    statuses = Counter()
    seen: set[str] = set()
    for case in cases:
        if type(case) is not dict or set(case) != {
            "case_id", "domain", "status", "python_version", "evidence_sha256",
        }:
            raise BranchBFailure(FailureCode.INPUT_SCHEMA, "golden case fields are incomplete")
        case_id = case["case_id"]
        domain = case["domain"]
        status = case["status"]
        if type(case_id) is not str or not case_id or case_id in seen:
            raise BranchBFailure(FailureCode.INPUT_SCHEMA, "golden case IDs must be unique and nonempty")
        seen.add(case_id)
        if domain not in GOLDEN_DOMAINS or status not in _ALLOWED_STATUSES:
            raise BranchBFailure(FailureCode.INPUT_SCHEMA, "unknown golden domain or status")
        version = case["python_version"]
        digest = case["evidence_sha256"]
        if status in ("passed", "failed"):
            if (type(version) is not str or not _PY314.fullmatch(version)
                    or type(digest) is not str or not _DIGEST.fullmatch(digest)):
                raise BranchBFailure(
                    FailureCode.INPUT_SCHEMA,
                    "executed golden cases require actual Python 3.14 version and SHA-256 evidence",
                )
        elif version is not None or digest is not None:
            raise BranchBFailure(
                FailureCode.INPUT_SCHEMA,
                "pending or blocked golden cases cannot claim execution evidence",
            )
        counts[domain] += 1
        statuses[status] += 1

    return {
        "schedule_domains": list(GOLDEN_DOMAINS),
        "domain_case_counts": dict(counts),
        "case_count": len(cases),
        "status_counts": {name: statuses[name] for name in sorted(_ALLOWED_STATUSES)},
        "missing_domains": [name for name in GOLDEN_DOMAINS if not counts[name]],
        "all_supplied_cases_passed": bool(cases) and statuses["passed"] == len(cases),
        "scientific_golden_certified": False,
        "pilot_authorization": False,
    }
