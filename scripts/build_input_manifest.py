#!/usr/bin/env python3
"""Create the logical input manifest after the release data are assembled."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
INACTIVE_TOP_LEVEL = {
    "data/activity_2019.pkl",
    "data/activity_groot.pkl",
    "data/activity_slope_2019.pkl",
    "data/activity_slope_groot.pkl",
    "data/latency_2019.pkl",
    "data/latency_groot.pkl",
    "data/slope_volition_0239.pkl",
    "data/slope_volition_2019.pkl",
}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def main() -> None:
    large_path = DATA / "large_files_manifest.json"
    large = json.loads(large_path.read_text(encoding="utf-8"))
    large_by_path = {item["logical_path"]: item for item in large["files"]}
    rows = []

    for path in sorted(DATA.rglob("*")):
        if not path.is_file() or "archives" in path.parts:
            continue
        if path.name in {"input_manifest.csv", "large_files_manifest.json", "excluded_files.csv", ".gitkeep"}:
            continue
        relative = str(path.relative_to(ROOT))
        if relative in large_by_path:
            continue
        if path.suffix not in {".pkl", ".npy"}:
            continue
        rows.append(
            {
                "logical_path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": digest(path),
                "storage": "regular-git-blob",
                "code_status": "inactive-retained" if relative in INACTIVE_TOP_LEVEL else "active-input",
            }
        )

    for relative, item in large_by_path.items():
        rows.append(
            {
                "logical_path": relative,
                "size_bytes": item["size_bytes"],
                "sha256": item["sha256"],
                "storage": "split-gzip; restore with ./run prepare-data",
                "code_status": "active-input",
            }
        )

    rows.sort(key=lambda row: row["logical_path"])
    output = DATA / "input_manifest.csv"
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {output} ({len(rows)} logical inputs)")


if __name__ == "__main__":
    main()

