import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from plot_config_new import set_nature_style, save_fig, COLORS
import seaborn as sns
set_nature_style()

def plot_fig9_new():
    # === 数据路径 ===
    file_path = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\ratio_base_unit.csv'
    try:
        data = pd.read_csv(file_path).dropna()
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return

    # === 配置：3行2列 ===
    # Row 1: All (Unit)
    # Row 2: In (Unit_in)
    # Row 3: Out (Unit_out)
    configs = [
        # (a) Runoff All (Blue)
        {'mean': 'all_run_mean', 'ci': 'all_run_ci', 'color': COLORS['blue'],
         'title': r'(a) $R_r^{unit}$', 'ylabel': r'Runoff ratio $R_r^{unit}$'},
        # (b) Discharge All (Red)
        {'mean': 'all_dis_mean', 'ci': 'all_dis_ci', 'color': COLORS['red'],
         'title': r'(b) $R_d^{unit}$', 'ylabel': r'Discharge ratio $R_d^{unit}$'},
        
        # (c) Runoff In (Blue)
        {'mean': 'in_run_mean', 'ci': 'in_run_ci', 'color': COLORS['blue'],
         'title': r'(c) $R_r^{unit_{in}}$', 'ylabel': r'$R_r^{unit_{in}}$'},
        # (d) Discharge In (Red)
        {'mean': 'in_dis_mean', 'ci': 'in_dis_ci', 'color': COLORS['red'],
         'title': r'(d) $R_d^{unit_{in}}$', 'ylabel': r'$R_d^{unit_{in}}$'},
        
        # (e) Runoff Out (Blue)
        {'mean': 'out_run_mean', 'ci': 'out_run_ci', 'color': COLORS['blue'],
         'title': r'(e) $R_r^{unit_{out}}$', 'ylabel': r'$R_r^{unit_{out}}$'},
        # (f) Discharge Out (Red)
        {'mean': 'out_dis_mean', 'ci': 'out_dis_ci', 'color': COLORS['red'],
         'title': r'(f) $R_d^{unit_{out}}$', 'ylabel': r'$R_d^{unit_{out}}$'}
    ]

    fig, axes = plt.subplots(3, 2, figsize=(12, 12))
    axes = axes.flatten()

    x_vals = np.arange(len(data)) # 横轴：简单的序号索引

    for idx, cfg in enumerate(configs):
        ax = axes[idx]
        mean_col = cfg['mean']
        ci_col = cfg['ci']
        color = cfg['color']
        
        if mean_col not in data.columns: continue

        # 1. 绘制误差棒 (作为背景，颜色较淡)
        # alpha=0.3 让误差棒不喧宾夺主
        ax.errorbar(x_vals, data[mean_col], yerr=data[ci_col]/2, 
                    fmt='none', # 不画点，只画线
                    ecolor=color, elinewidth=0.8, capsize=0, alpha=0.3, zorder=1)
        
        # 2. 绘制散点 (作为前景，颜色较深，带白边)
        # edgecolor='white' 增加颗粒感和精致度
        ax.scatter(x_vals, data[mean_col], 
                   c=color, s=15, alpha=0.9, edgecolor='white', linewidth=0.3, zorder=2)
        
        # 3. 计算统计量
        mu = np.mean(data[mean_col])
        val_min, val_max = np.min(data[mean_col]), np.max(data[mean_col])
        ci_min, ci_max = np.min(data[ci_col]), np.max(data[ci_col])

        # 4. 绘制均值线 (深黑色实线)
        ax.axhline(y=mu, color='black', linestyle='-', linewidth=1.5, zorder=3, label='Mean')

        # 5. 添加极简统计文本 (左上角)
        # 使用 LaTeX 格式优化排版
        stats_text = (f'Mean: {mu:.2f}\n'
                      f'Range: {val_min:.2f} ~ {val_max:.2f}\n'
                      f'CI Range: {ci_min:.2f} ~ {ci_max:.2f}')
        
        ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, ha='left', va='top',
                fontsize=13, linespacing=1.4)

        # 6. 美化
        ax.set_title(cfg['title'], loc='left')
        ax.set_ylabel(cfg['ylabel'])
        
        # 隐藏X轴刻度 (因为是任意序号)，只在最后一行保留轴线
        if idx < 4:
            ax.set_xticks([])
        else:
            ax.set_xlabel('River index')
            # 可以只显示每50或100个刻度
            # ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
        
        # Y轴保留2位小数
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
        
        # 适当扩宽Y轴范围，防止极值贴边
        y_span = val_max - val_min
        ax.set_ylim(val_min - y_span*0.1, val_max + y_span*0.35) # 顶部留多一点给文字
        
        sns.despine(ax=ax)

    plt.tight_layout()
    save_fig('f09.pdf')
    save_fig('f09.png', format='png')
    #plt.show()

if __name__ == "__main__":
    plot_fig9_new()