from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

TARGET_COLUMN = 'WATER_IN_TEMP'
TIME_COLUMN = 'data_index'
NUM_SLICES = 7
TOP_N = 5


def calculate_fft(data: pd.DataFrame, time_col: str, target_col: str):
    """Compute FFT and return positive frequency components."""
    time_intervals = np.diff(data[time_col])
    f_s_avg = 1 / np.mean(time_intervals)

    fft_values = fft(data[target_col].values)
    freqs = fftfreq(len(data), 1 / f_s_avg)
    amplitudes = np.abs(fft_values) / len(data)

    positive_freqs = freqs[:len(freqs) // 2]
    positive_amplitudes = amplitudes[:len(amplitudes) // 2]

    return positive_freqs, positive_amplitudes, f_s_avg


def main():
    fig, axes = plt.subplots(NUM_SLICES, 2, figsize=(12, 16))

    for num in range(1, NUM_SLICES + 1):
        file_path = DATA_PATH / "slice_data" / f"sliced_part_{num}.csv"
        slice_df = pd.read_csv(file_path)
        time = range(len(slice_df))

        axes[num - 1, 0].plot(time, slice_df[TARGET_COLUMN], label='Coever WATER_IN_TEMP')
        axes[num - 1, 0].set_title(f"Slice {num} - Original")
        axes[num - 1, 0].set_ylim(20, 42)
        axes[num - 1, 0].legend(fontsize=7)

        positive_freqs, positive_amplitudes, f_s_avg = calculate_fft(slice_df, TIME_COLUMN, TARGET_COLUMN)

        axes[num - 1, 1].plot(positive_freqs, positive_amplitudes, marker='o', label="Frequency component")
        axes[num - 1, 1].axvline(
            x=f_s_avg / 2, color='r', linestyle='--',
            label=f"Nyquist ({f_s_avg/2:.3f} Hz)"
        )
        axes[num - 1, 1].set_xlabel("Frequency (Hz)")
        axes[num - 1, 1].set_ylabel("Amplitude")
        axes[num - 1, 1].set_title(f"FFT - {f_s_avg:.3f} Hz sampling")
        axes[num - 1, 1].legend(fontsize=7)

        top_indices = np.argsort(positive_amplitudes)[-TOP_N:][::-1]
        for i, (idx, val, freq) in enumerate(
            zip(top_indices, positive_amplitudes[top_indices], positive_freqs[top_indices]), 1
        ):
            print(f"Slice {num} Top {i}: Value={val:.4f}, index={idx}, frequency={freq:.6f}")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
