import pandas as pd
import os

#定义csv文件夹路径
csv_folder='/data_seagate/zhaocs/data/hydroatlas/data_csv'

#读取所有文件
file_list=os.listdir(csv_folder)
csv_files=[file for file in file_list if file.endswith('.csv')]

# 创建一个空的 DataFrame 用于储存结果
result_df = pd.DataFrame()

for csv_file in csv_files:
    #读取csv文件
    csv_path=os.path.join(csv_folder,csv_file)

    # 读取文件
    df=pd.read_csv(csv_path)

    #根据 ordstra 分组并对 runoff 进行累加
    grouped = df.groupby(['MAIN_RIV','ORD_STRA']).agg({'LENGTH_KM':'mean'}).reset_index()

    #删除runoff为0或nan的行
    grouped=grouped[grouped['LENGTH_KM']!=0]
    grouped=grouped[grouped['LENGTH_KM'].notna()]

    # 将累加 runoff 添加到结果 DataFrame 中
    result_df = result_df.append(grouped, ignore_index=True)

# 将结果保存到 excel 文件
result_df.to_excel('/data_seagate/zhaocs/data/hydroatlas/data_class/mean_length_all.xlsx', index=False)