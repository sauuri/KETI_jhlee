from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

COL_TIME = "collect_time"


def main():
    df = pd.read_csv(
        DATA_PATH / "Processed_Filtered_Final_0206_data_add_Instant_Power.csv",
        index_col=0,
        low_memory=False,
    )

    data = df[['temp', 'WATER_IN_TEMP']]

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    scaled_data = pd.DataFrame(scaled_data, columns=['temp', 'WATER_IN_TEMP'])

    fig1, ax1 = plt.subplots(1, 1, figsize=(12, 10))
    ax1.scatter(df[COL_TIME], scaled_data['temp'], label='scale raw data photo temp')
    ax1.scatter(df[COL_TIME], scaled_data['WATER_IN_TEMP'], label='scale raw data cover WATER_IN_TEMP')
    ax1.legend()

    fig2, ax2 = plt.subplots(1, 1, figsize=(12, 10))
    ax2.legend()

    plt.show()


if __name__ == "__main__":
    main()
