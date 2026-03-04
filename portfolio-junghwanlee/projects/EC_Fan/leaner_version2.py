"""
Surrogate model training module for EC Fan optimization.

Objective variables:
    average_T     : Maximization (converted to minimization by negation)
    Torque_Ripple : Minimization
    Cogging_T     : Minimization

Constraint variable:
    Slot_Area     : >= 270  (handled in optimizer_2.py)

Scaling note:
    X (design variables) : NOT scaled — raw physical units used as-is
    y (objective/constraint values) : MinMax scaled to [0, 1] for model training
"""

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os import cpu_count
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import r2_score as compute_r2
from xgboost import XGBRegressor
from model_2 import lb, ub  # noqa: F401  (used by optimizer)

DATA_PATH = r"data/20240819_2th_ECmotor_SuperCom_loadcase_total.csv"
N_FEATURES = 6
TEST_RATIO = 0.2


def _minmax_scale(data):
    """Apply Min-Max scaling to a DataFrame and return (scaled, min, max)."""
    min_val = data.min()
    max_val = data.max()
    scaled = (data - min_val) / (max_val - min_val)
    return scaled, min_val, max_val


def base_leaner(target_variable: str, use_cv: str):
    """
    Train an XGBoost surrogate model for the given target variable.

    Parameters
    ----------
    target_variable : str
        One of 'average_T', 'Torque_Ripple', 'Cogging_T', 'Slot_Area'.
    use_cv : str
        'y' to run RandomizedSearchCV and save a new model,
        'n' to load a previously saved model from disk.

    Returns
    -------
    model        : fitted XGBRegressor
    X            : full feature DataFrame (unscaled)
    y            : full target Series (scaled, sign-flipped for maximization)
    importance_df: DataFrame with permutation importance scores (cv='y' only)
    r2           : R² score on test set
    """
    cpus = round(0.8 * cpu_count())

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    df = pd.read_csv(DATA_PATH, header=0, low_memory=False)

    df_DV = df.iloc[:, list(range(N_FEATURES)) + [-1]]   # 6 design variables
    df_obj = df.iloc[:, 6:-1]                            # objective/constraint columns

    # ------------------------------------------------------------------
    # y scaling: MinMax applied to all objective/constraint columns
    # X scaling: NOT applied (raw physical units)
    # ------------------------------------------------------------------
    scaled_obj, min_val, max_val = _minmax_scale(df_obj)

    data = pd.concat([df_DV, scaled_obj], axis=1)

    X = data.iloc[:, :N_FEATURES]

    if target_variable == "average_T":
        # Convert maximization → minimization by negating
        y = -data[target_variable]
    else:
        y = data[target_variable]

    # ------------------------------------------------------------------
    # Train / test split
    # ------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_RATIO, random_state=42
    )

    # ------------------------------------------------------------------
    # Model training
    # ------------------------------------------------------------------
    if use_cv == "y":
        param_dist = {
            "n_estimators":     [100, 200, 300, 400, 500],
            "max_depth":        [3, 4, 5, 6, 7],
            "learning_rate":    [0.01, 0.05, 0.1, 0.2],
            "subsample":        [0.6, 0.7, 0.8, 0.9, 1.0],
            "colsample_bytree": [0.6, 0.7, 0.8, 0.9, 1.0],
            "gamma":            [0, 0.1, 0.2, 0.3, 0.4],
            "reg_alpha":        [0, 0.01, 0.1, 1],
            "reg_lambda":       [0, 0.01, 0.1, 1],
        }

        xgb = XGBRegressor(random_state=42, n_jobs=cpus)
        random_search = RandomizedSearchCV(
            xgb,
            param_distributions=param_dist,
            n_iter=10,
            scoring="neg_mean_squared_error",
            cv=5,
            verbose=2,
            random_state=42,
            n_jobs=cpus,
        )
        random_search.fit(X_train, y_train)

        best_model = random_search.best_estimator_
        y_pred = best_model.predict(X_test)

        # R² score on full dataset
        r2 = best_model.score(X, y)
        print(f"[{target_variable}] R² (full data): {r2:.4f}")

        # Feature importance (built-in gain-based)
        importance_df = pd.DataFrame({
            "Feature":    X.columns,
            "Importance": best_model.feature_importances_,
        }).sort_values("Importance", ascending=False)

        print(f"[{target_variable}] Best params: {random_search.best_params_}")

        with open(f"models/DV2_XGB_Regressor_best_model_{target_variable}.pickle", "wb") as f:
            pickle.dump(best_model, f)

        return best_model, X, y, importance_df, r2

    else:
        # Load pre-trained model
        model_path = f"models/DV2_XGB_Regressor_best_model_{target_variable}.pickle"
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Saved model not found at '{model_path}'. "
                "Run with use_cv='y' first to train and save the model."
            )

        y_pred = model.predict(X_test)
        r2 = compute_r2(y_test, y_pred)
        print(f"[{target_variable}] R² (test set): {r2:.4f}")

        return model, X, y, pd.DataFrame(), r2
