from pathlib import Path

import pandas as pd

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

COL_INDEX = "data_index"

SLICE_BOUNDARIES = [
    21145, 60496,
    279147, 325807,
    365662, 408354,
    452056, 496964,
    538608, 584186,
    625871, 664079,
    885040, 930268,
]


def main():
    data = pd.read_csv(DATA_PATH / "Processed_Filtered_Final_0204_data.csv")
    data.rename(columns={"Unnamed: 0": COL_INDEX}, inplace=True)
    df = data.copy()

    matching_indices = df[df[COL_INDEX].isin(SLICE_BOUNDARIES)].index
    index_tuples = list(zip(matching_indices[::2], matching_indices[1::2]))

    output_dir = DATA_PATH / "slice_data"
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, (a, b) in enumerate(index_tuples):
        sliced = data.iloc[a:b].copy()
        sliced["collect_time"] = sliced["collect_time"] + 1
        file_name = output_dir / f"0121_sliced_part_{idx + 1}.csv"
        sliced.to_csv(file_name, index=False)
        print(f"{file_name} saved.")


if __name__ == "__main__":
    main()
