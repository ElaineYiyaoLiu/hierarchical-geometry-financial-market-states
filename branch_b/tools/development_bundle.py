"""Package explicitly reviewed Branch B bytes; never discover or execute files.

Development-only packaging infrastructure, not a certified validation runner.
The caller must review actual contents for Branch B access and public disclosure
before supplying bytes and their independently recorded SHA-256 digests.
Digests bind that review to bytes; they do not perform or authenticate the review.
"""
from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
from io import BytesIO
import json
import platform
import re
import sys
import zipfile


SCHEMA_VERSION = "branch-b-development-bundle-v1"
MANIFEST_NAME = "bundle_manifest.json"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
# Operational bounds for small development snapshots, not scientific limits.
MAX_FILES = 512
MAX_PAYLOAD_BYTES = 16 * 1024 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
MAX_ARCHIVE_BYTES = MAX_PAYLOAD_BYTES + 1024 * 1024


class BundleError(ValueError):
    """Malformed, changed, or unreviewed development bundle."""


def _require_python314() -> None:
    if sys.version_info[:2] != (3, 14):
        raise BundleError("development bundle operations require Python 3.14")


def _digest(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise BundleError("expected a lowercase SHA-256 digest")
    return value


def _revision(value: object) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise BundleError("expected an explicit 40-character source revision")
    return value


def _path(name: object) -> str:
    if not isinstance(name, str) or re.fullmatch(r"[A-Za-z0-9_./-]+", name) is None:
        raise BundleError("bundle paths must be relative ASCII POSIX paths")
    parts = name.split("/")
    if len(parts) < 2 or parts[0] != "branch_b":
        raise BundleError("payload paths must be inside branch_b")
    if any(part in ("", ".", "..", "__pycache__") or part.startswith(".") for part in parts):
        raise BundleError("noncanonical or generated-cache path")
    if name.endswith((".pyc", ".pyo")):
        raise BundleError("generated Python caches are not source files")
    return name


def _reviewed_payload(files: Mapping[str, bytes], reviewed_sha256: Mapping[str, str]) -> dict[str, bytes]:
    if not isinstance(files, Mapping) or not isinstance(reviewed_sha256, Mapping):
        raise BundleError("files and reviewed digests must be mappings")
    payload = dict(files)
    reviewed = dict(reviewed_sha256)
    if not 1 <= len(payload) <= MAX_FILES:
        raise BundleError("development snapshot must contain 1 to 512 files")
    for name in (*payload, *reviewed):
        _path(name)
    if set(payload) != set(reviewed):
        raise BundleError("payload and reviewed inventory differ")
    names = sorted(payload)
    folded = {name.casefold() for name in names}
    if len(folded) != len(names):
        raise BundleError("case-colliding payload paths")
    for name in names:
        parts = name.casefold().split("/")
        if any("/".join(parts[:i]) in folded for i in range(1, len(parts))):
            raise BundleError("file and directory paths collide")
    total = 0
    for name, content in payload.items():
        if not isinstance(content, bytes):
            raise BundleError("payload values must be immutable bytes")
        total += len(content)
        if total > MAX_PAYLOAD_BYTES:
            raise BundleError("development snapshot exceeds operational size limit")
        if sha256(content).hexdigest() != _digest(reviewed[name]):
            raise BundleError("payload bytes differ from the reviewed digest")
    return payload


def _file_records(payload: Mapping[str, bytes]) -> list[dict]:
    return [
        {"path": name, "byte_count": len(payload[name]), "sha256": sha256(payload[name]).hexdigest()}
        for name in sorted(payload)
    ]


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _archive(payload: Mapping[str, bytes], manifest: dict) -> bytes:
    entries = dict(payload)
    entries[MANIFEST_NAME] = _json_bytes(manifest)
    if len(entries[MANIFEST_NAME]) > MAX_MANIFEST_BYTES:
        raise BundleError("development manifest exceeds operational size limit")
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, entries[name])
    result = buffer.getvalue()
    if len(result) > MAX_ARCHIVE_BYTES:
        raise BundleError("development archive exceeds operational size limit")
    return result


