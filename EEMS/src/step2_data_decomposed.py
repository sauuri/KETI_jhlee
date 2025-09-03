import pandas as pd
from pathlib import Path
from natsort import os_sorted
from datetime import datetime


def read_parquet_file(file: Path) -> pd.DataFrame:
    return pd.read_parquet(file)


def load_and_group_by_motor(parquet_files: list[Path]) -> tuple[list[pd.DataFrame], list[pd.DataFrame]]:
    inner_list, outer_list = [], []
    for pq_file in parquet_files:
        df = read_parquet_file(pq_file)
        print(f" Loaded: {pq_file.name}  -> rows: {len(df):,}")
        if "inner" in pq_file.name:
            inner_list.append(df)
        elif "outer" in pq_file.name:
            outer_list.append(df)
        else:
            raise ValueError(f"Unknown file type: {pq_file.name}")
    return inner_list, outer_list


def split_motor_by_machine_code(df: pd.DataFrame, mapping: dict[str,str]) -> dict[str, pd.DataFrame]:
    return {map_name : df[df['machine_code'] == map_machine_code] for map_name, map_machine_code in mapping.items()}


def save_motor_data(df: pd.DataFrame, motor_name: str, output_dir: Path):
    df = df.copy()
    df['collect_time'] = pd.to_datetime(df['collect_time'], format='mixed')
    df_sorted = df.sort_values("collect_time").reset_index(drop=True)

    file_name_parquet = f"TORAY_{motor_name}_filtered_decomposed.parquet"
    file_name_csv = f"TORAY_{motor_name}_filtered_decomposed.csv"


    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_output_dir = output_dir / file_name_parquet
    csv_output_dir = output_dir / file_name_csv

    df_sorted.to_parquet(parquet_output_dir)
    df_sorted.to_csv(csv_output_dir)

    start = df_sorted['collect_time'].iloc[0]
    end = df_sorted['collect_time'].iloc[-1]

    print(f"[{motor_name}]")
    print(f"  Rows:        {len(df_sorted):,}")
    print(f"  Time range:  {start} ~ {end}")
    print(f"  Parquet saved: {parquet_output_dir}")
    print("   Success\n")



def main():
    base_filtered_dir = Path.cwd().parents[1] / "data" / "filtered" / "TORAY"
    base_output_dir = Path.cwd().parents[1] / "data" / "decomposed" / "TORAY"

    include_power = input("Do you want to include instantaneous power ('Load_Active_Power')? [y/n]: ")
    include_power = include_power.lower() == 'y'

    if include_power:
        input_dir = base_filtered_dir / "parquet_active_power"
        output_dir = base_output_dir / "parquet_active_power"
    else:
        input_dir = base_filtered_dir / "parquet"
        output_dir = base_output_dir / "parquet"

    parquet_files = os_sorted(input_dir.glob("*.parquet"))

    print(f"[STEP2] TORAY Decomposition Log")
    print(f"Started at: {datetime.now()}\n")
    print(f"Total parquet files: {len(parquet_files)}\n")

    inner_df_list, outer_df_list = load_and_group_by_motor(parquet_files)

    inner_map = {"P1730A":"FEMS11_01", "P1730B":"FEMS11_02"}
    outer_map = {
        "P7412A_MCC":"FEMS11_01",
        "P7412B_MCC":"FEMS11_02",
        "P7412A_EXT":"FEMS12_01",
        "P7412B_EXT":"FEMS12_02",
    }

    inner_df = pd.concat(inner_df_list, ignore_index=True)
    outer_df = pd.concat(outer_df_list, ignore_index=True)

    inner_dict = split_motor_by_machine_code(inner_df, inner_map)
    outer_dict = split_motor_by_machine_code(outer_df, outer_map)

    motor_dict = {**inner_dict, **outer_dict}

    for name, df in motor_dict.items():
        save_motor_data(df, name, output_dir)


if __name__ == "__main__":
    main()
