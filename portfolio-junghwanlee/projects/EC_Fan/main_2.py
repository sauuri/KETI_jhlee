"""
EC Fan Multi-Objective Optimization — main entry point.

Pipeline
--------
1. Train (or load) XGBoost surrogate models for each objective and constraint.
2. Run NSGA-III multi-objective optimization via pymoo.
3. Return the pymoo Result object (Pareto-optimal solutions).

Objectives  (all minimization inside pymoo):
    average_T     → maximization; negated in leaner_2.py
    Torque_Ripple → minimization
    Cogging_T     → minimization

Constraint:
    Slot_Area >= 270  (G(x) = 270 - Slot_Area <= 0 in optimizer_2.py)
"""

import os
import matplotlib.pyplot as plt
from leaner_2 import base_leaner
from optimizer_2 import optimize


def main(tar_list: list, con_list: list, use_cv: str,
         save_importance_figure: bool = True, opt_settings: dict = None):
    """
    Build surrogate models and run NSGA-III optimization.

    Parameters
    ----------
    tar_list              : list of objective variable names
    con_list              : list of constraint variable names
    use_cv                : 'y' to train with RandomizedSearchCV, 'n' to load saved models
    save_importance_figure: whether to save feature importance plots (only relevant if use_cv='y')
    opt_settings          : optional dict of NSGA3 keyword arguments

    Returns
    -------
    pymoo Result object
    """

    def build_surrogates(var_list: list) -> list:
        container = []
        for target in var_list:
            model, X, y, importance_df, r2 = base_leaner(target, use_cv)
            container.append(model)

            if use_cv == "y" and save_importance_figure and not importance_df.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(importance_df["Feature"], importance_df["Importance"])
                ax.bar_label(bars, fmt="%.4f", label_type="edge")
                ax.set_xlabel("Feature")
                ax.set_ylabel("Importance")
                ax.set_title(f"Feature Importance — {target}  (R²={r2:.4f})")
                fig.tight_layout()

                os.makedirs("figure", exist_ok=True)
                fig.savefig(f"figure/DV2_{target}.png", dpi=300)
                plt.close(fig)

        return container

    surr_container = build_surrogates(tar_list)
    con_container  = build_surrogates(con_list)

    res = optimize(
        model_list=surr_container,
        con_list=con_container,
        settings=opt_settings,
    )

    return res


if __name__ == "__main__":
    use_cv = input("Enable cross-validation? (y/n): ").strip().lower()

    res = main(
        tar_list=["average_T", "Torque_Ripple", "Cogging_T"],
        con_list=["Slot_Area"],
        use_cv=use_cv,
        save_importance_figure=True,
    )
