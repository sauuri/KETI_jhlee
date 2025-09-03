import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import time

plt.rcParams['font.family'] = 'Times New Roman'

'''
(P_current + P_next) / 2 * Δt_hours는 순간 전력 데이터를
시간 구간별 소비 전력량(Wh)으로 변환하는 사다리꼴 적분 공식임.
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
        group_hours = set(group['collect_time'].dt.hour.unique())
        missing = sorted(full_hours - group_hours)

        # 시간 간격 계산 (단위: hours)
        group['time_diff_hours'] = group['collect_time'].diff().dt.total_seconds() / SECONDS_PER_HOUR

        if include_power:
            # Calculate total power energy consumption (Wh) for each time interval from instantaneous active power data

            # 평균 전력 계산 (사다리꼴 공식, 단위: W)
            group['avg_power'] = (group['Load_Active_Power'] + group['Load_Active_Power'].shift(1)) / 2

            # 구간별 전력량 계산 (단위: W * hours = Wh)
            group['interval_consumption'] = group['avg_power'] * group['time_diff_hours']

            target_column = 'calc_load_total_power_consumption'

            # 누적 전력량 계산 (단위: Wh)
            group[target_column] = group['interval_consumption'].cumsum()
            target = group[target_column]  # 단위: Wh

        else:
            target_column = 'Load_Total_Power_Consumption'
            target = group['Load_Total_Power_Consumption']  # 단위: Wh (원본 데이터)

        # 총 전력 소비량 차이 (단위: Wh)
        total_diff = target.iloc[-1] - target.iloc[1]

        reasons = []
        if (group['time_diff_hours'][1:] >= 1).any(): # 1 = 1시간
            reasons.append('over_1h_gap')
        if missing:
            reasons.append('missing_hour')

        # 평균값이 거의 0에 가까운지 체크 (단위: Wh)
        if target.mean() < 1e-6:    # 0.000001 Wh
            reasons.append('almost_zero_mean')

        MINIMUM_ENERGY_THRESHOLD = 1000  # Wh 기준
        if abs(total_diff) < MINIMUM_ENERGY_THRESHOLD:
            reasons.append(f'total_consumption_under_{MINIMUM_ENERGY_THRESHOLD}Wh')

        if reasons:
            missing_info.append({
                'motor': motor_name,
                'date': date,
                'missing_reason': ';'.join(reasons),
                'missing_hours': missing if missing else None,
            })
            print(f" {date} → Skip saving, reasons: {reasons}")
            continue

        highlight = target[target.diff() > 1].index

        # if not highlight.empty:
        #     start_idx, end_idx = highlight[0], highlight[-1]
        #     start_time_seg = df.loc[start_idx, 'collect_time']
        #     end_time_seg = df.loc[end_idx, 'collect_time']
        #     operating_duration = (end_time_seg - start_time_seg).total_seconds() / 3600
        #     operating_diff = df.loc[end_idx, 'Load_Total_Power_Consumption'] - df.loc[
        #         start_idx, 'Load_Total_Power_Consumption']
        #     operating_diff_rate = operating_diff / operating_duration if operating_duration > 0 else np.nan


        start_dt = group['collect_time'].min()
        end_dt = group['collect_time'].max()
        fname = f"{start_dt.strftime('%Y-%m-%d_%H%M%S')}_to_{end_dt.strftime('%Y-%m-%d_%H%M%S')}"


        # 시각화 저장 (주석 해제 시 활성화)
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.scatter(group['collect_time'], target - target.min(), s=3)
        ax.set_title(
            f"{motor_name} | {start_dt.strftime('%Y-%m-%d %H:%M:%S')} ~ {end_dt.strftime('%Y-%m-%d %H:%M:%S')}",
            fontsize=12
        )
        ax.set_xlabel("Time")
        ax.set_ylabel(f"adjusetd {target_column}")
        ax.grid(True)

        # 두 번째 y축 (오른쪽) 생성
        ax2 = ax.twinx()
        ax2.plot(group['collect_time'], target.diff(), color='red', label='Derivative', alpha=0.3, zorder=0)
        ax2.set_ylabel("Derivative", color='red')
        ax2.tick_params(axis='y', labelcolor='red')


        # TODO(PC24-11, 2025-08-14 11:59): [span 시각화]










        # text_lines = [
        #     f"Total period: {start_dt.strftime('%Y-%m-%d %H:%M:%S')} → {end_dt.strftime('%Y-%m-%d %H:%M:%S')}",
        #     f"Total diff (24h): {total_diff:.2f} Wh",
        #     f"Total diff rate: {total_diff_rate:.2f} Wh/h",
        #     f"Operating period: {start_time_seg.strftime('%Y-%m-%d %H:%M:%S')} → {end_time_seg.strftime('%Y-%m-%d %H:%M:%S')}",
        #     f"Operating duration: {operating_duration:.2f} hours",
        #     f"Operating diff: {operating_diff:.2f} Wh",
        #     f"Operating diff rate: {operating_diff_rate:.2f} Wh/h"
        # ]
        #
        # text_x = df["collect_time"].iloc[int(len(df) * 0.01)]
        # text_y = shifted_power.min() + 0.05 * shifted_power.max()

        # ax.text(
        #     text_x,
        #     text_y,
        #     "\n".join(text_lines),
        #     fontsize=11,
        #     va='bottom',
        #     ha='left',
        #     bbox=dict(facecolor='white', edgecolor='gray', alpha=0.85)
        # )

        # Parquet 저장 (주석 해제 시 활성화)
        group.to_parquet(parquet_dir / f"{fname}.parquet", index=False)
        print(f" Saved: {parquet_dir / f'{fname}.parquet'}")

        # saved_info.append({
        #     'motor': motor_name,
        #     'date': date,
        #     'diff': total_diff,
        #     'diff_rate': avg_wh_per_hour,
        #     'first_value': group['Load_Total_Power_Consumption'].iloc[0],
        #     'last_value': group['Load_Total_Power_Consumption'].iloc[-2],
        #     'delta_t': delta_t,
        # })

        plot_fname = f"{fname}.png"
        fig.savefig(plot_dir / plot_fname, dpi=600)
        plt.close(fig)
        print(f"Plot: {plot_dir / plot_fname}")

    return missing_info, saved_info

def find_step_changes(data, min_step_size=1000, min_duration=30):
    """
    계단식 변화 구간 찾기

    Parameters:
    - data: pandas Series (전력 소비량 데이터)
    - min_step_size: 최소 변화량 (Wh)
    - min_duration: 최소 지속 시간 (데이터 포인트 수)

    Returns:
    - segments: 구간 정보 리스트
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
        if abs(current_value - current_level) > min_step_size:
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

            # 새 구간 시작
            segment_start_idx = i
            segment_start_time = data.index[i]
            current_level = current_value

    # 마지막 구간 처리
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

    return segments


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
