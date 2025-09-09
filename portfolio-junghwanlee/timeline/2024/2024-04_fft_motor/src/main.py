import pandas as pd
import matplotlib.pyplot as plt
import os
import csv

# 폴더 경로 설정
folder_path = rf'C:\Users\PC24-11\Desktop\KETI_jhlee\portfolio-junghwanlee\timeline\2024\2024-04_fft_motor\data'
# 폴더 내의 모든 파일과 폴더의 이름을 가져오기
files = os.listdir(folder_path)

# CSV 파일들의 이름만 가져오기
csv_files = [file for file in files if file.endswith('.csv')]

print(csv_files)

dataset = {}
for i in range(0, 30):
    dataset[i] = pd.read_csv(folder_path + '\\'+csv_files[i])

print(dataset[0]['Timestamp'], "전체 타임스탬프 길이", len(dataset[0]['Timestamp']))
print(dataset[0]['Timestamp'][:100])

# 데이터셋의 'Timestamp' 열의 처음 100개 값 가져오기
timestamps = dataset[0]['Timestamp'][:-1]

print(type(timestamps))
# 결과를 저장할 리스트 초기화

# 결측값 확인
# missing_values = timestamps.isnull().sum()
# print("missing_values", missing_values)

interpolated_values = []
total = 0
# 두 번째 값부터 마지막 값까지 처리
for i in range(0, len(timestamps)-1):
    # 이전 값에서 현재 값을 뺀 후 전체 갯수로 나누어 보간값 계산
    interpolated_value = (timestamps[i+1] - timestamps[i])
    interpolated_values.append(interpolated_value)
    total += interpolated_values[i]

interpolate_value = total/(len(interpolated_values))

# -------------------------------------------------------
#sa = 1874
#(dataset[0]).iloc[:1874,1:4].plot()
#(dataset[0]).iloc[sa:2*sa,1:4].plot()
#(dataset[0]).iloc[2*sa:3*sa,1:4].plot()
#(dataset[0]).iloc[::,1:4].plot()


num = 6

# 평균과 표준편차 계산
mean_x = dataset[num-1].iloc[::,1:2].mean()
mean_y = dataset[num-1].iloc[::,2:3].mean()
mean_z = dataset[num-1].iloc[::,3:4].mean()

std_dev_x = dataset[num-1].iloc[::,1:2].std()
std_dev_y = dataset[num-1].iloc[::,2:3].std()
std_dev_z = dataset[num-1].iloc[::,3:4].std()

# 각 변수에 대한 이상치 기준 설정 (평균 ± 3 표준편차)
normal_distribution = 3
lower_bound_x = mean_x - normal_distribution * std_dev_x
upper_bound_x = mean_x + normal_distribution * std_dev_x
lower_bound_y = mean_y - normal_distribution * std_dev_y
upper_bound_y = mean_y + normal_distribution * std_dev_y
lower_bound_z = mean_z - normal_distribution * std_dev_z
upper_bound_z = mean_z + normal_distribution * std_dev_z

# 이상치 제거
dataset_no_outliers_x = dataset[num-1].iloc[::,1:2][(dataset[num-1].iloc[::,1:2] >= lower_bound_x) & (dataset[num-1].iloc[::, 1:2] <= upper_bound_x)].dropna()
dataset_no_outliers_y = dataset[num-1].iloc[::,2:3][(dataset[num-1].iloc[::,2:3] >= lower_bound_y) & (dataset[num-1].iloc[::, 2:3] <= upper_bound_y)].dropna()
dataset_no_outliers_z = dataset[num-1].iloc[::,3:4][(dataset[num-1].iloc[::,3:4] >= lower_bound_z) & (dataset[num-1].iloc[::, 3:4] <= upper_bound_z)].dropna()


# 이상치를 제외한 데이터 그래프
# 그래프 크기 설정
plt.figure(figsize=(20, 15))

# X 축 그래프
plt.subplot(5, 1, 1)  # 5행 1열 중 첫 번째 위치
plt.plot(dataset_no_outliers_x.index, dataset_no_outliers_x, label='X axis', color='blue')
plt.legend()
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('X axis Data without Outliers')

# Y 축 그래프
plt.subplot(5, 1, 2)  # 5행 1열 중 두 번째 위치
plt.plot(dataset_no_outliers_y.index, dataset_no_outliers_y, label='Y axis', color='orange')
plt.legend()
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('Y axis Data without Outliers')

# Z 축 그래프
plt.subplot(5, 1, 3)  # 5행 1열 중 세 번째 위치
plt.plot(dataset_no_outliers_z.index, dataset_no_outliers_z, label='Z axis', color='green')
plt.legend()
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('Z axis Data without Outliers')


plt.subplot(5, 1, 4)  # 5행 1열 중 네 번째 위치
plt.plot(dataset_no_outliers_x.index, dataset_no_outliers_x, label='X axis')
plt.plot(dataset_no_outliers_y.index, dataset_no_outliers_y, label='Y axis')
plt.plot(dataset_no_outliers_z.index, dataset_no_outliers_z, label='Z axis')
plt.legend()
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('total axis Data without Outliers')


plt.subplot(5, 1, 5)  # 5행 1열 중 다섯 번째 위치
plt.plot((dataset[num+1]).iloc[::,1:2], label='X axis')
plt.plot((dataset[num+1]).iloc[::,2:3], label='Y axis')
plt.plot((dataset[num+1]).iloc[::,3:4], label='Z axis')
plt.legend()
plt.legend()
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('total axis original Data')


plt.figure(figsize=(20, 15))

plt.subplot(2, 1, 1)  # 5행 1열 중 네 번째 위치
plt.plot(dataset_no_outliers_x.index, dataset_no_outliers_x, label='X axis')
plt.plot(dataset_no_outliers_y.index, dataset_no_outliers_y, label='Y axis')
plt.plot(dataset_no_outliers_z.index, dataset_no_outliers_z, label='Z axis')
plt.legend()
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('total axis Data without Outliers')


plt.subplot(2, 1, 2)  # 5행 1열 중 다섯 번째 위치
plt.plot((dataset[num+1]).iloc[::,1:2], label='X axis')
plt.plot((dataset[num+1]).iloc[::,2:3], label='Y axis')
plt.plot((dataset[num+1]).iloc[::,3:4], label='Z axis')
plt.legend()
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('total axis original Data')

plt.tight_layout()  # 그래프 간격 조정
plt.show()

print("len(dataset[num+1].iloc[::,1:2]",len(dataset[num+1].iloc[::,1:2]))
print("len(dataset[num+1].iloc[::,2:3]",len(dataset[num+1].iloc[::,2:3]))
print("len(dataset[num+1].iloc[::,3:4]",len(dataset[num+1].iloc[::,3:4]))
print("len(dataset_no_outliers_x)",len(dataset_no_outliers_x))
print("len(dataset_no_outliers_y)",len(dataset_no_outliers_y))
print("len(dataset_no_outliers_z)",len(dataset_no_outliers_z))