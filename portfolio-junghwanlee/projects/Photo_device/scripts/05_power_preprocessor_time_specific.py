from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"
FIGURE_PATH = BASE_PATH / "figures"

pd.set_option("display.max_columns", None)

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Times New Roman'
plt.rcParams['mathtext.rm'] = 'serif'
plt.rcParams['mathtext.it'] = 'serif:italic'
plt.rcParams['mathtext.bf'] = 'serif:bold'
plt.rcParams['mathtext.fontset'] = 'custom'

COL_TIME = "collect_time"
COL_POWER = "Load_Total_Power_Consumption"

POWER_LOWER = 0
POWER_UPPER = 600


def preprocessor(feasible_consumption=False, split_running_status=False):
    _refined = pd.read_csv(
        DATA_PATH / "0115_Final_merged_df.csv",
        header=0,
        low_memory=False,
    )

    cols_status = ['Time']
    cols_interest = _refined.columns.drop(COL_TIME)
    refined = _refined.drop(cols_status, axis=1)

    for col in refined.columns:
        if col == COL_TIME:
            refined[col] = pd.to_datetime(refined[col], format="mixed")
        else:
            refined[col] = pd.to_numeric(refined[col], errors="coerce").astype(np.float32)

    first_nonzero_idx = refined[cols_interest].prod(axis=1).ne(0).idxmax()
    refined = refined.iloc[first_nonzero_idx:].reset_index(drop=True)

    refined[cols_interest] = refined[cols_interest].interpolate()
    refined = refined[refined[cols_interest].prod(axis=1) != 0].reset_index(drop=True)

    refined['time'] = refined[COL_TIME]
    refined[COL_TIME] = refined[COL_TIME].diff().dt.total_seconds().fillna(0).cumsum()

    it = 1
    if feasible_consumption:
        instant_consumption = refined[COL_POWER].diff().to_numpy()
        while np.any(instant_consumption[1:] < 0):
            print(f"Power filtering at loop: {it}")
            indexer_infeasible = np.argwhere(instant_consumption < 0).ravel()
            refined.loc[indexer_infeasible, COL_POWER] = np.nan
            refined[COL_POWER] = refined[COL_POWER].ffill()
            instant_consumption = refined[COL_POWER].diff().to_numpy(dtype=np.float32)
            it += 1

    refined.to_csv(DATA_PATH / "0116_data_refined_test.csv")

    if split_running_status:
        if not feasible_consumption:
            raise ValueError("'feasible_consumption' must be True to use split_running_status")
        filtered = worktime_slicer(refined)
        return _refined, refined, filtered

    return _refined, refined


def worktime_slicer(df):
    col_set = set(df.columns)
    if COL_TIME not in col_set or COL_POWER not in col_set:
        raise KeyError(f"'{COL_TIME}' and/or '{COL_POWER}' is not in columns")

    instant_consumption = df[COL_POWER].diff()

    mask = (instant_consumption > POWER_LOWER) & (instant_consumption <= POWER_UPPER)
    _instant_power = instant_consumption[mask]
    _filtered = df[mask].copy()
    _filtered["Instant_Power"] = _instant_power.to_numpy()

    return _filtered


if __name__ == "__main__":
    raw, processed, filtered = preprocessor(feasible_consumption=True, split_running_status=True)

    df_type = filtered
    df_type.to_csv(DATA_PATH / "0115_real_data_refined_test.csv")

    scaler = MinMaxScaler()

    col_ignore = ["time", "Instant_Power"]

    x = df_type[COL_TIME]
    ys = scaler.fit_transform(df_type.drop(col_ignore, axis=1))
    labels = df_type.columns.drop(col_ignore)

    f, a = plt.subplots(figsize=(30, 15))
    for ind, label in enumerate(labels):
        a.scatter(x=x, y=ys[:, ind], alpha=0.7, s=10, label=label)

    a.grid(which='both', linestyle='dashed')
    a.legend()
    FIGURE_PATH.mkdir(parents=True, exist_ok=True)
    f.savefig(FIGURE_PATH / "0115_whole2.png", dpi=300)
    df_type.to_csv(DATA_PATH / "Final_3_0115_data.csv", index=False, header=True)
