import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
# 导入数据
data = pd.read_excel(r'E:\研究\河网与径流\河网分级拓扑学\data\data_class/nor_discharge_1-10.xlsx')
data=data.dropna()

#设置字体
title_font=fm.FontProperties(family='SimHei',size=30)
axis_font=fm.FontProperties(family='Times New Roman',size=24)
tick_font=fm.FontProperties(family='Times New Roman',size=22)

################################################################################
#描述性统计分析
# 绘制箱型统计图
#plt.figure(figsize=(10,6))
""" ax=data.boxplot(column='Normalized_Discharge',by='ORD_STRA',grid=False,patch_artist=True,
boxprops=dict(color='black',facecolor='#4C72B0',alpha=0.6,linewidth=1.5),
medianprops=dict(color='black',linewidth=1.5),
whiskerprops=dict(color='black',linewidth=1.5),
flierprops=dict(marker='o', markerfacecolor='#333333', markeredgecolor='#333333', markersize=3),
capprops=dict(color='black'))
ax.set_title('Discharge grouped by ORD_STRA',fontproperties=title_font)
plt.suptitle('')
plt.xlabel('River Level (ORD_STRA)',fontproperties=axis_font)
plt.ylabel('Normalized Discharge',fontproperties=axis_font)
plt.xticks(fontproperties=axis_font)
plt.yticks(fontproperties=axis_font)
plt.grid(axis='y',color='#DDDDDD',linestyle='-',linewidth=1)
plt.show()

# 按等级分组计算统计量
stat_desc = data.groupby('ORD_STRA')['Normalized_Total_Discharge'].describe()
print(stat_desc) """

""" # 绘制每个等级下归一化径流量的分布情况
data.boxplot(column='Normalized_Total_Discharge', by='ORD_STRA')
plt.show() """

# 根据箱线图确定异常值的范围
level_groups = data.groupby('ORD_STRA')
outliers = pd.DataFrame()

