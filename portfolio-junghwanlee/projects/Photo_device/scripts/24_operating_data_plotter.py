from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

COL_TIME = "collect_time"


def main():
    Operating_data = pd.read_csv(
        DATA_PATH / "Operating_Filtered_0206_data.csv",
        low_memory=False,
    )

    data = Operating_data[["temp", "WATER_IN_TEMP"]]

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    scaled_data = pd.DataFrame(scaled_data, columns=["temp", "WATER_IN_TEMP"])

    fig1, ax1 = plt.subplots(1, 1, figsize=(12, 10))
    ax1.scatter(Operating_data[COL_TIME], scaled_data["temp"], label="scaled photo temp (operating)")
    ax1.scatter(Operating_data[COL_TIME], scaled_data["WATER_IN_TEMP"], label="scaled cover WATER_IN_TEMP (operating)")
    ax1.set_title("Operating Data")
    ax1.legend()

    plt.show()


if __name__ == "__main__":
    main()
