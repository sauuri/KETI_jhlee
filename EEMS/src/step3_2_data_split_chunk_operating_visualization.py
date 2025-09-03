import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import time

plt.rcParams['font.family'] = 'Times New Roman'


def process_chunk_file(file: Path, motor_name: str, save_figure_dir: Path):
    """Process a single 24h chunk parquet file and save its plot."""
    plot_dir = save_figure_dir / motor_name / "24h" / "well plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(file)
    df['delta_power'] = df['Load_Total_Power_Consumption'].diff()

    fig, ax = plt.subplots(figsize=(15, 8))

    shifted_power = df["Load_Total_Power_Consumption"] - df["Load_Total_Power_Consumption"].min()
    ax.scatter(df["collect_time"], shifted_power, s=1, label='Shifted Power')

    total_diff = df['Load_Total_Power_Consumption'].iloc[-2] - df['Load_Total_Power_Consumption'].iloc[0]
    total_diff_rate = total_diff / 24  # 24시간 기준

    start_dt = df['collect_time'].iloc[0]
    end_dt = df['collect_time'].iloc[-2]
    fname = f"{start_dt.strftime('%Y-%m-%d_%H%M%S')}_to_{end_dt.strftime('%Y-%m-%d_%H%M%S')}"

    ax.set_title(f"{motor_name} | {fname}", fontsize=14)

    # 상승 구간 탐지
    highlight = df[df['delta_power'] > 1].index
    if not highlight.empty:
        start_idx, end_idx = highlight[0], highlight[-1]
        start_time_seg = df.loc[start_idx, 'collect_time']
        end_time_seg = df.loc[end_idx, 'collect_time']
        operating_duration = (end_time_seg - start_time_seg).total_seconds() / 3600
        operating_diff = df.loc[end_idx, 'Load_Total_Power_Consumption'] - df.loc[start_idx, 'Load_Total_Power_Consumption']
        operating_diff_rate = operating_diff / operating_duration if operating_duration > 0 else np.nan

        ax.scatter(
            df["collect_time"].iloc[highlight],
            shifted_power.iloc[highlight],
            color='orange',
            s=4,
            label='Significant Rise'
        )

        text_lines = [
            f"Total period: {start_dt.strftime('%Y-%m-%d %H:%M:%S')} → {end_dt.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total diff (24h): {total_diff:.2f} Wh",
            f"Total diff rate: {total_diff_rate:.2f} Wh/h",
            f"Operating period: {start_time_seg.strftime('%Y-%m-%d %H:%M:%S')} → {end_time_seg.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Operating duration: {operating_duration:.2f} hours",
            f"Operating diff: {operating_diff:.2f} Wh",
            f"Operating diff rate: {operating_diff_rate:.2f} Wh/h"
        ]

        text_x = df["collect_time"].iloc[int(len(df) * 0.01)]
        text_y = shifted_power.min() + 0.05 * shifted_power.max()

        ax.text(
            text_x,
            text_y,
            "\n".join(text_lines),
            fontsize=11,
            va='bottom',
            ha='left',
            bbox=dict(facecolor='white', edgecolor='gray', alpha=0.85)
        )

    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Load_Total_Power_Consumption (shifted)", fontsize=12)
    ax.tick_params(axis='both', labelsize=10)
    ax.grid(True)
    ax.legend(fontsize=10)

    plt.subplots_adjust(bottom=0.15)
    plt.tight_layout()

    plot_fname = f"{fname}.png"
    fig.savefig(plot_dir / plot_fname, dpi=600)
    plt.close(fig)

    print(f"Plot saved: {plot_dir / plot_fname}")


def process_motor_dir(motor_dir: Path, save_figure_dir: Path):
    """Process all 24h chunk files for a given motor."""
    chunk_dir = motor_dir / "24h"
    chunk_files = sorted(chunk_dir.rglob("*.parquet"))
    print(f"Processing motor: {motor_dir.name} → {len(chunk_files)} files")

    for file in chunk_files:
        process_chunk_file(file, motor_dir.name, save_figure_dir)


def main():

    start_time = time.time()
    run_timestamp = time.ctime(start_time).replace(' ', '_').replace(':', '-')

    base_folder = "Mon_Aug_11_13-43-22_2025"
    base_dir = Path.cwd().parents[1] / "data" / "chunked" / "TORAY_active_power"


    save_figure_dir = Path.cwd().parents[1] / "data" / "chunked" / "TORAY_active_power" / base_folder


    motor_dirs = sorted([p for p in base_dir.iterdir() if p.is_dir()])
    #motor_dirs = motor_dirs[:1]  # 첫 번째 모터만 처리 (필요 시 수정)

    start_time = time.time()
    for motor_dir in motor_dirs:
        process_motor_dir(motor_dir, save_figure_dir)

    elapsed = time.time() - start_time
    print(f"Total runtime: {elapsed:.2f} seconds ({elapsed / 60:.2f} minutes)")


if __name__ == "__main__":
    main()
