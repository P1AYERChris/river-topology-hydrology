import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import numpy as np
import seaborn as sns
from scipy import stats
from matplotlib import rcParams
from statistics import mean
from sklearn.metrics import explained_variance_score,r2_score,median_absolute_error,mean_squared_error,mean_absolute_error
from scipy.stats import pearsonr
import matplotlib.font_manager as fm

# 文件路径
file1 = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元/ratio_base_unit.xlsx'
file2 = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元/ratio_base_unit_catch.xlsx'

# 从Excel中提取q数据
data1 = pd.read_excel(file1, usecols=['id', 'in_run_mean','out_run_mean','all_run_mean'])
data2 = pd.read_excel(file2, usecols=['id', 'in_catch_mean','out_catch_mean','all_catch_mean'])


# 初始化一个空列表用于存储结果
products = []

# 循环遍历表1的每一行
for index, row in data1.iterrows():
    # 获取表1当前行的值
    id_value = row['id']
    in_run_mean_value = row['in_run_mean']
    out_run_mean_value = row['out_run_mean']
    all_run_mean_value = row['all_run_mean']
    
    # 在表2中查找相应的行
    matching_rows2 = data2[(data2['id'] == id_value)]

    # 如果在表2中都有匹配的行
    if not matching_rows2.empty :
        # 取出表2的值
        in_catch_mean_value = matching_rows2['in_catch_mean'].values[0]
        out_catch_mean_value = matching_rows2['out_catch_mean'].values[0]
        all_catch_mean_value = matching_rows2['all_catch_mean'].values[0]
    
    products.append([id_value, all_run_mean_value, all_catch_mean_value])

# 将结果转换为DataFrame
products_df = pd.DataFrame(products, columns=['id', 'rr', 'rc'])
# 过滤掉含有NaN的行
products_df = products_df.dropna()

