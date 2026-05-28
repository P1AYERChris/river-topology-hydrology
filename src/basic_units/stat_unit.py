import h5py
import numpy as np

# 将 'your_file.mat' 替换为你的 MATLAB 文件路径
file_path = r'E:\研究\河网与径流\河网分级拓扑学\data\data_河网单元\river_units_ratio.mat'

# 打开文件
with h5py.File(file_path, 'r') as f:
    # 列出文件中的所有组
    print("Keys: %s" % f.keys())
    
    # 访问数据集
    dataset_name = list(f.keys())[0]  # 替换为你想要访问的数据集名称
    data = f[dataset_name][:]
    
    # 打印数据
    print(data)
