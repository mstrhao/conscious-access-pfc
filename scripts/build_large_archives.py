#!/usr/bin/env python3
"""Build split, lossless gzip archives for data files above GitHub's blob limit."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import time
import zlib
from pathlib import Path


FILES = (
    "ssDat_full_groot.pkl",
    "ssDat_full_2019.pkl",
    "ssDat_rsp_0239.pkl",
    "ssDat_full_0239.pkl",
    "cswm_reconsDA_groot.pkl",
    "ssDat_rsp_groot.pkl",
    "cswm_recons_groot.pkl",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class PartWriter:
    def __init__(self, directory: Path, stem: str, part_bytes: int):
        self.directory = directory
        self.stem = stem
        self.part_bytes = part_bytes
        self.paths: list[Path] = []
        self.handle = None
        self.in_part = 0
        self.total = 0

    def _open_next(self) -> None:
        if self.handle is not None:
            self.handle.close()
        path = self.directory / f"{self.stem}.gz.part{len(self.paths) + 1:03d}"
        self.paths.append(path)
        self.handle = path.open("wb")
        self.in_part = 0

    def write(self, payload: bytes) -> None:
        view = memoryview(payload)
        while view:
            if self.handle is None or self.in_part == self.part_bytes:
                self._open_next()
            count = min(len(view), self.part_bytes - self.in_part)
            self.handle.write(view[:count])
            self.in_part += count
            self.total += count
            view = view[count:]

    def close(self) -> None:
        if self.handle is not None:
            self.handle.close()
            self.handle = None


def build_one(source: Path, archive_dir: Path, part_bytes: int, level: int) -> dict:
    for stale in archive_dir.glob(f"{source.name}.gz.part*"):
        stale.unlink()

    started = time.monotonic()
    source_hash = hashlib.sha256()
    compressor = zlib.compressobj(level, zlib.DEFLATED, 31)
    writer = PartWriter(archive_dir, source.name, part_bytes)
    try:
        with source.open("rb") as handle:
            for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                source_hash.update(block)
                writer.write(compressor.compress(block))
        writer.write(compressor.flush())
    finally:
        writer.close()

    parts = [
        {
            "path": str(path.relative_to(archive_dir.parent)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in writer.paths
    ]
    return {
        "logical_path": f"data/{source.name}",
        "size_bytes": source.stat().st_size,
        "sha256": source_hash.hexdigest(),
        "compression": f"gzip-level-{level}",
        "compressed_size_bytes": writer.total,
        "parts": parts,
        "build_seconds": round(time.monotonic() - started, 3),
    }


def adopt_one(source: Path, compressed: Path, archive_dir: Path, part_bytes: int) -> dict:
    """Split an already verified gzip stream and independently verify its payload."""
    for stale in archive_dir.glob(f"{source.name}.gz.part*"):
        stale.unlink()
    started = time.monotonic()
    writer = PartWriter(archive_dir, source.name, part_bytes)
    try:
        with compressed.open("rb") as handle:
            for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                writer.write(block)
    finally:
        writer.close()

    source_sha = sha256(source)
    restored = hashlib.sha256()
    restored_size = 0
    with gzip.open(compressed, "rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            restored.update(block)
            restored_size += len(block)
    if restored_size != source.stat().st_size or restored.hexdigest() != source_sha:
        raise RuntimeError(f"Precompressed payload mismatch: {compressed}")

    parts = [
        {
            "path": str(path.relative_to(archive_dir.parent)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in writer.paths
    ]
    return {
        "logical_path": f"data/{source.name}",
        "size_bytes": source.stat().st_size,
        "sha256": source_sha,
        "compression": "gzip-level-6",
        "compressed_size_bytes": writer.total,
        "parts": parts,
        "build_seconds": round(time.monotonic() - started, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--part-bytes", type=int, default=90_000_000)
    parser.add_argument("--level", type=int, default=6)
    parser.add_argument("--precompressed-dir", type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for name in FILES:
        source = args.source_dir / name
        if not source.is_file():
            raise SystemExit(f"Missing source: {source}")
        if args.precompressed_dir:
            compressed = args.precompressed_dir / f"{name}.gz"
            if not compressed.is_file():
                raise SystemExit(f"Missing precompressed stream: {compressed}")
            entry = adopt_one(source, compressed, args.output_dir, args.part_bytes)
        else:
            entry = build_one(source, args.output_dir, args.part_bytes, args.level)
        entries.append(entry)
        ratio = entry["compressed_size_bytes"] / entry["size_bytes"]
        print(
            f"{name}: {len(entry['parts'])} parts, "
            f"ratio={ratio:.3f}, {entry['build_seconds']:.1f}s"
        )

    manifest = {
        "schema_version": 1,
        "algorithm": "gzip stream split into ordered parts",
        "part_size_limit_bytes": args.part_bytes,
        "files": entries,
    }
    path = args.output_dir.parent / "large_files_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
