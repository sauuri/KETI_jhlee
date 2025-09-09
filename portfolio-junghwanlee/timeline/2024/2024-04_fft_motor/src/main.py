import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


# 폴더 경로 설정
folder_path = rf'C:\Users\PC24-11\Desktop\KETI_jhlee\portfolio-junghwanlee\timeline\2024\2024-04_fft_motor\data'
plot_save_path = rf'C:\Users\PC24-11\Desktop\KETI_jhlee\portfolio-junghwanlee\timeline\2024\2024-04_fft_motor\plots'
# 폴더 내의 모든 파일과 폴더의 이름을 가져오기
files = os.listdir(folder_path)

# CSV 파일들의 이름만 가져오기
csv_files = [file for file in files if file.endswith('.csv')]


def remove_outliers_normal_distribution(dataset, datanum, std_num):
    mean_x =    dataset[datanum-1].iloc[::,1:2].mean()
    mean_y =    dataset[datanum-1].iloc[::,2:3].mean()
    mean_z =    dataset[datanum-1].iloc[::,3:4].mean()
    std_dev_x = dataset[datanum-1].iloc[::,1:2].std()
    std_dev_y = dataset[datanum-1].iloc[::,2:3].std()
    std_dev_z = dataset[datanum-1].iloc[::,3:4].std()

    # 각 변수에 대한 이상치 기준 설정 (평균 ± 3 표준편차)
    normal_distribution = std_num
    lower_bound_x = mean_x - normal_distribution * std_dev_x
    upper_bound_x = mean_x + normal_distribution * std_dev_x
    lower_bound_y = mean_y - normal_distribution * std_dev_y
    upper_bound_y = mean_y + normal_distribution * std_dev_y
    lower_bound_z = mean_z - normal_distribution * std_dev_z
    upper_bound_z = mean_z + normal_distribution * std_dev_z

    # 이상치 제거
    dataset_no_outliers_x = dataset[datanum-1].iloc[::,1:2][(dataset[datanum-1].iloc[::,1:2] >= lower_bound_x) & (dataset[datanum-1].iloc[::, 1:2] <= upper_bound_x)].dropna()
    dataset_no_outliers_y = dataset[datanum-1].iloc[::,2:3][(dataset[datanum-1].iloc[::,2:3] >= lower_bound_y) & (dataset[datanum-1].iloc[::, 2:3] <= upper_bound_y)].dropna()
    dataset_no_outliers_z = dataset[datanum-1].iloc[::,3:4][(dataset[datanum-1].iloc[::,3:4] >= lower_bound_z) & (dataset[datanum-1].iloc[::, 3:4] <= upper_bound_z)].dropna()

    # 이상치를 제외한 데이터 그래프
    # 그래프 크기 설정
    fig1, axs1 = plt.subplots(5, 1, figsize=(20, 25))

    # X 축 그래프
    axs1[0].plot(dataset_no_outliers_x.index, dataset_no_outliers_x, label='X axis', color='blue')
    axs1[0].legend()
    axs1[0].set_xlabel('Index')
    axs1[0].set_ylabel('Value')
    axs1[0].set_title('X axis Data without Outliers')

    # Y 축 그래프
    axs1[1].plot(dataset_no_outliers_y.index, dataset_no_outliers_y, label='Y axis', color='orange')
    axs1[1].legend()
    axs1[1].set_xlabel('Index')
    axs1[1].set_ylabel('Value')
    axs1[1].set_title('Y axis Data without Outliers')

    # Z 축 그래프
    axs1[2].plot(dataset_no_outliers_z.index, dataset_no_outliers_z, label='Z axis', color='green')
    axs1[2].legend()
    axs1[2].set_xlabel('Index')
    axs1[2].set_ylabel('Value')
    axs1[2].set_title('Z axis Data without Outliers')

    # total axis 그래프
    axs1[3].plot(dataset_no_outliers_x.index, dataset_no_outliers_x, label='X axis')
    axs1[3].plot(dataset_no_outliers_y.index, dataset_no_outliers_y, label='Y axis')
    axs1[3].plot(dataset_no_outliers_z.index, dataset_no_outliers_z, label='Z axis')
    axs1[3].legend()
    axs1[3].set_xlabel('Index')
    axs1[3].set_ylabel('Value')
    axs1[3].set_title('Total axis Data without Outliers')

    # original data 그래프
    axs1[4].plot(dataset[datanum-1].iloc[:,1:2], label='X axis')
    axs1[4].plot(dataset[datanum-1].iloc[:,2:3], label='Y axis')
    axs1[4].plot(dataset[datanum-1].iloc[:,3:4], label='Z axis')
    axs1[4].legend()
    axs1[4].set_xlabel('Index')
    axs1[4].set_ylabel('Value')
    axs1[4].set_title('Total axis original Data')
    plt.tight_layout()  # 그래프 간격 조정

    # 그래프 크기 설정
    fig2, axs2 = plt.subplots(2, 1, figsize=(20, 15))

    # 이상치를 제외한 데이터 그래프
    axs2[0].plot(dataset_no_outliers_x.index, dataset_no_outliers_x, label='X axis')
    axs2[0].plot(dataset_no_outliers_y.index, dataset_no_outliers_y, label='Y axis')
    axs2[0].plot(dataset_no_outliers_z.index, dataset_no_outliers_z, label='Z axis')
    axs2[0].legend()
    axs2[0].set_xlabel('Index')
    axs2[0].set_ylabel('Value')
    axs2[0].set_title('Total axis Data without Outliers')

    # 원본 데이터 그래프
    axs2[1].plot(dataset[datanum-1].iloc[:,1:2], label='X axis')
    axs2[1].plot(dataset[datanum-1].iloc[:,2:3], label='Y axis')
    axs2[1].plot(dataset[datanum-1].iloc[:,3:4], label='Z axis')
    axs2[1].legend()
    axs2[1].set_xlabel('Index')
    axs2[1].set_ylabel('Value')
    axs2[1].set_title('Total axis original Data')
    plt.tight_layout()  # 그래프 간격 조정

    fig1.savefig(f"{plot_save_path}/outlier_removal_detailed.png")
    fig2.savefig(f"{plot_save_path}/outlier_removal_comparison.png")


