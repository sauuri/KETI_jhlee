from pathlib import Path

import pandas as pd
import numpy as np

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

START_TIME = pd.to_datetime('2024-08-30 12:00:00 AM', format='%Y-%m-%d %I:%M:%S %p')
END_TIME = pd.to_datetime('2024-09-10 12:00:00 AM', format='%Y-%m-%d %I:%M:%S %p')

COLS_FINAL = ['Time', 'pres', 'temp', 'WATER_IN_TEMP', 'WATER_IN_PRESSURE', 'Load_Total_Power_Consumption']


def main():
    Photo_df = pd.read_csv(DATA_PATH / "Photo_data" / "Photo_df.csv", index_col=0, low_memory=False)
    Coever_df = pd.read_csv(DATA_PATH / "HN_data" / "HN_data_refined.csv", low_memory=False)

    Photo_df['Time'] = pd.to_datetime(Photo_df['Time'], format='%Y-%m-%d %I:%M:%S %p', errors='coerce')

    Coever_df['collect_time'] = pd.to_datetime(Coever_df['collect_time'])
    Coever_df['collect_time'] = Coever_df['collect_time'].dt.strftime('%Y-%m-%d %I:%M:%S %p')

    time_range = pd.date_range(start=START_TIME, end=END_TIME, freq='s')

    Photo_filtered = Photo_df[(Photo_df['Time'] >= START_TIME) & (Photo_df['Time'] <= END_TIME)]

    Coever_df['collect_time'] = pd.to_datetime(
        Coever_df['collect_time'], format='%Y-%m-%d %I:%M:%S %p', errors='coerce'
    )
    Coever_filtered = Coever_df[
        (Coever_df['collect_time'] >= START_TIME) & (Coever_df['collect_time'] <= END_TIME)
    ]

    Photo_filtered_unique = Photo_filtered.drop_duplicates(subset=['Time'])
    Coever_filtered_unique = Coever_filtered.drop_duplicates(subset=['collect_time'])

    set1_photo = set(Photo_filtered_unique['Time'])
    set1_coever = set(Coever_filtered_unique['collect_time'])
    set2 = set(time_range)

    missing_times_photo = list(set2 - set1_photo)
    missing_times_coever = list(set2 - set1_coever)

    new_rows_photo = pd.DataFrame({'Time': missing_times_photo})
    new_rows_coever = pd.DataFrame({'collect_time': missing_times_coever})

    Photo_df_with_missing = pd.concat([Photo_filtered, new_rows_photo], axis=0)
    Coever_df_with_missing = pd.concat([Coever_filtered, new_rows_coever], axis=0)

    Photo_df_with_missing = Photo_df_with_missing.sort_values(by='Time').reset_index(drop=True)
    Coever_df_with_missing = Coever_df_with_missing.sort_values(by='collect_time').reset_index(drop=True)

    Photo_df_with_missing = Photo_df_with_missing.drop_duplicates(subset=['Time'])
    Coever_df_with_missing = Coever_df_with_missing.drop_duplicates(subset=['collect_time'])

    Photo_df_with_missing = Photo_df_with_missing.interpolate(method='linear')
    Coever_df_with_missing = Coever_df_with_missing.interpolate(method='linear')

    Photo_df_with_missing['Time'] = pd.to_datetime(
        Photo_df_with_missing['Time'], format='%Y-%m-%d %I:%M:%S %p', errors='coerce'
    )
    Coever_df_with_missing['collect_time'] = pd.to_datetime(
        Coever_df_with_missing['collect_time'], format='%Y-%m-%d %I:%M:%S %p', errors='coerce'
    )

    Coever_df_with_missing.rename(columns={'collect_time': 'Time'}, inplace=True)

    merged_final_df = pd.merge(Photo_df_with_missing, Coever_df_with_missing, how='inner', on='Time')
    merged_df = merged_final_df.sort_values(by='Time').reset_index(drop=True)

    data = merged_df[COLS_FINAL]
    return data


if __name__ == "__main__":
    data = main()
    print(data)
