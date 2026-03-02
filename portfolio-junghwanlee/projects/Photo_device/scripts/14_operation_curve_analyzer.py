from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

COL_POWER = 'Load_Total_Power_Consumption'
COL_TIME = 'collect_time'
DIFF_THRESHOLD = 10000


def detect_machine_operation(data, param, threshold=DIFF_THRESHOLD):
    """
    Detect machine operation start and end points.

    Parameters
    ----------
    data : DataFrame
    param : str
        Column name representing operating state.
    threshold : int
        Change detection threshold.

    Returns
    -------
    operation_start_points, operation_end_points : DataFrame, DataFrame
    """
    data_diff = data[param].diff()
    data_diff_index = data_diff.index

    nonzero_diff_index = data_diff_index[np.where(data_diff != 0)]

    start_condition = nonzero_diff_index.diff() > threshold
    operation_start_points = data.loc[
        data_diff[data_diff[nonzero_diff_index].index].loc[start_condition].index
    ]

    reversed_data = data[::-1]
    inverse_data_diff = reversed_data[param].diff()
    inverse_nonzero_diff_index = inverse_data_diff.loc[inverse_data_diff != 0].index
    inverse_nonzero_diff_values = inverse_data_diff.loc[inverse_data_diff != 0]

    end_condition = inverse_nonzero_diff_values[inverse_nonzero_diff_index.diff() < -threshold]
    operation_end_points = reversed_data.loc[end_condition.index]

    return operation_start_points, operation_end_points


def slice_operation_data(process_data, operation_start_points, operation_end_points, time_column):
    """Slice data between start and end operation points."""
    collected_operate_slices = []
    for i, j in zip(operation_start_points[time_column], operation_end_points[time_column][::-1]):
        i, j = map(int, (i, j))
        collected_operate_slices.append(process_data[i:j])
    return collected_operate_slices


def interpolate_operation_segments(process_data, collected_operate_slices, param):
    """Linear interpolate between start and end index of each operation segment."""
    interp_index = []
    interp_values = []

    for segment in collected_operate_slices:
        min_idx = min(segment.index)
        max_idx = max(segment.index)
        index_values = np.arange(min_idx, max_idx + 1)
        slice_values = np.interp(
            index_values,
            [min_idx, max_idx],
            [process_data[param][min_idx], process_data[param][max_idx]],
        )
        interp_index.append(index_values)
        interp_values.append(slice_values)

    print("Interpolation complete.")
    return interp_index, interp_values


def polynomial_quadratic_fit(collected_operate_slices, param, degree=2):
    y_pred_poly = []
    for segment in collected_operate_slices:
        min_idx = min(segment.index)
        max_idx = max(segment.index)
        index_values = np.arange(min_idx, max_idx + 1)
        coefficients = np.polyfit(index_values, segment[param].to_numpy(), degree)
        a, b, c = coefficients
        print(f"Fit: y = {a:.8f}x² + {b:.6f}x + {c:.4f}")
        y_pred_poly.append(np.polyval(coefficients, index_values))
    return y_pred_poly


def plot_experiment_results(
    process_data, operate_data, collected_operate_slices,
    param, interp_values, y_pred_poly, time_column
):
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.scatter(process_data[time_column], process_data[param], label='Total Data', alpha=0.9)
    ax.scatter(operate_data[time_column], operate_data[param], label='Operating Data', alpha=0.9)

    interp_colors = ["#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"]
    poly_colors = ["#5fd35f", "#ff5733", "#b388eb", "#c0896f", "#ff98e8", "#b5b5b5", "#f0e800"]

    for idx, segment in enumerate(collected_operate_slices):
        seg_idx = segment.index
        ax.scatter(seg_idx, interp_values[idx], color=interp_colors[idx], label='Interpolated', alpha=0.5)
        ax.scatter(seg_idx, y_pred_poly[idx], color=poly_colors[idx], label='Polynomial Fit', alpha=0.5)
        ax.axvline(x=min(seg_idx), color='red', linestyle='--', linewidth=0.5, alpha=0.3)
        ax.axvline(x=max(seg_idx), color='blue', linestyle='--', linewidth=0.5, alpha=0.3)

    ax.legend(loc='best')
    plt.show()


def calculate_r2_score(process_data, collected_operate_slices, param, interp_values, y_pred_poly):
    for idx, segment in enumerate(collected_operate_slices):
        min_idx = min(segment.index)
        max_idx = max(segment.index)
        actual = process_data[param][min_idx:max_idx + 1]
        r2_interp = r2_score(actual, interp_values[idx])
        r2_poly = r2_score(actual, y_pred_poly[idx])
        print(f"Slice {idx+1}: R²(Interp)={r2_interp:.6f}, R²(Poly)={r2_poly:.6f}")


def jhlee_curve_fit(process_data, collected_operate_slices, param, time_column=COL_TIME):
    """Quadratic curve fit through start and end points of each operation segment."""
    fig, ax = plt.subplots(1, 1, figsize=(18, 12))
    ax.scatter(process_data[time_column], process_data[param], label='Total Data', alpha=0.5)

    popt_box = []

    for idx, segment in enumerate(collected_operate_slices):
        min_idx = min(segment.index)
        max_idx = max(segment.index)

        xdata = segment[time_column].to_numpy()
        ydata = segment[param].to_numpy()

        x_1 = segment.loc[min_idx, time_column]
        y_1 = segment.loc[min_idx, param]
        x_2 = segment.loc[max_idx, time_column]
        y_2 = segment.loc[max_idx, param]

        def func(x, a):
            return a * (x - x_1) * (x - x_2) + y_1 + (y_2 - y_1) / (x_2 - x_1) * (x - x_1)

        denominator = (xdata - x_1) * (xdata - x_2)
        if np.any(denominator == 0):
            a_min = 0
        else:
            a_min = (4 * y_1 * y_2 - (y_1 + y_2) ** 2) / (4 * denominator)

        if np.isnan(a_min) or np.isinf(a_min):
            a_min = 0

        try:
            popt, _ = curve_fit(func, xdata, ydata, bounds=([max(0, a_min)], [np.inf]))
            popt_box.append(popt)
            ax.scatter(xdata, func(xdata, *popt), label=f"Fit {idx}")
            ax.axvline(x_1, color='red', linestyle='--', linewidth=0.5, alpha=0.3)
            ax.axvline(x_2, color='blue', linestyle='--', linewidth=0.5, alpha=0.3)
        except RuntimeError as e:
            print(f"Curve fitting failed for slice {idx}: {e}")

    plt.legend()
    plt.show()
    return popt_box


if __name__ == '__main__':
    Processing_data = pd.read_csv(DATA_PATH / "Processed_0206_data.csv", low_memory=False)
    Operating_data = pd.read_csv(DATA_PATH / "Operating_Filtered_0206_data.csv", low_memory=False)

    operation_start_points, operation_end_points = detect_machine_operation(
        Processing_data, param=COL_POWER, threshold=DIFF_THRESHOLD
    )
    collected_operate_slices = slice_operation_data(
        Processing_data, operation_start_points, operation_end_points, time_column=COL_TIME
    )
    interp_index, interp_values = interpolate_operation_segments(
        Processing_data, collected_operate_slices, COL_POWER
    )
    popt_box = jhlee_curve_fit(
        Processing_data, collected_operate_slices, param=COL_POWER, time_column=COL_TIME
    )
