import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import os
from scipy import stats
from plot_config_new import set_nature_style, save_fig, COLORS

set_nature_style()

# === 1. 绘图子函数 ===

def plot_scaling_panel(ax, df_wet, df_dry, val_col, title, ylabel):
    """绘制分组折线图 + 误差带"""
    # 聚合计算：均值、标准差
    wet_stats = df_wet.groupby('ORD_STRA')[val_col].agg(['mean', 'std'])
    dry_stats = df_dry.groupby('ORD_STRA')[val_col].agg(['mean', 'std'])

    # 1. 湿润区 (Humid - Blue)
    ax.plot(wet_stats.index, wet_stats['mean'], 'o-', 
            color=COLORS['blue'], lw=2, markersize=6, label='Humid (AI $\geq$ 0.65)')
    # 添加误差带 (Mean ± Std)
    ax.fill_between(wet_stats.index, 
                    wet_stats['mean'] - wet_stats['std'], 
                    wet_stats['mean'] + wet_stats['std'], 
                    color=COLORS['blue'], alpha=0.15, edgecolor='none')
    
    # 2. 干旱区 (Arid - Red)
    ax.plot(dry_stats.index, dry_stats['mean'], 's--', 
            color=COLORS['red'], lw=2, markersize=6, label='Arid (AI < 0.65)')
    # 添加误差带
    ax.fill_between(dry_stats.index, 
                    dry_stats['mean'] - dry_stats['std'], 
                    dry_stats['mean'] + dry_stats['std'], 
                    color=COLORS['red'], alpha=0.15, edgecolor='none')

    # 3. 美化
    ax.set_title(title, loc='left', fontsize=21)
    ax.set_xlabel(r'River order $\omega$',fontsize=19)
    ax.set_ylabel(ylabel, fontsize=19)
    ax.legend(loc='best', frameon=False, fontsize=17)
    sns.despine(ax=ax)

def plot_box_panel(ax, wet_series, dry_series, title, ylabel):
    """绘制分组箱线图"""
    # 构建绘图数据
    df_wet = pd.DataFrame({'Value': wet_series, 'Region': 'Humid'})
    df_dry = pd.DataFrame({'Value': dry_series, 'Region': 'Arid'})
    data = pd.concat([df_wet, df_dry])
    
    # 绘制箱线图
    # showfliers=False 隐藏离群点，聚焦核心分布
    sns.boxplot(x='Region', y='Value', data=data, ax=ax,
                palette=[COLORS['blue'], COLORS['red']], width=0.5,
                boxprops=dict(alpha=0.8, linewidth=1.5, edgecolor='black'),
                medianprops=dict(color='white', linewidth=2),
                whiskerprops=dict(color='black', linewidth=1.5),
                capprops=dict(color='black', linewidth=1.5),
                showfliers=False) 

    # T-test 检验
    t_stat, p_val = stats.ttest_ind(wet_series.dropna(), dry_series.dropna(), equal_var=False)
    
    # 在图中添加 P值 说明
    # ax.text(0.95, 0.95, f'$p={p_val:.2e}$', transform=ax.transAxes, 
    #         ha='right', va='top', fontsize=10)
    
    ax.set_title(title, loc='left',fontsize=21)
    ax.set_ylabel(ylabel,fontsize=19)
    ax.set_xlabel('') # 移除 Region 标签
    #设置x轴标签字体大小
    ax.tick_params(axis='x', labelsize=19)
    sns.despine(ax=ax)

# === 2. 主程序 ===

def plot_fig14_new():
    # 路径配置 (保持您的原始路径)
    basin_shp_path = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\流域\BasinATLAS_v10_shp\BasinATLAS_v10_lev12.shp"
    river_map_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\合并流域河流.csv"
    file_Rr = r'E:\研究\河网与径流\河网分级拓扑学\data\data_class\nor_accumulated_runoff_q.xlsx'
    file_Rd = r'E:\研究\河网与径流\河网分级拓扑学\data\data_class\nor_mean_discharge_q.xlsx'
    file_Unit = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\ratio_base_unit.xlsx'
    temp_ai_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\basin_aridity_extracted.csv"

    print("Step 1: Loading Climate Data...")
    # 1. 准备气候数据 (优先读取缓存)
    if os.path.exists(temp_ai_file):
        df_basin_ai = pd.read_csv(temp_ai_file)
    else:
        print("Warning: Cached AI file not found. Attempting to load SHP...")
        try:
            gdf = gpd.read_file(basin_shp_path, ignore_geometry=True)
            df_basin_ai = pd.DataFrame(gdf[['HYBAS_ID', 'ari_ix_uav']])
        except:
            print("Error: Cannot load SHP. Check file paths or geopandas installation.")
            return

    print("Step 2: Merging Data...")
    try:
        # 读取宏观数据
        df_macro_rr = pd.read_excel(file_Rr)[['MAIN_RIV', 'ORD_STRA', 'q']].rename(columns={'q': 'Rr'})
        df_macro_rd = pd.read_excel(file_Rd)[['MAIN_RIV', 'ORD_STRA', 'q']].rename(columns={'q': 'Rd'})
        df_macro = pd.merge(df_macro_rr, df_macro_rd, on=['MAIN_RIV', 'ORD_STRA'], how='outer')
        
        # 读取微观数据
        df_micro = pd.read_excel(file_Unit)[['id', 'all_run_mean']].rename(columns={'id': 'MAIN_RIV', 'all_run_mean': 'R_unit'}).dropna()
        
        # 关联气候
        df_map = pd.read_csv(river_map_file)
        df_map.columns = [c.strip() for c in df_map.columns]
        df_link = pd.merge(df_map, df_basin_ai, left_on='HYBAS_L12', right_on='HYBAS_ID', how='left')
        network_ai = df_link.groupby('MAIN_RIV')['ari_ix_uav'].mean().reset_index()
        
        # 合并
        df_macro_final = pd.merge(df_macro, network_ai, on='MAIN_RIV', how='inner')
        df_micro_final = pd.merge(df_micro, network_ai, on='MAIN_RIV', how='inner')
    except Exception as e:
        print(f"Data processing error: {e}")
        return

    # 3. 分组 (湿润 vs 干旱)
    AI_THRESHOLD = 65
    macro_wet = df_macro_final[df_macro_final['ari_ix_uav'] >= AI_THRESHOLD]
    macro_dry = df_macro_final[df_macro_final['ari_ix_uav'] < AI_THRESHOLD]
    micro_wet = df_micro_final[df_micro_final['ari_ix_uav'] >= AI_THRESHOLD]
    micro_dry = df_micro_final[df_micro_final['ari_ix_uav'] < AI_THRESHOLD]

    print("Step 3: Plotting...")
    # 创建 1x3 画布
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # (a) Runoff Ratio Scaling
    plot_scaling_panel(axes[0], macro_wet, macro_dry, 'Rr', 
                       r'(a) Runoff ratio $R_r$', 'Runoff ratio')
    
    # (b) Discharge Ratio Scaling
    plot_scaling_panel(axes[1], macro_wet, macro_dry, 'Rd', 
                       r'(b) Discharge ratio $R_d$', 'Discharge ratio')
    
    # (c) Basic Unit Invariance
    plot_box_panel(axes[2], micro_wet['R_unit'], micro_dry['R_unit'], 
                   r'(c) Basic unit invariance', r'Basic unit ratio $R_r^{unit}$')

    plt.tight_layout()
    save_fig('f14.pdf')
    save_fig('f14.png', format='png')
    #plt.show()

if __name__ == '__main__':
    plot_fig14_new()