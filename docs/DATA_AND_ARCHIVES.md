# Data inventory and archive design

`data/input_manifest.csv` is the authoritative logical-input inventory. It
records the relative path, uncompressed byte size, SHA-256, storage route and
whether each retained object is read by the active notebook cells.

Seven active inputs are stored as split gzip archives because their original
pickle blobs exceed GitHub's ordinary-Git limit:

- `ssDat_full_groot.pkl`
- `ssDat_full_2019.pkl`
- `ssDat_rsp_0239.pkl`
- `ssDat_full_0239.pkl`
- `cswm_reconsDA_groot.pkl`
- `ssDat_rsp_groot.pkl`
- `cswm_recons_groot.pkl`

The compression is byte-preserving. `./run prepare-data` joins the ordered
parts as a stream, decompresses to a temporary file, checks the original
SHA-256 and size, and then performs an atomic rename. It never treats a merely
successful decompression as sufficient validation.

## Excluded inactive exemplars

The current `02_single_neuron.ipynb` concretely reads 14 of the 21 supplied
example-neuron files. These seven have no active reference and are excluded
from this GitHub package while remaining untouched in the source `_code` tree:

- `example_neuron/0239_20231017_neuron_1333_loc_3_3.pkl`
- `example_neuron/0239_20231017_neuron_133_loc_6_6.pkl`
- `example_neuron/0239_20231017_neuron_1568_loc_5_6.pkl`
- `example_neuron/0239_20231017_neuron_1568_loc_6_6.pkl`
- `example_neuron/groot_20240628_neuron_30_loc_4_4.pkl`
- `example_neuron/groot_20240628_neuron_51_loc_6_3.pkl`
- `example_neuron/groot_20240628_neuron_80_loc_3_6.pkl`

`data/excluded_files.csv` records their original sizes and hashes. If an older
or newly restored analysis references one of them, it must be deliberately
re-added and the manifest regenerated.

Eight small top-level files that are not read by current active cells are
retained and marked `inactive-retained` in the input manifest to avoid silently
discarding possible legacy summary objects.

