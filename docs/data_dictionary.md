# Data Dictionary

## HydroATLAS / RiverATLAS Identifiers

| Field | Meaning |
| --- | --- |
| `HYRIV_ID` | RiverATLAS / HydroRIVERS segment identifier |
| `MAIN_RIV` | Main-river / river-network identifier used for basin-level grouping |
| `HYBAS_ID` | HydroBASINS basin identifier |
| `HYBAS_L12` | HydroBASINS level-12 basin identifier linked to a river segment |
| `PFAF_ID` | Pfafstetter code |
| `ORD_STRA` | Horton-Strahler order |
| `NEXT_DOWN` | Downstream HydroBASINS identifier |

## Hydrological Variables

| Variable | Meaning | Unit / interpretation |
| --- | --- | --- |
| `run_mm_cyr` / RMC | Long-term mean annual runoff depth | mm yr-1 |
| `dis_m3_pyr` / DMP | Long-term mean annual natural discharge | m3 s-1 |
| cumulative runoff | RMC multiplied by catchment area and converted to volume | m3 yr-1 |
| mean discharge | Mean discharge statistic for grouped river segments | m3 s-1 |

## H-S Order Ratios

| Symbol | Meaning |
| --- | --- |
| `R_r(omega)` | Adjacent-order runoff ratio |
| `R_d(omega)` | Adjacent-order discharge ratio |
| `Rtilde_r` | Characteristic runoff ratio estimated by log-linear fitting |
| `Rtilde_d` | Characteristic discharge ratio estimated by log-linear fitting |

## Basic-Unit Variables

| Symbol / field | Meaning |
| --- | --- |
| `lambda` | Topological characteristic length of a basic unit |
| `R(lambda)` | Normalized runoff function of characteristic length |
| `D(lambda)` | Normalized discharge function of characteristic length |
| `R_unit` | Hydrological runoff ratio of a basic unit |
| `D_unit` | Hydrological discharge ratio of a basic unit |

The characteristic length is an integer topological length defined by the number
of inner links in a basic unit. It is not a continuous metric length in metres or
kilometres.

