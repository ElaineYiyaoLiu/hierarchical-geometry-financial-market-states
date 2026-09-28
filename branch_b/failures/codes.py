from __future__ import annotations

from enum import StrEnum


class FailureCode(StrEnum):
    INPUT_SCHEMA = "INPUT_SCHEMA"
    NONFINITE_INPUT = "NONFINITE_INPUT"
    DEGENERATE_DISTANCE = "DEGENERATE_DISTANCE"
    NUMERICAL_FIT = "NUMERICAL_FIT"
    TIMEOUT = "TIMEOUT"
    DEGENERATE_TREE = "DEGENERATE_TREE"
    INSUFFICIENT_BOOTSTRAP = "INSUFFICIENT_BOOTSTRAP"
    OUTPUT_SCHEMA = "OUTPUT_SCHEMA"
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"


class BranchBFailure(RuntimeError):
    def __init__(self, code: FailureCode, message: str):
        super().__init__(message)
        self.code = code


class ConfigurationRequired(RuntimeError):
    """Raised when a protocol/freeze choice is intentionally not yet specified."""
