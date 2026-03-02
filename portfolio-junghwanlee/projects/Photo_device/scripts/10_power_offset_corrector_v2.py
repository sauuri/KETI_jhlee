from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

COL_POWER = "Load_Total_Power_Consumption"


def apply_offset_correction(data, col):
    consumption = data[col].copy()
    original_consumption = consumption.copy()
    instant_consumption = consumption.diff().to_numpy()
    indexer_infeasible = np.argwhere(instant_consumption < 0).ravel()

    offset = instant_consumption[indexer_infeasible].cumsum()
    consumption = consumption.to_numpy()

    for (i, replace_index, next_index) in zip(
        range(len(offset)), indexer_infeasible, np.roll(indexer_infeasible, -1)
    ):
        instant_consumption[replace_index] = instant_consumption[replace_index - 1]
        consumption[replace_index] += np.abs(offset[i])
        reference_index = replace_index + 1

        if reference_index < next_index:
            for j in range(next_index - reference_index):
                consumption[reference_index + j] += np.abs(offset[i])
        if next_index == indexer_infeasible[0]:
            if reference_index < original_consumption.index[-1]:
                for j in range(original_consumption.index[-1] - reference_index):
                    consumption[reference_index + j] += np.abs(offset[i])

    return original_consumption, consumption


def main():
    input_path = DATA_PATH / "HN_data" / "HN.csv"
    output_path = DATA_PATH / "HN_data" / "HN_consumption.csv"

    data = pd.read_csv(input_path, index_col=0, low_memory=False)

    original_consumption, consumption = apply_offset_correction(data, COL_POWER)

    data[COL_POWER] = pd.DataFrame(consumption)

    n = len(data)
    fig, ax = plt.subplots(2, 1, figsize=(18, 12))

    ax[0].plot(np.arange(n), original_consumption, label='RAW original consumption')
    ax[0].plot(np.arange(n), consumption, label='Offset process consumption')
    ax[0].set_xlim(0, n - 1)
    ax[0].set_ylim(original_consumption.min(), original_consumption.max())
    ax[0].legend()

    ax[1].plot(np.arange(n), original_consumption, label='RAW original consumption')
    ax[1].plot(np.arange(n), consumption, label='Offset process consumption')
    ax[1].set_xlim(1.343e6, 1.343e6 + 500)
    ax[1].set_ylim(9.67225e6, 9.67800e6)
    ax[1].legend()

    fig2, ax2 = plt.subplots(1, 1, figsize=(18, 12))
    diff = consumption - original_consumption
    ax2.scatter(np.arange(n), diff, label='Offset-RAWconsumption')
    ax2.set_xlim(0, n - 1)
    ax2.set_ylim(diff.min(), diff.max())
    ax2.legend()

    plt.tight_layout()
    plt.show()

    data.to_csv(output_path)


if __name__ == "__main__":
    main()
