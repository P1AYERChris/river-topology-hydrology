# Workflow

## 1. Representative River-Network Selection

Scripts in `src/traditional_order/` select representative river networks from
HydroATLAS/RiverATLAS-derived tables. The main criteria are:

- complete H-S orders from 1 to 7;
- at least 1000 river segments per network;
- sufficient non-missing hydrological attributes for order-based statistics.

Expected output: a table of selected `MAIN_RIV` identifiers and associated
metadata.

## 2. H-S Order Hydrological Statistics

The traditional-order scripts group river segments by `MAIN_RIV` and
`ORD_STRA`, then calculate:

- cumulative runoff by H-S order;
- mean discharge by H-S order;
- catchment area, length, and segment-count summaries;
- normalized hydrological variables within each river network.

## 3. Runoff and Discharge Ratios

Adjacent-order ratios are computed directly from grouped H-S statistics.
Log-linear fitting is also used to estimate characteristic runoff and discharge
ratios under a geometric-progression hypothesis.

## 4. Basic-Unit Extraction

Scripts in `src/basic_units/` implement the river-network pyramid decomposition.
The MATLAB Live Scripts document the original processing used to identify inner
and outer basic units and calculate their hydrological statistics.

## 5. Characteristic-Length Analysis

Basic units from different pyramid decomposition levels are assigned to the same
characteristic-length group when they share the same integer topological length
`lambda`. Hydrological statistics are then summarized within each `lambda`
group.

## 6. Spatial and Climate Metadata

Scripts in `src/scaling_climate/` link river-network identifiers to
HydroBASINS/BasinATLAS attributes, including aridity index information used for
humid/arid grouping.

## 7. Figure Generation

Scripts in `figures/` generate the manuscript figures from processed tables.
The map script `plot_table2_basin_map.py` uses the RiverATLAS-to-HydroBASINS
membership table to draw the spatial distribution of representative river
basins.

