# River Topology and Hydrological Scaling

This repository contains the analysis and figure-generation code associated with
the manuscript on hydrological-topological scaling patterns in global river
networks.

The workflow combines Horton-Strahler ordering, HydroATLAS/RiverATLAS
hydrological attributes, and a river-network pyramid decomposition framework to
analyse scaling relationships in 228 representative river basins.

## Repository Structure

```text
river-topology-hydrology/
  src/
    traditional_order/   # H-S order statistics, normalization, and ratios
    basic_units/         # River-network basic-unit extraction and statistics
    scaling_climate/     # Cross-scale links, spatial metadata, climate grouping
  figures/               # Scripts used to generate manuscript figures
  data/
    README.md            # Data sources and expected local layout
  docs/
    workflow.md          # End-to-end workflow and script dependencies
    data_dictionary.md   # Key variables and units
  archive/               # Reserved for non-essential exploratory scripts
```

## Data Availability

The raw HydroATLAS, RiverATLAS/HydroRIVERS, and HydroBASINS datasets are not
included because of their size. They are publicly available from HydroSHEDS /
HydroATLAS data portals. The scripts expect local copies of these datasets and
intermediate processed tables generated from them.

See [data/README.md](data/README.md) for the expected inputs and data-source
notes.

## Code Workflow

The main workflow is:

1. Select representative river networks with complete H-S orders 1-7 and at
   least 1000 river segments.
2. Compute H-S-order hydrological statistics for cumulative runoff and mean
   discharge.
3. Estimate runoff and discharge ratios by adjacent-order ratios and log-linear
   fitting.
4. Extract river-network basic units through pyramid decomposition.
5. Compute hydrological ratios and characteristic-length statistics for basic
   units.
6. Generate the final manuscript figures.

See [docs/workflow.md](docs/workflow.md) for details.

## Environment

Python scripts were developed with the scientific Python stack:

```bash
pip install -r requirements.txt
```

Some basic-unit extraction and statistics scripts are MATLAB Live Scripts
(`.mlx`). These are included to document the original processing workflow.

## Paths

Several scripts in this archive were originally run in a local project
environment and may contain absolute paths. Before rerunning, update the input
and output paths at the top of each script or adapt them to a local project-root
configuration. The file names and column names are documented in
[docs/data_dictionary.md](docs/data_dictionary.md).

## Manuscript Figure Notes

The `figures/` directory contains the figure scripts closest to the revised HESS
submission. During revision, some figure numbers changed because redundant
figures were removed or moved to the Supporting Information. The script names
therefore reflect the original working figure numbers rather than final
publication numbering.

