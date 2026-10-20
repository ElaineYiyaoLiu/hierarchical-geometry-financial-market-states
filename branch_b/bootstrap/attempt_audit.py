"""Descriptive audit of attempted bootstrap records; no support decisions.

Counts do not replace protocol-frozen minimum-success, reliability, interval,
or failure-sensitivity rules. This module does not inspect experimental data.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from branch_b.bootstrap.engine import BootstrapReplicate


def audit_bootstrap_attempts(records: Sequence[BootstrapReplicate]) -> dict:
    """Count actual attempt outcomes without dropping or reclassifying failures.

    A malformed attempt is reported as inconsistent, never silently counted as
    successful. Uncoded exceptions remain visible in the exception breakdown.
    """
    if not isinstance(records, (list, tuple)):
        raise TypeError("bootstrap records must be a list or tuple")
    codes: Counter[str] = Counter()
    exceptions: Counter[str] = Counter()
    success = failure = inconsistent = 0
    for record in records:
        if not isinstance(record, BootstrapReplicate):
            raise TypeError("each bootstrap record must be BootstrapReplicate")
        if record.failure is None and record.result is not None:
            success += 1
        elif record.failure is not None and record.result is None:
            failure += 1
            if not isinstance(record.failure, dict):
                raise TypeError("bootstrap failure must be a dictionary")
            code = record.failure.get("failure_code")
            exception_type = record.failure.get("exception_type")
            if code is not None:
                if not isinstance(code, str):
                    raise TypeError("bootstrap failure code must be a string")
                codes[code] += 1
            if not isinstance(exception_type, str):
                raise TypeError("bootstrap failure exception type must be a string")
            exceptions[exception_type] += 1
        else:
            inconsistent += 1
    return {
        "attempt_count": len(records),
        "successful_return_count": success,
        "failed_attempt_count": failure,
        "inconsistent_record_count": inconsistent,
        "failure_codes": dict(sorted(codes.items())),
        "exception_types": dict(sorted(exceptions.items())),
        "scientific_success_certified": False,
        "reliability_decision": None,
    }
