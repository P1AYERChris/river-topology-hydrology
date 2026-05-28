import pandas as pd

#读取xlsx文件
df=pd.read_csv(r'E:\研究\河网与径流\河网分级拓扑学\data\data_class/accumulated_runoff.csv')

#进行归一化
df['Normalized_Total_RUNOFF'] = df.groupby('MAIN_RIV')['Total_RUNOFF'].transform(lambda x: x / x.max())
df['Normalized_Total_CATCH'] = df.groupby('MAIN_RIV')['Total_CATCH'].transform(lambda x: x / x.max())
# 保存结果到 xlsx 文件
df.to_excel('E:\研究\河网与径流\河网分级拓扑学\data\data_class/nor_accumulated_runoff.xlsx', index=False)