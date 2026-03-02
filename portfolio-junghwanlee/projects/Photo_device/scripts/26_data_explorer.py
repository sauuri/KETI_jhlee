from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

COL_POWER = "Load_Total_Power_Consumption"


def main():
    Processing_data = pd.read_csv(DATA_PATH / "Processed_0206_data.csv", index_col=0, low_memory=False)
    Operating_data = pd.read_csv(DATA_PATH / "Operating_Filtered_0206_data.csv", low_memory=False)

    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.scatter(np.arange(len(Processing_data)), Processing_data[COL_POWER], label="consumption")
    ax.scatter(Operating_data["collect_time"], Operating_data[COL_POWER], label="Operating consumption")
    ax.legend()
    plt.show()

    consumption_diff = np.unique(Processing_data[COL_POWER].diff())
    print(consumption_diff)
    print(consumption_diff[consumption_diff > 0])


if __name__ == "__main__":
    main()
