#!/usr/bin/env python3
"""Read-only checks for an AsterFire Ent installation ZIP (Python stdlib only)."""

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from pathlib import Path


RUNTIME_DIRS = {"dist", "handlers", "agent", "schemas"}
FORBIDDEN_PARTS = {".git", ".asterfire", "node_modules", "__pycache__", ".npmrc", ".pypirc"}
MAX_EXPANDED_BYTES = 512 * 1024 * 1024  # Checker budget, not a platform limit.


class InvalidBundle(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidBundle(message)


def check_path(name, is_dir=False):
    require(bool(name) and "\\" not in name, f"Nonportable ZIP path: {name!r}")
    raw = name[:-1] if is_dir and name.endswith("/") else name
    parts = raw.split("/")
    require(all(p and p not in {".", ".."} for p in parts), f"Unsafe ZIP path: {name!r}")
    require(not any(re.search(r'[<>:"|?*\x00-\x1f]', p) or p.endswith((".", " "))
                    for p in parts), f"Nonportable ZIP path: {name!r}")
    require(not any(re.fullmatch(r"(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])", p.split(".")[0], re.I)
                    for p in parts), f"Reserved Windows filename: {name!r}")
    require(not any(p.casefold() in FORBIDDEN_PARTS or p.casefold().startswith(".env")
                    for p in parts), f"Runtime/credential config must not be bundled: {name!r}")
    top = parts[0]
    require((raw == "manifest.json" and not is_dir) or top in RUNTIME_DIRS,
            f"Unexpected package root: {name!r}")
    require(is_dir or raw == "manifest.json" or len(parts) > 1,
            f"Expected a directory under package root: {name!r}")
    return raw


def load_json(raw, name):
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidBundle(f"Invalid UTF-8 JSON: {name}") from exc


def validate_bundle(path, source=None, app_id=None, version=None):
    require(path.is_file(), "Installation ZIP does not exist")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        require(entries, "Empty ZIP")
        require(sum(info.file_size for info in entries) <= MAX_EXPANDED_BYTES,
                "Expanded ZIP exceeds this checker's 512 MiB inspection budget")
        seen = set()
        files = {}
        for info in entries:
            # Windows ZipInfo normalizes backslashes in filename; inspect the original.
            raw_name = info.orig_filename
            normalized = check_path(raw_name, info.is_dir())
            require(normalized.casefold() not in seen,
                    f"Duplicate or case-colliding ZIP path: {info.filename!r}")
            seen.add(normalized.casefold())
            require(not info.flag_bits & 1, "Encrypted ZIP entries are unsupported")
            mode = stat.S_IFMT(info.external_attr >> 16)
            require(mode in (0, stat.S_IFREG, stat.S_IFDIR),
                    f"Special file / symlink must not be bundled: {info.filename!r}")
            if not info.is_dir():
                # ZipFile.read also checks each entry's CRC; nothing is extracted.
                files[raw_name] = archive.read(info)

    require("manifest.json" in files, "Missing manifest.json at ZIP root")
    require(bool(files.get("dist/remoteEntry.js", b"").strip()),
            "Missing or empty dist/remoteEntry.js")
    # A file cannot also be the parent directory of another file.
    folded_files = {name.casefold() for name in files}
    for name in files:
        parent_parts = name.split("/")[:-1]
        for length in range(1, len(parent_parts) + 1):
            require("/".join(parent_parts[:length]).casefold() not in folded_files,
                    f"File/directory path collision: {name!r}")

    manifest = load_json(files["manifest.json"], "manifest.json")
    require(isinstance(manifest, dict), "Manifest must be a JSON object")
    for field in ("id", "version"):
        require(isinstance(manifest.get(field), str) and bool(manifest[field].strip()),
                f"Manifest requires a nonempty string: {field}")
    if app_id is not None:
        require(manifest["id"] == app_id, "Manifest app id differs from --app-id")
    if version is not None:
        require(manifest["version"] == version, "Manifest version differs from --version")
    datasets = manifest.get("datasets", [])
    require(isinstance(datasets, list), "Manifest datasets must be a list")
    for item in datasets:
        require(isinstance(item, dict), "Each dataset declaration must be an object")
        schema = item.get("schema")
        require(isinstance(schema, str) and schema.startswith("schemas/"),
                "Dataset schema must refer to schemas/ inside the package")
        check_path(schema)
        require(schema in files, f"Dataset schema missing from package: {schema!r}")
        require(isinstance(load_json(files[schema], schema), (dict, bool)),
                f"Schema must be a JSON Schema object or boolean: {schema!r}")

    if source is not None:
        require(source.is_dir(), "--source is not an App directory")
        expected = {"manifest.json"}
        for root in RUNTIME_DIRS:
            directory = source / root
            if directory.exists():
                require(not directory.is_symlink(), f"Source runtime root is a symlink: {root}")
                require(directory.is_dir(), f"Source runtime root is not a directory: {root}")
                for candidate in directory.rglob("*"):
                    relative = candidate.relative_to(source)
                    if any(p in {"__pycache__", ".DS_Store"} for p in relative.parts):
                        continue
                    require(not candidate.is_symlink(), "Source runtime directory contains a symlink")
                    if candidate.is_file() and candidate.suffix not in {".pyc", ".pyo"}:
                        expected.add(relative.as_posix())
        require(expected == set(files),
                "Bundle/source runtime file lists differ "
                f"(missing in ZIP: {sorted(expected - set(files))!r}; "
                f"extra in ZIP: {sorted(set(files) - expected)!r})")
        for name, contents in files.items():
            require((source / name).is_file(), f"Source runtime file missing: {name!r}")
            require((source / name).read_bytes() == contents,
                    f"Bundle/source contents differ: {name!r}")

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "ok": True,
        "app_id": manifest["id"],
        "version": manifest["version"],
        "runtime_files": len(files),
        "source_matches": source is not None,
        "sha256": digest.hexdigest(),
        "scope": "ZIP structure, CRC, declared schema JSON, optional runtime file comparison only",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--source", type=Path, help="Compare packaged runtime files with this App directory")
    parser.add_argument("--app-id")
    parser.add_argument("--version")
    args = parser.parse_args()
    try:
        result = validate_bundle(args.bundle, args.source, args.app_id, args.version)
    except (InvalidBundle, OSError, zipfile.BadZipFile, RuntimeError,
            NotImplementedError, OverflowError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True))
        return 1
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
