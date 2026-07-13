# Expected outputs

## Validation

```text
PACKAGE PASS: 6 notebooks, 94 logical inputs, 7 split archives
```

## Lightweight demo

`./run demo` prints `DEMO PASS` and creates:

- `results/demo/behavior_overview.pdf`
- `results/demo/behavior_overview.csv`
- `results/demo/summary.json`

The JSON must match `expected_outputs/demo_summary.json` byte-for-byte after
normal JSON formatting. PDFs are not expected to have identical hashes across
operating systems because fonts/renderers can differ; compare the CSV/JSON
numeric artifacts.

## Selected notebook execution

`./run notebook 01` creates:

- `results/executed_notebooks/01_behavior.ipynb`

Equivalent names are produced for notebooks 02-06. The executed notebook is
the complete review artifact for inline figures and printed statistics.
Active `savefig` calls additionally populate `results/figures/`.
Each successful run also writes `results/run_records/<notebook>.json` with the
measured runtime, Python version, platform and data path.

No output should be written into the tracked input-data directory. The empty
`data/_figs/` directory exists only for compatibility with legacy manual use.
