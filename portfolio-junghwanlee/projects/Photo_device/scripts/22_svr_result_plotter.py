from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"


def main():
    result = pd.read_csv(
        DATA_PATH / "0206_Slice_1_Hyperparameter_SVR_FFT_Result_temp_to_WATER_IN_TEMP_data_-1.csv",
        index_col=0,
    )

    standard_scaler = StandardScaler()
    minmax_scaler = MinMaxScaler()

    standard_data = standard_scaler.fit_transform(result)
    minmax_data = minmax_scaler.fit_transform(result)

    scaled_df = pd.DataFrame(standard_data, columns=result.columns)
    minmax_df = pd.DataFrame(minmax_data, columns=result.columns)

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    ax.plot(result["y_true"], label="y_true")
    ax.plot(result["y_pred"], label="y_pred")
    ax.plot(result["X"], label="explain variable")
    ax.legend(fontsize=7)

    fig2, ax2 = plt.subplots(1, 1, figsize=(12, 10))
    ax2.plot(scaled_df["y_true"], label="standard_y_true")
    ax2.plot(scaled_df["y_pred"], label="standard_y_pred")
    ax2.plot(scaled_df["X"], label="standard_explain variable")
    ax2.legend(fontsize=7)

    fig3, ax3 = plt.subplots(1, 1, figsize=(12, 10))
    ax3.plot(minmax_df["y_true"], label="minmax_y_true")
    ax3.plot(minmax_df["y_pred"], label="minmax_y_pred")
    ax3.plot(minmax_df["X"], label="minmax_explain variable")
    ax3.legend(fontsize=7)

    residuals = result["y_true"] - result["y_pred"]

    plt.figure(figsize=(8, 4))
    plt.plot(residuals)
    plt.axhline(0, color="red", linestyle="--")
    plt.title("Residuals Plot")

    plt.show()


if __name__ == "__main__":
    main()
