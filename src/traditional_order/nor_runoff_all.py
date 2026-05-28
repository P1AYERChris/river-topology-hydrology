import pandas as pd

#读取xlsx文件
df=pd.read_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/accumulated_runoff_all.xlsx')

#进行归一化

df['Normalized_Accumulated_RUNOFF'] = df.groupby('MAIN_RIV')['Accumulated_RUNOFF'].transform(lambda x: x / x.max())
df['Normalized_RUNOFF'] = df.groupby('MAIN_RIV')['RUNOFF'].transform(lambda x: x / x.max())
# 保存结果到 xlsx 文件
df.to_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/nor_accumulated_runoff_all.xlsx', index=False)