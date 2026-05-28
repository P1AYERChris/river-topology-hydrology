import pandas as pd

#读取xlsx文件
df=pd.read_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/class_runoff_1-7.xlsx')

#检查mainriv中数据最大值
max_values=df.groupby('MAIN_RIV')['P10_RUNOFF'].transform('max')
df=df.loc[max_values!=0]

#进行归一化
df['Normalized_MEAN_RUNOFF'] = df.groupby('MAIN_RIV')['MEAN_RUNOFF'].transform(lambda x: x / x.max())
df['Normalized_MEDIAN_RUNOFF'] = df.groupby('MAIN_RIV')['MEDIAN_RUNOFF'].transform(lambda x: x / x.max())
df['Normalized_P90_RUNOFF'] = df.groupby('MAIN_RIV')['P90_RUNOFF'].transform(lambda x: x / x.max())
df['Normalized_P10_RUNOFF'] = df.groupby('MAIN_RIV')['P10_RUNOFF'].transform(lambda x: x / x.max())

# 保存结果到 xlsx 文件
df.to_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/nor_class_runoff_1-7.xlsx', index=False)