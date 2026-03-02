from pathlib import Path

import numpy as np
import pandas as pd
from pygam import LinearGAM, s

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

NUM_SLICES = 7
NUM_SPLINES = 3
NUM_SPLINE_ORDER = 3


def smooth_dataframe(data: pd.DataFrame, num_splines: int, num_spline_order: int) -> pd.DataFrame:
    """
    Apply GAM spline smoothing to pressure and temperature columns.

    Parameters
    ----------
    data : pd.DataFrame
        Input dataframe with columns: pres, temp, WATER_IN_PRESSURE, WATER_IN_TEMP
    num_splines : int
        Number of splines.
    num_spline_order : int
        Spline order.

    Returns
    -------
    pd.DataFrame
        Dataframe with additional smoothed columns.
    """
    t = np.arange(len(data))

    gam_photo_pres = LinearGAM(s(0, n_splines=num_splines, spline_order=num_spline_order)).fit(
        t, data["pres"].to_numpy()
    )
    gam_photo_temp = LinearGAM(s(0, n_splines=num_splines, spline_order=num_spline_order)).fit(
        t, data["temp"].to_numpy()
    )
    gam_coever_pres = LinearGAM(s(0, n_splines=num_splines, spline_order=num_spline_order)).fit(
        t, data["WATER_IN_PRESSURE"].to_numpy()
    )
    gam_coever_temp = LinearGAM(s(0, n_splines=num_splines, spline_order=num_spline_order)).fit(
        t, data["WATER_IN_TEMP"].to_numpy()
    )

    data = data.copy()
    data.loc[:, "PRES_SMOOTH"] = gam_photo_pres.predict(t)
    data.loc[:, "TEMP_SMOOTH"] = gam_photo_temp.predict(t)
    data.loc[:, "WATER_IN_PRESSURE_SMOOTH"] = gam_coever_pres.predict(t)
    data.loc[:, "WATER_IN_TEMP_SMOOTH"] = gam_coever_temp.predict(t)

    return data


if __name__ == "__main__":
    input_dir = DATA_PATH / "slice_data"
    output_dir = DATA_PATH

    for num in range(1, NUM_SLICES + 1):
        input_file = input_dir / f"sliced_part_{num}.csv"
        output_file = output_dir / f"final_smooth_sliced_part_{num}_splines_{NUM_SPLINES}.csv"

        data = pd.read_csv(input_file, low_memory=False)
        smooth_data = smooth_dataframe(data, NUM_SPLINES, NUM_SPLINE_ORDER)
        smooth_data.to_csv(output_file, index=False, header=True)
