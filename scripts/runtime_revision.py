"""Deterministic, domain-separated runtime revisions for Self Iteration.

This module deliberately treats development manifests and package receipts as
cross-checks. Revisions are always recomputed from the checkout or archive raw
bytes and normalized modes.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unicodedata
import zipfile


DOMAIN = "self-iteration/runtime-revision/v1"
ALGORITHM = "sha256"
SCHEMA_VERSION = 1
UINT64_MAX = (1 << 64) - 1
REVISION_PREFIX = "sha256:"


class RuntimeRevisionError(ValueError):
    """A deterministic contract violation, identified by its short code."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _u64(value):
    if not isinstance(value, int) or value < 0 or value > UINT64_MAX:
        raise RuntimeRevisionError("u64_overflow")
    return value.to_bytes(8, "big")


def frame(value):
    if not isinstance(value, bytes):
        raise RuntimeRevisionError("frame_not_bytes")
    return _u64(len(value)) + value


def _canonical_path(path):
    if not isinstance(path, str):
        raise RuntimeRevisionError("path_not_text")
    try:
        encoded = path.encode("utf-8", "strict")
    except UnicodeError as exc:
        raise RuntimeRevisionError("path_not_utf8") from exc
    if not path or path.startswith("/") or "\\" in path or "\x00" in path:
        raise RuntimeRevisionError("path_not_canonical")
    if unicodedata.normalize("NFC", path) != path:
        raise RuntimeRevisionError("path_not_nfc")
    if any(part in {"", ".", ".."} for part in path.split("/")):
        raise RuntimeRevisionError("path_not_canonical")
    if len(encoded) > UINT64_MAX:
        raise RuntimeRevisionError("u64_overflow")
    return path, encoded


def _normalized_mode(mode):
    if mode not in {"0644", "0755"}:
        raise RuntimeRevisionError("mode_not_normalized")
    return mode


def _entry_parts(item):
    if not isinstance(item, dict):
        raise RuntimeRevisionError("entry_not_object")
    path, path_bytes = _canonical_path(item.get("path"))
    mode = _normalized_mode(item.get("mode"))
    data = item.get("data")
    if not isinstance(data, bytes):
        raise RuntimeRevisionError("entry_data_not_bytes")
    _u64(len(data))
    return path, path_bytes, mode, data


def _sorted_entries(entries, file_count=None):
    if not isinstance(entries, (list, tuple)):
        raise RuntimeRevisionError("inventory_not_list")
    if file_count is None:
        file_count = len(entries)
    _u64(file_count)
    parsed = [_entry_parts(item) for item in entries]
    parsed.sort(key=lambda item: item[1])
    paths = [item[0] for item in parsed]
    if len(paths) != len(set(paths)):
        raise RuntimeRevisionError("duplicate_path")
    return parsed, file_count


def calculate_revision(entries, file_count=None):
    """Return the v1 revision for independently supplied runtime entries."""
    parsed, count = _sorted_entries(entries, file_count)
    digest = hashlib.sha256()
    digest.update(frame(DOMAIN.encode("utf-8")))
    digest.update(_u64(count))
    for _path, path_bytes, mode, data in parsed:
        digest.update(frame(path_bytes))
        digest.update(frame(mode.encode("ascii")))
        digest.update(frame(data))
    return REVISION_PREFIX + digest.hexdigest()


def _mode_from_stat(mode):
    return "0755" if mode & stat.S_IXUSR else "0644"


def _read_regular_file(path, initial, before_read=None):
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if before_read is not None:
        before_read(path)
    try:
        descriptor = os.open(str(path), flags)
    except OSError as exc:
        raise RuntimeRevisionError("checkout_read_failed") from exc
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise RuntimeRevisionError("checkout_not_regular")
        if (opened.st_dev, opened.st_ino, opened.st_size) != (
            initial.st_dev,
            initial.st_ino,
            initial.st_size,
        ):
            raise RuntimeRevisionError("checkout_drift")
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if (final.st_dev, final.st_ino, final.st_size) != (
        initial.st_dev,
        initial.st_ino,
        initial.st_size,
    ):
        raise RuntimeRevisionError("checkout_drift")
    return b"".join(chunks)


