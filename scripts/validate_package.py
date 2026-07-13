#!/usr/bin/env python3
"""Validate checksums, archive parts, notebook hygiene, and Git blob sizes."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
GIT_BLOB_LIMIT = 100_000_000


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def main() -> None:
    required = (
        "README.md",
        "LICENSE",
        "CITATION.cff",
        "environment.yml",
        "requirements-lock.txt",
        "run",
        "docs/INSTALL.md",
        "docs/HARDWARE_AND_RUNTIME.md",
        "docs/FIGURE_CODE_MAP.md",
        "expected_outputs/README.md",
        "data/input_manifest.csv",
        "data/large_files_manifest.json",
    )
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        raise RuntimeError(f"Missing release files: {missing}")

    notebooks = sorted(ROOT.glob("[0-9][0-9]_*.ipynb"))
    if len(notebooks) != 6:
        raise RuntimeError(f"Expected 6 notebooks, found {len(notebooks)}")
    for path in notebooks:
        text = path.read_text(encoding="utf-8")
        if "_init_update" in text:
            raise RuntimeError(f"Private bootstrap remains in {path.name}")
        if "pmodel" in text:
            raise RuntimeError(f"Removed pmodel reference remains in {path.name}")
        json.loads(text)

    large = json.loads((DATA / "large_files_manifest.json").read_text(encoding="utf-8"))
    large_paths = {item["logical_path"] for item in large["files"]}
    for entry in large["files"]:
        for part in entry["parts"]:
            path = DATA / part["path"].removeprefix("data/")
            if not path.is_file():
                raise RuntimeError(f"Missing archive part: {path}")
            if path.stat().st_size != part["size_bytes"] or digest(path) != part["sha256"]:
                raise RuntimeError(f"Archive part mismatch: {path}")

    with (DATA / "input_manifest.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 94:
        raise RuntimeError(f"Expected 94 retained logical inputs, found {len(rows)}")
    for row in rows:
        if row["logical_path"] in large_paths:
            continue
        path = ROOT / row["logical_path"]
        if not path.is_file():
            raise RuntimeError(f"Missing input: {path}")
        if path.stat().st_size != int(row["size_bytes"]) or digest(path) != row["sha256"]:
            raise RuntimeError(f"Input mismatch: {path}")

    excluded = {
        "0239_20231017_neuron_1333_loc_3_3.pkl",
        "0239_20231017_neuron_133_loc_6_6.pkl",
        "0239_20231017_neuron_1568_loc_5_6.pkl",
        "0239_20231017_neuron_1568_loc_6_6.pkl",
        "groot_20240628_neuron_30_loc_4_4.pkl",
        "groot_20240628_neuron_51_loc_6_3.pkl",
        "groot_20240628_neuron_80_loc_3_6.pkl",
    }
    present_excluded = [name for name in excluded if (DATA / "example_neuron" / name).exists()]
    if present_excluded:
        raise RuntimeError(f"Excluded exemplars present: {present_excluded}")

    skip_roots = {ROOT / "results", DATA / "_figs"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(parent in path.parents for parent in skip_roots):
            continue
        relative = str(path.relative_to(ROOT))
        if relative in large_paths:
            continue
        if path.stat().st_size >= GIT_BLOB_LIMIT:
            raise RuntimeError(f"Git blob is >=100,000,000 bytes: {relative}")

    compile_targets = [ROOT / "_defs" / name for name in ("_init.py", "iplot.py", "istats.py")]
    compile_targets += sorted((ROOT / "scripts").glob("*.py"))
    for path in compile_targets:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    print(f"PACKAGE PASS: 6 notebooks, {len(rows)} logical inputs, {len(large['files'])} split archives")


if __name__ == "__main__":
    main()
