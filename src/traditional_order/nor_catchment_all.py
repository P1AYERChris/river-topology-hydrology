import pandas as pd

#读取xlsx文件
df=pd.read_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/mean_catchment_all.xlsx')

#进行归一化

df['Normalized_CATCHMENT'] = df.groupby('MAIN_RIV')['CATCH_SKM'].transform(lambda x: x / x.max())
# 保存结果到 xlsx 文件
df.to_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/nor_mean_catchment_all.xlsx', index=False)