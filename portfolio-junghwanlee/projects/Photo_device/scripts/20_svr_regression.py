from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

SVR_PARAM_GRID = {
    'C': [0.0001, 0.001],
    'epsilon': [0.0001, 0.001, 0.01, 0.05, 0.1],
    'kernel': ['rbf'],
    'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
}

N_JOBS = 18


def eval_metrics(y, y_pred):
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    return (
        f"MAE: {mae:.5f}",
        f"RMSE: {rmse:.5f}",
        f"R²: {r2:.5f}",
    )


def main():
    fft_temp = pd.read_csv(
        DATA_PATH / "FFT_Results_slice_0206_filtered_temp_frequency_0.001.csv",
        index_col=0, low_memory=False,
    )
    fft_water_temp = pd.read_csv(
        DATA_PATH / "FFT_Results_slice_0206_filtered_WATER_IN_TEMP_frequency_0.001.csv",
        index_col=0, low_memory=False,
    )

    X = fft_temp.to_numpy().reshape(-1, 1)
    y = fft_water_temp.to_numpy().reshape(-1,)

    grid_search = GridSearchCV(
        SVR(), SVR_PARAM_GRID, cv=5, scoring='neg_mean_squared_error',
        n_jobs=N_JOBS, verbose=2,
    )
    grid_search.fit(X, y)

    print("Best parameters:", grid_search.best_params_)
    print("Best MSE:", -grid_search.best_score_)

    best_model = SVR(**grid_search.best_params_)
    best_model.fit(X, y)
    y_pred = best_model.predict(X)

    metrics = eval_metrics(y, y_pred)
    print(f"SVR Model Metrics: {metrics}")

    error1 = y - y_pred

    result = pd.DataFrame({
        'y_true': y,
        'y_pred': y_pred.ravel(),
        'error1': error1,
        'X': X.ravel(),
    })
    result.to_csv(DATA_PATH / "0206_Slice_1_Hyperparameter_SVR_FFT_Result_temp_to_WATER_IN_TEMP_data.csv")


if __name__ == "__main__":
    main()
