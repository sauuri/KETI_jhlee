from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

plt.rcParams['font.family'] = 'Times New Roman'

'''
(P_current + P_next) / 2 * Δt_hours is the trapezoidal integration formula
to convert instantaneous power data into interval energy consumption (Wh).

For more details, please refer to https://en.wikipedia.org/wiki/Trapezoidal_rule
'''

def get_motor_name(stem: str) -> str:
    """Extract motor name from file stem."""
    exception_filenames = ['P1730A', 'P1730B']
    parts = stem.split("_")
    if any(exc in stem for exc in exception_filenames):
        return '_'.join(parts[:2])
    return '_'.join(parts[:3])


def process_file(pq_file: Path, output_dir: Path, full_hours: set, include_power: bool) -> tuple[list, list]:
    """Process a single parquet file and return missing_info, saved_info."""
    missing_info = []
    saved_info = []

    print(f"Processing file: {pq_file.name}")
    df = pd.read_parquet(pq_file)
    df['collect_time'] = pd.to_datetime(df['collect_time'], format='mixed', errors='coerce').dt.round('S')
    df = df.sort_values('collect_time').reset_index(drop=True)
    df['date'] = df['collect_time'].dt.date

    motor_name = get_motor_name(pq_file.stem)

    parquet_dir = output_dir / motor_name / "24h" / "parquets"
    plot_dir = output_dir / motor_name / "24h" / "plots"
    parquet_dir.mkdir(parents=True, exist_ok=True)
    plot_dir.mkdir(parents=True, exist_ok=True)

    SECONDS_PER_HOUR = 3600

    for date, group in df.groupby('date'):
        group = group.copy() # protect against SettingWithCopy
        group_hours = set(group['collect_time'].dt.hour.unique())
        missing = sorted(full_hours - group_hours)

        # Calculate time difference (unit: hours)
        group['time_diff_hours'] = group['collect_time'].diff().dt.total_seconds() / SECONDS_PER_HOUR

        if include_power:
            # Calculate total power energy consumption (Wh) for each time interval from instantaneous active power data

            # Average power (trapezoidal rule, unit: W)
            group['avg_power'] = (group['Load_Active_Power'] + group['Load_Active_Power'].shift(1)) / 2

            # Interval consumption (W * hours = Wh)
            group['interval_consumption'] = group['avg_power'] * group['time_diff_hours']

            target_column = 'calc_load_total_power_consumption'

            # Cumulative energy consumption (unit: Wh)
            group[target_column] = group['interval_consumption'].cumsum()
            target = group[target_column]  # Wh

        else:
            target_column = 'Load_Total_Power_Consumption'
            target = group['Load_Total_Power_Consumption']  # Wh (original data)

        # Total consumption difference (unit: Wh)
        total_diff = target.iloc[-1] - target.iloc[1]

        reasons = []
        if (group['time_diff_hours'][1:] >= 1).any(): # gap >= 1 hour
            reasons.append('over_1h_gap')
        if missing:
            reasons.append('missing_hour')
        if target.mean() < 1e-6:    # Check if mean value is nearly zero (unit: Wh) 0.000001 Wh
            reasons.append('almost_zero_mean')

        MINIMUM_ENERGY_THRESHOLD = 1000  # Wh threshold
        if abs(total_diff) < MINIMUM_ENERGY_THRESHOLD:
            reasons.append(f'total_consumption_under_{MINIMUM_ENERGY_THRESHOLD}Wh')

        if reasons:
            missing_info.append({
                'motor': motor_name,
                'date': date,
                'missing_reason': ';'.join(reasons),
                'missing_hours': missing if missing else None,
            })
            print(f" {date} -> Skip saving, reasons: {reasons}")
            continue

        # Compute delta_t (hours) and average diff rate (Wh/h)

        start_dt = group['collect_time'].min()
        end_dt = group['collect_time'].max()

        delta_t = (end_dt - start_dt).total_seconds() / 3600.0
        diff_rate = total_diff / delta_t if delta_t > 0 else np.nan

        fname = f"{start_dt.strftime('%Y-%m-%d_%H%M%S')}_to_{end_dt.strftime('%Y-%m-%d_%H%M%S')}"

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.scatter(group['collect_time'], target - target.min(), s=3)
        ax.set_title(
            f"{motor_name} | {start_dt.strftime('%Y-%m-%d %H:%M:%S')} ~ {end_dt.strftime('%Y-%m-%d %H:%M:%S')}",
            fontsize=12
        )
        ax.set_xlabel("Time")
        ax.set_ylabel(f"adjusetd {target_column}")
        ax.grid(True)

        ax2 = ax.twinx()
        ax2.plot(group['collect_time'], target.diff(), color='red', label='Derivative', alpha=0.3, zorder=0)
        ax2.set_ylabel("Derivative", color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        group.to_parquet(parquet_dir / f"{fname}.parquet", index=False)
        print(f" Saved: {parquet_dir / f'{fname}.parquet'}")

        # Summarize saved info
        # Note: 'first_value'/'last_value' base on chosen target series
        saved_info.append({
            'motor': motor_name,
            'date': str(date),
            'total_diff_Wh': total_diff,
            'diff_rate_Wh_per_h': float(diff_rate) if np.isfinite(diff_rate) else None,
            'delta_t_hours': float(delta_t),
            'first_value_Wh': float(target.iloc[0]),
            'last_value_Wh': float(target.iloc[-1]),
            'start': start_dt,
            'end': end_dt
        })

        plot_fname = f"{fname}.png"
        fig.savefig(plot_dir / plot_fname, dpi=600)
        plt.close(fig)
        print(f"Plot: {plot_dir / plot_fname}")

    return missing_info, saved_info

def find_step_changes(data, min_step_size=1000, min_duration=30):
    """
    Detect step-like changes in power consumption data.

    Parameters
    ----------
    data : pandas.Series
        Power consumption data.
    min_step_size : int, optional
        Minimum step size to detect (Wh).
    min_duration : int, optional
        Minimum duration of a stable segment (number of points).

    Returns
    -------
    list of dict
        A list of detected segments, where each segment dictionary contains:
        - 'start_idx' : int, start index of the segment
        - 'end_idx'   : int, end index of the segment
        - 'start_time': timestamp of the first point
        - 'end_time'  : timestamp of the last point
        - 'level'     : baseline power level of the segment
        - 'duration'  : segment length in number of points
        - 'type'      : segment type (e.g., 'stable')
    """
    segments = []

    if len(data) == 0:
        return segments

    current_level = data.iloc[0]
    segment_start_idx = 0
    segment_start_time = data.index[0]

    for i in range(1, len(data)):
        current_value = data.iloc[i]

        # 현재 레벨과 큰 차이가 나면 새 구간으로 판단
        # If there is a significant difference from the current level,
        # consider it as the start of a new segment
        if abs(current_value - current_level) > min_step_size:
            # If the previous segment is long enough, save it
            # 이전 구간이 충분히 길면 저장
            duration = i - segment_start_idx
            if duration > min_duration:
                segments.append({
                    'start_idx': segment_start_idx,
                    'end_idx': i - 1,
                    'start_time': segment_start_time,
                    'end_time': data.index[i - 1],
                    'level': current_level,
                    'duration': duration,
                    'type': 'stable'
                })

            segment_start_idx = i
            segment_start_time = data.index[i]
            current_level = current_value

    final_duration = len(data) - segment_start_idx
    if final_duration > min_duration:
        segments.append({
            'start_idx': segment_start_idx,
            'end_idx': len(data) - 1,
            'start_time': segment_start_time,
            'end_time': data.index[-1],
            'level': current_level,
            'duration': final_duration,
            'type': 'stable'
        })

    return segments # list of segment dictionaries with start/end info


def main():
    start_time = time.time()
    run_timestamp = time.ctime(start_time).replace(' ', '_').replace(':', '-')

    base_dir = Path.cwd().parents[1] / "data" / "decomposed" / "TORAY"
    base_output_dir = Path.cwd().parents[1] / "data" / "chunked"

    while True:
        include_power: str = input("Do you want to include instantaneous power ('Load_Active_Power')? [y/n]: ")
        if include_power.lower() == 'y':
            input_dir = base_dir / "parquet_active_power"
            output_dir = base_output_dir / "TORAY_active_power" / run_timestamp
            break
        elif include_power.lower() == 'n':
            input_dir = base_dir / "TORAY"
            output_dir = base_output_dir / "TORAY" / run_timestamp
            break
        else:
            print("Please enter 'y' or 'n'.")

    parquet_files = sorted(input_dir.glob("*.parquet"))

    select_parquet_files = False
    if select_parquet_files:

        target_files = []
        for file in parquet_files:
            if 'P7412A_MCC' in str(file):
                print(f"Found: {file}")
                target_files.append(file)

        parquet_files = target_files
        print(parquet_files)

    full_hours = set(range(24))

    all_missing_info = []
    all_saved_info = []
    for pq_file in parquet_files:
        missing_info, saved_info = process_file(pq_file, output_dir, full_hours, include_power)
        all_missing_info.extend(missing_info)
        all_saved_info.extend(saved_info)

    if all_missing_info:
        df_missing = pd.DataFrame(all_missing_info)
        df_missing.to_csv(output_dir / "missing_24h_summary.csv", index=False)
        print(f"❗ Missing summary saved: {output_dir / 'missing_24h_summary.csv'}")

    if all_saved_info:
        df_saved = pd.DataFrame(all_saved_info)
        df_saved.to_csv(output_dir / "saved_24h_summary.csv", index=False)
        print(f"Saved summary saved: {output_dir / 'saved_24h_summary.csv'}")

    elapsed = time.time() - start_time
    print(f"Total runtime: {elapsed:.2f} seconds ({elapsed / 60:.2f} minutes)")


if __name__ == "__main__":
    main()
