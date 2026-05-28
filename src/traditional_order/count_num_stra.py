import pandas as pd
import os

#定义csv文件夹路径
csv_folder='/data_seagate/zhaocs/data/hydroatlas/data_csv'

#读取所有文件
file_list=os.listdir(csv_folder)
csv_files=[file for file in file_list if file.endswith('.csv')]

#初始化计数器
count=0

#初始化字典
river_segement_counts={}
count1=0
count2=0
count3=0
count4=0
count5=0
count6=0
count7=0
count8=0
count9=0

for csv_file in csv_files:
    #读取csv文件
    csv_path=os.path.join(csv_folder,csv_file)
    df=pd.read_csv(csv_path)
    for _,group in df.groupby('MAIN_RIV'):
        #检查流域分级是否包含1-7
        if set(range(1,8)).issubset(set(group['ORD_STRA'])):
            count+=1
            #统计符合条件的河流的河段数量
            river_segement_counts[group['MAIN_RIV'].iloc[0]]=len(group)

#保存为新的csv
#river_segement_counts_df=pd.DataFrame(river_segement_counts.items(),columns=['MAIN_RIV','segement_counts'])
#river_segement_counts_df.to_csv('/data_seagate/zhaocs/data/hydroatlas/data_class/classified_river.csv',index=False)

print('符合条件的河网数量：',count)
#print('河流的河段数量:')

for river ,a in river_segement_counts.items():
    river=str(river)
    if river[0]=='1':
        count1+=1
    if river[0]=='2':
        count2+=1
    if river[0]=='3':
        count3+=1
    if river[0]=='4':
        count4+=1
    if river[0]=='5':
        count5+=1
    if river[0]=='6':
        count6+=1
    if river[0]=='7':
        count7+=1
    if river[0]=='8':
        count8+=1
    if river[0]=='9':
        count9+=1
print(count1,count2,count3,count4,count5,count6,count7,count8,count9)