def inventory_checkout(runtime_root, before_read=None):
    """Snapshot only regular files below a physical runtime root."""
    root = Path(runtime_root)
    try:
        root_status = os.lstat(root)
    except OSError as exc:
        raise RuntimeRevisionError("runtime_root_unreadable") from exc
    if stat.S_ISLNK(root_status.st_mode) or not stat.S_ISDIR(root_status.st_mode):
        raise RuntimeRevisionError("runtime_root_not_directory")

    entries = []

    def walk(directory, prefix):
        try:
            children = list(os.scandir(directory))
        except OSError as exc:
            raise RuntimeRevisionError("checkout_list_failed") from exc
        for child in sorted(children, key=lambda candidate: candidate.name.encode("utf-8", "surrogateescape")):
            relative = child.name if not prefix else prefix + "/" + child.name
            _canonical_path(relative)
            try:
                child_status = os.lstat(child.path)
            except OSError as exc:
                raise RuntimeRevisionError("checkout_lstat_failed") from exc
            if stat.S_ISLNK(child_status.st_mode):
                raise RuntimeRevisionError("checkout_symlink")
            if stat.S_ISDIR(child_status.st_mode):
                walk(child.path, relative)
            elif stat.S_ISREG(child_status.st_mode):
                entries.append({
                    "path": relative,
                    "mode": _mode_from_stat(child_status.st_mode),
                    "data": _read_regular_file(child.path, child_status, before_read),
                })
            else:
                raise RuntimeRevisionError("checkout_not_regular")

    walk(str(root), "")
    _sorted_entries(entries)
    return entries


def inventory_zip(archive_path, expected_inventory):
    """Read a rootless ZIP and require it to contain exactly expected paths."""
    try:
        expected = set(expected_inventory)
    except TypeError as exc:
        raise RuntimeRevisionError("archive_inventory_invalid") from exc
    for path in expected:
        _canonical_path(path)
    entries = []
    seen = set()
    try:
        archive = zipfile.ZipFile(archive_path)
    except (OSError, zipfile.BadZipFile) as exc:
        raise RuntimeRevisionError("archive_unreadable") from exc
    with archive:
        for info in archive.infolist():
            path, _encoded = _canonical_path(info.filename)
            unix_mode = (info.external_attr >> 16) & 0xFFFF
            kind = stat.S_IFMT(unix_mode)
            if info.is_dir() or kind == stat.S_IFDIR:
                raise RuntimeRevisionError("archive_directory_entry")
            if kind not in {0, stat.S_IFREG}:
                raise RuntimeRevisionError("archive_special_entry")
            if path in seen:
                raise RuntimeRevisionError("archive_duplicate_path")
            seen.add(path)
            if path not in expected:
                raise RuntimeRevisionError("archive_out_of_inventory")
            try:
                data = archive.read(info)
            except (OSError, zipfile.BadZipFile) as exc:
                raise RuntimeRevisionError("archive_read_failed") from exc
            entries.append({"path": path, "mode": _mode_from_stat(unix_mode), "data": data})
    if seen != expected:
        raise RuntimeRevisionError("archive_inventory_mismatch")
    _sorted_entries(entries)
    return entries


def _file_fact(item):
    path, _path_bytes, mode, data = _entry_parts(item)
    return {"path": path, "mode": mode, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def manifest_for_checkout(runtime_root, runtime_root_name):
    entries = inventory_checkout(runtime_root)
    sorted_entries, _count = _sorted_entries(entries)
    ordered = [{"path": path, "mode": mode, "data": data} for path, _encoded, mode, data in sorted_entries]
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN,
        "algorithm": ALGORITHM,
        "runtime_root": runtime_root_name,
        "files": [_file_fact(item) for item in ordered],
        "runtime_revision": calculate_revision(ordered),
    }