def build_development_bundle(
    files: Mapping[str, bytes],
    *,
    reviewed_sha256: Mapping[str, str],
    source_revision: str,
    review_reference: str,
) -> bytes:
    """Build a reproducible ZIP from bytes already cleared for this disclosure.

    No filesystem scanning, source import, network access, or bank processing.
    The source revision is a caller assertion, not a Git authenticity check.
    Identical bytes, review reference, source revision, and Python patch version
    produce identical archives; the ZIP container has fixed timestamps/modes.
    """
    _require_python314()
    payload = _reviewed_payload(files, reviewed_sha256)
    _revision(source_revision)
    if not isinstance(review_reference, str) or not review_reference.strip():
        raise BundleError("a content-review reference is required")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "scope": "development_only",
        "scientific_authorization": False,
        "source_revision": source_revision,
        "content_review_reference": review_reference,
        "created_with": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
        },
        "files": _file_records(payload),
    }
    return _archive(payload, manifest)


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    value = {}
    for key, item in pairs:
        if key in value:
            raise BundleError("duplicate manifest key")
        value[key] = item
    return value


def verify_development_bundle(
    bundle: bytes,
    *,
    expected_sha256: str,
    reviewed_sha256: Mapping[str, str],
    expected_source_revision: str,
) -> dict:
    """Verify against external digests, not just an archive's own manifest.

    Read members in memory only; never extract, import, or execute them.
    Success establishes byte/inventory integrity, not permission or readiness.
    """
    _require_python314()
    expected = _digest(expected_sha256)
    revision = _revision(expected_source_revision)
    if not isinstance(bundle, bytes) or len(bundle) > MAX_ARCHIVE_BYTES:
        raise BundleError("expected bounded immutable archive bytes")
    if sha256(bundle).hexdigest() != expected:
        raise BundleError("archive checksum mismatch")
    try:
        with zipfile.ZipFile(BytesIO(bundle), "r") as archive:
            members = archive.infolist()
            names = [member.filename for member in members]
            if not 2 <= len(members) <= MAX_FILES + 1 or len(set(names)) != len(names):
                raise BundleError("empty, oversized, or duplicate archive inventory")
            if names.count(MANIFEST_NAME) != 1:
                raise BundleError("development manifest missing")
            total = 0
            for member in members:
                if member.filename != MANIFEST_NAME:
                    _path(member.filename)
                limit = MAX_MANIFEST_BYTES if member.filename == MANIFEST_NAME else MAX_PAYLOAD_BYTES
                if member.is_dir() or member.file_size > limit:
                    raise BundleError("invalid archive member or size")
                if member.compress_type != zipfile.ZIP_STORED or member.flag_bits & 1:
                    raise BundleError("compressed or encrypted members are not supported")
                if member.external_attr >> 16 != 0o100644:
                    raise BundleError("archive members must be regular non-executable files")
                total += member.file_size
            if total > MAX_PAYLOAD_BYTES + MAX_MANIFEST_BYTES:
                raise BundleError("archive contents exceed operational size limit")
            manifest = json.loads(archive.read(MANIFEST_NAME).decode("utf-8"), object_pairs_hook=_unique_object)
            payload = {name: archive.read(name) for name in names if name != MANIFEST_NAME}
    except (zipfile.BadZipFile, UnicodeError, json.JSONDecodeError, EOFError, RuntimeError) as exc:
        raise BundleError("malformed development archive") from exc

    required = {"schema_version", "scope", "scientific_authorization", "source_revision", "content_review_reference", "created_with", "files"}
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise BundleError("invalid development manifest schema")
    if manifest["schema_version"] != SCHEMA_VERSION or manifest["scope"] != "development_only":
        raise BundleError("unsupported development manifest")
    if manifest["scientific_authorization"] is not False:
        raise BundleError("development bundles cannot grant scientific authorization")
    if manifest["source_revision"] != revision:
        raise BundleError("source revision mismatch")
    if not isinstance(manifest["content_review_reference"], str) or not manifest["content_review_reference"].strip():
        raise BundleError("content-review reference missing")
    runtime = manifest["created_with"]
    if not isinstance(runtime, dict) or set(runtime) != {"python_implementation", "python_version"}:
        raise BundleError("producer environment missing")
    if not isinstance(runtime["python_version"], str) or not runtime["python_version"].startswith("3.14."):
        raise BundleError("producer must record Python 3.14")
    if not isinstance(runtime["python_implementation"], str) or not runtime["python_implementation"]:
        raise BundleError("producer implementation missing")
    payload = _reviewed_payload(payload, reviewed_sha256)
    records = _file_records(payload)
    if manifest["files"] != records:
        raise BundleError("manifest inventory, byte count, or file checksum mismatch")
    manifest["files"] = records
    if bundle != _archive(payload, manifest):
        raise BundleError("noncanonical development archive")
    return {"integrity_verified": True, "scientific_authorization": False, "bundle_sha256": expected, "manifest": manifest}
