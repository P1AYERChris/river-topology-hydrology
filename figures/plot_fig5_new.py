import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
from scipy.optimize import curve_fit
from plot_config_new import set_nature_style, save_fig, COLORS

set_nature_style()

def line_func(x, k, b): return k * x + b

# === 数据清洗 ===
def get_clean_data(df, val_col):
    data = []
    for level, group in df.groupby('ORD_STRA'):
        q1, q3 = group[val_col].quantile([0.25, 0.75])
        iqr = q3 - q1
        valid = group[(group[val_col] >= q1 - 1.5*iqr) & (group[val_col] <= q3 + 1.5*iqr)]
        for val in valid[val_col]:
            if val > 0:
                data.append({'Order': int(level), 'Value': np.log(val), 'Raw': val})
    return pd.DataFrame(data)

# === 计算斜率/比率 ===
def get_ratios(df, val_col):
    slopes = []
    df['log_val'] = np.log(df[val_col].replace(0, np.nan))
    for name, group in df.groupby('MAIN_RIV'):
        group = group.dropna(subset=['log_val'])
        if len(group) < 3: continue
        try:
            p, _ = curve_fit(line_func, group['ORD_STRA'], group['log_val'])
            slopes.append(p[0])
        except: pass
    
    # 转换为 Ratio (e^k)
    ratios = np.exp(np.array(slopes))
    ratios = ratios[ratios < np.percentile(ratios, 99)] # 剔除极值优化显示
    return ratios

# === 绘图函数 A: 比率图 (Box + Scatter + Mean) ===
def plot_ratio_panel(ax, df, val_col, title, ylabel, color):
    plot_df = get_clean_data(df, val_col)
    if plot_df.empty: return

    # 1. 散点云 (加深颜色 alpha=0.4)
    sns.stripplot(x='Order', y='Raw', data=plot_df, ax=ax,
                  color=color, alpha=0.4, size=3, jitter=0.25, zorder=0)

    # 2. 箱线图
    sns.boxplot(x='Order', y='Raw', data=plot_df, ax=ax,
                width=0.4, showfliers=False, zorder=1,
                boxprops=dict(facecolor='white', edgecolor=color, linewidth=1.5, alpha=0.8),
                whiskerprops=dict(color=color, linewidth=1.5),
                capprops=dict(color=color, linewidth=1.5),
                medianprops=dict(color='black', linewidth=1.5))

    # 3. 均值连线
    means = plot_df.groupby('Order')['Raw'].mean()
    x_coords = np.arange(len(means))
    ax.plot(x_coords, means.values, color='black', marker='o', markersize=5, lw=2, zorder=3, label='Mean')
    
    # 4. 全局均值
    ax.axhline(plot_df['Raw'].mean(), color='gray', ls='--', lw=1.5, zorder=0)

    ax.set_title(title, loc='left')
    ax.set_xlabel('River order')
    ax.set_ylabel(ylabel)
    sns.despine(ax=ax)

# === 绘图函数 B: Horton定律 (Box + Scatter + Regression + Violin Inset) ===
def plot_horton_complex(ax, df, val_col, title, ylabel, color, inset_pos):
    plot_df = get_clean_data(df, val_col)
    if plot_df.empty: return

    # 1. 散点云 (加深颜色 alpha=0.4)
    sns.stripplot(x='Order', y='Value', data=plot_df, ax=ax,
                  color=color, alpha=0.4, size=2.5, jitter=0.25, zorder=0)

    # 2. 箱线图
    sns.boxplot(x='Order', y='Value', data=plot_df, ax=ax,
                width=0.4, showfliers=False, zorder=1,
                boxprops=dict(facecolor='white', edgecolor=color, linewidth=1.2, alpha=0.8),
                whiskerprops=dict(color=color, linewidth=1.2),
                capprops=dict(color=color, linewidth=1.2),
                medianprops=dict(color='black', linewidth=1.5))

    # 3. 回归线 + 95% CI
    x_discrete = plot_df['Order'].values
    y_val = plot_df['Value'].values
    x_min = x_discrete.min()
    sns.regplot(x=x_discrete - x_min, y=y_val, ax=ax, scatter=False,
                color='black', line_kws={'linewidth': 2, 'linestyle': '--'}, 
                ci=95, truncate=True)

    # 4. Inset: 小提琴图 (指定位置)
    ratios = get_ratios(df, val_col)
    if len(ratios) > 0:
        # inset_pos 格式: [x, y, width, height]
        ax_ins = ax.inset_axes(inset_pos)
        
        ratio_df = pd.DataFrame({'Ratio': ratios})
        sns.violinplot(y='Ratio', data=ratio_df, ax=ax_ins, 
                       color=color, inner='quartile', linewidth=1, alpha=0.9)
        
        mean_ratio = np.mean(ratios)
        symbol = 'R_r' if 'Runoff' in ylabel else 'R_d'
        ax_ins.set_title(f'$\\tilde{{{symbol}}}={mean_ratio:.2f}$', fontsize=10, pad=3)
        ax_ins.set_xticks([]); ax_ins.set_ylabel('')
        ax_ins.tick_params(axis='y', labelsize=8)
        ax_ins.patch.set_alpha(0)

    # 美化
    ax.set_title(title, loc='left')
    ax.set_xlabel('River order')
    ax.set_ylabel(ylabel)
    
    def exp_fmt(x, pos): return f'{np.exp(x):.0e}'
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(exp_fmt))
    sns.despine(ax=ax)

def plot_fig5_new():
    root = r'E:\研究\河网与径流\河网分级拓扑学\data\data_class'
    try:
        df_rq = pd.read_excel(f'{root}/nor_accumulated_runoff_q.xlsx').dropna()
        df_dq = pd.read_excel(f'{root}/nor_mean_discharge_q.xlsx').dropna()
        df_rn = pd.read_excel(f'{root}/nor_accumulated_runoff.xlsx').dropna()
        df_dn = pd.read_excel(f'{root}/nor_discharge_1-10.xlsx').dropna()
    except Exception as e:
        print(f"数据读取失败: {e}")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    ax1, ax2, ax3, ax4 = axes.flatten()

    # (a) Runoff Ratio
    plot_ratio_panel(ax1, df_rq, 'q', '(a) Runoff ratio $R_r$', 'Runoff ratio', COLORS['blue'])

    # (b) Discharge Ratio
    plot_ratio_panel(ax2, df_dq, 'q', '(b) Discharge ratio $R_d$', 'Discharge ratio', COLORS['red'])

    # (c) Runoff Law -> Inset 左下 [0.05, 0.05, 0.3, 0.35]
    plot_horton_complex(ax3, df_rn, 'Normalized_Total_RUNOFF', 
                        '(c) Runoff law', 'Normalized runoff', COLORS['blue'], 
                        inset_pos=[0.05, 0.05, 0.3, 0.35])

    # (d) Discharge Law -> Inset 右下 [0.65, 0.05, 0.3, 0.35]
    plot_horton_complex(ax4, df_dn, 'Normalized_Discharge', 
                        '(d) Discharge law', 'Normalized discharge ', COLORS['red'], 
                        inset_pos=[0.65, 0.05, 0.3, 0.35])

    plt.tight_layout()
    save_fig('f05.pdf')
    save_fig('f05.png', format='png')
    #plt.show()

if __name__ == '__main__':
    plot_fig5_new()