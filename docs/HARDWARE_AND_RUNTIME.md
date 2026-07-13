# Hardware and runtime statement

## Packaging/test host

- macOS 14.6 (arm64)
- Apple M3, 8 CPU cores
- 24 GB RAM
- Python 3.12.13 audit environment

No identifying hardware serial number or device identifier is recorded.

## Resource guidance

- Validation/demo: 2 CPU cores and 4 GB RAM are sufficient.
- Behavior, single-neuron, population, color-shape and derived-model notebooks:
  16 GB RAM is a practical baseline.
- `03_statespace.ipynb`: at least 32 GB RAM is recommended; 64 GB provides a
  safer margin. Some resampling expressions can transiently materialize arrays
  on the order of 11 GB in addition to the loaded pickle and Python overhead.
- GPU: not required for the supplied notebooks.
- Disk: reserve at least 8 GB for the repository, environment, restored data,
  and generated results.

## Verified release-notebook timings

All six sanitized release notebooks completed without Python cell errors on the
host above, using checksum-restored data. Approximate execution spans were 2.1
s (`01`), 12.2 s (`02`), 53.9 s (`03`), 19.5 s (`04`), 5.7 s (`05`) and 12.7 s
(`06`), excluding environment installation and archive restoration. Archive
restoration of all seven large files took about 10 s on the same SSD. These are
orientation values, not guaranteed wall-clock times. Peak-memory behavior,
filesystem speed, BLAS implementation and CPU count can change them materially.

The deterministic demo's measured runtime and result path are printed by
`./run demo`. A Code Ocean build and full `./run all` benchmark should be
recorded in the capsule metadata after the final capsule run.
