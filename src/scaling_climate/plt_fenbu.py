import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.colors import Normalize
import warnings
import pandas as pd
import pyproj
# 忽略特定警告
warnings.filterwarnings("ignore", category=UserWarning, message="Geometry is in a geographic CRS")

# Step 1: 读取 SHP 文件
shp_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\流域\amtls.shp"
gdf = gpd.read_file(shp_file)

# 确保 SHP 文件中包含必要的列
attribute_columns = ["q", "in_run_mea", "out_run_me", "all_run_me"]
for col in attribute_columns:
    if col not in gdf.columns:
        raise ValueError(f"SHP 文件中缺少属性列: {col}")

# Step 2: 处理几何对象并计算纬度
# 确保 GeoDataFrame 的坐标系统是 WGS84
if gdf.crs is None:
    gdf = gdf.set_crs(epsg=4326)
elif gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

# 计算纬度范围
gdf["Latitude"] = gdf.geometry.centroid.y
latitude_bins = np.linspace(-90, 90, 11)  # 将纬度范围分为 10 个区间（每 18° 一个区间）

# Step 3: 计算纬度带
gdf["Latitude_Band"] = np.digitize(gdf["Latitude"], bins=latitude_bins) - 1

# Step 4: 创建绘图函数
def plot_distribution_and_curve(gdf, attribute, output_file):
    """绘制属性的全球分布图和纬度统计曲线"""
    fig, (map_ax, curve_ax) = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw={'width_ratios': [3, 1]})
    
    # 过滤数据 - 使用正确的 NaN 检测
    gdf_filtered = gdf[~pd.isna(gdf[attribute])]  # 非 NaN 值区域
    gdf_nan = gdf[pd.isna(gdf[attribute])]        # NaN 值区域
    global_min = gdf_filtered[attribute].min()
    global_max = gdf_filtered[attribute].max()
    
    # 禁用自动设置 aspect，避免错误
    plt.rcParams['axes.autolimit_mode'] = 'round_numbers'
    
    # 设置图例名称
    legend_label = {
        "q": "$R_r$",
        "in_run_mea": "$R_r^{\t{unit_{in}}}$",
        "out_run_me": "$R_r^{\t{unit_{out}}}$", 
        "all_run_me": "$R_r^{unit}$"
    }.get(attribute, f"{attribute} values")

    # 尝试使用安全的默认参数进行绘图
    gdf_nan.plot(
        ax=map_ax,
        color='lightgrey',  # 设置全部为灰色
        linewidth=0,  # 添加细边框以区分不同区域
        edgecolor='black',
        # 禁用方面比设置，使用固定值
        aspect=1.0  
    )
    
    # 只绘制非零区域
    gdf_filtered.plot(
        column=attribute,
        ax=map_ax,
        cmap="viridis",
        legend=False,  # 禁用图例
        legend_kwds={'shrink': 0.6, 'label': f"{attribute} values"},
        vmin=global_min,
        vmax=global_max,
        linewidth=0,  # 添加细边框以区分不同区域
        edgecolor='black',
        # 禁用方面比设置，使用固定值
        aspect=1.0
        )
    #给地图加上经纬虚线
    map_ax.grid(color='lightgrey', linestyle='--', linewidth=0.5)
    # 创建单独的色标，放在地图下方
    norm = Normalize(vmin=global_min, vmax=global_max)
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
    sm.set_array([])
    
    # 添加色标到图的底部
    cbar = fig.colorbar(sm, ax=map_ax, orientation='horizontal', 
                        pad=0.05, shrink=0.7, label=legend_label)
    cbar.set_label(legend_label, fontsize=14)  # 设置标签文字大小
    cbar.ax.tick_params(labelsize=12)  # 设置刻度标签文字大小
    map_ax.set_title(f"Global Distribution of {attribute}", fontsize=14)
    map_ax.set_xticks([])
    map_ax.set_yticks([])
    # 隐藏地图框线
    #map_ax.axis('off')
    # 第二个子图：纬度统计曲线
    # 确保只使用非零值计算统计量
    band_stats = gdf_filtered.groupby("Latitude_Band").agg({attribute: ["mean", "std", "count"]})
    
    # 准备数据
    band_means = band_stats[attribute]["mean"] if not band_stats.empty else pd.Series()
    band_stds = band_stats[attribute]["std"] if not band_stats.empty else pd.Series()
    
    # 初始化数组
    full_band_means = np.full(len(latitude_bins) - 1, np.nan)
    full_band_stds = np.full(len(latitude_bins) - 1, np.nan)
    
    # 填充数据
    for i, mean in band_means.items():
        if 0 <= i < len(full_band_means):
            full_band_means[i] = mean
    
    for i, std in band_stds.items():
        if 0 <= i < len(full_band_stds):
            full_band_stds[i] = std
    
    # 用0替换标准差中的NaN值
    full_band_stds = np.nan_to_num(full_band_stds, nan=0)
    
    # 获取纬度区间中心点
    band_centers = (latitude_bins[:-1] + latitude_bins[1:]) / 2
    
    # 绘制均值曲线
    curve_ax.plot(full_band_means, band_centers, label="Mean", color="blue")
    
    # 绘制标准差区域
    curve_ax.fill_betweenx(band_centers, 
                         full_band_means - full_band_stds, 
                         full_band_means + full_band_stds, 
                         color="blue", alpha=0.3, label="Std Dev")
    # 动态设置x轴范围，根据实际数据
    # 计算数据范围（包含标准差）
    data_min = np.nanmin(full_band_means - full_band_stds)
    data_max = np.nanmax(full_band_means + full_band_stds)
    
    # 如果最小值和最大值相同，添加一些边距
    if data_min == data_max:
        data_min -= 0.1 * abs(data_min) if data_min != 0 else 0.1
        data_max += 0.1 * abs(data_max) if data_max != 0 else 0.1
    
    # 添加一些边距，使图表更美观
    x_range = data_max - data_min
    margin = x_range * 0.1  # 10% 的边距
    
    # 设置x轴范围
    curve_ax.set_xlim(data_min - margin, data_max + margin)
    # 设置坐标轴标签
    curve_ax.set_xlabel(legend_label, fontsize=14)
    curve_ax.set_ylabel("Latitude (°)", fontsize=14)
    #curve_ax.set_title("Latitude Statistics", fontsize=14)
    #设置纵轴范围-90到90
    curve_ax.set_ylim(-90, 90)
    # 添加竖直参考线
    curve_ax.axvline(x=0, color="gray", linestyle="--", linewidth=0.8)
    #设置坐标轴数值字体大小
    curve_ax.tick_params(axis='both', which='major', labelsize=12)
    # 添加图例
    curve_ax.legend()
     # 确保折线图与地图高度一致
    # 保持纵轴的对齐和统一大小
    pos1 = map_ax.get_position()
    pos2 = curve_ax.get_position()
    curve_ax.set_position([pos2.x0, pos1.y0, pos2.width, pos1.height])
    #让折线图更靠近左图

    # 调整布局并保存图像
    #plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close(fig)

# Step 5: 确保输出文件夹存在
output_folder = r"E:\研究\河网与径流\河网分级拓扑学\pic"
os.makedirs(output_folder, exist_ok=True)

# Step 6: 为每个属性绘制图像
for attribute in attribute_columns:
    output_file = f"{output_folder}\\{attribute}_distribution_with_curve.png"
    plot_distribution_and_curve(gdf, attribute, output_file)
    print(f"图像已保存至: {output_file}")