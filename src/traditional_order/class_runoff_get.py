import pandas as pd
import os

#定义csv文件夹路径
csv_folder='/data_seagate/zhaocs/data/hydroatlas/data_csv'

#读取所有文件
file_list=os.listdir(csv_folder)
csv_files=[file for file in file_list if file.endswith('.csv')]
df_b = pd.read_csv('/data_seagate/zhaocs/data/hydroatlas/data_class/classified_river.csv')

# 创建一个空的 DataFrame 用于储存结果
result_df = pd.DataFrame()

for csv_file in csv_files:
    #读取csv文件
    csv_path=os.path.join(csv_folder,csv_file)

    # 读取文件a
    df_a=pd.read_csv(csv_path)

    # 遍历 B 中的每个 mainriv 值
    for main_riv_b in df_b['MAIN_RIV'].unique():

        # 选择 A 中 mainriv 列值与当前 mainriv_b 值相同的行
        rows_a = df_a[df_a['MAIN_RIV'] == main_riv_b]
        
        #定义lambda函数
        p90_runoff=lambda x:x.quantile(0.9)
        p10_runoff=lambda x:x.quantile(0.1)

        # 根据 ordstra 分组并对 runoff 进行运算
        grouped = rows_a.groupby('ORD_STRA')['run_mm_cyr'].agg(['mean','median',p90_runoff,p10_runoff]).reset_index()
        grouped.columns=['ORD_STRA','MEAN_RUNOFF','MEDIAN_RUNOFF','P90_RUNOFF','P10_RUNOFF']
        # 遍历分组结果，将每个 ordstra 对应的runoff 添加到结果 DataFrame 中
        for index, row in grouped.iterrows():
            result_df = result_df.append({'MAIN_RIV': main_riv_b, 'ORD_STRA': row['ORD_STRA'], 'MEAN_RUNOFF': row['MEAN_RUNOFF'],'MEDIAN_RUNOFF':row['MEDIAN_RUNOFF'],'P90_RUNOFF':\
                                          row['P90_RUNOFF'],'P10_RUNOFF':row['P10_RUNOFF']}, ignore_index=True)

# 将结果保存到 CSV 文件
result_df.to_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/class_runoff.xlsx', index=False)