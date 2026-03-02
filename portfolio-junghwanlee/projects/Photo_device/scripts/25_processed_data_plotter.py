from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from scipy.signal import correlate

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

PHOTO_COLUMN = "temp"
COEVER_COLUMN = "WATER_IN_TEMP"


def apply_standard_scaler(X, Y, apply_scaling=True):
    if apply_scaling:
        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(X[[PHOTO_COLUMN]])
        y_scaled = scaler.fit_transform(Y[[COEVER_COLUMN]])
        return pd.DataFrame(x_scaled, columns=[PHOTO_COLUMN]), pd.DataFrame(y_scaled, columns=[COEVER_COLUMN])
    return X, Y


def cross_correlation_function(X, Y):
    n = len(X)
    x = np.ravel(X)
    y = np.ravel(Y)

    lags = np.arange(-n + 1, n)
    cross_corr = correlate(x - np.mean(x), y - np.mean(y), mode="full") / (np.std(x) * np.std(y) * n)

    best_lag = lags[np.argmax(cross_corr)]
    best_corr = np.max(cross_corr)

    print(f"Optimal lag: {best_lag}")
    print(f"Max Cross-Correlation: {best_corr:.6f}")

    series_delayed_y = np.roll(y, shift=best_lag)

    if best_lag > 0:
        series_delayed_y[:best_lag] = np.nan
    elif best_lag < 0:
        series_delayed_y[best_lag:] = np.nan

    return lags, cross_corr, best_lag, best_corr, series_delayed_y


if __name__ == "__main__":
    test_data_list = [1, 3, 5, 10, 25, 50, 100, 1000, 10000]

    base_ifft_path = DATA_PATH / "IFFT_result_data"
    selected = test_data_list[5]

    Photo_data = pd.read_csv(
        base_ifft_path / f"Denoising_FFT_result_{selected}_{PHOTO_COLUMN}.csv",
        index_col=0, low_memory=False,
    )
    Coever_data = pd.read_csv(
        base_ifft_path / f"Denoising_FFT_result_{selected}_{COEVER_COLUMN}.csv",
        index_col=0, low_memory=False,
    )

    X, Y = apply_standard_scaler(Photo_data, Coever_data, apply_scaling=False)

    lags, cross_corr, best_lag, best_corr, series_delayed_y = cross_correlation_function(X, Y)

    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.plot(X.to_numpy(), label="Photo", alpha=1)
    ax.plot(series_delayed_y, label="Shift Coever", alpha=1)
    ax.plot(Y.to_numpy(), label="Coever", alpha=0.7)
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.legend()

    plt.show()
