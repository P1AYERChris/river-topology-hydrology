import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, binned_statistic
from plot_config_new import set_nature_style, save_fig, COLORS

set_nature_style()

def get_clean_data(df, x_col, y_col):
    df = df[[x_col, y_col]].dropna()
    df = df[np.isfinite(df[x_col]) & np.isfinite(df[y_col])]
    for col in [x_col, y_col]:
        q1 = df[col].quantile(0.05) 
        q3 = df[col].quantile(0.95)
        iqr = q3 - q1
        df = df[(df[col] >= q1 - 1.5*iqr) & (df[col] <= q3 + 1.5*iqr)]
    return df

def plot_decoupling_panel(ax, x, y, title, xlabel, ylabel, main_color, macro_slope=1.0):
    # 1. 坐标轴设置
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    x_span = x_max - x_min
    y_span = y_max - y_min
    ax.set_xlim(x_min - x_span*0.05, x_max + x_span*0.05)
    ax.set_ylim(y_min - y_span * 0.3, y_max + y_span * 0.35)

    # 2. 背景散点
    try:
        if len(x) > 5000:
            idx = np.random.choice(len(x), 5000, replace=False)
            x_s, y_s = x.iloc[idx], y.iloc[idx]
        else:
            x_s, y_s = x, y
        xy = np.vstack([x_s, y_s])
        z = gaussian_kde(xy)(xy)
        idx_sort = z.argsort()
        ax.scatter(x_s.iloc[idx_sort], y_s.iloc[idx_sort], c=z[idx_sort], s=15, 
                   cmap='Greys', alpha=0.15, edgecolor='none', zorder=0)
    except:
        ax.scatter(x, y, color='gray', s=10, alpha=0.1, zorder=0)

    # === 3. 核心修改：全局均值线 (Global Mean Line) ===
    # 代表拓扑不变量 (Invariant)
    global_mean = np.mean(y)
    ax.axhline(global_mean, color=main_color, linewidth=3, linestyle='-', 
               label='Invariant mean', zorder=4)

    # === 4. 离散的分箱点 (Binned Points) ===
    # 移除连线 (fmt='o')，强调基本单元的独立性
    df_temp = pd.DataFrame({'x': x, 'y': y})
    df_temp['bin'] = pd.cut(df_temp['x'], bins=12)
    bin_stats = df_temp.groupby('bin', observed=True)['y'].agg(['mean', 'count', 'std'])
    bin_centers = [b.mid for b in bin_stats.index]
    valid_mask = (bin_stats['count'] > 0) & np.isfinite(bin_stats['mean'])
    
    if valid_mask.sum() > 1:
        valid_centers = np.array(bin_centers)[valid_mask]
        valid_means = bin_stats.loc[valid_mask, 'mean'].values
        valid_sems = (bin_stats.loc[valid_mask, 'std'] / np.sqrt(bin_stats.loc[valid_mask, 'count'])).values
        
        # fmt='o': 只画点，不连线
        # ecolor: 误差棒颜色
        # mfc='white': 也就是 marker face color 白色，做成空心点效果，好看
        ax.errorbar(valid_centers, valid_means, yerr=valid_sems, fmt='o', 
                    color=main_color, ecolor=main_color, 
                    markersize=8, markeredgewidth=2, mfc='white', 
                    capsize=3, zorder=5, label='Binned means')

    # === 5. 宏观参考线 (Macro Ref) ===
    x_mean_all, y_mean_all = np.mean(x), np.mean(y)
    x_ref = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 100)
    y_ref = macro_slope * (x_ref - x_mean_all) + y_mean_all
    ax.plot(x_ref, y_ref, color='black', linestyle='--', linewidth=1.5, alpha=0.6, 
            label=f'Macro Reference (Slope={macro_slope})', zorder=3)

    # 6. 统计说明
    stats_text = f"Mean $\\approx$ {global_mean:.2f}" # 强调均值恒定
    ax.text(0.95, 0.05, stats_text, transform=ax.transAxes, ha='right', va='bottom', 
            fontsize=14,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.85, pad=3))

    ax.set_title(title, loc='left')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(loc='upper left', frameon=False, fontsize=12)

    return

def plot_fig13_new():
    root = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元'
    def load(f):
        try: return pd.read_excel(f)
        except: return pd.read_csv(f.replace('.xlsx','.csv'))
    try:
        base = load(f'{root}/ratio_base_unit.xlsx')
        catch = load(f'{root}/ratio_base_unit_catch.xlsx')
        upcatch = load(f'{root}/ratio_base_unit_upcatch.xlsx')
    except Exception as e:
        print(f"Error: {e}")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # (a) Runoff (Blue)
    if 'id' in base.columns and 'id' in catch.columns:
        df_b = pd.merge(base[['id', 'all_run_mean']], catch[['id', 'all_catch_mean']], on='id')
        df_b = get_clean_data(df_b, 'all_catch_mean', 'all_run_mean')
        plot_decoupling_panel(ax1, df_b['all_catch_mean'], df_b['all_run_mean'],
                              r'(a) Runoff decoupling',
                              r'Unit count ratio $R_C^{unit}$', r'Unit runoff ratio $R_r^{unit}$',
                              COLORS['blue'], macro_slope=1.0)

    # (b) Discharge (Red)
    if 'id' in base.columns and 'id' in upcatch.columns:
        df_a = pd.merge(base[['id', 'all_dis_mean']], upcatch[['id', 'all_catch_mean']], on='id')
        df_a = get_clean_data(df_a, 'all_catch_mean', 'all_dis_mean')
        plot_decoupling_panel(ax2, df_a['all_catch_mean'], df_a['all_dis_mean'],
                              r'(b) Discharge decoupling', 
                              r'Unit area ratio $R_A^{unit}$', r'Unit discharge ratio $R_d^{unit}$',
                              COLORS['red'], macro_slope=1.0)

    plt.tight_layout()
    save_fig('f13.pdf')
    save_fig('f13.png', format='png')
    #plt.show()

if __name__ == '__main__':
    plot_fig13_new()