# Installation and execution

## Supported environment

- Python 3.12.13
- Linux or macOS
- CPU execution; no GPU is required by the supplied figure-analysis routes

The tested package snapshot is recorded in `environment.yml` and
`requirements-lock.txt`. Package builds still depend on network speed and the
availability of wheels for the host platform.

## Conda/Mamba installation

From the repository root:

```bash
conda env create -f environment.yml
conda activate conscious-access
./run validate
./run demo
```

Allow approximately 5-15 minutes for a first uncached environment build.

## Python venv alternative

Use Python 3.12.13:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
./run validate
./run demo
```

## Restoring large inputs

Before a full notebook run:

```bash
./run prepare-data
```

The command verifies the split archives, restores seven original pickle files,
and validates their byte size and SHA-256 before replacing any target. Reserve
at least 8 GB of free disk space for the clone, environment, restored data, and
results.

The files use Python pickle. Only load the checksum-verified files distributed
with this release; pickle is not a safe interchange format for untrusted data.

## Running analyses

Start with the lightweight route:

```bash
./run demo
```

Then execute a selected notebook:

```bash
./run notebook 01
./run notebook 03
```

The executed copy is written under `results/executed_notebooks/`. For
interactive inspection:

```bash
./run lab
```

Notebook execution must begin from the repository root when launched manually,
or use the supplied `./run` entry point, which sets the working directory and
data/results paths.

