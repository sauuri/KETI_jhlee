from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft, fftfreq

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

TARGET_COLUMN = 'WATER_IN_TEMP'
TIME_COLUMN = 'data_index'
SLICE_NUM = 1


def calculate_fft(data: pd.DataFrame, time_col: str, target_col: str):
    """Compute FFT and return full spectrum results."""
    time_intervals = np.diff(data[time_col])
    f_s_avg = 1 / np.mean(time_intervals)

    fft_values = fft(data[target_col].values)
    freqs = fftfreq(len(data), 1 / f_s_avg)
    amplitudes = np.abs(fft_values) / len(data)

    positive_freqs = freqs[:len(freqs) // 2]
    positive_amplitudes = amplitudes[:len(amplitudes) // 2]

    return positive_freqs, positive_amplitudes, f_s_avg, fft_values, freqs, amplitudes


def main():
    file_path = DATA_PATH / "slice_data" / f"sliced_part_{SLICE_NUM}.csv"
    slice_df = pd.read_csv(file_path)
    time = range(len(slice_df))

    positive_freqs, positive_amplitudes, f_s_avg, fft_values, freqs, amplitudes = calculate_fft(
        slice_df, TIME_COLUMN, TARGET_COLUMN
    )

    n_total = len(positive_amplitudes)
    n_25 = n_total // 4
    n_50 = n_total // 2
    n_75 = (n_total * 3) // 4

    top_1_indices = np.argsort(positive_amplitudes)[-1:][::-1]
    top_5_indices = np.argsort(positive_amplitudes)[-5:][::-1]
    top_n_25_indices = np.argsort(positive_amplitudes)[-n_25:][::-1]
    top_n_50_indices = np.argsort(positive_amplitudes)[-n_50:][::-1]
    top_n_75_indices = np.argsort(positive_amplitudes)[-n_75:][::-1]
    top_n_100_indices = np.argsort(positive_amplitudes)[::-1]

    # Figure 1: Original signal + FFT
    fig1, ax1 = plt.subplots(1, 2, figsize=(14, 8))
    ax1[0].plot(time, slice_df[TARGET_COLUMN], c='orange', label='WATER_IN_TEMP')
    ax1[0].set_title(f"Original slice {SLICE_NUM}")
    ax1[0].set_ylim(20, 42)
    ax1[0].legend(fontsize=12)

    ax1[1].plot(positive_freqs, positive_amplitudes, marker='o', label="Frequency component")
    ax1[1].axvline(x=f_s_avg / 2, color='r', linestyle='--', label=f"Nyquist ({f_s_avg/2:.3f} Hz)")
    ax1[1].set_xlabel("Frequency (Hz)")
    ax1[1].set_ylabel("Amplitude")
    ax1[1].set_title(f"FFT - {f_s_avg:.3f} Hz sampling")
    ax1[1].legend(fontsize=12)

    # Figure 2: Top-N% frequency component comparison
    fig2, ax2 = plt.subplots(2, 3, figsize=(16, 10))

    for (ax, indices, title) in [
        (ax2[0, 0], top_1_indices, "Top 1"),
        (ax2[0, 1], top_5_indices, "Top 5"),
        (ax2[0, 2], top_n_25_indices, "Top 25%"),
        (ax2[1, 0], top_n_50_indices, "Top 50%"),
        (ax2[1, 1], top_n_75_indices, "Top 75%"),
        (ax2[1, 2], top_n_100_indices, "Top 100%"),
    ]:
        ax.plot(positive_freqs[indices], positive_amplitudes[indices], marker='o', label=f"{title} Components")
        ax.axvline(x=f_s_avg / 2, color='r', linestyle='--')
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Amplitude")
        ax.set_title(f"{title} Frequency Components")
        ax.legend(fontsize=10)
        ax.grid()

    # Figure 3: IFFT reconstruction
    inverse_signal = ifft(fft_values)
    fig3, ax3 = plt.subplots(2, 1, figsize=(16, 10))
    ax3[0].plot(time, slice_df[TARGET_COLUMN], c='orange', label='Original WATER_IN_TEMP')
    ax3[0].set_title(f"Original slice {SLICE_NUM}")
    ax3[0].set_xlabel("Time (s)")
    ax3[0].set_ylabel("Amplitude")
    ax3[0].legend()
    ax3[0].grid()

    ax3[1].plot(time, inverse_signal.real, label="Reconstructed Signal (IFFT)")
    ax3[1].set_title("Reconstructed Signal using IFFT")
    ax3[1].set_xlabel("Time (s)")
    ax3[1].set_ylabel("Amplitude")
    ax3[1].legend()
    ax3[1].grid()

    plt.tight_layout()
    plt.show()

    for i, (idx, val, freq) in enumerate(
        zip(top_n_100_indices, positive_amplitudes[top_n_100_indices], positive_freqs[top_n_100_indices]), 1
    ):
        print(f"Top {i}: Value={val:.6f}, index={idx}, frequency={freq:.6f}")


if __name__ == "__main__":
    main()
