import matplotlib.pyplot as plt
import seaborn as sns
import os

# === 1. 定义保存路径 ===
SAVE_DIR = r'E:\研究\河网与径流\河网分级拓扑学\pic\提交图片hess'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def save_fig(filename, format='pdf'):
    full_path = os.path.join(SAVE_DIR, filename)
    #保存为指定格式
    plt.savefig(full_path, dpi=300, bbox_inches='tight', pad_inches=0.1, format=format)
    print(f"图片已保存至: {full_path}")

# === 2. Nature/Science 顶刊绘图风格 ===
def set_nature_style():
    # 基础重置
    sns.set_theme(style="ticks")
    
    plt.rcParams.update({

        # === 关键修改：替换为 HESS 推荐的无衬线字体 ===
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica"],
        "mathtext.default": "regular", # 强制公式符号使用主字体，避免产生混合字体
        
        # 字号保持之前调整过的大字号即可
        "font.size": 14,           
        "axes.labelsize": 16,      
        "axes.titlesize": 18,      
        "xtick.labelsize": 16,     
        "ytick.labelsize": 16,     
        "legend.fontsize": 13,
        
        # 线条
        "axes.linewidth": 1.5,
        "xtick.major.width": 1.5,
        "ytick.major.width": 1.5,
        "xtick.major.size": 6,
        "ytick.major.size": 6,
        "xtick.direction": "in",
        "ytick.direction": "in",
        
        # 布局
        "figure.dpi": 300,
        "figure.figsize": (12, 10),
        "savefig.dpi": 300,
    })

# === 3. 高级配色方案 ===
COLORS = {
    'blue': '#3C5488',   # Nature Blue: 几何/静态
    'red': '#E64B35',    # Nature Red: 水文/动态
    'grey': '#7F7F7F',   # 辅助
    'black': '#202020'   # 深黑
}