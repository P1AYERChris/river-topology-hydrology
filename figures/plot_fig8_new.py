import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm
import seaborn as sns
from plot_config_new import set_nature_style, save_fig, COLORS

set_nature_style()

def line_func(x, k, b): return k * x + b

# === 核心数据处理 (保持不变) ===
def get_slopes(grouped, col_idx):
    slopes = []
    for name, group in grouped:
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
        
        try:
            p, _ = curve_fit(line_func, x_norm, y_norm)
            k = p[0]
            if k > 0: slopes.append(k)
        except:
            pass
            
    slopes = np.array(slopes)
    if len(slopes) > 0:
        limit = np.percentile(slopes, 99.5)
        slopes = slopes[slopes <= limit]
    return slopes

# === 绘图函数更新 ===
def plot_dist_panel(ax, data, title, xlabel, color):
    if len(data) < 10: return 

    mu, sigma = np.mean(data), np.std(data)
    N = len(data)
    
    # === 1. 计算绘图范围 (关键修改) ===
    # 强制左侧从0开始，右侧增加 30% 缓冲
    data_min = 0 # 斜率物理意义 > 0
    data_max = data.max()
    data_range = data_max - data.min() # 实际数据的跨度
    
    x_right_limit = data_max + data_range * 0.4 # 右侧留白
    
    # 2. 绘制填充 KDE
    sns.kdeplot(data, ax=ax, color=color, fill=True, alpha=0.2, linewidth=1.5, zorder=1, label='KDE')
    
    # 3. 绘制正态分布拟合 (延伸到新的右边界)
    x_grid = np.linspace(data_min, x_right_limit, 200)
    ax.plot(x_grid, norm.pdf(x_grid, mu, sigma), 
            color='black', linestyle='--', linewidth=1.2, label='Normal fit', zorder=2)
    
    # 4. 绘制均值线
    ax.axvline(mu, color=color, linestyle='-', linewidth=1.5, label='Mean', zorder=2)
    
    # 5. 统计信息 (左上角)
    txt = f'$N={N}$\n$\\mu={mu:.2f}$\n$\\sigma={sigma:.2f}$'
    ax.text(0.05, 0.95, txt, transform=ax.transAxes, ha='left', va='top', fontsize=13, linespacing=1.3)
    
    # 6. 图例 (右上角)
    ax.legend(loc='upper right', frameon=False, fontsize=9, handlelength=1.5)
    
    # 7. 美化与范围设置
    ax.set_title(title, loc='left')
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Density')
    
    # 设置最终的 X 轴范围
    ax.set_xlim(0, x_right_limit)
    
    sns.despine(ax=ax)

def plot_fig8_new():
    file_path = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\P_river_mean.csv'
    try:
        data = pd.read_csv(file_path, header=None)
        for c in range(10): data[c] = pd.to_numeric(data[c], errors='coerce')
        grouped = data.groupby(10)
    except Exception as e:
        print(f"数据读取失败: {e}")
        return

    configs = [
        {'col': 1, 'color': COLORS['blue'], 'title': r'(a) Slope $k_r$', 'xlabel': r'Slope $k_r$'},
        {'col': 4, 'color': COLORS['blue'], 'title': r'(b) Slope $k_r^{in}$', 'xlabel': r'Slope $k_r^{in}$'},
        {'col': 7, 'color': COLORS['blue'], 'title': r'(c) Slope $k_r^{out}$', 'xlabel': r'Slope $k_r^{out}$'},
        
        {'col': 2, 'color': COLORS['red'],  'title': r'(d) Slope $k_d$', 'xlabel': r'Slope $k_d$'},
        {'col': 5, 'color': COLORS['red'],  'title': r'(e) Slope $k_d^{in}$', 'xlabel': r'Slope $k_d^{in}$'},
        {'col': 8, 'color': COLORS['red'],  'title': r'(f) Slope $k_d^{out}$', 'xlabel': r'Slope $k_d^{out}$'}
    ]

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    axes = axes.flatten()

    for i, cfg in enumerate(configs):
        print(f"Processing {cfg['title']}...")
        slopes = get_slopes(grouped, cfg['col'])
        plot_dist_panel(axes[i], slopes, cfg['title'], cfg['xlabel'], cfg['color'])

    plt.tight_layout()
    save_fig('f08.pdf')
    save_fig('f08.png', format='png')
    #plt.show()

if __name__ == '__main__':
    plot_fig8_new()