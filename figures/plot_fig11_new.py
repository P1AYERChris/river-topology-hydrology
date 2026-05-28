import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from sklearn.metrics import mean_squared_error
from plot_config_new import set_nature_style, save_fig

set_nature_style()

def filter_outliers(df, col_name):
    q1 = df[col_name].quantile(0.25)
    q3 = df[col_name].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return df[(df[col_name] >= lower) & (df[col_name] <= upper)]

def plot_scatter_panel(ax, x, y, title, xlabel, ylabel, cmap_name):
    # 1. 密度计算
    try:
        xy = np.vstack([x, y])
        z = gaussian_kde(xy)(xy)
        idx = z.argsort()
        x, y, z = x.iloc[idx], y.iloc[idx], z[idx]
    except:
        z = np.ones_like(x)

    # 2. 绘制散点 (密度着色)
    ax.scatter(x, y, c=z, s=15, cmap=cmap_name, alpha=0.8, edgecolor='none', label='Observations')
    
    # 3. 唯一的参照线：1:1 线 (黑色虚线)
    max_val = max(x.max(), y.max())
    limit = max_val * 1.05
    ax.plot([0, limit], [0, limit], color='black', linestyle='--', linewidth=1.5, label='1:1 Reference')
    
    # 4. 统计指标 (关注偏差)
    N = len(x)
    RMSE = np.sqrt(mean_squared_error(x, y))
    # Bias: 正值代表高估，负值代表低估
    BIAS = np.mean(y - x) 
    
    stats_text = (f"$N={N}$\n"
                  f"$BIAS={BIAS:.2f}$\n"
                  f"$RMSE={RMSE:.2f}$")
    
    ax.text(0.95, 0.05, stats_text, transform=ax.transAxes, ha='right', va='bottom',
            fontsize=13, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=3))

    # 5. 美化
    ax.set_title(title, loc='left')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_aspect('equal', adjustable='box')
    
    ax.legend(loc='upper left', frameon=False, fontsize=12)
    
    return

def plot_fig11_new():
    root = r'E:\研究\河网与径流\河网分级拓扑学\data\data_class'
    try:
        # Runoff
        d1 = pd.read_excel(f'{root}/nor_accumulated_runoff_q.xlsx', usecols=['MAIN_RIV', 'ORD_STRA', 'q'])
        d2 = pd.read_excel(f'{root}/catch_q.xlsx', usecols=['MAIN_RIV', 'ORD_STRA', 'q'])
        df_r = pd.merge(d1, d2, on=['MAIN_RIV', 'ORD_STRA'], suffixes=('_y', '_x')).dropna()
        df_r = filter_outliers(df_r, 'q_y')
        df_r = filter_outliers(df_r, 'q_x')

        # Discharge
        d3 = pd.read_excel(f'{root}/nor_mean_discharge_q.xlsx', usecols=['MAIN_RIV', 'ORD_STRA', 'q'])
        d4 = pd.read_excel(f'{root}/upland_q.xlsx', usecols=['MAIN_RIV', 'ORD_STRA', 'q'])
        df_d = pd.merge(d3, d4, on=['MAIN_RIV', 'ORD_STRA'], suffixes=('_y', '_x')).dropna()
        df_d = filter_outliers(df_d, 'q_y')
        df_d = filter_outliers(df_d, 'q_x')
    except Exception as e:
        print(f"Data Error: {e}")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

    # (a) Runoff
    plot_scatter_panel(ax1, df_r['q_x'], df_r['q_y'], 
                       r'(a) Runoff ratio verification', 
                       r'Catchment ratio $R_C/R_B$', r'Runoff ratio $R_r$', 
                       cmap_name='Blues')

    # (b) Discharge
    plot_scatter_panel(ax2, df_d['q_x'], df_d['q_y'], 
                       r'(b) Discharge ratio verification', 
                       r'Area ratio $R_A$', r'Discharge ratio $R_d$', 
                       cmap_name='Reds')

    plt.tight_layout()
    save_fig('f11.pdf')
    save_fig('f11.png', format='png')
    #plt.show()

if __name__ == '__main__':
    plot_fig11_new()