# 根据箱型图剔除q1异常的行
q1 = products_df['rr'].quantile(0.25)
q3 = products_df['rr'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
# 计算剔除异常值前后的行数
original_count = len(products_df)
# 剔除异常值
products_df = products_df[(products_df['rr'] >= lower_bound) & (products_df['rr'] <= upper_bound)]
# 计算剔除的行数和占比
removed_count = original_count - len(products_df)
percentage_removed = (removed_count / original_count) * 100
# 打印剔除的行数和占比
print("剔除的行数：", removed_count)
print("剔除的占比：{:.2f}%".format(percentage_removed))

# 根据箱型图剔除异常的行
q1 = products_df['rc'].quantile(0.25)
q3 = products_df['rc'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
# 计算剔除异常值前后的行数
original_count = len(products_df)
# 剔除异常值
products_df = products_df[(products_df['rc'] >= lower_bound) & (products_df['rc'] <= upper_bound)]
# 计算剔除的行数和占比
removed_count = original_count - len(products_df)
percentage_removed = (removed_count / original_count) * 100
# 打印剔除的行数和占比
print("剔除的行数：", removed_count)
print("剔除的占比：{:.2f}%".format(percentage_removed))

# 创建新的DataFrame，按MAIN_RIV分组，计算q1和q2*q3的均值
#products_df = products_df.groupby('MAIN_RIV', as_index=False).agg({'q1': 'mean', 'q2*q3': 'mean'})
y=products_df['rr']
x=products_df['rc']

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
config = {"font.family":'Times New Roman',"font.size": 20,"mathtext.fontset":'stix'}
# 应用配置
plt.rcParams.update(config)
#绘图
fig, ax = plt.subplots(figsize=(8, 6))
#plt.plot(x, lower_confidence_bound, linestyle='--', color='black', label='95% Prediction Band')
#plt.plot(x, upper_confidence_bound, linestyle='--', color='black')
scatter = ax.scatter(x, y, marker='o', c=z, edgecolors=None, s=15,cmap='RdBu_r',alpha=0.8)
cbar = plt.colorbar(scatter, shrink=1, orientation='vertical', extend='both', pad=0.015, aspect=30, label='frequency')
#plt.plot([0, 5], [0, 5], 'red', lw=1.5, linestyle='--', label='1:1 line') 
plt.plot(x, regression_line, 'black', lw=1.5, label='Regression Line') 
ax.grid(True, linestyle='--', alpha=0.2)
plt.xlabel('$R_C^{unit}$', fontproperties=axis_font) 
plt.ylabel('$R_r^{unit}$', fontproperties=axis_font) 
#统计值注释
plt.text(4.35, 1.258, '$Slope=%.2f$' % k, fontproperties='Times New Roman', horizontalalignment='right')
plt.text(4.35,1.246, '$R^2=%.2f$' % R2, family = 'Times New Roman', horizontalalignment='right')
plt.text(4.35,1.234, '$BIAS=%.2f$' % BIAS, family = 'Times New Roman', horizontalalignment='right')
plt.text(4.35,1.222, '$N=%.0f$' % N, family = 'Times New Roman', horizontalalignment='right')
plt.text(4.35,1.21, '$RMSE=%.2f$' % RMSE, family = 'Times New Roman', horizontalalignment='right')
#网格设置和区域设置
plt.axis([2, 4.5, 1.2, 1.4])  # 设置线的范围

ax.legend(loc='upper left', frameon = False)
plt.tight_layout()
plt.show() 

# 文件路径
file1 = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元/ratio_base_unit.xlsx'
file2 = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元/ratio_base_unit_upcatch.xlsx'

# 从Excel中提取q数据
data1 = pd.read_excel(file1, usecols=['id', 'in_dis_mean','out_dis_mean','all_dis_mean'])
data2 = pd.read_excel(file2, usecols=['id', 'in_catch_mean','out_catch_mean','all_catch_mean'])


# 初始化一个空列表用于存储结果
products = []

# 循环遍历表1的每一行
for index, row in data1.iterrows():
    # 获取表1当前行的值
    id_value = row['id']
    in_dis_mean_value = row['in_dis_mean']
    out_dis_mean_value = row['out_dis_mean']
    all_dis_mean_value = row['all_dis_mean']
    # 在表2中查找相应的行
    matching_rows2 = data2[(data2['id'] == id_value)]

    # 如果在表2中都有匹配的行
    if not matching_rows2.empty :
        # 取出表2的值
        in_catch_mean_value = matching_rows2['in_catch_mean'].values[0]
        out_catch_mean_value = matching_rows2['out_catch_mean'].values[0]
        all_catch_mean_value = matching_rows2['all_catch_mean'].values[0]
    
    products.append([id_value, all_dis_mean_value, all_catch_mean_value])

# 将结果转换为DataFrame
products_df = pd.DataFrame(products, columns=['id', 'rd', 'rc'])
# 过滤掉含有NaN的行
products_df = products_df.dropna()

# 根据箱型图剔除q1异常的行
q1 = products_df['rd'].quantile(0.25)
q3 = products_df['rd'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
# 计算剔除异常值前后的行数
original_count = len(products_df)
# 剔除异常值
products_df = products_df[(products_df['rd'] >= lower_bound) & (products_df['rd'] <= upper_bound)]
# 计算剔除的行数和占比
removed_count = original_count - len(products_df)
percentage_removed = (removed_count / original_count) * 100
# 打印剔除的行数和占比
print("剔除的行数：", removed_count)
print("剔除的占比：{:.2f}%".format(percentage_removed))

# 根据箱型图剔除异常的行
q1 = products_df['rc'].quantile(0.25)
q3 = products_df['rc'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
# 计算剔除异常值前后的行数
original_count = len(products_df)
# 剔除异常值
products_df = products_df[(products_df['rc'] >= lower_bound) & (products_df['rc'] <= upper_bound)]
# 计算剔除的行数和占比
removed_count = original_count - len(products_df)
percentage_removed = (removed_count / original_count) * 100
# 打印剔除的行数和占比
print("剔除的行数：", removed_count)
print("剔除的占比：{:.2f}%".format(percentage_removed))

# 创建新的DataFrame，按MAIN_RIV分组，计算q1和q2*q3的均值
#products_df = products_df.groupby('MAIN_RIV', as_index=False).agg({'q1': 'mean', 'q2*q3': 'mean'})
y=products_df['rd']
x=products_df['rc']

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
config = {"font.family":'Times New Roman',"font.size": 20,"mathtext.fontset":'stix'}
# 应用配置
plt.rcParams.update(config)
#绘图
fig, ax = plt.subplots(figsize=(8, 6))
#plt.plot(x, lower_confidence_bound, linestyle='--', color='black', label='95% Prediction Band')
#plt.plot(x, upper_confidence_bound, linestyle='--', color='black')
scatter = ax.scatter(x, y, marker='o', c=z, edgecolors=None, s=15,cmap='RdBu_r',alpha=0.8)
cbar = plt.colorbar(scatter, shrink=1, orientation='vertical', extend='both', pad=0.015, aspect=30, label='frequency')
#plt.plot([0, 5], [0, 5], 'red', lw=1.5, linestyle='--', label='1:1 line') 
plt.plot(x, regression_line, 'black', lw=1.5, label='Regression Line') 
ax.grid(True, linestyle='--', alpha=0.2)
plt.xlabel('$R_A^{unit}$', fontproperties=axis_font) 
plt.ylabel('$R_d^{unit}$', fontproperties=axis_font) 
#统计值注释
plt.text(0.77, 0.72, '$Slope=%.2f$' % k, fontproperties='Times New Roman', horizontalalignment='right')
plt.text(0.77,0.695, '$R^2=%.2f$' % R2, family = 'Times New Roman', horizontalalignment='right')
plt.text(0.77,0.67, '$BIAS=%.2f$' % BIAS, family = 'Times New Roman', horizontalalignment='right')
plt.text(0.77,0.645, '$N=%.0f$' % N, family = 'Times New Roman', horizontalalignment='right')
plt.text(0.77,0.62, '$RMSE=%.2f$' % RMSE, family = 'Times New Roman', horizontalalignment='right')
#网格设置和区域设置
plt.axis([0.35, 0.8, 0.6, 1])  # 设置线的范围

ax.legend(loc='upper left', frameon = False)
plt.tight_layout()
plt.show() 