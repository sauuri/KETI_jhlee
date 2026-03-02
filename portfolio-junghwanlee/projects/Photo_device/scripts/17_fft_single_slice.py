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


def calculate_fft(data: pd.DataFrame, time_col: str, target_col: str, n_fft: int):
    """Compute FFT with specified number of points."""
    time_intervals = np.diff(data[time_col])
    f_s_avg = 1 / np.mean(time_intervals)

    fft_values = fft(data[target_col].values, n=n_fft)
    freqs = fftfreq(n_fft, d=1 / f_s_avg)
    amplitudes = np.abs(fft_values) * 2 / n_fft

    positive_freqs = freqs[:n_fft // 2]
    positive_amplitudes = amplitudes[:n_fft // 2]

    return positive_freqs, positive_amplitudes, f_s_avg, fft_values, freqs, amplitudes


def main():
    file_path = DATA_PATH / "slice_data" / f"sliced_part_{SLICE_NUM}.csv"
    slice_df = pd.read_csv(file_path)
    time = range(len(slice_df))

    positive_freqs, positive_amplitudes, f_s_avg, fft_values, freqs, amplitudes = calculate_fft(
        slice_df, TIME_COLUMN, TARGET_COLUMN, len(time)
    )
    y_recovered = ifft(fft_values)

    # Figure 1: 4-panel FFT analysis
    fig, axes = plt.subplots(1, 4, figsize=(30, 8))

    axes[0].plot(time, slice_df[TARGET_COLUMN], c='orange', label='WATER_IN_TEMP')
    axes[0].set_title(f"Original slice {SLICE_NUM}")
    axes[0].legend(fontsize=12)

    axes[1].plot(positive_freqs, positive_amplitudes, marker='o', label="Frequency component")
    axes[1].axvline(x=f_s_avg / 2, color='r', linestyle='--', label=f"Nyquist ({f_s_avg/2:.3f} Hz)")
    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("Amplitude")
    axes[1].set_title(f"FFT - {f_s_avg:.3f} Hz")
    axes[1].legend(fontsize=12)

    axes[2].plot(freqs, amplitudes, marker='o', label="Full spectrum")
    axes[2].axvline(x=f_s_avg / 2, color='r', linestyle='--', label=f"Nyquist ({f_s_avg/2:.3f} Hz)")
    axes[2].set_xlabel("Frequency (Hz)")
    axes[2].set_ylabel("Amplitude")
    axes[2].set_title(f"Full FFT - {f_s_avg:.3f} Hz")
    axes[2].legend(fontsize=12)

    axes[3].plot(np.arange(len(y_recovered)), y_recovered.real, label="Recovered (IFFT)")
    axes[3].set_xlabel("Time (s)")
    axes[3].set_ylabel("Amplitude")
    axes[3].set_title("IFFT Reconstruction")
    axes[3].legend()

    plt.tight_layout()

    # Figure 2: filtered IFFT
    fft_values_filtered = fft_values.copy()
    fft_values_filtered[np.abs(freqs) > 0.01] = 0
    y_recovered_filtered = ifft(fft_values_filtered)

    fig2, axes2 = plt.subplots(1, 5, figsize=(30, 8))

    axes2[0].plot(time, slice_df[TARGET_COLUMN], c='orange', label='WATER_IN_TEMP')
    axes2[0].set_title(f"Original slice {SLICE_NUM}")
    axes2[0].legend(fontsize=12)

    axes2[1].plot(positive_freqs, positive_amplitudes, marker='o', label="Positive freqs")
    axes2[1].axvline(x=f_s_avg / 2, color='r', label=f"Nyquist ({f_s_avg/2:.3f} Hz)")
    axes2[1].set_xlabel("Frequency (Hz)")
    axes2[1].set_ylabel("Amplitude")
    axes2[1].set_title(f"FFT - {f_s_avg:.3f} Hz")
    axes2[1].legend(fontsize=12)

    axes2[2].plot(freqs, amplitudes, marker='o', label="Full spectrum")
    axes2[2].axvline(x=f_s_avg / 2, color='r', label=f"Nyquist ({f_s_avg/2:.3f} Hz)")
    axes2[2].set_xlabel("Frequency (Hz)")
    axes2[2].set_ylabel("Amplitude")
    axes2[2].set_title(f"Full FFT - {f_s_avg:.3f} Hz")
    axes2[2].legend(fontsize=12)

    axes2[3].plot(freqs, amplitudes, marker='o', label="Full spectrum")
    axes2[3].axvline(x=f_s_avg / 2, color='r', label=f"Nyquist ({f_s_avg/2:.3f} Hz)")
    axes2[3].set_xlabel("Frequency (Hz)")
    axes2[3].set_ylabel("Amplitude")
    axes2[3].legend(fontsize=12)

    axes2[4].plot(np.arange(len(y_recovered_filtered)), y_recovered_filtered.real, label="Filtered IFFT (>0.01 Hz removed)")
    axes2[4].set_xlabel("Time (s)")
    axes2[4].set_ylabel("Amplitude")
    axes2[4].set_title("Filtered IFFT")
    axes2[4].legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
