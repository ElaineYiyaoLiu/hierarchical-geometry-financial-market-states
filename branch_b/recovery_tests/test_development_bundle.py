"""Synthetic packaging tests only; no scientific data, fitter, or bank access."""
from hashlib import sha256
from io import BytesIO
import json
import zipfile

import pytest

from branch_b.tools import development_bundle as bundler
from branch_b.tools.development_bundle import BundleError, build_development_bundle, verify_development_bundle


# Deliberate synthetic revision, not a claim about repository provenance.
SOURCE = "1" * 40
REVIEW = "synthetic fixture contents reviewed in this test source"


def _files():
    return {"branch_b/example.py": b"VALUE = 1\n", "branch_b/notes.md": b"Synthetic packaging fixture only.\n"}


def _digests(files):
    return {name: sha256(content).hexdigest() for name, content in files.items()}


def _build(files=None):
    files = _files() if files is None else files
    return build_development_bundle(files, reviewed_sha256=_digests(files), source_revision=SOURCE, review_reference=REVIEW)


def _verify(bundle, files=None, **overrides):
    files = _files() if files is None else files
    kwargs = {"expected_sha256": sha256(bundle).hexdigest(), "reviewed_sha256": _digests(files), "expected_source_revision": SOURCE}
    kwargs.update(overrides)
    return verify_development_bundle(bundle, **kwargs)


def _entries(bundle):
    with zipfile.ZipFile(BytesIO(bundle)) as archive:
        return [(info.filename, archive.read(info)) for info in archive.infolist()]


def _rewrite(entries):
    """Independent ZIP writer with the documented development container settings."""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, content in entries:
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return buffer.getvalue()


def test_bundle_is_byte_identical_across_input_mapping_order():
    files = _files()
    first = _build(files)
    second = _build(dict(reversed(list(files.items()))))
    assert first == second
    assert files == _files()
    assert _verify(first)["integrity_verified"] is True


def test_roundtrip_records_exact_bytes_and_real_python314():
    bundle = _build()
    report = _verify(bundle)
    assert report["scientific_authorization"] is False
    assert report["bundle_sha256"] == sha256(bundle).hexdigest()
    manifest = report["manifest"]
    assert manifest["scope"] == "development_only"
    assert manifest["source_revision"] == SOURCE
    assert manifest["created_with"]["python_version"].startswith("3.14.")
    assert manifest["files"] == [
        {"path": name, "byte_count": len(content), "sha256": sha256(content).hexdigest()}
        for name, content in sorted(_files().items())
    ]
    with zipfile.ZipFile(BytesIO(bundle)) as archive:
        for info in archive.infolist():
            assert info.date_time == (1980, 1, 1, 0, 0, 0)
            assert info.compress_type == zipfile.ZIP_STORED
            assert info.external_attr >> 16 == 0o100644


def test_changed_bytes_cannot_reuse_review_digests():
    files = _files()
    reviewed = _digests(files)
    files["branch_b/example.py"] = b"VALUE = 2\n"
    with pytest.raises(BundleError, match="reviewed digest"):
        build_development_bundle(files, reviewed_sha256=reviewed, source_revision=SOURCE, review_reference=REVIEW)


@pytest.mark.parametrize("name", [
    "../outside.py", "/branch_b/a.py", "branch_b/../a.py", "branch_b//a.py",
    "branch_b/./a.py", "branch_b/a\\b.py", "branch_b/.hidden/a.py",
    "branch_b/__pycache__/a.pyc", "branch_b/a.pyc", "other/a.py", "branch_b/a\x00.py",
])
def test_noncanonical_or_out_of_scope_paths_are_rejected(name):
    with pytest.raises(BundleError):
        _build({name: b"synthetic"})


@pytest.mark.parametrize("files", [
    {"branch_b/A.py": b"a", "branch_b/a.py": b"b"},
    {"branch_b/a": b"a", "branch_b/a/b.py": b"b"},
])
def test_case_and_file_directory_collisions_are_rejected(files):
    with pytest.raises(BundleError, match="collid"):
        _build(files)


