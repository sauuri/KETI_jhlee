from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

COL_POWER = 'Load_Total_Power_Consumption'
DIFF_THRESHOLD = 10000


def detect_operation_boundaries(processing_data, col, threshold):
    """Detect start and end indices of machine operation periods."""
    data_diff = processing_data[col].diff()
    data_diff_index = data_diff.index

    not_0_diff_index = data_diff_index[np.where(data_diff != 0)]
    not_0_diff = data_diff.loc[np.where(data_diff != 0)]

    mask = not_0_diff_index.diff() > threshold
    high_diff = processing_data.loc[data_diff[data_diff[not_0_diff_index].index].loc[mask].index]

    processing_data_inverse = processing_data[::-1]
    data_diff_inverse = processing_data_inverse[col].diff()
    not_0_diff_inverse = data_diff_inverse.loc[data_diff_inverse != 0]
    not_0_diff_index_inverse = data_diff_inverse.loc[data_diff_inverse != 0].index

    mask_inverse = not_0_diff_inverse[not_0_diff_index_inverse.diff() < -threshold]
    low_diff = processing_data_inverse.loc[mask_inverse.index]

    return high_diff, low_diff


def main():
    Processing_data = pd.read_csv(DATA_PATH / "Processed_0206_data.csv", low_memory=False)
    Operating_data = pd.read_csv(DATA_PATH / "Operating_Filtered_0206_data.csv", low_memory=False)

    high_diff, low_diff = detect_operation_boundaries(Processing_data, COL_POWER, DIFF_THRESHOLD)

    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.scatter(np.arange(len(Processing_data)), Processing_data[COL_POWER], label='consumption')
    ax.scatter(Operating_data['collect_time'], Operating_data[COL_POWER], label='Operating consumption')

    for i in range(len(high_diff['collect_time'])):
        ax.axvline(x=high_diff['collect_time'].iloc[i], color='red', linestyle='--', linewidth=2)
        ax.axvline(x=low_diff['collect_time'].iloc[i], color='blue', linestyle='--', linewidth=2)

    ax.legend()
    plt.show()

    for idx, (i, j) in enumerate(zip(high_diff['collect_time'], low_diff['collect_time'][::-1])):
        print(i, j)
        slice_data = Processing_data.loc[i:j]


if __name__ == "__main__":
    main()
