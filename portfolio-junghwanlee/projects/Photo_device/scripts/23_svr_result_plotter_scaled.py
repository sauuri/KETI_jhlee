from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"


def main():
    result = pd.read_csv(
        DATA_PATH / "0206_Slice_1_Hyperparameter_SVR_FFT_Result_temp_to_WATER_IN_TEMP_data_-1.csv",
        index_col=0,
    )

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.plot(result["y_true"], label="y_true (before fit)")
    ax.plot(result["y_pred"], label="y_pred (before fit)")
    ax.plot(result["X"], label="explain variable (before fit)")
    ax.legend(fontsize=7)

    plt.show()


if __name__ == "__main__":
    main()
