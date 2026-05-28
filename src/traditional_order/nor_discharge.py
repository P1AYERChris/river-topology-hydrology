import pandas as pd

#读取xlsx文件
df=pd.read_excel(r'E:\研究\河网与径流\河网分级拓扑学\data\data_class\mean_discharge.xlsx')

#进行归一化
df['Normalized_Discharge'] = df.groupby('MAIN_RIV')['DISCHARGE'].transform(lambda x: x / x.max())

# 保存结果到 xlsx 文件
df.to_excel(r'E:\研究\河网与径流\河网分级拓扑学\data\data_class/nor_discharge_1-10.xlsx', index=False)