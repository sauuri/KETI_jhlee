from pathlib import Path
import sys

import numpy as np
import pandas as pd

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

COLS_TO_INSPECT = [
    "collect_time",
    "Load_Total_Power_Consumption",
    "WATER_IN_TEMP",
    "WATER_IN_PRESSURE",
]


def main():
    data_coever = pd.read_csv(
        DATA_PATH / "HN_data" / "HN_consumption.csv",
        header=0,
        index_col=0,
        keep_default_na=True,
        low_memory=False,
    ).fillna(0)

    data_photo = pd.read_csv(
        DATA_PATH / "HN_data" / "HN_consumption.csv",
        header=0,
        index_col=0,
        keep_default_na=True,
        low_memory=False,
    ).fillna(0)

    for col in data_photo.columns:
        if col == "collect_time":
            data_photo[col] = pd.to_datetime(data_photo[col], format="mixed")
        else:
            data_photo[col] = pd.to_numeric(data_photo[col], errors="coerce").astype(np.float32)

    data_rf = data_photo[COLS_TO_INSPECT].copy()
    data_rf.to_csv(DATA_PATH / "HN_data" / "data_refined.csv", index=False, header=True)

    print(f"Memory consumption for RAW(Single Precision): {sys.getsizeof(data_photo)*1e-6:.3f} bytes")
    print(f"Memory consumption for REF(Single Precision): {sys.getsizeof(data_rf)*1e-6:.3f} bytes")


if __name__ == "__main__":
    main()