for level, group in level_groups:
    q1 = group['Normalized_Discharge'].quantile(0.25)
    q3 = group['Normalized_Discharge'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    level_outliers = group[(group['Normalized_Discharge'] < lower_bound) | (group['Normalized_Discharge'] > upper_bound)]
    level_outliers.loc['ORD_STRA'] = level
    outliers = pd.concat([outliers, level_outliers])

# 打印异常值数量和占比
""" num_outliers = len(outliers)
percentage_outliers = num_outliers / len(data) * 100
print("异常数据数量：", num_outliers)
print("异常数据占比：", percentage_outliers, "%") """

# 删除匹配outliers中mainriv列的数据
data = data[~data['MAIN_RIV'].isin(outliers['MAIN_RIV'])]

# 打印剔除匹配outliers中mainriv列数据后的数据数量
""" num_data_without_outliers = len(data)
print("剔除匹配outliers中MAIN_RIV列数据后的数据数量:", num_data_without_outliers)
print('剩余河流数量：',data['MAIN_RIV'].nunique()) """
################################################################################

################################################################################
""" #相关性分析
import numpy as np
from scipy.stats import spearmanr

# 计算Spearman等级相关系数
corr, p_value = spearmanr(data['ORD_STRA'], data['Normalized_Total_Discharge'])
print(f"Spearman correlation: {corr}, p-value: {p_value}") """
################################################################################

################################################################################
#回归建模
#分类编码+ensemble模型
""" from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 对等级进行标签编码
label_encoder = LabelEncoder()
data['ORD_STRA'] = label_encoder.fit_transform(data['ORD_STRA'])

# 对编码后的等级进行一热编码
onehot_encoder = OneHotEncoder()
X = onehot_encoder.fit_transform(data['ORD_STRA'].values.reshape(-1, 1)).toarray()
y = data['Normalized_Total_Discharge'].values

# 划分训练测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 训练随机森林回归模型
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# 评估模型性能
y_pred = rf_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"MSE: {mse}") """
################################################################################

################################################################################
#函数拟合分析
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import seaborn as sns


#按照mainriv分组
grouped=data.groupby('MAIN_RIV')

# 定义指数函数
def exp_func(x, a, b,c):
    return a * np.exp(b * x)+c

#定义线性函数
def line_func(x,k,b):
    return k*x+b

# 存储每条河流的趋势线参数
all_params = []
failed_rivers=[]

#创建空dataframe用于储存结果
q_df=pd.DataFrame(columns=['MAIN_RIV','ratio_discharge_nihe'])

#创造一个绘图窗口
fig,ax=plt.subplots(figsize=(12,6))

# 需要确保数据中没有零或负值
data['Log_Normalized_Discharge'] = np.log(data['Normalized_Discharge']
                                             .replace(0, np.nan))
box=data.boxplot(column='Log_Normalized_Discharge',by='ORD_STRA',grid=False,patch_artist=True,
boxprops=dict(color='black',facecolor='#4C72B0',alpha=1,linewidth=1.5),
medianprops=dict(color='black',linewidth=1.5),
whiskerprops=dict(color='black',linewidth=1.5),
flierprops=dict(marker='o', markerfacecolor='#333333', markeredgecolor='#333333', markersize=2),
capprops=dict(color='black',linewidth=1.5),ax=ax,zorder=2)
plt.suptitle('') 
# 遍历每条河流
for name, group in grouped:
    level = (group['ORD_STRA'].values)
    discharge = group['Normalized_Discharge'].values

    # 跳过 discharge 为 0 的数据组
    if 0 in discharge:
        failed_rivers.append(name)
        continue

    discharge = np.log(discharge)

    try:

        # 绘制原始数据点
        #ax.scatter(level, discharge, s=30, marker='o',edgecolors='k',facecolors='#B797C6',zorder=2,linewidth=1)

        # 对当前河流进行趋势线拟合
        params, _ = curve_fit(line_func, level, discharge)
        k=params[0]
        all_params.append(params)

        #保存数据
        q_df = pd.concat([q_df, pd.DataFrame({'MAIN_RIV': [name], 'ratio_runoff_zhijie':np.exp(k)})], ignore_index=True)
        # 绘制拟合曲线

        # 绘制拟合曲线
        x_fit = np.linspace(min(level), max(level), 100)
        y_fit = line_func(x_fit, *params)
        ax.plot(x_fit, y_fit, color='black', linewidth=1,alpha=0.8,zorder=1,linestyle='--')

    except:
        failed_rivers.append(name)

# 添加图例
#ax.legend(loc='upper left', fontsize=10, framealpha=0.5)

#保存数据
#q_df.to_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/ratio_discharge_nihe.xlsx', index=False)

# 绘制小提琴图
ax_violin=fig.add_axes([0.7,0.2,0.2,0.25])
slops=[param[0] for param in all_params]
slops=np.exp(slops)
sns.violinplot(data=slops, ax=ax_violin, orient='v',color='#3C5BA8')
ax_violin.set_xlabel('')
ax_violin.set_ylabel('')
ax_violin.set_title('Distribution of $\~{R_d}$', fontproperties=axis_font)
ax_violin.tick_params(axis='y', which='major',direction='in',labelsize=10)
ax_violin.set_xticks([])
for label in ax_violin.get_yticklabels():
    label.set_fontname('Times New Roman')

# 美化图形
ax.set_xticklabels(ax.get_xticks(), fontproperties=axis_font)
ax.set_yticklabels(ax.get_yticks(), fontproperties=axis_font)

ax.set_xlabel('River Order',fontproperties=axis_font)
ax.set_ylabel('Normalized Discharge', fontproperties=axis_font)
ax.set_title('Discharge data and fitted curves', fontproperties=title_font)
ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
#ax.grid(True, linestyle='--', linewidth=0.5)
#ax.tick_params(axis='both', which='major')

#设置y轴刻度为真实值的指数,格式为科学记数法
def scale_formatter(x, pos):
    return f'{np.exp(x):.0e}'
ax.yaxis.set_major_formatter(ticker.FuncFormatter(scale_formatter))

plt.xticks(fontproperties=axis_font)
plt.yticks(fontproperties=axis_font)
plt.tight_layout()
plt.show()

#再次剔除异常数据
data=data[~data['MAIN_RIV'].isin(failed_rivers)]

# 将所有参数存储为DataFrame
all_params = pd.DataFrame(all_params, columns=['k', 'b'])

""" #计算参数统计量
print('参数统计量：')
print(all_params.describe())

#可视化参数分布
all_params.hist(bins=20,figsize=(12,4))
plt.show() """

""" from scipy.stats import probplot,kstest,norm
# 对每个参数进行正态性检验
for param in ['k', 'b']:
    # PP 图
    fig, ax = plt.subplots(figsize=(8, 6))
    probplot(all_params[param], dist=norm, plot=ax)
    ax.set_title(f'PP Plot for Parameter {param}')
    ax.set_xlabel('Theoretical Quantiles')
    ax.set_ylabel('Empirical Quantiles')
    plt.show()

    # QQ 图
    fig, ax = plt.subplots(figsize=(8, 6))
    probplot(all_params[param], dist=norm, plot=ax)
    ax.set_title(f'QQ Plot for Parameter {param}')
    ax.set_xlabel('Theoretical Quantiles')
    ax.set_ylabel('Sample Quantiles')
    plt.show()
    
    # Kolmogorov-Smirnov检验
    mu=np.mean(all_params[param])
    sigma=np.std(all_params[param])
    stat, p_value = kstest(all_params[param], 'norm',args=(mu,sigma))
    print('mu:',mu,'sigma:',sigma)
    print(f'Kolmogorov-Smirnov Test (Parameter {param}):')
    print(f'Statistic = {stat:.4f}, p-value = {p_value:.4f}')

    # 解释p-value
    alpha = 0.05
    if p_value > alpha:
        print(f'无法拒绝正态分布假设 (p-value = {p_value:.4f} > {alpha})')
    else:
        print(f'拒绝正态分布假设 (p-value = {p_value:.4f} <= {alpha})')
    print('-' * 30) """
###############################################################################
from scipy.stats import gaussian_kde,norm
k_value=all_params['k']
k_value=np.exp(k_value)
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

#在图中加入一条竖直虚线，位置在均值处，最低点到纵轴0处
plt.axvline(x=mu, color='r', linestyle='--', linewidth=1)

# 绘制正态分布曲线
normal_dist = norm.pdf(x, mu, sigma)
plt.plot(x, normal_dist, color='b', linestyle='--', linewidth=2, label='Normal Distribution')
plt.legend(fontsize=24)
#设置legend在图的右上方
plt.legend(loc='upper right', prop=axis_font)
# 在图中显示数据量 N、均值和方差
text_x = 5
text_y = 0.8
plt.text(text_x, text_y, f'N: {N:.0f}\nμ: {mu:.2f}\nσ: {sigma:.2f}', fontproperties=axis_font)
plt.yticks(fontproperties=tick_font)  
plt.xticks(fontproperties=tick_font) 
plt.xlabel('Discharge Ratios $\~{R_d}$', fontproperties=axis_font)
plt.ylabel('Density', fontproperties=axis_font)
plt.title('Distribution of discharge ratios', fontproperties=title_font)
#plt.grid(True)
plt.show()