import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, norm
from scipy.optimize import curve_fit
import seaborn as sns
from plot_config_new import set_nature_style, save_fig, COLORS

set_nature_style()

def line_func(x, k, b): return k * x + b

# ... (保持 filter_rivers_by_iqr, get_fitted_slopes, get_river_means 函数不变) ...
# 请务必保留之前正确的清洗和计算函数

def filter_rivers_by_iqr(df, val_col):
    outliers = pd.DataFrame()
    for level, group in df.groupby('ORD_STRA'):
        q1 = group[val_col].quantile(0.25)
        q3 = group[val_col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        level_outliers = group[(group[val_col] < lower) | (group[val_col] > upper)]
        outliers = pd.concat([outliers, level_outliers])
    
    if not outliers.empty:
        cleaned_df = df[~df['MAIN_RIV'].isin(outliers['MAIN_RIV'])].copy()
    else:
        cleaned_df = df.copy()
    return cleaned_df

def get_fitted_slopes(df, val_col):
    df_clean = filter_rivers_by_iqr(df, val_col)
    log_col = 'log_val'
    df_clean[log_col] = np.log(df_clean[val_col].replace(0, np.nan))
    slopes = []
    for name, group in df_clean.groupby('MAIN_RIV'):
        level = group['ORD_STRA'].values
        val = group[log_col].values
        if len(level) < 2 or np.isnan(val).any(): continue
        try:
            p, _ = curve_fit(line_func, level, val)
            slopes.append(p[0])
        except: pass
    return np.exp(slopes)

def get_river_means(df, val_col, exclude_order_2=False):
    df_clean = filter_rivers_by_iqr(df, val_col)
    if exclude_order_2:
        df_clean = df_clean[df_clean['ORD_STRA'] != 2]
    means = df_clean.groupby('MAIN_RIV')[val_col].mean()
    return means.values

# === 绘图函数更新 ===
def plot_dist_panel(ax, data, title, xlabel, color):
    data = data[~np.isnan(data) & ~np.isinf(data)]
    if len(data) == 0: return

    mu, sigma = np.mean(data), np.std(data)
    N = len(data)
    
    # 1. Filled KDE
    sns.kdeplot(data, ax=ax, color=color, fill=True, alpha=0.2, linewidth=1.5, zorder=1, label='KDE')
    
    # 2. Normal Fit
    x = np.linspace(data.min(), data.max(), 200)
    ax.plot(x, norm.pdf(x, mu, sigma), color='black', linestyle='--', linewidth=1.2, label='Normal fit', zorder=2)
    
    # 3. Mean Line
    ax.axvline(mu, color=color, linestyle='-', linewidth=1.5, label='Mean', zorder=2)
    
    # 4. Stats Text
    txt = f'$N={N}$\n$\\mu={mu:.2f}$\n$\\sigma={sigma:.2f}$'
    ax.text(0.05, 0.95, txt, transform=ax.transAxes, ha='left', va='top', fontsize=13)
    
    # === 5. Add Legend ===
    ax.legend(loc='upper right', frameon=False, fontsize=9, handlelength=1.5)
    
    ax.set_title(title, loc='left')
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Density')
    
    # 图6可以保持从0开始，或者也改为自适应
    # ax.set_xlim(left=0) 
    
    sns.despine(ax=ax)

def plot_fig6_new():
    root = r'E:\研究\河网与径流\河网分级拓扑学\data\data_class'
    try:
        df_rq = pd.read_excel(f'{root}/nor_accumulated_runoff_q.xlsx').dropna()
        df_dq = pd.read_excel(f'{root}/nor_mean_discharge_q.xlsx').dropna()
        df_rn = pd.read_excel(f'{root}/nor_accumulated_runoff.xlsx').dropna()
        df_dn = pd.read_excel(f'{root}/nor_discharge_1-10.xlsx').dropna()
    except Exception as e:
        print(f"数据读取失败: {e}")
        return

    data_a = get_river_means(df_rq, 'q', exclude_order_2=False)
    data_b = get_fitted_slopes(df_rn, 'Normalized_Total_RUNOFF')
    data_c = get_river_means(df_rq, 'q', exclude_order_2=True)
    data_d = get_river_means(df_dq, 'q', exclude_order_2=False)
    data_e = get_fitted_slopes(df_dn, 'Normalized_Discharge')
    data_f = get_river_means(df_dq, 'q', exclude_order_2=True)

    configs = [
        (data_a, '(a) Runoff ratio $R_r$', 'Runoff ratio', COLORS['blue']),
        (data_b, '(b) Horton ratio (from Slope)', 'Horton ratio', COLORS['blue']),
        (data_c, '(c) Runoff ratio (No Order 2)', 'Runoff ratio', COLORS['blue']),
        (data_d, '(d) Discharge ratio $R_d$', 'Discharge ratio', COLORS['red']),
        (data_e, '(e) Horton ratio (from Slope)', 'Horton ratio', COLORS['red']),
        (data_f, '(f) Discharge ratio (No Order 2)', 'Discharge ratio', COLORS['red'])
    ]

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    axes = axes.flatten()

    for i, (data, title, xlabel, color) in enumerate(configs):
        plot_dist_panel(axes[i], data, title, xlabel, color)

    plt.tight_layout()
    save_fig('f06.pdf')
    save_fig('f06.png', format='png')
    #plt.show()

if __name__ == '__main__':
    plot_fig6_new()