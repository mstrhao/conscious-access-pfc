#!/usr/bin/env python3
"""Verify archive parts and atomically restore the seven large pickle files."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "large_files_manifest.json"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class MultipartReader(io.RawIOBase):
    def __init__(self, paths: list[Path]):
        self.paths = iter(paths)
        self.current = None

    def readable(self) -> bool:
        return True

    def readinto(self, buffer) -> int:
        view = memoryview(buffer)
        total = 0
        while total < len(view):
            if self.current is None:
                try:
                    self.current = next(self.paths).open("rb")
                except StopIteration:
                    break
            count = self.current.readinto(view[total:])
            if count:
                total += count
            else:
                self.current.close()
                self.current = None
        return total

    def close(self) -> None:
        if self.current is not None:
            self.current.close()
        super().close()


def verify_parts(entry: dict) -> list[Path]:
    paths = []
    for part in entry["parts"]:
        path = ROOT / "data" / part["path"].removeprefix("data/")
        if not path.is_file():
            raise RuntimeError(f"Missing archive part: {path}")
        if path.stat().st_size != part["size_bytes"]:
            raise RuntimeError(f"Size mismatch: {path}")
        if file_hash(path) != part["sha256"]:
            raise RuntimeError(f"SHA-256 mismatch: {path}")
        paths.append(path)
    return paths


def restore(entry: dict, data_dir: Path, check_only: bool = False) -> None:
    target = data_dir / Path(entry["logical_path"]).name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        valid = (
            target.stat().st_size == entry["size_bytes"]
            and file_hash(target) == entry["sha256"]
        )
        if valid:
            print(f"verified {entry['logical_path']}")
            return
        if check_only:
            raise RuntimeError(f"Invalid restored file: {target}")

    paths = verify_parts(entry)
    if check_only:
        print(f"verified archive parts for {entry['logical_path']}")
        return

    temporary = target.with_suffix(target.suffix + ".partial")
    digest = hashlib.sha256()
    size = 0
    with MultipartReader(paths) as raw:
        with gzip.GzipFile(fileobj=io.BufferedReader(raw), mode="rb") as source:
            with temporary.open("wb") as destination:
                for block in iter(lambda: source.read(8 * 1024 * 1024), b""):
                    destination.write(block)
                    digest.update(block)
                    size += len(block)

    if size != entry["size_bytes"] or digest.hexdigest() != entry["sha256"]:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"Restored checksum mismatch: {entry['logical_path']}")
    os.replace(temporary, target)
    print(f"restored {entry['logical_path']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "data",
        help="Restore into this data directory (default: repository data/).",
    )
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        restore(entry, args.data_dir.resolve(), args.check_only)
    print("LARGE DATA PASS")


if __name__ == "__main__":
    main()
