# Data Inputs

This repository does not include the raw HydroATLAS, RiverATLAS/HydroRIVERS, or
HydroBASINS files because they are large public datasets.

## Main Public Data Products

- HydroATLAS / RiverATLAS version 1.0
- HydroRIVERS / HydroBASINS from HydroSHEDS
- WaterGAP-derived runoff and discharge attributes distributed with HydroATLAS

## Key Input Tables Used by the Scripts

The scripts refer to the following processed or source-derived tables:

- `classified_river.csv`: selected representative river networks.
- `nor_accumulated_runoff.xlsx`: normalized cumulative runoff by H-S order.
- `nor_discharge_1-10.xlsx`: normalized discharge by H-S order.
- `nor_accumulated_runoff_q.xlsx`: runoff-ratio table by H-S order.
- `nor_mean_discharge_q.xlsx`: discharge-ratio table by H-S order.
- `ratio_base_unit.csv` / `ratio_base_unit.xlsx`: basic-unit hydrological
  ratios.
- `P_river_mean.csv`: characteristic-length statistics for basic units.
- `合并结果.csv`: RiverATLAS segment to HydroBASINS level-12 membership table
  (`HYRIV_ID`, `HYBAS_L12`, `MAIN_RIV`).
- `合并流域河流.csv`: spatial lookup table linking selected rivers, HydroBASINS
  IDs, and Pfafstetter regions.

## Recommended Local Layout

```text
data/
  raw/
    RiverATLAS/
    HydroBASINS/
    BasinATLAS/
  processed/
    data_class/
    data_河网单元/
    data_shp/
```

If a different layout is used, update the path variables at the top of each
script.

