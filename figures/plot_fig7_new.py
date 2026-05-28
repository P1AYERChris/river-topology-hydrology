import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error
import seaborn as sns
from plot_config_new import set_nature_style, save_fig, COLORS

set_nature_style()

def line_func(x, k, b): return k * x + b

def plot_statistical_flow(ax, grouped_data, col_idx, title, ylabel, main_color):
    """
    升级版：统计流体图 + 线性回归验证指标
    """
    # === 1. 数据准备与插值 ===
    grid_points = 100
    x_grid = np.linspace(0, 1, grid_points)
    y_interpolated_list = []
    slopes = []
    
    # 收集有效数据
    for name, group in grouped_data:
        sum_col = group[3].values
        cut_idx = len(sum_col)
        for i in range(len(sum_col)):
            if sum_col[i] < 0.05:
                cut_idx = i
                break
        
        length = group[0].values[0:cut_idx]
        val = group[col_idx].values[0:cut_idx]
        
        if len(length) < 3 or len(val) < 3: continue
        l_min, l_max = length.min(), length.max()
        v_min, v_max = val.min(), val.max()
        if l_max == l_min or v_max == v_min: continue
        
        x_norm = (length - l_min) / (l_max - l_min)
        y_norm = (val - v_min) / (v_max - v_min)
        
        sort_idx = np.argsort(x_norm)
        try:
            # 插值到标准网格
            y_interp = np.interp(x_grid, x_norm[sort_idx], y_norm[sort_idx])
            y_interpolated_list.append(y_interp)
            
            # 计算单条河流斜率 (用于小提琴图)
            p, _ = curve_fit(line_func, x_norm, y_norm)
            if p[0] > 0: slopes.append(p[0])
        except:
            continue

    if not y_interpolated_list: return

    # === 2. 计算流体统计量 ===
    y_matrix = np.array(y_interpolated_list) # Shape: (N_rivers, 100)
    
    y_mean = np.nanmean(y_matrix, axis=0)
    y_05 = np.nanpercentile(y_matrix, 5, axis=0)
    y_95 = np.nanpercentile(y_matrix, 95, axis=0)
    
    # === 3. 计算全局线性回归指标 (替代图12功能) ===
    # 将矩阵展平，相当于把所有点放在一起做回归
    # X 数据需要重复 N_rivers 次
    N_rivers = y_matrix.shape[0]
    X_flat = np.tile(x_grid, N_rivers)
    Y_flat = y_matrix.flatten()
    
    # 清洗 NaN
    mask = np.isfinite(Y_flat)
    X_flat = X_flat[mask]
    Y_flat = Y_flat[mask]
    
    # 计算回归
    slope_global, intercept_global = np.polyfit(X_flat, Y_flat, 1)
    r2_global = pearsonr(X_flat, Y_flat)[0] ** 2
    rmse_global = np.sqrt(mean_squared_error(Y_flat, slope_global * X_flat + intercept_global))
    
    # === 4. 绘图 ===
    # A. 90% 范围带
    ax.fill_between(x_grid, y_05, y_95, color=main_color, alpha=0.2, zorder=0, linewidth=0, label='5-95% Range')
    
    # B. 均值趋势线
    trend_color = '#1f4e79' if main_color == COLORS['blue'] else '#8b0000'
    ax.plot(x_grid, y_mean, color=trend_color, linewidth=2, linestyle='-', zorder=1, label='Mean Trend')

    # C. 全局回归线 (可选，画出来可以对比 Mean Trend 和 Linear 的区别，或者仅展示文字)
    # 这里我们仅用虚线示意，证明 Mean Trend 几乎就是直线
    y_fit_line = slope_global * x_grid + intercept_global
    ax.plot(x_grid, y_fit_line, color='black', linestyle=':', linewidth=1.5, zorder=2, label='Linear Fit')

    # === 5. Inset: 斜率分布 (保持不变) ===
    if len(slopes) > 0:
        ax_ins = ax.inset_axes([0.1, 0.6, 0.35, 0.35])
        df_slopes = pd.DataFrame({'k': slopes})
        sns.violinplot(y='k', data=df_slopes, ax=ax_ins, 
                       color=main_color, inner='quartile', linewidth=0.8, alpha=0.9)
        mean_k = np.mean(slopes)
        ax_ins.set_title(f'Mean $k={mean_k:.2f}$', fontsize=9, pad=2)
        ax_ins.set_xticks([])
        ax_ins.set_xlabel('')
        ax_ins.set_ylabel('')
        ax_ins.tick_params(axis='y', labelsize=8, direction='in', length=2)
        ax_ins.patch.set_alpha(0)

    # === 6. 添加统计信息文本 (整合图12内容) ===
    # 放在右下角
    stats_text = (f"Linearity check:\n"
                  f"$Slope={slope_global:.2f}$\n"
                  f"$R^2={r2_global:.2f}$\n"
                  f"$RMSE={rmse_global:.2f}$")
    
    ax.text(0.95, 0.05, stats_text, transform=ax.transAxes, ha='right', va='bottom',
            fontsize=12, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2))

    # === 7. 美化 ===
    ax.set_title(title, loc='left')
    ylab_final = ylabel.replace('Norm.', 'Normalized')
    ax.set_ylabel(ylab_final)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel(r'Normalized length $\lambda$')
    sns.despine(ax=ax)

def plot_fig7_new():
    file_path = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\P_river_mean.csv'
    try:
        data = pd.read_csv(file_path, header=None)
        for c in range(10): data[c] = pd.to_numeric(data[c], errors='coerce')
        grouped = data.groupby(10)
    except Exception as e:
        print(f"数据读取失败: {e}")
        return

    # 3行2列配置
    configs = [
        {'col': 1, 'color': COLORS['blue'], 'title': r'(a) $R(\lambda)$', 'ylab': 'Norm. runoff'},
        {'col': 2, 'color': COLORS['red'],  'title': r'(b) $D(\lambda)$', 'ylab': 'Norm. discharge'},
        {'col': 4, 'color': COLORS['blue'], 'title': r'(c) $R^{in}(\lambda)$', 'ylab': 'Norm. runoff (in)'},
        {'col': 5, 'color': COLORS['red'],  'title': r'(d) $D^{in}(\lambda)$', 'ylab': 'Norm. discharge (in)'},
        {'col': 7, 'color': COLORS['blue'], 'title': r'(e) $R^{out}(\lambda)$', 'ylab': 'Norm. runoff (out)'},
        {'col': 8, 'color': COLORS['red'],  'title': r'(f) $D^{out}(\lambda)$', 'ylab': 'Norm. discharge (out)'}
    ]

    fig, axes = plt.subplots(3, 2, figsize=(10, 12))
    axes = axes.flatten()

    for i, cfg in enumerate(configs):
        print(f"Processing {cfg['title']}...")
        plot_statistical_flow(axes[i], grouped, cfg['col'], cfg['title'], cfg['ylab'], cfg['color'])

    plt.tight_layout()
    save_fig('f07.pdf')
    save_fig('f07.png', format='png')
    #plt.show()

if __name__ == '__main__':
    plot_fig7_new()