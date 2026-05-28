import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import numpy as np
import seaborn as sns
# 文件路径
file1 = r'E:\研究\河网与径流\河网分级拓扑学\data\data_class/nor_accumulated_runoff_1-7.xlsx'
file2 = r'E:\研究\河网与径流\河网分级拓扑学\data\data_class/count.xlsx'

# 从Excel中提取q数据
data1 = pd.read_excel(file1, usecols=['MAIN_RIV', 'ORD_STRA', 'Total_CATCH'])
data2 = pd.read_excel(file2, usecols=['MAIN_RIV', 'ORD_STRA', 'count'])

# 初始化一个空列表用于存储
products = []

# 循环遍历表1的每一行
for index, row in data1.iterrows():
    # 获取表1当前行的值
    main_riv_value = row['MAIN_RIV']
    ord_stra_value = row['ORD_STRA']
    q1_value = row['Total_CATCH']
    
    # 在表2中查找相应的行
    matching_rows2 = data2[(data2['MAIN_RIV'] == main_riv_value) & (data2['ORD_STRA'] == ord_stra_value)]

    # 如果在表2和表3中都有匹配的行
    if not matching_rows2.empty:
        # 取出表2和表3的q值
        q2_value = matching_rows2['count'].values[0]
        
        # 存储q1和q2*q3的乘积
        products.append([main_riv_value,ord_stra_value,q1_value, q2_value ])

# 将结果转换为DataFrame
products_df = pd.DataFrame(products, columns=['MAIN_RIV', 'ORD_STRA', 'Total_CATCH', 'count'])
# 过滤掉含有NaN的行
products_df = products_df.dropna()
#保存文件
products_df.to_excel(r'E:\研究\河网与径流\河网分级拓扑学\data\data_class\mean_catch.xlsx', index=False)