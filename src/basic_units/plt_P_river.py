import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import geom
from scipy.optimize import curve_fit
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
import seaborn as sns
from sklearn.metrics import r2_score
import seaborn as sns
from scipy import stats
from matplotlib import rcParams
from statistics import mean
from sklearn.metrics import explained_variance_score,r2_score,median_absolute_error,mean_squared_error,mean_absolute_error
from scipy.stats import pearsonr

#设置字体
title_font=fm.FontProperties(family='SimHei',size=22)
axis_font=fm.FontProperties(family='Times New Roman',size=20)
tick_font=fm.FontProperties(family='Times New Roman',size=20)
# 导入数据
data = pd.read_csv(r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\P_river_mean.csv', header=None)

# 获取河网分组
grouped = data.groupby(10)  # 第11列的索引是10
#统计组中最少元素数量
min_elements = grouped.size().min()
print('最少元素数量:', min_elements)
# 存储每条河流的趋势线参数
all_params = []
failed_rivers=[]

#定义线性函数
def line_func(x,k,b):
    return k*x+b

# 存储归一化后的数据
normalized_lengths = []
normalized_ps = []

#创建绘图窗口
fig, ax = plt.subplots(figsize=(12, 6))
# 遍历每条河流
for name, group in grouped:
    sum=group[3]
    for i in range(len(sum)):
        if sum.iloc[i]<0.05:
            break
    length= group[0][0:i]
    p = group[1][0:i]
    #记得在外单元统计时删去所有特征长度为0的行！！！！

    #将length和p都归到0-1之间
    length = (length - length.min()) / (length.max() - length.min())
    p = (p - p.min()) / (p.max() - p.min())
    #length = (length) / (length.max())
    #p = (p ) / (p.max())
    # 存储归一化后的数据
    normalized_lengths.append(length)
    normalized_ps.append(p)
    # 跳过 p 为 nan 的数据组

    if np.isnan(p).any():
        failed_rivers.append(name)
        continue
    try:
        # 绘制原始数据点
        #ax.scatter( length,p, s=10, marker='o',edgecolors='k',facecolors='#B797C6',zorder=2,linewidth=1)
        params, _ = curve_fit(line_func, length, p)

        all_params.append(params)

        # 提取斜率（假设line_func为线性函数，params[0]应为斜率）
        slope = params[0]
        
        # 检查斜率是否小于0
        if slope < 0:
            failed_rivers.append(name)
            continue

        # 绘制拟合曲线
        x_fit = np.linspace(min(length), max(length), 100)
        y_fit = line_func(x_fit, *params)
    
        """ # 计算 R² 值
        r_squared = r2_score(p, y_fit)
        #如果R^2小于0.85，打印出来
        if r_squared<0.85:
            print(name,r_squared) """

        ax.plot(x_fit, y_fit, color='black', linewidth=2,alpha=0.5,zorder=1,linestyle=':')
            
        #设置横轴和纵轴范围都是0-1
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    except:
        failed_rivers.append(name)

# 最后可以选择保存归一化的数据
normalized_data = pd.DataFrame({
    'Normalized_Length': np.concatenate(normalized_lengths),
    'Normalized_P': np.concatenate(normalized_ps)
})
# 输出归一化后的数据到CSV文件（可选）
#normalized_data.to_csv(r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\normalized_P.csv', index=False)

""" #删除normalized_data中nan的行
normalized_data.dropna(inplace=True)

y=normalized_data['Normalized_P']
x=normalized_data['Normalized_Length']

# 计算散点密度
xy = np.vstack([x, y])
z = stats.gaussian_kde(xy)(xy)
idx = z.argsort()
x, y, z = x.iloc[idx], y.iloc[idx], z[idx] 

# 拟合（若换MK，自行操作）最小二乘
def slope(xs, ys):
    m = (((mean(xs) * mean(ys)) - mean(xs * ys)) / ((mean(xs) * mean(xs)) - mean(xs * xs)))
    b = mean(ys) - m * mean(xs)
    return m, b
k, b = slope(x, y)
regression_line = []
for a in x:
    regression_line.append((k * a) + b)

#计算指标
N=len(x)
BIAS = mean(x - y)
MSE = mean_squared_error(x, y)
RMSE = np.power(MSE, 0.5)
R2 = pearsonr(x, y).statistic
adjR2 = 1-((1-r2_score(x,y))*(len(x)-1))/(len(x)-5-1)
MAE = mean_absolute_error(x, y)
EV = explained_variance_score(x, y)
NSE = 1 - (RMSE ** 2 / np.var(x))

#设置字体
title_font=fm.FontProperties(family='SimHei',size=30)
axis_font=fm.FontProperties(family='Times New Roman',size=24)
tick_font=fm.FontProperties(family='Times New Roman',size=24)

#计算置信区间
n = 1
t_value = 1.96  # 95% 置信区间对应的 t 值
std_err = np.std(y - (k * x+b ))
margin_of_error = t_value * (std_err / np.sqrt(n))
lower_confidence_bound = k * x +b - margin_of_error
upper_confidence_bound = k * x  +b+ margin_of_error

#设置字体
config = {"font.family":'Times New Roman',"font.size": 20,"mathtext.fontset":'stix'}
# 应用配置
plt.rcParams.update(config) """

""" #绘图
fig, ax = plt.subplots(figsize=(8, 6))
#plt.plot(x, lower_confidence_bound, linestyle='--', color='black', label='95% Prediction Band')
#plt.plot(x, upper_confidence_bound, linestyle='--', color='black')
scatter = ax.scatter(x, y, marker='o', c=z, edgecolors=None, s=15,cmap='RdBu_r',alpha=0.8)
cbar = plt.colorbar(scatter, shrink=1, orientation='vertical', extend='both', pad=0.015, aspect=30, label='frequency')
#plt.plot([0, 1], [0, 1], 'red', lw=1.5, linestyle='--', label='1:1 line') 
plt.plot(x, regression_line, 'black', lw=1.5, label='Regression Line') 
ax.grid(True, linestyle='--', alpha=0.2)
plt.xlabel('Normalized $\lambda$', fontproperties=axis_font) 
plt.ylabel('Normalized Discharge $D(\lambda)$', fontproperties=axis_font) 
#统计值注释
plt.text(0.95,0.26, '$R^2=%.2f$' % R2, family = 'Times New Roman', horizontalalignment='right')
plt.text(0.95,0.19, '$BIAS=%.2f$' % BIAS, family = 'Times New Roman', horizontalalignment='right')
plt.text(0.95,0.12, '$N=%.0f$' % N, family = 'Times New Roman', horizontalalignment='right')
plt.text(0.95,0.05, '$RMSE=%.2f$' % RMSE, family = 'Times New Roman', horizontalalignment='right')
#网格设置和区域设置
plt.axis([0, 1, 0, 1])  # 设置线的范围
ax.legend(loc='upper left', frameon = False)
plt.tight_layout()
plt.show()

#绘制第二张图
fig, ax = plt.subplots(figsize=(8, 6)) """
plt.title('Discharge data and fitted curve', fontproperties=title_font)
plt.xlabel('Normalized River Characteristic Length', fontproperties=axis_font)
plt.ylabel('Normalized Discharge $D^{\t{out}}(\lambda)$', fontproperties=axis_font)


# 绘制小提琴图
ax_violin=fig.add_axes([0.18,0.56,0.2,0.25])
slops=[param[0] for param in all_params]
#剔除小于0的斜率
slops=[i for i in slops if i>0]
sns.violinplot(data=slops, ax=ax_violin, orient='v',color='#3C5BA8')
ax_violin.set_xlabel('')
ax_violin.set_ylabel('')
ax_violin.set_title('Distribution of ${k_d^{\t{out}}}$', fontproperties=axis_font)
ax_violin.tick_params(axis='y', which='major',direction='in',labelsize=10)
ax_violin.set_xticks([])

ax.set_xticklabels(ax.get_xticks(), fontproperties=axis_font)
ax.set_yticklabels(ax.get_yticks(), fontproperties=axis_font)
ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))
for label in ax_violin.get_yticklabels():
    label.set_fontname('Times New Roman')
plt.xticks(fontproperties=axis_font)
plt.yticks(fontproperties=axis_font)
plt.tight_layout()
plt.show()

# 将所有参数存储为DataFrame
all_params = pd.DataFrame(all_params, columns=['k', 'b'])
k_value=all_params['k']
#剔除小于0的斜率
k_value=k_value[k_value>0]
from scipy.stats import gaussian_kde,expon,norm

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
text_x = 0.3
text_y = 2.5
plt.text(text_x, text_y, f'N: {N:.0f}\nμ: {mu:.2f}\nσ: {sigma:.2f}', fontproperties=axis_font)
#在图中加入一条竖直虚线，位置在均值处，最低点到纵轴0处
plt.axvline(x=mu, color='r', linestyle='--', linewidth=1)
plt.yticks(fontproperties=tick_font)  
plt.xticks(fontproperties=tick_font) 
plt.xlabel('${k_r}$', fontproperties=axis_font)
plt.ylabel('Density', fontproperties=axis_font)
plt.title('Distribution of ${k_r}$', fontproperties=title_font)
#plt.grid(True)
plt.show()