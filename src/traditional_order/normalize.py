import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# 指定包含 CSV 文件的文件夹
input_folder = '/data_seagate/zhaocs/data/hydroatlas/data_csv'

# 遍历文件夹中的所有文件
for filename in os.listdir(input_folder):
    # 检查文件是否是 CSV 文件
    if filename.endswith('.csv'):
        # 构建完整的文件路径
        file_path = os.path.join(input_folder, filename)

        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        #创建一个新的表
        new_df=df[['HYRIV_ID','MAIN_RIV','ENDORHEIC','DIST_DN_KM','DIST_UP_KM','slp_dg_cav','slp_dg_uav','sgr_dk_rav','run_mm_cyr']].copy()
        
        # 定义函数来计算河网密度
        #def calculate_network_density_length(row):
            #return row['LENGTH_KM'] / row['CATCH_SKM']
        
        #def calculate_network_density_area(row):
            #return row['ria_ha_csu'] / row['CATCH_SKM']
        
        #def calculate_network_density_allArea(row):
            #eturn row['ria_ha_usu'] / row['UPLAND_SKM']

        # 计算河网密度并添加到新的DataFrame 中
        new_df['network_density_length'] = df.loc[:,'LENGTH_KM']/df.loc[:,'CATCH_SKM']#df.apply(calculate_network_density_length, axis=1)
        new_df['network_density_area'] = df.loc[:,'ria_ha_csu']/df.loc[:,'CATCH_SKM']#df.apply(calculate_network_density_area, axis=1)
        new_df['network_density_allArea'] = df.loc[:,'ria_ha_usu']/df.loc[:,'UPLAND_SKM']#df.apply(calculate_network_density_allArea, axis=1)

        #定义要归一化的列
        normalized_columns=['DIST_DN_KM','DIST_UP_KM','slp_dg_cav','slp_dg_uav','sgr_dk_rav','run_mm_cyr','network_density_length','network_density_area','network_density_allArea']

        #创建归一化器
        scaler=MinMaxScaler()
        
        #循环归一化
        for group_name,group_data in new_df.groupby('MAIN_RIV'):
            group_normalized_data = scaler.fit_transform(group_data[normalized_columns].values)
            new_df.loc[group_data.index,normalized_columns] = group_normalized_data

        # 使用 'MAIN_RIV' 列对数据进行分组并归一化
        #scaler=MinMaxScaler()
        #grouped_rivers = df.groupby('MAIN_RIV')['network_density','DIST_DN_KM','run_mm_cyr'].transform(lambda x: scaler.fit_transform(x.values.reshape(-1,1)))

        #添加归一化数据到原始数据中
        #normalized_columns=['network_density_nor','DIST_DN_KM_nor','run_mm_cyr_nor']
        #df[normalized_columns]=grouped_rivers

        # 指定要保存的文件名（为原始文件名添加 '_normalized' 后缀）
        output_folder='/data_seagate/zhaocs/data/hydroatlas/data_nor_csv'
        output_filename = filename.rsplit('.', 1)[0] + '_normalized.csv'
        output_file_path = os.path.join(output_folder, output_filename)

        # 保存归一化后的数据到新的 CSV 文件
        new_df.to_csv(output_file_path,index=False)