def _load_json(path, finding):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeRevisionError(finding)


def _manifest_findings(manifest, expected_root=None):
    if not isinstance(manifest, dict):
        return ["manifest_not_object"]
    required = {"schema_version", "domain", "algorithm", "runtime_root", "files", "runtime_revision"}
    if set(manifest) != required:
        return ["manifest_fields_invalid"]
    if manifest["schema_version"] != SCHEMA_VERSION or manifest["domain"] != DOMAIN or manifest["algorithm"] != ALGORITHM:
        return ["manifest_header_invalid"]
    if expected_root is not None and manifest["runtime_root"] != expected_root:
        return ["manifest_runtime_root_mismatch"]
    if not isinstance(manifest["files"], list):
        return ["manifest_files_invalid"]
    entries = []
    try:
        for fact in manifest["files"]:
            if not isinstance(fact, dict) or set(fact) != {"path", "mode", "bytes", "sha256"}:
                return ["manifest_file_fields_invalid"]
            if not isinstance(fact["bytes"], int) or fact["bytes"] < 0:
                return ["manifest_file_facts_invalid"]
            _canonical_path(fact["path"])
            _normalized_mode(fact["mode"])
            if not isinstance(fact["sha256"], str) or len(fact["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in fact["sha256"]):
                return ["manifest_file_facts_invalid"]
            entries.append(fact["path"])
    except RuntimeRevisionError:
        return ["manifest_file_facts_invalid"]
    if entries != sorted(entries, key=lambda value: value.encode("utf-8")) or len(entries) != len(set(entries)):
        return ["manifest_file_order_invalid"]
    revision = manifest["runtime_revision"]
    if not _valid_revision(revision):
        return ["manifest_runtime_revision_invalid"]
    return []


def write_manifest(runtime_root, manifest_path, runtime_root_name="self-iteration"):
    """Atomically write the sole permitted production mutation: a manifest."""
    manifest = manifest_for_checkout(runtime_root, runtime_root_name)
    target = Path(manifest_path)
    if not target.parent.is_dir():
        raise RuntimeRevisionError("manifest_parent_missing")
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=".runtime-manifest-", dir=str(target.parent))
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, target)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return manifest


def check_manifest(runtime_root, manifest_path, runtime_root_name="self-iteration"):
    try:
        manifest = _load_json(manifest_path, "manifest_unreadable")
    except RuntimeRevisionError as exc:
        return [exc.code]
    findings = _manifest_findings(manifest, runtime_root_name)
    if findings:
        return findings
    try:
        actual = manifest_for_checkout(runtime_root, runtime_root_name)
    except RuntimeRevisionError as exc:
        return [exc.code]
    if actual["runtime_revision"] != manifest["runtime_revision"]:
        return ["manifest_runtime_revision_mismatch"]
    if actual["files"] != manifest["files"]:
        return ["manifest_file_facts_mismatch"]
    return []


def _valid_revision(value):
    return isinstance(value, str) and len(value) == 71 and value.startswith(REVISION_PREFIX) and all(
        character in "0123456789abcdef" for character in value[len(REVISION_PREFIX) :]
    )


def policy_digest(policy_path):
    try:
        return hashlib.sha256(Path(policy_path).read_bytes()).hexdigest()
    except OSError as exc:
        raise RuntimeRevisionError("policy_unreadable") from exc


def _archive_sha256(path):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise RuntimeRevisionError("archive_unreadable") from exc
    return hashlib.sha256(raw).hexdigest(), len(raw)