@pytest.mark.parametrize("reviewed", [{}, {"branch_b/extra.py": "0" * 64}])
def test_review_inventory_must_match_exactly(reviewed):
    with pytest.raises(BundleError, match="inventory"):
        build_development_bundle(_files(), reviewed_sha256=reviewed, source_revision=SOURCE, review_reference=REVIEW)


def test_mutable_or_nonbyte_payloads_are_rejected():
    with pytest.raises(BundleError, match="immutable bytes"):
        build_development_bundle({"branch_b/a.py": bytearray(b"x")}, reviewed_sha256={"branch_b/a.py": sha256(b"x").hexdigest()}, source_revision=SOURCE, review_reference=REVIEW)


def test_missing_review_reference_is_not_an_approval():
    with pytest.raises(BundleError, match="review reference"):
        build_development_bundle(_files(), reviewed_sha256=_digests(_files()), source_revision=SOURCE, review_reference=" ")


def test_archive_digest_and_revision_are_externally_bound():
    bundle = _build()
    with pytest.raises(BundleError, match="checksum mismatch"):
        _verify(bundle, expected_sha256="0" * 64)
    with pytest.raises(BundleError, match="revision mismatch"):
        _verify(bundle, expected_source_revision="2" * 40)


def test_rebuilt_self_consistent_archive_cannot_bypass_external_review():
    changed = _files()
    changed["branch_b/example.py"] = b"VALUE = 999\n"
    altered = _build(changed)
    # Even accepting this ZIP's digest does not accept changed reviewed file bytes.
    with pytest.raises(BundleError, match="reviewed digest"):
        _verify(altered)


@pytest.mark.parametrize("mutation", ["extra", "missing", "duplicate", "reordered"])
def test_altered_archive_inventory_or_order_fails(mutation):
    entries = _entries(_build())
    if mutation == "extra":
        entries.append(("branch_b/extra.py", b"synthetic extra file"))
    elif mutation == "missing":
        entries = [(name, content) for name, content in entries if name != "branch_b/example.py"]
    elif mutation == "duplicate":
        entries.append(entries[0])
    else:
        entries.reverse()
    if mutation == "duplicate":
        with pytest.warns(UserWarning, match="Duplicate name"):
            altered = _rewrite(entries)
    else:
        altered = _rewrite(entries)
    with pytest.raises(BundleError):
        _verify(altered)


@pytest.mark.parametrize("field,value", [("scientific_authorization", True), ("scope", "official"), ("schema_version", "unknown")])
def test_bundle_cannot_promote_itself_to_official_status(field, value):
    entries = _entries(_build())
    altered_entries = []
    for name, content in entries:
        if name == bundler.MANIFEST_NAME:
            manifest = json.loads(content)
            manifest[field] = value
            content = json.dumps(manifest).encode()
        altered_entries.append((name, content))
    with pytest.raises(BundleError):
        _verify(_rewrite(altered_entries))


def test_manifest_byte_count_mismatch_is_rejected():
    entries = _entries(_build())
    altered = []
    for name, content in entries:
        if name == bundler.MANIFEST_NAME:
            manifest = json.loads(content)
            manifest["files"][0]["byte_count"] += 1
            content = json.dumps(manifest).encode()
        altered.append((name, content))
    with pytest.raises(BundleError, match="byte count"):
        _verify(_rewrite(altered))


def test_zip_with_trailing_bytes_is_not_canonical():
    with pytest.raises(BundleError, match="noncanonical"):
        _verify(_build() + b"synthetic trailer")


def test_both_public_operations_refuse_other_python_versions(monkeypatch):
    bundle = _build()
    # Guard simulation only; actual test execution remains Python 3.14.
    monkeypatch.setattr(bundler.sys, "version_info", (3, 13, 0))
    with pytest.raises(BundleError, match="require Python 3.14"):
        _build()
    with pytest.raises(BundleError, match="require Python 3.14"):
        _verify(bundle)


def test_small_development_size_bound_is_enforced(monkeypatch):
    monkeypatch.setattr(bundler, "MAX_PAYLOAD_BYTES", 1)
    with pytest.raises(BundleError, match="operational size"):
        _build()