#-----------------------------------------------------------------------------------

# fft 
# 시간 데이터 생성
def fft_plot_timestamp(dataset, datanum):
    # 데이터 보간
    interpolated_data_func_x = interp1d(dataset[datanum-1]["Timestamp"], dataset[datanum-1].iloc[::, 1:2], axis=0)
    interpolated_data_func_y = interp1d(dataset[datanum-1]["Timestamp"], dataset[datanum-1].iloc[::, 2:3], axis=0)
    interpolated_data_func_z = interp1d(dataset[datanum-1]["Timestamp"], dataset[datanum-1].iloc[::, 3:4], axis=0)
    interpolated_time = np.linspace(dataset[datanum-1]["Timestamp"].min(), 
                                    dataset[datanum-1]["Timestamp"].max(), 
                                num=dataset[datanum-1]["Timestamp"].shape[0])

    # 보간 함수를 사용하여 보간된 값을 얻음
    interpolated_data_x = interpolated_data_func_x(interpolated_time)
    interpolated_data_y = interpolated_data_func_y(interpolated_time)
    interpolated_data_z = interpolated_data_func_z(interpolated_time)

    # 주파수 계산
    frequency_x = np.fft.fft(interpolated_data_x, axis=0)
    frequency_y = np.fft.fft(interpolated_data_y, axis=0)
    frequency_z = np.fft.fft(interpolated_data_z, axis=0)

    frequency_abs_x = abs(frequency_x)
    frequency_abs_y = abs(frequency_y)
    frequency_abs_z = abs(frequency_z)

    # 시프트된 주파수 계산
    shifted_frequency_x = np.fft.fftshift(frequency_x)
    shifted_frequency_y = np.fft.fftshift(frequency_y)
    shifted_frequency_z = np.fft.fftshift(frequency_z)

    shifted_frequency_abs_x = abs(shifted_frequency_x)
    shifted_frequency_abs_y = abs(shifted_frequency_y)
    shifted_frequency_abs_z = abs(shifted_frequency_z)

    frequency_range = np.linspace(0, 1, frequency_abs_x.shape[0])
    sampling_rate = 1800
    real_frequency = frequency_range * sampling_rate / 2
    
    # 시프트된 주파수 도메인에서의 FFT 결과 그리기
    shifted_frequency_range = np.linspace(-1, 1, shifted_frequency_abs_x.shape[0])

    f_t2, a_t2 = plt.subplots(3, 3, figsize=(14, 25))

    # 시간 도메인에서의 데이터 그래프
    a_t2[0, 0].set_title("Time domain (X)")
    a_t2[0, 0].plot(interpolated_time, interpolated_data_x)
    a_t2[0, 1].set_title("Time domain (Y)")
    a_t2[0, 1].plot(interpolated_time, interpolated_data_y)
    a_t2[0, 2].set_title("Time domain (Z)")
    a_t2[0, 2].plot(interpolated_time, interpolated_data_z)

    # 주파수 도메인에서의 FFT 결과 그래프
    a_t2[1, 0].set_title("Frequency domain (Original X)")
    a_t2[1, 0].plot(real_frequency, frequency_abs_x)
    a_t2[1, 1].set_title("Frequency domain (Original Y)")
    a_t2[1, 1].plot(real_frequency, frequency_abs_y)
    a_t2[1, 2].set_title("Frequency domain (Original Z)")
    a_t2[1, 2].plot(real_frequency, frequency_abs_z)

    # 시프트된 주파수 도메인에서의 FFT 결과 그래프
    a_t2[2, 0].set_title("Frequency domain (Shifted X)")
    a_t2[2, 0].plot(shifted_frequency_range, shifted_frequency_abs_x)
    a_t2[2, 1].set_title("Frequency domain (Shifted Y)")
    a_t2[2, 1].plot(shifted_frequency_range, shifted_frequency_abs_y)
    a_t2[2, 2].set_title("Frequency domain (Shifted Z)")
    a_t2[2, 2].plot(shifted_frequency_range, shifted_frequency_abs_z)

    f_t2.savefig(f'{plot_save_path}/Time_Domain_Signal_Frequency_Domain_Spectrum.png')

