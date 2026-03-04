"""
Visualization module for NSGA-III optimization results (EC Fan project).

Functions
---------
plot_convergence(res)
    Plot constraint violation convergence over generations.

plot_pareto_optimal_solutions(res)
    3D scatter plot of Pareto-optimal solutions in objective space.

plot_final_population(res)
    3D scatter plot comparing final population vs Pareto front.

inverse_minmax(scaled_data, min_val, max_val)
    Inverse-transform MinMax-scaled values back to original scale.
"""

import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


# ---------------------------------------------------------------------------
# Inverse transform
# ---------------------------------------------------------------------------

def inverse_minmax(scaled_data, min_val, max_val):
    """Inverse MinMax transform: recover original-scale values."""
    return scaled_data * (max_val - min_val) + min_val


# ---------------------------------------------------------------------------
# Convergence plot
# ---------------------------------------------------------------------------

def plot_convergence(res, save_path: str = None):
    """
    Plot average constraint violation (CV) of the population over generations.

    The vertical dashed line marks the first generation where the entire
    population becomes feasible (avg CV <= 0).

    Parameters
    ----------
    res       : pymoo Result object (must have res.history).
    save_path : str, optional. If provided, saves the figure to this path.
    """
    hist = res.history

    n_evals = []
    hist_cv_avg = []

    for algo in hist:
        n_evals.append(algo.evaluator.n_eval)
        hist_cv_avg.append(algo.pop.get("CV").mean())

    feasible_gens = np.where(np.array(hist_cv_avg) <= 0.0)[0]
    if len(feasible_gens) > 0:
        k = feasible_gens.min()
        print(f"Whole population feasible at generation {k} "
              f"after {n_evals[k]} evaluations.")
    else:
        k = None
        print("Population did not become fully feasible within the run.")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(n_evals, hist_cv_avg, color="black", lw=0.7, label="Avg. CV of Pop")
    ax.scatter(n_evals, hist_cv_avg, facecolor="none", edgecolor="black", marker="p")
    if k is not None:
        ax.axvline(n_evals[k], color="red", linestyle="--", label="All Feasible")
    ax.set_title("Convergence")
    ax.set_xlabel("Function Evaluations")
    ax.set_ylabel("Average Constraint Violation")
    ax.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=600)
    plt.show()


# ---------------------------------------------------------------------------
# Pareto front plot
# ---------------------------------------------------------------------------

def plot_pareto_optimal_solutions(res, save_path: str = "figure/Pareto_optimal_solutions_graph.png"):
    """
    3D scatter plot of Pareto-optimal solutions in objective space.

    Axes represent the three objectives:
        X — average_T  (negated; lower = better torque)
        Y — Torque_Ripple
        Z — Cogging_T
    """
    F = res.F

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(F[:, 0], F[:, 1], F[:, 2],
               s=30, facecolors="none", edgecolors="blue", alpha=0.9)
    ax.set_title("Pareto-Optimal Solutions")
    ax.set_xlabel("average_T (negated)")
    ax.set_ylabel("Torque_Ripple")
    ax.set_zlabel("Cogging_T")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=600)
    plt.show()


# ---------------------------------------------------------------------------
# Final population + Pareto front overlay
# ---------------------------------------------------------------------------

def plot_final_population(res, save_path: str = "figure/Final_Pop+Pareto_optimal_solutions_graph.png"):
    """
    3D scatter plot overlaying the final population (blue) and Pareto front (red).
    """
    pop_F = res.pop.get("F")
    F = res.F

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(pop_F[:, 0], pop_F[:, 1], pop_F[:, 2],
               s=50, facecolors="none", edgecolors="blue", alpha=0.7,
               label=f"Final Population (n={len(pop_F)})")
    ax.scatter(F[:, 0], F[:, 1], F[:, 2],
               s=25, facecolors="none", edgecolors="red", alpha=0.9,
               label=f"Pareto Front (n={len(F)})")

    ax.set_title("Final Population vs Pareto Front")
    ax.set_xlabel("average_T (negated)")
    ax.set_ylabel("Torque_Ripple")
    ax.set_zlabel("Cogging_T")
    ax.legend()
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=600)
    plt.show()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with open("models/DV2_nsga3_result.pickle", "rb") as f:
        res = pickle.load(f)

    plot_convergence(res, save_path="figure/Convergence_graph.png")
    plot_pareto_optimal_solutions(res)
    plot_final_population(res)
