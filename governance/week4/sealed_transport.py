"""Cryptographic release transport. Approval and freeze review remain separate."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey)


def canonical_bytes(payload: dict) -> bytes:
    if sys.version_info[:2] != (3, 14):
        raise RuntimeError("Python 3.14 required")
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def sign(payload: dict, private_key: Ed25519PrivateKey) -> dict:
    return {"payload": payload, "signature_hex": private_key.sign(canonical_bytes(payload)).hex()}


def verify(envelope: dict, *, trusted_public_key: bytes, expected_signer: str,
           expected_scope: str, expected_contract_sha256: str,
           expected_initial_manifest_sha256: str, allowed_release_fields: list[str]) -> dict:
    """Use an independently supplied key and exact frozen field allowlist."""
    if set(envelope) != {"payload", "signature_hex"}:
        raise ValueError("unexpected envelope fields")
    payload = envelope["payload"]
    required = {"scope", "signer_id", "contract_sha256", "initial_output_manifest_sha256",
                "issued_at_utc", "trigger", "uniform_total_per_sentinel", "released_fields"}
    if not isinstance(payload, dict) or set(payload) != required:
        raise ValueError("unexpected payload fields")
    try:
        Ed25519PublicKey.from_public_bytes(trusted_public_key).verify(
            bytes.fromhex(envelope["signature_hex"]), canonical_bytes(payload))
    except (InvalidSignature, ValueError, TypeError) as exc:
        raise ValueError("invalid release signature") from exc
    if payload["signer_id"] != expected_signer or payload["scope"] != expected_scope:
        raise ValueError("signer or scope mismatch")
    for key, expected in (("contract_sha256", expected_contract_sha256),
                          ("initial_output_manifest_sha256", expected_initial_manifest_sha256)):
        if (not isinstance(expected, str) or len(expected) != 64 or
            any(c not in "0123456789abcdef" for c in expected) or payload[key] != expected):
            raise ValueError("contract or manifest binding mismatch")
    if type(payload["trigger"]) is not bool:
        raise ValueError("binary trigger required")
    if (type(payload["uniform_total_per_sentinel"]) is not int or
        payload["uniform_total_per_sentinel"] != (10 if payload["trigger"] else 5)):
        raise ValueError("uniform count mismatch")
    if (not isinstance(allowed_release_fields, list) or
        any(not isinstance(field, str) for field in allowed_release_fields) or
        len(set(allowed_release_fields)) != len(allowed_release_fields) or
        not isinstance(payload["released_fields"], dict) or
        set(payload["released_fields"]) != set(allowed_release_fields)):
        raise ValueError("release fields differ from exact allowlist")
    issued = datetime.fromisoformat(payload["issued_at_utc"].replace("Z", "+00:00"))
    if issued.tzinfo is None or issued.utcoffset().total_seconds() != 0:
        raise ValueError("UTC issue time required")
    return {"signature_valid": True, "signer": expected_signer,
            "trusted_key_sha256": hashlib.sha256(trusted_public_key).hexdigest(),
            "signed_payload_sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest(),
            "transport_verified": True, "operational_authorization_granted": False}
