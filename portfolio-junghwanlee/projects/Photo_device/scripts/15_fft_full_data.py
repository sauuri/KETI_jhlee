from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"
FIGURE_PATH = BASE_PATH / "figures"

SLICE_ONE_NUM = 12542  # Single slice size for demonstration


def fft_calculation(slice_time: pd.Series, slice_data: pd.Series, data_columns: str, fft_data_num: int = 3):
    """Apply FFT, zero out all but top-N components, and reconstruct via IFFT."""
    time_length = len(slice_time)
    fft_applied = np.fft.fft(slice_data.to_numpy(), n=time_length)

    amplitudes = np.abs(fft_applied) * 2 / time_length
    sorted_indices = np.argsort(amplitudes)[::-1]

    fft_applied[sorted_indices[fft_data_num:]] = 0
    fft_smoothed = np.fft.ifft(fft_applied)

    _plot_fft_result(slice_time, slice_data, fft_smoothed, data_columns, fft_data_num)

    return pd.DataFrame(np.abs(fft_smoothed))


def _plot_fft_result(slice_time, slice_data, y_recovered_slice, data_columns, fft_data_num):
    fig, ax = plt.subplots(1, 2, figsize=(20, 8))
    ax[0].plot(np.arange(len(slice_time)), slice_data, c='orange', label=data_columns)
    ax[0].set_title(f"Original signal ({data_columns})")
    ax[0].legend()

    ax[1].plot(np.arange(len(y_recovered_slice)), y_recovered_slice.real, label="Recovered Signal (IFFT)")
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Amplitude")
    ax[1].set_title(f"IFFT using top {fft_data_num} components")
    ax[1].legend()

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    file_path = DATA_PATH / "Operating_Filtered_0206_data.csv"
    Operating_data = pd.read_csv(file_path)

    time_columns = 'collect_time'
    Photo_columns = 'temp'
    Coever_columns = 'WATER_IN_TEMP'

    slice_df = Operating_data[:SLICE_ONE_NUM]
    slice_time = slice_df[time_columns]
    slice_photo = slice_df[Photo_columns]
    slice_coever = slice_df[Coever_columns]

    test_data_list = [1, 3, 5, 10, 25, 50, 100, 1000, 10000]

    for fft_data_num in test_data_list:
        fft_calculation(slice_time, slice_photo, Photo_columns, fft_data_num)
        fft_calculation(slice_time, slice_coever, Coever_columns, fft_data_num)
