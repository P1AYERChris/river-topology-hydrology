"""
Create a global map of the 228 representative river basins.

This script is intended to replace the regional-count Table 2 with a map-based
figure for the HESS revision. It uses the existing project data:

1. A representative-basin result table with MAIN_RIV values.
2. The river-to-basin lookup table linking MAIN_RIV to HYBAS_L12.
3. HydroBASINS level-12 polygons linked to all RiverATLAS segments in each
   selected MAIN_RIV network.
4. BasinATLAS level-01 polygons as a light global background.

Required packages:
    geopandas pandas matplotlib openpyxl

Example:
    python plot_table2_basin_map.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


# ----------------------------
# User-editable paths
# ----------------------------
PROJECT_ROOT = Path(r"E:\研究\河网与径流\河网分级拓扑学")

REPRESENTATIVE_BASIN_FILE = PROJECT_ROOT / r"data\data_class\nor_accumulated_runoff_q.xlsx"
RIVER_BASIN_LOOKUP_FILE = PROJECT_ROOT / r"data\data_shp\合并流域河流.csv"
RIVER_BASIN_FULL_MEMBERSHIP_FILE = PROJECT_ROOT / r"data\data_shp\合并结果.csv"
HYDROBASINS_L05_DIR = PROJECT_ROOT / r"data\data_shp\流域\5级"
HYDROBASINS_L12_DIR = PROJECT_ROOT / r"data\data_shp\流域\12级"
BASIN_ATLAS_L12 = (
    PROJECT_ROOT
    / r"data\data_shp\流域\BasinATLAS_v10_shp\BasinATLAS_v10_lev12.shp"
)
BASIN_ATLAS_L01 = (
    PROJECT_ROOT
    / r"data\data_shp\流域\BasinATLAS_v10_shp\BasinATLAS_v10_lev01.shp"
)

OUTPUT_DIR = PROJECT_ROOT / r"pic\提交图片hess"
OUTPUT_STEM = "figure_global_representative_basins"

# Robinson projection gives a compact global map with a better manuscript aspect
# ratio than raw longitude-latitude coordinates.
MAP_CRS = "+proj=robin +lon_0=0 +datum=WGS84 +units=m +no_defs"

# Use "riveratlas_membership" for polygons linked to all RiverATLAS segments in
# each selected MAIN_RIV network. This matches the basin-membership table used
# in this project. Alternative modes are kept for diagnostics only:
# "level12_upstream" and "level05_prefix".
BASIN_GEOMETRY_MODE = "riveratlas_membership"
ADD_AREA_BUBBLES = False
DRAW_LAND_BACKGROUND = False
SHOW_MAP_LEGEND = False


REGION_LABELS = {
    "1": "Africa",
    "2": "Europe and Middle East",
    "3": "Siberia",
    "4": "Asia",
    "5": "Oceania",
    "6": "South America",
    "7": "North and Central America",
    "8": "Arctic Region",
    "9": "Greenland",
}

REGION_COLORS = {
    "Africa": "#D55E00",
    "Europe and Middle East": "#0072B2",
    "Siberia": "#56B4E9",
    "Asia": "#E69F00",
    "Oceania": "#009E73",
    "South America": "#CC79A7",
    "North and Central America": "#F0E442",
    "Arctic Region": "#8DA0CB",
    "Greenland": "#6A3D9A",
}

REGION_ORDER = [
    "Africa",
    "Europe and Middle East",
    "Siberia",
    "Asia",
    "Oceania",
    "South America",
    "North and Central America",
    "Arctic Region",
    "Greenland",
]


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 9,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 8,
            "axes.linewidth": 0.8,
            "figure.dpi": 300,
            "savefig.dpi": 600,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def read_representative_main_rivers(path: Path) -> pd.Series:
    df = pd.read_excel(path, usecols=["MAIN_RIV"])
    main_rivers = df["MAIN_RIV"].dropna().astype("int64").drop_duplicates()
    if len(main_rivers) != 228:
        print(f"Warning: found {len(main_rivers)} unique MAIN_RIV values, expected 228.")
    return main_rivers


def read_hydrobasins_level05(folder: Path) -> gpd.GeoDataFrame:
    shp_files = sorted(folder.glob("*lev05*.shp"))
    if not shp_files:
        raise FileNotFoundError(f"No level-05 HydroBASINS shapefiles found in: {folder}")

    frames = []
    for shp_file in shp_files:
        print(f"Reading {shp_file.name}")
        frame = gpd.read_file(shp_file)
        frame["source_file"] = shp_file.name
        frames.append(frame)

    basins = pd.concat(frames, ignore_index=True)
    basins = gpd.GeoDataFrame(basins, geometry="geometry", crs=frames[0].crs)

    required = {"HYBAS_ID", "PFAF_ID", "SUB_AREA", "UP_AREA", "geometry"}
    missing = required.difference(basins.columns)
    if missing:
        raise ValueError(f"Missing required HydroBASINS fields: {sorted(missing)}")

    return basins


def read_hydrobasins_level12_filtered(folder: Path, needed_ids: set[int]) -> gpd.GeoDataFrame:
    shp_files = sorted(folder.glob("*lev12*.shp"))
    if not shp_files:
        raise FileNotFoundError(f"No level-12 HydroBASINS shapefiles found in: {folder}")

    frames = []
    for shp_file in shp_files:
        print(f"Reading {shp_file.name}")
        frame = gpd.read_file(shp_file)
        frame["HYBAS_ID"] = frame["HYBAS_ID"].astype("int64")
        frame = frame[frame["HYBAS_ID"].isin(needed_ids)].copy()
        print(f"  matched polygons: {len(frame):,}")
        if not frame.empty:
            frame["source_file"] = shp_file.name
            frames.append(frame)

    if not frames:
        raise ValueError("No selected HYBAS_L12 polygons were found in the level-12 shapefiles.")

    basins = pd.concat(frames, ignore_index=True)
    basins = gpd.GeoDataFrame(basins, geometry="geometry", crs=frames[0].crs)

    required = {"HYBAS_ID", "SUB_AREA", "UP_AREA", "geometry"}
    missing = required.difference(basins.columns)
    if missing:
        raise ValueError(f"Missing required HydroBASINS fields: {sorted(missing)}")

    return basins


def prepare_selected_basins_from_riveratlas_membership(
    lookup: pd.DataFrame,
) -> gpd.GeoDataFrame:
    selected_main_rivers = set(lookup["MAIN_RIV"].astype("int64"))

    print("Reading RiverATLAS-to-HydroBASINS full membership table...")
    chunks = []
    for chunk in pd.read_csv(
        RIVER_BASIN_FULL_MEMBERSHIP_FILE,
        usecols=["MAIN_RIV", "HYBAS_L12"],
        chunksize=1_000_000,
    ):
        chunk = chunk[chunk["MAIN_RIV"].isin(selected_main_rivers)]
        if not chunk.empty:
            chunks.append(chunk)

    if not chunks:
        raise ValueError("No selected MAIN_RIV records found in the full membership table.")

    membership = pd.concat(chunks, ignore_index=True).drop_duplicates()
    membership["MAIN_RIV"] = membership["MAIN_RIV"].astype("int64")
    membership["HYBAS_L12"] = membership["HYBAS_L12"].astype("int64")

    membership = membership.merge(
        lookup[["MAIN_RIV", "region", "region_code"]],
        on="MAIN_RIV",
        how="left",
    )

    print(f"Selected RiverATLAS segment memberships: {len(membership):,}")
    print(f"Selected MAIN_RIV values: {membership['MAIN_RIV'].nunique():,}")
    print(f"Selected level-12 HYBAS_ID values: {membership['HYBAS_L12'].nunique():,}")

    needed_ids = set(membership["HYBAS_L12"])
    geometries = read_hydrobasins_level12_filtered(HYDROBASINS_L12_DIR, needed_ids)

    selected = geometries[["HYBAS_ID", "SUB_AREA", "UP_AREA", "geometry"]].merge(
        membership,
        left_on="HYBAS_ID",
        right_on="HYBAS_L12",
        how="inner",
    )

    selected = selected.to_crs("EPSG:4326")
    dissolved = selected.dissolve(
        by="MAIN_RIV",
        aggfunc={
            "region": "first",
            "region_code": "first",
            "SUB_AREA": "sum",
            "UP_AREA": "max",
        },
    ).reset_index()

    dissolved["region"] = pd.Categorical(
        dissolved["region"],
        categories=REGION_ORDER,
        ordered=True,
    )
    dissolved = dissolved.sort_values(["region", "SUB_AREA"], ascending=[True, False])

    total_area_mkm2 = dissolved["SUB_AREA"].sum() / 1_000_000
    print(f"Representative RiverATLAS-linked basins mapped: {len(dissolved)}")
    print(f"Total mapped level-12 area: {total_area_mkm2:.2f} million km2")
    return dissolved


def build_upstream_membership(
    basin_attributes: pd.DataFrame,
    outlet_table: pd.DataFrame,
) -> pd.DataFrame:
    """Return HYBAS_ID membership for the full upstream area of each outlet."""
    required = {"HYBAS_ID", "NEXT_DOWN"}
    missing = required.difference(basin_attributes.columns)
    if missing:
        raise ValueError(f"Missing required BasinATLAS topology fields: {sorted(missing)}")

    basin_attributes = basin_attributes[["HYBAS_ID", "NEXT_DOWN"]].copy()
    basin_attributes["HYBAS_ID"] = basin_attributes["HYBAS_ID"].astype("int64")
    basin_attributes["NEXT_DOWN"] = basin_attributes["NEXT_DOWN"].fillna(0).astype("int64")

    upstream_lookup = (
        basin_attributes.groupby("NEXT_DOWN")["HYBAS_ID"]
        .apply(list)
        .to_dict()
    )

    records = []
    for row in outlet_table.itertuples(index=False):
        main_riv = int(row.MAIN_RIV)
        outlet_id = int(row.HYBAS_L12)
        region = row.region
        region_code = row.region_code

        visited = set()
        stack = [outlet_id]
        while stack:
            hybas_id = stack.pop()
            if hybas_id in visited:
                continue
            visited.add(hybas_id)
            stack.extend(upstream_lookup.get(hybas_id, []))

        for hybas_id in visited:
            records.append(
                {
                    "MAIN_RIV": main_riv,
                    "HYBAS_ID": hybas_id,
                    "outlet_hybas_l12": outlet_id,
                    "region": region,
                    "region_code": region_code,
                }
            )

    membership = pd.DataFrame.from_records(records)
    print(f"Upstream level-12 basin memberships: {len(membership):,}")
    print(f"Unique level-12 polygons used: {membership['HYBAS_ID'].nunique():,}")
    return membership


def prepare_selected_basins_level12_upstream(
    lookup: pd.DataFrame,
) -> gpd.GeoDataFrame:
    print("Reading BasinATLAS level-12 topology attributes...")
    attrs = gpd.read_file(
        BASIN_ATLAS_L12,
        ignore_geometry=True,
    )
    attrs["HYBAS_ID"] = attrs["HYBAS_ID"].astype("int64")

    membership = build_upstream_membership(attrs, lookup)
    needed_ids = set(membership["HYBAS_ID"].astype("int64"))

    print("Reading BasinATLAS level-12 geometries. This may take several minutes...")
    geometries = gpd.read_file(BASIN_ATLAS_L12)
    geometries["HYBAS_ID"] = geometries["HYBAS_ID"].astype("int64")
    geometries = geometries[geometries["HYBAS_ID"].isin(needed_ids)].copy()

    selected = geometries[["HYBAS_ID", "SUB_AREA", "UP_AREA", "geometry"]].merge(
        membership,
        on="HYBAS_ID",
        how="inner",
    )

    selected = selected.to_crs("EPSG:4326")
    dissolved = selected.dissolve(
        by="MAIN_RIV",
        aggfunc={
            "region": "first",
            "region_code": "first",
            "SUB_AREA": "sum",
            "UP_AREA": "max",
            "outlet_hybas_l12": "first",
        },
    ).reset_index()

    dissolved["region"] = pd.Categorical(
        dissolved["region"],
        categories=REGION_ORDER,
        ordered=True,
    )
    dissolved = dissolved.sort_values(["region", "SUB_AREA"], ascending=[True, False])

    total_area_mkm2 = dissolved["SUB_AREA"].sum() / 1_000_000
    print(f"Representative upstream basins mapped: {len(dissolved)}")
    print(f"Total mapped upstream area: {total_area_mkm2:.2f} million km2")
    return dissolved


def prepare_selected_basins() -> gpd.GeoDataFrame:
    main_rivers = read_representative_main_rivers(REPRESENTATIVE_BASIN_FILE)

    lookup = pd.read_csv(
        RIVER_BASIN_LOOKUP_FILE,
        usecols=["MAIN_RIV", "HYBAS_L12", "PFAF_ID"],
    )
    lookup = lookup[lookup["MAIN_RIV"].isin(main_rivers)].copy()
    lookup = lookup.drop_duplicates(subset=["MAIN_RIV"])

    if lookup.empty:
        raise ValueError("No matching HYBAS_L12 records found for the selected MAIN_RIV values.")

    # The selected river-network outlet is recorded at level 12. For a global
    # overview figure, match the basin to a coarser HydroBASINS level using the
    # Pfafstetter prefix. In the current representative set, the five-digit
    # prefix yields 228 unique basin polygons, matching the number of selected
    # river networks.
    lookup["pfaf_l05"] = lookup["PFAF_ID"].astype(str).str[:5]
    if lookup["pfaf_l05"].nunique() != len(lookup):
        print(
            "Warning: the five-digit Pfafstetter prefix is not unique for every "
            "selected MAIN_RIV. The map will still be drawn, but some basins may "
            "share the same level-05 polygon."
        )

    # The first Pfafstetter digit follows the HydroBASINS regional domains.
    lookup["region_code"] = lookup["pfaf_l05"].str[0]
    lookup["region"] = lookup["region_code"].map(REGION_LABELS)

    if BASIN_GEOMETRY_MODE == "riveratlas_membership":
        selected = prepare_selected_basins_from_riveratlas_membership(lookup)
        print("Regional counts:")
        print(selected["region"].value_counts().reindex(REGION_ORDER).fillna(0).astype(int))
        return selected

    if BASIN_GEOMETRY_MODE == "level12_upstream":
        selected = prepare_selected_basins_level12_upstream(lookup)
        print("Regional counts:")
        print(selected["region"].value_counts().reindex(REGION_ORDER).fillna(0).astype(int))
        return selected

    if BASIN_GEOMETRY_MODE != "level05_prefix":
        raise ValueError(
            "BASIN_GEOMETRY_MODE must be 'riveratlas_membership', "
            "'level12_upstream', or 'level05_prefix'."
        )

    basins = read_hydrobasins_level05(HYDROBASINS_L05_DIR)
    basins["HYBAS_ID"] = basins["HYBAS_ID"].astype("int64")
    basins["pfaf_l05"] = basins["PFAF_ID"].astype(str).str[:5]

    selected = basins.merge(
        lookup,
        on="pfaf_l05",
        how="inner",
        suffixes=("", "_selected"),
    )
    if selected.empty:
        raise ValueError("No BasinATLAS level-05 polygons matched the selected Pfafstetter prefixes.")

    selected = selected.to_crs("EPSG:4326")

    selected["region"] = pd.Categorical(
        selected["region"],
        categories=REGION_ORDER,
        ordered=True,
    )
    selected = selected.sort_values(["region", "SUB_AREA"], ascending=[True, False])

    print(f"Representative basins mapped: {selected['MAIN_RIV'].nunique()}")
    print(f"Level-05 basin polygons mapped: {len(selected)}")
    print("Regional counts:")
    print(selected.drop_duplicates("MAIN_RIV")["region"].value_counts().reindex(REGION_ORDER).fillna(0).astype(int))

    return selected


def plot_map(selected_basins: gpd.GeoDataFrame) -> None:
    setup_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    selected_plot = selected_basins.to_crs(MAP_CRS).copy()

    if ADD_AREA_BUBBLES:
        # Use centroids and area-scaled bubbles as an optional visual aid.
        selected_points = selected_plot.copy()
        selected_points["geometry"] = selected_plot.geometry.representative_point()
        selected_points["plot_area"] = selected_points["UP_AREA"].fillna(selected_points["SUB_AREA"])
        area_min = selected_points["plot_area"].min()
        area_max = selected_points["plot_area"].max()
        if area_max > area_min:
            selected_points["bubble_size"] = (
                14
                + 150
                * (selected_points["plot_area"] - area_min)
                / (area_max - area_min)
            )
        else:
            selected_points["bubble_size"] = 35

    fig = plt.figure(figsize=(11.8, 4.9))
    gs = fig.add_gridspec(
        nrows=1,
        ncols=2,
        width_ratios=[5.2, 1.05],
        left=0.006,
        right=0.975,
        bottom=0.11,
        top=0.90,
        wspace=0.02,
    )
    ax = fig.add_subplot(gs[0, 0])
    ax_bar = fig.add_subplot(gs[0, 1])

    if DRAW_LAND_BACKGROUND:
        # This background is optional. HydroBASINS global polygons can create
        # horizontal projection artifacts, so it is disabled by default.
        background = gpd.read_file(BASIN_ATLAS_L01).to_crs(MAP_CRS)
        background.plot(
            ax=ax,
            facecolor="#F4F4F4",
            edgecolor="none",
            linewidth=0,
            zorder=1,
        )

    for region in REGION_ORDER:
        subset = selected_plot[selected_plot["region"] == region]
        if subset.empty:
            continue
        subset.plot(
            ax=ax,
            facecolor=REGION_COLORS[region],
            edgecolor="#2B2B2B",
            linewidth=0.20,
            alpha=0.62,
            label=region,
            zorder=3,
        )
        if ADD_AREA_BUBBLES:
            point_subset = selected_points[selected_points["region"] == region]
            point_subset.plot(
                ax=ax,
                color=REGION_COLORS[region],
                markersize=point_subset["bubble_size"],
                edgecolor="#1F1F1F",
                linewidth=0.28,
                alpha=0.82,
                zorder=4,
            )

    ax.set_title("(a) Spatial distribution", loc="left", pad=5, fontweight="bold")
    ax.set_axis_off()
    ax.set_aspect("equal")

    if SHOW_MAP_LEGEND:
        legend = ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.50, -0.09),
            ncol=5,
            frameon=True,
            framealpha=0.95,
            borderpad=0.45,
            columnspacing=0.9,
            handlelength=1.3,
            handletextpad=0.5,
        )
        legend.get_frame().set_edgecolor("#BBBBBB")
        legend.get_frame().set_linewidth(0.6)

    counts = (
        selected_basins["region"]
        .value_counts()
        .reindex(REGION_ORDER)
        .fillna(0)
        .astype(int)
    )

    y_positions = list(range(len(REGION_ORDER)))
    bar_colors = [REGION_COLORS[r] for r in REGION_ORDER]
    ax_bar.barh(y_positions, counts.values, color=bar_colors, edgecolor="#333333", linewidth=0.25)
    ax_bar.set_yticks(y_positions)
    ax_bar.set_yticklabels(
        [
            "Africa",
            "Europe and\nMiddle East",
            "Siberia",
            "Asia",
            "Oceania",
            "South America",
            "North and\nCentral America",
            "Arctic Region",
            "Greenland",
        ],
        fontsize=7,
    )
    ax_bar.invert_yaxis()
    ax_bar.set_xlabel("Number of basins", fontsize=8)
    ax_bar.set_title("(b) Regional counts", loc="left", pad=5, fontweight="bold")
    ax_bar.tick_params(axis="x", labelsize=7, length=2)
    ax_bar.tick_params(axis="y", length=0)
    ax_bar.grid(axis="x", color="#E0E0E0", linewidth=0.35)
    ax_bar.set_axisbelow(True)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.spines["left"].set_visible(False)
    ax_bar.spines["bottom"].set_color("#777777")
    ax_bar.spines["bottom"].set_linewidth(0.7)
    for y, value in zip(y_positions, counts.values):
        ax_bar.text(value + 0.8, y, str(value), va="center", fontsize=7)
    ax_bar.set_xlim(0, max(counts.max() + 8, 10))
    ax_bar.margins(y=0.08)

    pdf_path = OUTPUT_DIR / f"{OUTPUT_STEM}.pdf"
    png_path = OUTPUT_DIR / f"{OUTPUT_STEM}.png"
    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png_path, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


def main() -> None:
    selected_basins = prepare_selected_basins()
    plot_map(selected_basins)


if __name__ == "__main__":
    main()