def plt_fft_result_30_split_axis(dataset):
    
    total_frequency_abs_x = []
    total_frequency_abs_y = []
    total_frequency_abs_z = []
    total_frequency_range = []
    for df in dataset:
        # 데이터 보간
        interpolated_data_func_x = interp1d(df["Timestamp"], df.iloc[::, 1:2], axis=0)
        interpolated_data_func_y = interp1d(df["Timestamp"], df.iloc[::, 2:3], axis=0)
        interpolated_data_func_z = interp1d(df["Timestamp"], df.iloc[::, 3:4], axis=0)
        interpolated_time = np.linspace(df["Timestamp"].min(),
                                        df["Timestamp"].max(),
                                    num=df["Timestamp"].shape[0])

        # 보간 함수를 사용하여 보간된 값을 얻음
        interpolated_data_x = interpolated_data_func_x(interpolated_time)
        interpolated_data_y = interpolated_data_func_y(interpolated_time)
        interpolated_data_z = interpolated_data_func_z(interpolated_time)
        # 주파수 계산
        frequency_x = np.fft.fft(interpolated_data_x, axis=0)
        frequency_y = np.fft.fft(interpolated_data_y, axis=0)
        frequency_z = np.fft.fft(interpolated_data_z, axis=0)
        frequency_abs_x = abs(frequency_x)
        frequency_abs_y = abs(frequency_y)
        frequency_abs_z = abs(frequency_z)
        # 시프트된 주파수 계산
        shifted_frequency_x = np.fft.fftshift(frequency_x)
        shifted_frequency_y = np.fft.fftshift(frequency_y)
        shifted_frequency_z = np.fft.fftshift(frequency_z)

        shifted_frequency_abs_x = abs(shifted_frequency_x)
        shifted_frequency_abs_y = abs(shifted_frequency_y)
        shifted_frequency_abs_z = abs(shifted_frequency_z)

        frequency_range = np.linspace(0, 1, frequency_abs_x.shape[0])
        # 시프트된 주파수 도메인에서의 FFT 결과 그리기

        shifted_frequency_range = np.linspace(-0.5, 0.5, shifted_frequency_abs_x.shape[0])

        total_frequency_abs_x.append(frequency_abs_x)
        total_frequency_abs_y.append(frequency_abs_y)
        total_frequency_abs_z.append(frequency_abs_z)
        total_frequency_range.append(frequency_range)

    f_t_x, a_t_x = plt.subplots(6, 5, figsize=(14, 25))
    f_t_y, a_t_y = plt.subplots(6, 5, figsize=(14, 25))
    f_t_z, a_t_z = plt.subplots(6, 5, figsize=(14, 25))
    a_t_x[0, 0].set_title("Frequency domain (No Shifted X)")
    a_t_y[0, 0].set_title("Frequency domain (No Shifted Y)")
    a_t_z[0, 0].set_title("Frequency domain (No Shifted Z)")

    for i in range(0, 30):
        row = i // 5
        col = i % 5
        a_t_x[row, col].plot(total_frequency_range[i], total_frequency_abs_x[i])
        a_t_y[row, col].plot(total_frequency_range[i], total_frequency_abs_y[i])
        a_t_z[row, col].plot(total_frequency_range[i], total_frequency_abs_z[i])
        print(row, col)

    f_t_x.savefig(f"{plot_save_path}/fourier_transform_x_results.png")
    f_t_y.savefig(f"{plot_save_path}/fourier_transform_y_results.png")
    f_t_z.savefig(f"{plot_save_path}/fourier_transform_z_results.png")

if __name__ == '__main__':
    original_dataset = []
    for i in  range(0, len(csv_files)):
        csv_data = pd.read_csv(folder_path+'\\'+csv_files[i])
        original_dataset.append(csv_data)

    # 결측치를 제거한 데이터프레임을 저장할 리스트
    cleaned_dataset = []
    # original_dataset에 저장된 각 데이터프레임에서 결측치를 제거하여 cleaned_dataset에 추가
    for df in original_dataset:
        cleaned_df = df.dropna()  # 결측치가 있는 행 제거
        cleaned_dataset.append(cleaned_df)

    ## 딕셔너리를 pickle 파일로 저장
    with open(f'{folder_path}/dataset_list.pickle', 'wb') as f:
        pickle.dump(cleaned_dataset, f)


    # (a) 이상치 제거 + 전/후 비교 (첫 번째 사용 가능한 파일)
    _ = remove_outliers_normal_distribution(cleaned_dataset, datanum=1, std_num=3.0)

    fft_plot_timestamp(cleaned_dataset, datanum=1)

    # (c) 30개 일괄 FFT 비교
    plt_fft_result_30_split_axis(cleaned_dataset)

    # 최종 표시
    plt.show()
