import pandas as pd
import numpy as np
from pathlib import Path
from natsort import os_sorted
from datetime import datetime

def read_csv_file(file: Path) -> pd.DataFrame:
    return pd.read_csv(file)


def filter_and_convert(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df_filtered = df[cols].copy()
    for col in df_filtered.select_dtypes(include=['float64', 'int64']).columns:
        df_filtered[col] = df_filtered[col].astype(np.float32)
    return df_filtered


def make_output_filename(file: Path) -> str:
    parts = file.stem.split('_')
    return f"{parts[0].upper()}_{parts[1]}_{parts[3]}_filtered.parquet"


def save_parquet(df_filtered: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df_filtered.to_parquet(path)


def print_summary(df_filtered: pd.DataFrame, csv_path: Path, parquet_path: Path):
    raw_file_size = csv_path.stat().st_size / 1e6
    parquet_file_size = parquet_path.stat().st_size / 1e6
    reduction_ratio = 100 * (1 - parquet_file_size / raw_file_size)

    start_time = df_filtered['collect_time'].iloc[0]
    end_time = df_filtered['collect_time'].iloc[-1]

    print(f"{'Start time:':<25} {start_time}")
    print(f"{'End time:':<25} {end_time}")
    print(f"{'Disk file size (CSV):':<25} {raw_file_size:.3f} MB")
    print(f"{'Disk file size (Parquet):':<25} {parquet_file_size:.3f} MB")
    print(f"{'Disk space reduction:':<25} {reduction_ratio:.1f}%\n")


def run_step1_main():
    csv_dir = Path.cwd().parents[1] / "data" / "original"
    base_output_dir = Path.cwd().parents[1] / "data" / "filtered" / "TORAY"
    csv_files = os_sorted(list(csv_dir.glob("*.csv")))

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    include_power = input("Do you want to include instantaneous power ('Load_Active_Power')? [y/n]: ")
    include_power = include_power.lower() == 'y'


    if include_power:
        output_dir = base_output_dir / "parquet_active_power" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = base_output_dir / "parquet" / timestamp

    for idx, csv_file in enumerate(csv_files):
        print(f"[{idx + 1}] Processing file: {csv_file.name}")
        df = read_csv_file(csv_file)
        cols_to_inspect = [
            'collect_time',
            'machine_code',
            'Load_Total_Power_Consumption',
        ]
        if include_power:
            if 'Load_Active_Power' in df.columns:
                cols_to_inspect.append('Load_Active_Power')
            else:
                print(f"{csv_file.name} does not contain 'Load_Active_Power'. Skipping.")
                continue

        df_filtered = filter_and_convert(df, cols_to_inspect)

        out_filename = make_output_filename(csv_file)
        out_path = output_dir / out_filename

        save_parquet(df_filtered, out_path)
        print_summary(df_filtered, csv_file, out_path)


if __name__ == "__main__":
    run_step1_main()
