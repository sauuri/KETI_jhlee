from pathlib import Path
from multiprocessing import Pool

import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"

NUM_SPLITS = 20

SVR_PARAM_GRID_MAIN = {
    "C": [0.1, 1, 10, 100],
    "epsilon": [0.01, 0.1, 0.5, 1.0],
    "gamma": ["scale", "auto"],
}

SVR_PARAM_GRID_ERROR = {
    "C": [0.001, 0.1, 1, 10, 100],
    "epsilon": [0.001, 0.01, 0.1, 0.5, 1.0],
    "gamma": ["scale", "auto"],
}


def eval_metrics(y, y_pred):
    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)
    return (
        f"MAE: {mae:.5f}",
        f"RMSE: {rmse:.5f}",
        f"R²: {r2:.5f}",
    )


def optimize_svr(X, y, param_grid):
    grid_search = GridSearchCV(
        SVR(), param_grid, cv=5, scoring="neg_mean_squared_error", n_jobs=-1, verbose=1
    )
    grid_search.fit(X, y)
    return grid_search.best_params_


def split_data(X, y, num_splits):
    X_splits = np.array_split(X, num_splits)
    y_splits = np.array_split(y, num_splits)
    return list(zip(X_splits, y_splits))


def train_and_predict(data):
    X, y = data

    best_params = optimize_svr(X, y, SVR_PARAM_GRID_MAIN)
    svr = SVR(**best_params)
    svr.fit(X, y)
    y_pred = svr.predict(X)

    error1 = y - y_pred

    best_params_error1 = optimize_svr(X, error1, SVR_PARAM_GRID_ERROR)
    model_error1 = SVR(**best_params_error1)
    model_error1.fit(X, error1)
    pred_error1 = model_error1.predict(X)

    y_pred_corrected = y_pred + pred_error1

    return {
        "y_true": y,
        "y_pred": y_pred,
        "error1": error1,
        "pred_error1": pred_error1,
        "svr_metrics": eval_metrics(y, y_pred),
        "error1_metrics": eval_metrics(error1, pred_error1),
        "corrected_metrics": eval_metrics(y, y_pred_corrected),
        "best_params": best_params,
        "best_params_error1": best_params_error1,
    }


if __name__ == "__main__":
    fft_temp = pd.read_csv(
        DATA_PATH / "FFT_Results_0206_filtered_temp_frequency_0.0002.csv",
        index_col=0, low_memory=False,
    )
    fft_water_temp = pd.read_csv(
        DATA_PATH / "FFT_Results_0206_filtered_WATER_IN_TEMP_frequency_0.0002.csv",
        index_col=0, low_memory=False,
    )

    X = fft_temp.to_numpy().reshape(-1, 1)
    y = fft_water_temp.to_numpy().reshape(-1,)

    data_splits = split_data(X, y, NUM_SPLITS)

    with Pool(processes=NUM_SPLITS) as pool:
        results = pool.map(train_and_predict, data_splits)

    final_results = pd.DataFrame({
        "y_true": np.concatenate([r["y_true"] for r in results]),
        "y_pred": np.concatenate([r["y_pred"] for r in results]),
        "error1": np.concatenate([r["error1"] for r in results]),
        "pred_error1": np.concatenate([r["pred_error1"] for r in results]),
    })

    print("Overall SVR Metrics:", eval_metrics(final_results["y_true"], final_results["y_pred"]))
    print("Overall Error1 Metrics:", eval_metrics(final_results["error1"], final_results["pred_error1"]))
    print("Overall Corrected Metrics:", eval_metrics(
        final_results["y_true"], final_results["y_pred"] + final_results["pred_error1"]
    ))
    print("Best params per split:", [r["best_params"] for r in results])
    print(final_results.head())
