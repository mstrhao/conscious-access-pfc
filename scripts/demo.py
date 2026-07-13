#!/usr/bin/env python3
"""Run a deterministic lightweight check using the three behavior inputs."""

from __future__ import annotations

import csv
import hashlib
import json
import pickle
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results" / "demo"
EXPECTED = {
    "M1": [3.8158, 20.5436, 38.5239, 60.0996, 70.6886],
    "M2": [3.249761904761905, 23.24190476190476, 44.59671428571429, 74.13842857142856, 85.11557142857143],
    "M3": [3.5967, 29.50655, 39.89165, 59.9179, 73.33325],
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    started = time.monotonic()
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    summary = {"schema_version": 1, "analysis": "stored behavior overview", "animals": {}}
    fig, axis = plt.subplots(figsize=(5.2, 3.4))
    contrasts = [0, 4, 8, 15, 100]

    for index, animal in enumerate(("M1", "M2", "M3"), start=1):
        path = DATA / f"behv_m{index}.pkl"
        with path.open("rb") as handle:
            payload = pickle.load(handle)
        values = np.asarray(payload["pfmncs"])[:, 4, [0, 1, 2, 3, 6]]
        means = values.mean(axis=0)
        sds = values.std(axis=0)
        np.testing.assert_allclose(means, EXPECTED[animal], rtol=0, atol=1e-10)
        summary["animals"][animal] = {
            "stored_rows": int(values.shape[0]),
            "mean_percent": means.tolist(),
            "sd_percent": sds.tolist(),
            "input_sha256": file_hash(path),
        }
        axis.errorbar(contrasts, means, yerr=sds, marker="o", capsize=2, label=animal)
        for contrast, mean, sd in zip(contrasts, means, sds):
            rows.append(
                {"animal": animal, "contrast_percent": contrast, "mean_percent": mean, "sd_percent": sd}
            )

    axis.set_xscale("symlog", linthresh=4)
    axis.set_xlabel("Stimulus contrast (%)")
    axis.set_ylabel("Correct trials (%)")
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(RESULTS / "behavior_overview.pdf")
    plt.close(fig)

    with (RESULTS / "behavior_overview.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"DEMO PASS ({time.monotonic() - started:.3f}s): {RESULTS}")


if __name__ == "__main__":
    main()

