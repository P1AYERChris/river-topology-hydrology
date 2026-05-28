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
file_big = r'E:\研究\河网与径流\河网分级拓扑学\data\data_class/nor_accumulated_runoff_q.xlsx'
file_small = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元/ratio_base_unit.xlsx'
# 从Excel中提取q数据
data_big = pd.read_excel(file_big, usecols=['MAIN_RIV', 'ORD_STRA', 'q'])
data_small = pd.read_excel(file_small, usecols=['id', 'in_run_mean','out_run_mean','all_run_mean'])
#对于data_big,将main_riv相同的数据的q合起来计算平均值
data_big = data_big.groupby(['MAIN_RIV']).mean().reset_index()
#将data_big和data_small按MAIN_RIV和id进行合并
data = pd.merge(data_big, data_small, left_on='MAIN_RIV', right_on='id')
#保存合并后的数据
data.to_excel(r'E:\研究\河网与径流\河网分级拓扑学\data\data_relation/大-小尺度比值.xlsx', index=False)