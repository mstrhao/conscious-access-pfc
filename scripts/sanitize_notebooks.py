#!/usr/bin/env python3
"""Apply documented, mechanical release edits to the six notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted(ROOT.glob("[0-9][0-9]_*.ipynb"))

RELEASE_NOTE = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "**Release-package note.** The private workstation bootstrap cell was removed. "
        "Paths are resolved by `_defs/_init.py`. Before manual use, run "
        "`./run prepare-data`; see `README.md` for the tested commands."
    ],
}


def transform_source(source: str) -> str:
    replacements = {
        "[:, 4, [0,1,2,3,6]]": "[:, 4, [[0,1,2,3,6]]]",
        "stats.linregress(np.arange(1, 6), a)": (
            "stats.linregress(np.arange(1, 6), np.ravel(a))"
        ),
        "outputdir+'/_figs/'": "figdir+'/'",
        'outputdir+"/_figs/': 'figdir+"/',
        "outputdir + '/_figs/": "figdir + '/",
        'outputdir + "/_figs/': 'figdir + "/',
        "stats.kstest(data, 'norm', args=(data.mean(), data.std()))": (
            "stats.kstest(data, lambda x: stats.norm.cdf("
            "x, loc=data.mean(), scale=data.std()))"
        ),
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    return source


def main() -> None:
    if len(NOTEBOOKS) != 6:
        raise SystemExit(f"Expected six notebooks, found {len(NOTEBOOKS)}")

    for path in NOTEBOOKS:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        cells = notebook["cells"]

        if cells and "_defs._init_update" in "".join(cells[0].get("source", [])):
            del cells[0]
        elif any("_defs._init_update" in "".join(c.get("source", [])) for c in cells):
            raise SystemExit(f"Unexpected private bootstrap position in {path.name}")

        if not cells or "Release-package note" not in "".join(cells[0].get("source", [])):
            cells.insert(0, RELEASE_NOTE.copy())

        for index, cell in enumerate(cells):
            source = "".join(cell.get("source", []))
            source = transform_source(source)
            cell["source"] = source.splitlines(keepends=True)
            cell.setdefault("id", f"{path.stem[:4]}-{index:03d}")
            if cell.get("cell_type") == "code":
                cell["execution_count"] = None
                cell["outputs"] = []

        path.write_text(
            json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
        print(f"sanitized {path.name}")


if __name__ == "__main__":
    main()
