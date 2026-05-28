import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import seaborn as sns
from plot_config_new import set_nature_style, save_fig, COLORS

set_nature_style()

def plot_dist_panel(ax, data, title, xlabel, color):
    # 1. 数据清洗
    data = data[~np.isin(data, [np.nan, np.inf, -np.inf])]
    if len(data) > 0:
        limit = np.percentile(data, 99.5)
        data = data[data <= limit]
    
    if len(data) < 2: return

    # 2. 统计参数
    mu, sigma = np.mean(data), np.std(data)
    N = len(data)
    
    # 3. 绘制填充 KDE
    sns.kdeplot(data, ax=ax, color=color, fill=True, alpha=0.2, linewidth=1.5, zorder=1, label='KDE')
    
    # 4. 绘制正态分布拟合
    # x_grid 范围也要相应扩大，保证曲线画完整
    data_range = data.max() - data.min()
    x_min_plot = data.min() - data_range * 0.4
    x_max_plot = data.max() + data_range * 0.4
    
    x_grid = np.linspace(x_min_plot, x_max_plot, 200)
    ax.plot(x_grid, norm.pdf(x_grid, mu, sigma), 
            color='black', linestyle='--', linewidth=1.2, label='Normal fit', zorder=2)
    
    # 5. 绘制均值线
    ax.axvline(mu, color=color, linestyle='-', linewidth=1.5, label='Mean', zorder=2)
    
    # 6. 统计信息 (固定在左上角)
    txt = f'$N={N}$\n$\\mu={mu:.2f}$\n$\\sigma={sigma:.2f}$'
    ax.text(0.05, 0.95, txt, transform=ax.transAxes, ha='left', va='top', 
            fontsize=13, linespacing=1.3)
    
    # 7. 图例 (固定在右上角)
    ax.legend(loc='upper right', frameon=False, fontsize=9, handlelength=1.5)
    
    # 8. 美化
    ax.set_title(title, loc='left')
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Density')
    
    # === 9. 关键修改：大幅扩宽 X 轴范围 ===
    # 左右各增加 30% 的缓冲空间，确保文字绝对不遮挡数据
    padding = data_range * 0.3
    ax.set_xlim(data.min() - padding, data.max() + padding)
    
    sns.despine(ax=ax)

def plot_fig10_new():
    file_path = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\ratio_base_unit.csv'
    try:
        data = pd.read_csv(file_path).dropna()
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return

    # 配置
    configs = [
        # Runoff (Blue)
        {'col': 'all_run_mean', 'color': COLORS['blue'], 
         'title': r'(a) $R_r^{unit}$', 'xlabel': r'Runoff ratio $R_r^{unit}$'},
        {'col': 'in_run_mean',  'color': COLORS['blue'], 
         'title': r'(b) $R_r^{unit_{in}}$', 'xlabel': r'Runoff ratio (in)'},
        {'col': 'out_run_mean', 'color': COLORS['blue'], 
         'title': r'(c) $R_r^{unit_{out}}$', 'xlabel': r'Runoff ratio (out)'},
        
        # Discharge (Red)
        {'col': 'all_dis_mean', 'color': COLORS['red'], 
         'title': r'(d) $R_d^{unit}$', 'xlabel': r'Discharge ratio $R_d^{unit}$'},
        {'col': 'in_dis_mean',  'color': COLORS['red'], 
         'title': r'(e) $R_d^{unit_{in}}$', 'xlabel': r'Discharge ratio (in)'},
        {'col': 'out_dis_mean', 'color': COLORS['red'], 
         'title': r'(f) $R_d^{unit_{out}}$', 'xlabel': r'Discharge ratio (out)'}
    ]

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    axes = axes.flatten()

    for i, cfg in enumerate(configs):
        col_name = cfg['col']
        if col_name in data.columns:
            print(f"Processing {cfg['title']}...")
            plot_dist_panel(axes[i], data[col_name], cfg['title'], cfg['xlabel'], cfg['color'])

    plt.tight_layout()
    save_fig('f10.pdf')
    save_fig('f10.png', format='png')
    #plt.show()

if __name__ == "__main__":
    plot_fig10_new()