def check_package_binding(manifest, archive_path, receipt_path, policy_path):
    findings = _manifest_findings(manifest)
    if findings:
        return findings
    expected_paths = {fact["path"] for fact in manifest["files"]}
    try:
        archive_entries = inventory_zip(archive_path, expected_paths)
    except RuntimeRevisionError as exc:
        return [exc.code]
    if calculate_revision(archive_entries) != manifest["runtime_revision"]:
        findings.append("archive_runtime_revision_mismatch")
    try:
        receipt = _load_json(receipt_path, "receipt_unreadable")
    except RuntimeRevisionError as exc:
        return findings + [exc.code]
    required = {"schema_version", "skill_name", "archive_sha256", "archive_size", "release_policy_sha256", "inventory", "files", "validation"}
    if not isinstance(receipt, dict) or set(receipt) != required or receipt.get("schema_version") != 3:
        return findings + ["receipt_schema_invalid"]
    try:
        archive_hash, archive_size = _archive_sha256(archive_path)
        current_policy = policy_digest(policy_path)
    except RuntimeRevisionError as exc:
        return findings + [exc.code]
    if receipt.get("archive_sha256") != archive_hash or receipt.get("archive_size") != archive_size:
        findings.append("receipt_archive_sha256_mismatch")
    archive_facts = [_file_fact(item) for item in sorted(archive_entries, key=lambda item: item["path"].encode("utf-8"))]
    if receipt.get("inventory") != [fact["path"] for fact in archive_facts]:
        findings.append("receipt_inventory_mismatch")
    expected_receipt_files = [{"path": fact["path"], "sha256": fact["sha256"], "size": fact["bytes"], "mode": fact["mode"]} for fact in archive_facts]
    if receipt.get("files") != expected_receipt_files:
        findings.append("receipt_file_facts_mismatch")
    if receipt.get("release_policy_sha256") != current_policy:
        findings.append("receipt_policy_digest_mismatch")
    return sorted(set(findings))


def classify_durable_state(state, revalidated=False):
    """Classify copied state without guessing provenance from a receipt alone."""
    if not isinstance(state, dict):
        state = {}
    revision = state.get("Skill runtime revision")
    source = state.get("Runtime revision source")
    allowed = {
        "checked development manifest",
        "independently recomputed verified archive",
        "host binding",
        "unknown",
    }
    if not _valid_revision(revision) or source not in allowed or source == "unknown":
        source = "unknown"
        established = False
    else:
        established = True
    return {
        "runtime_revision": revision if established else None,
        "source": source,
        "provenance_established": established,
        "safe_resume_allowed": bool(revalidated),
    }


def _result(findings):
    return {"ok": not findings, "findings": sorted(set(findings))}


def main(argv=None):
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    write = subcommands.add_parser("write")
    write.add_argument("--runtime-root", required=True)
    write.add_argument("--manifest", required=True)
    check = subcommands.add_parser("check")
    check.add_argument("--runtime-root", required=True)
    check.add_argument("--manifest", required=True)
    bindings = subcommands.add_parser("check-bindings")
    bindings.add_argument("--manifest", required=True)
    bindings.add_argument("--archive")
    bindings.add_argument("--receipt")
    bindings.add_argument("--policy")
    arguments = parser.parse_args(argv)
    if arguments.command == "write":
        try:
            write_manifest(arguments.runtime_root, arguments.manifest)
            result = _result([])
        except RuntimeRevisionError as exc:
            result = _result([exc.code])
    elif arguments.command == "check":
        result = _result(check_manifest(arguments.runtime_root, arguments.manifest))
    else:
        package_values = [arguments.archive, arguments.receipt, arguments.policy]
        if any(package_values) and not all(package_values):
            result = _result(["package_binding_group_incomplete"])
        else:
            try:
                manifest = _load_json(arguments.manifest, "manifest_unreadable")
                findings = _manifest_findings(manifest)
                if all(package_values):
                    findings.extend(check_package_binding(manifest, arguments.archive, arguments.receipt, arguments.policy))
                result = _result(findings)
            except RuntimeRevisionError as exc:
                result = _result([exc.code])
    print(json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
