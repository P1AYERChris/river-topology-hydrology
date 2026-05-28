import geopandas as gpd
import pandas as pd
import os

'''#打开shp文件，将HYRIV_ID和HYBAS_L12提取出来 保存为csv
# Step 1: 读取 SHP 文件
shp_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\河流\HydroRIVERS_v10_shp\HydroRIVERS_v10.shp"  # 替换为你的 SHP 文件路径
shp_data = gpd.read_file(shp_file)
# 提取需要的列
shp_data = shp_data[["HYRIV_ID", "HYBAS_L12"]]
# 保存为 CSV 文件
output_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\河流_base_info.csv"
shp_data.to_csv(output_file, index=False)'''
'''# Step 1: 读取 Excel 文件
excel_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\river_base_info.csv"  # 替换为你的 Excel 文件路径
excel_data = pd.read_csv(excel_file)
excel_data = excel_data[["HYRIV_ID", "HYBAS_L12"]]  # 只保留需要的列

# Step 2: 初始化结果 DataFrame
result_df = excel_data.copy()  # 保留 Excel 的结构

# Step 3: 读取文件夹中的全部shp文件
shp_folder = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\河网"  # 替换为你的 SHP 文件夹路径
shp_files = [os.path.join(shp_folder, f) for f in os.listdir(shp_folder) if f.endswith('.shp')]

# 合并所有 SHP 文件
shp_data = pd.concat([gpd.read_file(shp)[["HYRIV_ID", "MAIN_RIV"]] for shp in shp_files])

# 删除重复的 HYRIV_ID，保留第一个出现的 MAIN_RIV 值
shp_data = shp_data.drop_duplicates(subset="HYRIV_ID")

# Step 3: 合并 Excel 数据和 SHP 数据
result_df = pd.merge(excel_data, shp_data, on="HYRIV_ID", how="left")

# Step 4: 保存结果到新的 Excel 文件
output_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\合并结果.csv"
result_df.to_csv(output_file, index=False)
print(f"数据已成功保存到 {output_file}")'''
'''#打开生成的csv文件
excel_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\合并结果.csv"  # 替换为你的 Excel 文件路径
excel_data = pd.read_csv(excel_file)
#对于每个MAIN_RIV,只保留出现的第一个
excel_data = excel_data.drop_duplicates(subset="MAIN_RIV", keep='first')
#保存生成的新文件
output_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\合并结果_去重.csv"
excel_data.to_csv(output_file, index=False)'''
'''#打开生成的csv文件
excel_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\合并结果_去重.csv"  # 替换为你的 Excel 文件路径
excel_data = pd.read_csv(excel_file)
# Step 2: 初始化结果 DataFrame
result_df = excel_data.copy()  # 保留 Excel 的结构
#读取文件夹中的全部shp文件
shp_folder = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\流域\12级"  # 替换为你的 SHP 文件夹路径
shp_files = [os.path.join(shp_folder, f) for f in os.listdir(shp_folder) if f.endswith('.shp')]
# 合并所有 SHP 文件
shp_data = pd.concat([gpd.read_file(shp)[["HYBAS_ID", "PFAF_ID"]] for shp in shp_files])
#对于所有PFAF_ID，只保留前三位
shp_data["PFAF_ID_3"] = shp_data["PFAF_ID"].astype(str).str[:3]
shp_data["PFAF_ID_4"] = shp_data["PFAF_ID"].astype(str).str[:4]
# Step 3: 合并 csv 数据和 SHP 数据,根据csv中的HYBAS_L12和shp中的HYBAS_ID进行合并
result_df = pd.merge(result_df, shp_data, left_on="HYBAS_L12", right_on="HYBAS_ID", how="left")

# Step 4: 保存结果到新的 Excel 文件
output_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\合并流域河流.csv"
result_df.to_csv(output_file, index=False)'''
'''#打开生成的csv文件
excel_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\合并流域河流.csv"  # 替换为你的 Excel 文件路径
excel_data = pd.read_csv(excel_file)
# Step 2: 初始化结果 DataFrame
result_df = excel_data.copy()  # 保留 Excel 的结构
#打开另一个excel文件
excel_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_relation\大-小尺度比值.xlsx"  # 替换为你的 Excel 文件路径
excel_data2 = pd.read_excel(excel_file)
#两者根据MAIN_RIV进行合并，将PFAF_ID添加到excel_data2中
result_df = pd.merge(excel_data2, result_df, on="MAIN_RIV", how="left")
#保存结果到新的 Excel 文件
output_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_relation\大-小尺度比值_带流域.xlsx"
result_df.to_excel(output_file, index=False)'''
#打开生成的excel文件
excel_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_relation\大-小尺度比值_带流域.xlsx"  # 替换为你的 Excel 文件路径
excel_data = pd.read_excel(excel_file)
#打开文件夹中的所有shp文件
shp_folder = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\流域\4级"  # 替换为你的 SHP 文件夹路径
shp_files = [os.path.join(shp_folder, f) for f in os.listdir(shp_folder) if f.endswith('.shp')]
# 合并所有 SHP 文件
shp_data = pd.concat([gpd.read_file(shp) for shp in shp_files], ignore_index=True)
# 确保合并后的数据仍然是 GeoDataFrame
shp_data = gpd.GeoDataFrame(shp_data, geometry=shp_data.geometry)

# 遍历 Excel 数据的每一行
for index, row in excel_data.iterrows():
    # 检查“判断列”的值是否为 0
    if row["判断列"] == 0:
        # 获取 PFAF_ID_3 列的值
        pfaf_id_3 = str(row["PFAF_ID_3"])[:3]  # 取前三位
        
        # 在 SHP 数据中匹配 PFAF_ID 的前三位
        shp_data.loc[
            shp_data["PFAF_ID"].astype(str).str.startswith(pfaf_id_3), 
            ["q", "in_run_mean","out_run_mean","all_run_mean"]  # 替换为 Excel 中需要合并的列
        ] = row[["q", "in_run_mean","out_run_mean","all_run_mean"]].values  # 替换为具体列名
    
    elif row["判断列"] == 1:
        # 获取 PFAF_ID_4 列的值
        pfaf_id_4 = str(row["PFAF_ID_4"])[:4]  # 取前四位
        
        # 在 SHP 数据中匹配 PFAF_ID 的前四位
        matched_rows = shp_data[shp_data["PFAF_ID"].astype(str).str.startswith(pfaf_id_4)]
        
        # 在 SHP 数据中匹配 PFAF_ID 的前四位
        shp_data.loc[
            shp_data["PFAF_ID"].astype(str).str.startswith(pfaf_id_4), 
            ["q", "in_run_mean","out_run_mean","all_run_mean"]  # 替换为 Excel 中需要合并的列
        ] = row[["q", "in_run_mean","out_run_mean","all_run_mean"]].values  # 替换为具体列名
# Step 4: 保存结果到新的 SHP 文件
output_file = r"E:\研究\河网与径流\河网分级拓扑学\data\data_shp\流域\amtls.shp"  # 替换为输出文件路径
shp_data.to_file(output_file, driver='ESRI Shapefile', encoding='utf-8')
print(f"合并完成！结果已保存到 {output_file}")
