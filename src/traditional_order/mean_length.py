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
    # 读取文件
    
    csv_path=os.path.join(csv_folder,csv_file)
    df_a=pd.read_csv(csv_path)

    merged_df=df_a.merge(df_a,left_on='NEXT_DOWN',right_on='HYRIV_ID',suffixes=('_left','_right'))
    condition=merged_df['ORD_STRA_left']!=merged_df['ORD_STRA_right']
    rows_b=merged_df.loc[condition,df_a.columns+'_left']
    rows_b.columns=df_a.columns
    rows_b = pd.concat([rows_b,df_a[df_a['NEXT_DOWN'] == 0]],ignore_index=True)

    # 遍历 B 中的每个 mainriv 值
    for main_riv_b in df_b['MAIN_RIV'].unique():

        # 选择 A 中 mainriv 列值与当前 mainriv_b 值相同的行；数量统计用rowsb
        rows_a = rows_b[rows_b['MAIN_RIV'] == main_riv_b]

        #分组统计
        grouped = rows_a.groupby('ORD_STRA').agg({'dis_m3_pyr':'mean'}).reset_index()

        #删除runoff为0或nan的行 
        grouped=grouped[grouped['dis_m3_pyr']!=0]
        grouped=grouped[grouped['dis_m3_pyr'].notna()]

        # 遍历分组结果，将每个 ordstra 对应的累加 runoff 添加到结果 DataFrame 中
        for index, row in grouped.iterrows():
            result_df = result_df.append({'MAIN_RIV': main_riv_b, 'ORD_STRA': row['ORD_STRA'],'DISCHARGE':row['dis_m3_pyr']}, ignore_index=True)

# 将结果保存到 CSV 文件
result_df.to_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/mean_discharge.xlsx', index=False)