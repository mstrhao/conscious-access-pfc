# Conscious-access analysis and figure-reproduction package

Release candidate prepared for peer review of Nature Neuroscience manuscript
**NN-A96833**, “The Decomposition of Conscious Access: Working Memory for
Masked Sequences in Monkey Prefrontal Cortex.”

This repository contains six analysis notebooks, their shared helper code, and
the processed/derived inputs used by those notebooks. It is designed to let a
reviewer inspect the analyses and regenerate the notebooks' inline plots and
printed statistics without access to the authors' workstation paths.

## Quick start

Linux/macOS with Conda or Mamba:

```bash
conda env create -f environment.yml
conda activate conscious-access
./run validate
./run demo
./run prepare-data
./run notebook 01
```

The single entry point supports:

```text
./run validate
./run demo
./run prepare-data
./run notebook <01|02|03|04|05|06|name>
./run all
./run lab
```

`./run notebook 03`, for example, writes an executed copy with all inline plots
and printed results to `results/executed_notebooks/03_statespace.ipynb`.
`./run all` is provided for a clean high-memory environment; running one
notebook at a time is the recommended review route.

## Notebooks and scope

| Notebook | Main scope |
| --- | --- |
| `01_behavior.ipynb` | behavior and the corresponding Fig. 1, Fig. 3 and Fig. S1 analyses |
| `02_single_neuron.ipynb` | single-neuron summaries and example-neuron panels |
| `03_statespace.ipynb` | temporal generalization and state-space analyses |
| `04_population.ipynb` | population dynamics, latency, activity and rivalry analyses |
| `05_colorshape.ipynb` | color-shape learning/adaptation analyses |
| `06_model_prediction.ipynb` | derived control/model analyses corresponding to Fig. 6G-H |

The package starts from processed and derived analysis objects. It does **not**
contain raw imaging/electrophysiology recordings or the full upstream
preprocessing pipeline. The supplied `06_model_prediction.ipynb` analyzes the
derived Fig. 6G-H inputs; it does not contain RNN training code, checkpoints,
or producers for Fig. 6A-F. Manual schematics and microscopy/electrode-layout
panels are not computational outputs. See `docs/FIGURE_CODE_MAP.md`.

## Large data in ordinary Git

Seven logical pickle files exceed GitHub's 100 MB per-blob limit. They are
stored losslessly as ordered gzip streams split into parts of at most
90,000,000 bytes under `data/archives/`. Run:

```bash
./run prepare-data
```

to verify every part and atomically restore the original byte-identical files.
The logical-file SHA-256 values and every archive-part checksum are recorded in
`data/large_files_manifest.json`. Reconstructed files are ignored by Git.

This removes the per-blob blocker but does not make the repository small. The
compressed clone remains large; Git LFS, an archival data repository, or a Code
Ocean data asset is preferable if ordinary Git hosting becomes slow or rejects
the overall repository size.

## Reproducibility outputs

- `./run validate`: checks notebook hygiene, package files, input/archive
  checksums, Python syntax, exclusions, and the 100 MB Git-blob limit.
- `./run demo`: produces a deterministic behavior summary under
  `results/demo/` and checks exact expected means.
- `./run notebook ...`: produces an executed notebook under
  `results/executed_notebooks/`, preserving inline figures and statistics.
- Active figure-save calls write to `results/figures/`; commented legacy
  `savefig` lines are intentionally left commented.

Expected outputs are described in `expected_outputs/README.md`. Installation,
data, hardware, runtime, and limitations are documented under `docs/`.

Release verification on 2026-07-13: package validation passed; all seven split
archives restored byte-identically; the demo passed; and all six sanitized
notebooks completed without Python cell errors on macOS/Apple Silicon with
Python 3.12.13. A final Linux/Code Ocean run remains to be recorded after
importing the frozen Git revision.

## License and citation

Code is released under the MIT License, copyright 2026 Hao Zhou. Processed data
are supplied for verification of this manuscript; confirm any broader reuse
terms with the corresponding author. Citation metadata are in `CITATION.cff`.
