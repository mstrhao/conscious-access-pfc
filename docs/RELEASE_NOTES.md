# Release notes — 2026-07-13

- Copied the current `_code` notebooks, helper code and data into an isolated
  GitHub candidate; original source files were not modified.
- Removed the six first-cell imports of the unavailable, workstation-specific
  `_defs._init_update` module.
- Replaced working-directory/path-index logic with repository-relative data and
  results paths; added `_defs/__init__.py`.
- Confirmed `reconw_thres_groot.npy` is included and no `pmodel` reference
  remains.
- Flattened the behavior mean only at the `scipy.stats.linregress` call while
  retaining the original `(1,5)` plotting layout; this is a mechanical runtime
  fix and does not alter the plotted values.
- Expressed the three normal-CDF KS calls explicitly for SciPy API
  compatibility; the statistical interpretation is unchanged.
- Redirected active figure writes to `results/figures/` while preserving
  intentionally commented save lines.
- Excluded seven unreferenced example-neuron objects and documented them.
- Losslessly compressed and split seven files above 100 MB; added checksum-
  verified restoration.
- Added a pinned environment, one run entry point, demo, validation, expected
  outputs, manifests, installation/hardware/runtime statements, citation and
  MIT license.
