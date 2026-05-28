import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from plot_config_new import set_nature_style, save_fig, COLORS

set_nature_style()

def get_normalized_points(data, col_idx):
    # ... (保持原有的数据提取逻辑不变) ...
    x_list, y_list = [], []
    grouped = data.groupby(10)
    for name, group in grouped:
        sum_col = group[3].values
        cut_idx = len(sum_col)
        for i in range(len(sum_col)):
            if sum_col[i] < 0.05:
                cut_idx = i
                break
        length = group[0].values[0:cut_idx]
        val = group[col_idx].values[0:cut_idx]
        if len(length) < 2 or len(val) < 2: continue
        l_min, l_max = length.min(), length.max()
        v_min, v_max = val.min(), val.max()
        if l_max == l_min or v_max == v_min: continue
        length_norm = (length - l_min) / (l_max - l_min)
        val_norm = (val - v_min) / (v_max - v_min)
        x_list.extend(length_norm)
        y_list.extend(val_norm)
    return np.array(x_list), np.array(y_list)

def plot_hybrid_panel(ax, x, y, title, ylabel, cmap_name, main_color):
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    if len(x) < 10: return

    # 1. 密度散点背景
    if len(x) > 10000:
        idx = np.random.choice(len(x), 10000, replace=False)
        x_c, y_c = x[idx], y[idx]
    else:
        x_c, y_c = x, y
    try:
        xy = np.vstack([x_c, y_c])
        z = gaussian_kde(xy)(xy)
        idx_sort = z.argsort()
        x_plot, y_plot, z_plot = x_c[idx_sort], y_c[idx_sort], z[idx_sort]
    except:
        x_plot, y_plot, z_plot = x_c, y_c, np.ones_like(x_c)
        
    sc = ax.scatter(x_plot, y_plot, c=z_plot, s=5, cmap=cmap_name, alpha=0.15, edgecolor='none', rasterized=True)

    # 2. 统计分布带 (5-95%)
    df_temp = pd.DataFrame({'x': x, 'y': y})
    df_temp['bin'] = pd.cut(df_temp['x'], bins=25)
    stats = df_temp.groupby('bin')['y'].agg([
        lambda k: np.percentile(k, 5), 
        lambda k: np.percentile(k, 95),
        'mean' # 这里计算均值
    ]).rename(columns={'<lambda_0>': 'p05', '<lambda_1>': 'p95', 'mean': 'y_mean'})
    
    bin_centers = [b.mid for b in stats.index]
    y_p05 = stats['p05'].interpolate().fillna(method='bfill')
    y_p95 = stats['p95'].interpolate().fillna(method='bfill')
    y_mean = stats['y_mean'].interpolate().fillna(method='bfill')

    # 绘制置信区间
    ax.fill_between(bin_centers, y_p05, y_p95, color=main_color, alpha=0.25, zorder=1, label='5-95% Range')

    # 3. 绘制观测均值线 (Observed Mean Trend)
    # 这就是数据真实的走势，不需要回归
    ax.plot(bin_centers, y_mean, color=main_color, lw=2.5, zorder=3, label='Mean trend')

    # 4. 绘制理论参考线 (Theoretical Linear)
    # 连接 (0,0) 到 (1,1) 的黑色虚线
    ax.plot([0, 1], [0, 1], color='black', linestyle='--', lw=2, zorder=4, label='Linear reference')

    # 5. 美化
    ax.set_title(title, loc='left')
    ax.set_xlabel(r'Normalized length $\lambda$')
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend(loc='upper left', frameon=False, fontsize=12)
    
    return sc

def plot_fig12_new():
    file_path = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\P_river_mean.csv'
    try:
        data = pd.read_csv(file_path, header=None)
        for c in range(10): data[c] = pd.to_numeric(data[c], errors='coerce')
    except Exception as e:
        print(f"Error: {e}")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    x_r, y_r = get_normalized_points(data, 1)
    sc1 = plot_hybrid_panel(ax1, x_r, y_r, r'(a) Runoff shape', 
                            r'Normalized runoff $R(\lambda)$', 'Blues', COLORS['blue'])
    cbar1 = plt.colorbar(sc1, ax=ax1, fraction=0.046, pad=0.04)

    x_d, y_d = get_normalized_points(data, 2)
    sc2 = plot_hybrid_panel(ax2, x_d, y_d, r'(b) Discharge shape', 
                            r'Normalized discharge $D(\lambda)$', 'Reds', COLORS['red'])
    cbar2 = plt.colorbar(sc2, ax=ax2, fraction=0.046, pad=0.04)

    plt.tight_layout()
    save_fig('f12.pdf')
    save_fig('f12.png', format='png')
    #plt.show()

if __name__ == '__main__':
    plot_fig12_new()