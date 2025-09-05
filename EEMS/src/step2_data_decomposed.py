import logging
import pandas as pd
from pathlib import Path
from natsort import os_sorted
from datetime import datetime


# === Setup logging ===
log_dir = Path.cwd() / "preprocessing_logs"
log_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
log_file = log_dir / f"step2_device_motor_decomposition_log.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def read_parquet_file(file: Path) -> pd.DataFrame:
    return pd.read_parquet(file)


def load_and_group_by_motor(parquet_files: list[Path]) -> tuple[list[pd.DataFrame], list[pd.DataFrame]]:
    """
    Load parquet files and group them into inner/outer lists based on filename convention.

    Parameters
    ----------
    parquet_files: list[Path]
        List of input parquet file paths to load.
        Filenames must contain either 'inner' or 'outer'.

    Returns
    -------
    tuple[list[pd.DataFrame], list[pd.DataFrame]]
        A tuple of two lists:
        - First element: list of Dataframes from files containing 'inner'
        - Second element: list of Dataframes from files containing 'outer'

    Raises
    ------
    ValueError
        If a file name does not contain 'inner' or 'outer'.
    """
    inner_list, outer_list = [], []
    for pq_file in parquet_files:
        df = read_parquet_file(pq_file)
        logging.info(f"  Loaded: {pq_file.name}  -> rows: {len(df):,}")
        if "inner" in pq_file.name:
            inner_list.append(df)
        elif "outer" in pq_file.name:
            outer_list.append(df)
        else:
            raise ValueError(f"Unknown file type: {pq_file.name}")
    logging.info("")
    return inner_list, outer_list


# TODO(PC24-11, 2025-09-05 12:17): Edit the docstring for clarify


def split_motor_by_machine_code(df: pd.DataFrame, mapping: dict[str,str]) -> dict[str, pd.DataFrame]:
    """
    Split a DataFrame into multiple subsets based on 'machine_code' values.

    Parameters
    ----------
    df: pd.DataFrame
        Input DataFrame containing a 'machine_code' column.
    mapping: dict[str,str]
        Dictionary that maps motor names as keys to machine_code as values.
        Example: {"P1730A" : "FEMS11_01"} (keys=P1730A, values=FEMS11_01).

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary where each key is a motor name (from mapping) and each value
        is a DataFrame subset containing only rows with the corresponding machine_code.

    Examples
    --------
    # >>> mapping = {"P1730A" : "FEMS11_01"}
    # >>> result = split_motor_by_machine_code(df, mapping)
    # >>> list(result.keys())
    ['P1730A', 'P1730B']
    """
    return {map_name : df[df['machine_code'] == map_machine_code] for map_name, map_machine_code in mapping.items()}


def save_motor_data(df: pd.DataFrame, motor_name: str, output_dir: Path):
    """
    Save motor-specific DataFrame as a Parquet file with time-sorted rows.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing a 'collect_time' column.
    motor_name : str
        Motor name used for file naming (e.g., "P1730A").
    output_dir : Path
        Directory where the Parquet file will be saved.

    Returns
    -------
    None
        Saves a Parquet file and logs summary information (rows, time range, path).

    """
    df = df.copy()
    df['collect_time'] = pd.to_datetime(df['collect_time'], format='mixed')
    df_sorted = df.sort_values("collect_time").reset_index(drop=True)

    file_name_parquet = f"TORAY_{motor_name}_filtered_decomposed.parquet"
    # file_name_csv = f"TORAY_{motor_name}_filtered_decomposed.csv"

    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_output_dir = output_dir / file_name_parquet
    # csv_output_dir = output_dir / file_name_csv

    df_sorted.to_parquet(parquet_output_dir)
    # df_sorted.to_csv(csv_output_dir)

    start = df_sorted['collect_time'].iloc[0]
    end = df_sorted['collect_time'].iloc[-1]

    logging.info(f"[{motor_name}]")
    logging.info(f"   Rows:        {len(df_sorted):,}")
    logging.info(f"   Time range:  {start} ~ {end}")
    logging.info(f"   Parquet saved: {parquet_output_dir}")
    logging.info("   Success\n")


def main():
    base_filtered_dir = Path.cwd().parents[0] / "data" / "filtered" / "TORAY"
    base_output_dir = Path.cwd().parents[0] / "data" / "decomposed" / "TORAY"

    include_power = input("Do you want to include instantaneous power ('Load_Active_Power')? [y/n]: ")
    include_power = include_power.lower() == 'y'

    if include_power:
        input_dir = base_filtered_dir / "parquet_active_power"
        output_dir = base_output_dir / "parquet_active_power"
    else:
        input_dir = base_filtered_dir / "parquet"
        output_dir = base_output_dir / "parquet"

    parquet_files = os_sorted(input_dir.glob("*.parquet"))

    logging.info(f"[STEP2] TORAY Decomposition Log")
    logging.info(f"Started at: {datetime.now()}\n")
    logging.info(f"Total parquet files: {len(parquet_files)}\n")

    inner_df_list, outer_df_list = load_and_group_by_motor(parquet_files)

    inner_map = {"P1730A":"FEMS11_01", "P1730B":"FEMS11_02"}
    outer_map = {
        "P7412A_MCC": "FEMS11_01",
        "P7412B_MCC": "FEMS11_02",
        "P7412A_EXT": "FEMS12_01",
        "P7412B_EXT": "FEMS12_02",
    }

    inner_df = pd.concat(inner_df_list, ignore_index=True)
    outer_df = pd.concat(outer_df_list, ignore_index=True)

    inner_dict = split_motor_by_machine_code(inner_df, inner_map)
    outer_dict = split_motor_by_machine_code(outer_df, outer_map)

    motor_dict = {**inner_dict, **outer_dict}

    for name, df in motor_dict.items():
        save_motor_data(df, name, output_dir)

    logging.info(f"Finished at: {datetime.now()}\n")


if __name__ == "__main__":
    main()
