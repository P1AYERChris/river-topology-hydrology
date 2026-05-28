import geopandas as gpd

# 读取原始 Shapefile
input_shapefile = 'E:/研究/河网与径流/河网分级拓扑学/data/hydro_river/HydroRIVERS_v10_as_shp/HydroRIVERS_v10_as.shp'
gdf = gpd.read_file(input_shapefile)


# 打印列名
print(gdf.columns)

# 检查特定列是否存在
required_columns = ['HYRIV_ID', 'NEXT_DOWN', 'ORD_STRA', 'HYBAS_L12']
missing_columns = [col for col in required_columns if col not in gdf.columns]

if missing_columns:
    print(f"缺少列: {missing_columns}")
else:
    print("所有列都存在。")
""" #将shp文件的id列、下游列、h-s分级列、pspf编码列提取到新的dataframe中
river_base_info = gdf[['HYRIV_ID', 'NEXT_DOWN', 'ORD_STRA', 'HYBAS_L12']].copy()

#查找每个河段的上游河段数量
max_upstream_count=0
for index, row in river_base_info.iterrows():
    # 获取当前河段的下游河段ID
    downstream_id = row['HYRIV_ID']
    # 计算下游河段ID出现的次数，即上游河段数量
    upstream_count = river_base_info['NEXT_DOWN'].eq(downstream_id).sum()
    # 更新最大上游河段数量
    if upstream_count > max_upstream_count:
        max_upstream_count = upstream_count

#创建列存储上游河段的id和h-s分级数据
for i in range(max_upstream_count):
    river_base_info.loc[:,f'UPSTREAM_ID_{i+1}'] = None
    river_base_info.loc[:,f'UPSTREAM_HS_{i+1}'] = None

#遍历每个河段，查找其上游河段并存储到新的列中
for index, row in river_base_info.iterrows():
    # 获取当前河段的下游河段ID
    downstream_id = row['HYRIV_ID']
    # 计算下游河段ID出现的次数，即上游河段数量
    upstream_count = river_base_info['NEXT_DOWN'].eq(downstream_id).sum()
    # 遍历每个上游河段
    for i in range(upstream_count):
        # 获取当前河段的上游河段ID
        upstream_id = river_base_info[river_base_info['NEXT_DOWN'] == downstream_id].iloc[i]['HYRIV_ID']
        # 将上游河段ID和h-s分级数据存储到新的列中   
        river_base_info.at[index, f'UPSTREAM_ID_{i+1}'] = upstream_id
        river_base_info.at[index, f'UPSTREAM_HS_{i+1}'] = river_base_info[river_base_info['HYRIV_ID'] == upstream_id].iloc[0]['ORD_STRA'] 

#将riverbaseinfo保存为csv
river_base_info.to_csv('E:/研究/河网与径流/河网分级拓扑学/data/hydro_river/HydroRIVERS_v10_as_shp/river_base_info.csv', index=False) """














