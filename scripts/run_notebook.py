#!/usr/bin/env python3
"""Execute one release notebook and retain its inline figures and statistics."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]


def resolve_notebook(value: str) -> Path:
    candidates = [
        path
        for path in ROOT.glob("[0-9][0-9]_*.ipynb")
        if path.name == value or path.stem == value or path.name.startswith(value.zfill(2))
    ]
    if len(candidates) != 1:
        names = ", ".join(path.name for path in sorted(ROOT.glob("[0-9][0-9]_*.ipynb")))
        raise SystemExit(f"Choose one notebook by number, stem, or filename. Available: {names}")
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args()

    data_dir = Path(os.environ.get("CONSCIOUS_ACCESS_DATA_DIR", ROOT / "data")).resolve()
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "prepare_data.py"),
            "--data-dir",
            str(data_dir),
        ],
        check=True,
    )
    path = resolve_notebook(args.notebook)
    output_dir = ROOT / "results" / "executed_notebooks"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / path.name

    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ["CONSCIOUS_ACCESS_DATA_DIR"] = str(data_dir)
    os.environ["CONSCIOUS_ACCESS_RESULTS_DIR"] = str(ROOT / "results")
    notebook = nbformat.read(path, as_version=4)
    started = time.monotonic()
    client = NotebookClient(
        notebook,
        timeout=args.timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        allow_errors=False,
    )
    client.execute()
    nbformat.write(notebook, output)
    elapsed = time.monotonic() - started
    record_dir = ROOT / "results" / "run_records"
    record_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": 1,
        "status": "pass",
        "notebook": path.name,
        "runtime_seconds": round(elapsed, 3),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "data_dir": str(data_dir),
        "executed_notebook": str(output.relative_to(ROOT)),
    }
    record_path = record_dir / f"{path.stem}.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"NOTEBOOK PASS: {path.name} ({elapsed:.1f}s) -> {output}")


if __name__ == "__main__":
    main()
