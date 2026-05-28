import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import geom
from scipy.optimize import curve_fit
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
import seaborn as sns
from sklearn.metrics import r2_score

#设置字体
title_font=fm.FontProperties(family='SimHei',size=30)
axis_font=fm.FontProperties(family='Times New Roman',size=24)
tick_font=fm.FontProperties(family='Times New Roman',size=22)
# 导入数据
file_path = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\ratio_base_unit.csv'

data = pd.read_csv(file_path)
#清除为nan的行
data.dropna(inplace=True)
#创建绘图窗口
fig, ax = plt.subplots(figsize=(12, 6))
#横轴为河流数量
x_values=range(1, len(data) + 1)

plt.errorbar(x_values, data['in_dis_mean'], yerr=[data['in_dis_ci']/2, data['in_dis_ci']/2], elinewidth=0.4,fmt='o', color='black',alpha=0.7, capsize=2)
#plt.title('Scatter Plot of the Data',fontproperties=title_font)
plt.xlabel('', fontproperties=axis_font) 
plt.ylabel('$R_d^{\t{unit_{in}}}$', fontproperties=axis_font) 
#设置y轴范围
plt.ylim(0.4, 1.2)
mu=np.mean(data['in_dis_mean'])
min=np.min(data['in_dis_mean'])
max=np.max(data['in_dis_mean'])
min_ci=np.min(data['in_dis_ci'])
max_ci=np.max(data['in_dis_ci'])
#在图中加入一条横向虚线，位置在均值处，最低点到纵轴0处
plt.axhline(y=mu, color='r', linestyle='-', linewidth=2)
#在图的左上角加入文字，内容为均值、最小值、最大值、最小置信区间、最大置信区间,使用upper left对齐方式

plt.text( 0.1,0.8, s='mean(E): {:.2f}      E: {:.2f}~ {:.2f}\ndet: {:.2f}~ {:.2f}'.format(mu, min, max, min_ci, max_ci),
         transform=plt.gca().transAxes, fontproperties=axis_font)

ax.set_xticklabels(ax.get_xticks(), fontproperties=axis_font)
ax.set_yticklabels(ax.get_yticks(), fontproperties=axis_font)
ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
#不显示x轴刻度
#plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
plt.tight_layout()
plt.show()


from scipy.stats import gaussian_kde,expon,norm
k_value=data['in_dis_mean']
mu=np.mean(k_value)
sigma=np.std(k_value)
N=len(k_value)
print('mu:',mu,'sigma:',sigma)

# 绘制核密度图
plt.figure(figsize=(8, 8))
kde = gaussian_kde(k_value,bw_method='silverman')
x = np.linspace(k_value.min(), k_value.max(), 100)
plt.plot(x, kde(x), color='k', linewidth=2)
plt.fill_between(x, kde(x), color='gray', alpha=0.3)
# 绘制正态分布曲线
normal_dist = norm.pdf(x, mu, sigma)
plt.plot(x, normal_dist, color='b', linestyle='--', linewidth=2, label='Normal Distribution')
plt.legend(fontsize=24)
plt.legend(loc='upper left', prop=axis_font)
# 在图中显示数据量 N、均值和方差
text_x = 0.6
text_y = 0.6
plt.text(text_x, text_y, f'N: {N:.0f}\nμ: {mu:.2f}\nσ: {sigma:.2f}', transform=plt.gca().transAxes,fontproperties=axis_font)
#在图中加入一条竖直虚线，位置在均值处，最低点到纵轴0处
plt.axvline(x=mu, color='r', linestyle='--', linewidth=1)
plt.yticks(fontproperties=tick_font)  
plt.xticks(fontproperties=tick_font) 
plt.xlabel('$R_d^{\t{unit_{in}}}$', fontproperties=axis_font)
plt.ylabel('Density', fontproperties=axis_font)
plt.title('Distribution of $R_d^{\t{unit_{in}}}$', fontproperties=title_font)
#plt.grid(True)

plt.show()