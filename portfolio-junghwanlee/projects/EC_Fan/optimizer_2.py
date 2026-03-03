"""
Multi-objective optimization module using NSGA-III (via pymoo).

Objectives:
    F[0]  average_T     — minimization (negated in leaner_2.py for maximization)
    F[1]  Torque_Ripple — minimization
    F[2]  Cogging_T     — minimization

Inequality constraint (pymoo convention: G(x) <= 0 is feasible):
    G(x) = 270 - Slot_Area <= 0  →  Slot_Area >= 270

To add or remove constraints:
    1. Pass additional surrogate models via `con_list`.
    2. Extend the `_evaluate` method accordingly.

NSGA-III hyper-parameters:
    n_partitions = 40
        → das-dennis reference directions for 3 objectives
        → generates 861 reference points, which sets the effective pop_size.
"""

import pickle
import numpy as np
from xgboost import XGBRegressor
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.optimize import minimize
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SimulatedBinaryCrossover
from pymoo.operators.mutation.pm import PolynomialMutation
from pymoo.util.ref_dirs import get_reference_directions
from model_2 import lb, ub


class MOO(ElementwiseProblem):
    """Multi-objective optimization problem wrapping XGBoost surrogate models."""

    def __init__(self, models: list, model_constraints: list):
        self.models = models
        self.model_constraints = model_constraints

        super().__init__(
            n_var=6,
            n_obj=len(models),
            n_constr=len(model_constraints),
            xl=lb,
            xu=ub,
        )

    def _evaluate(self, x, out, *args, **kwargs):
        # Objective values: each surrogate predicts one objective
        out["F"] = [model.predict([x])[0] for model in self.models]

        # Inequality constraints: G(x) <= 0 means feasible (pymoo convention)
        # G = 270 - Slot_Area  →  feasible when Slot_Area >= 270
        if self.model_constraints:
            slot_area_pred = self.model_constraints[0].predict([x])[0]
            out["G"] = [270.0 - slot_area_pred]


def optimize(model_list: list, con_list: list, settings: dict = None):
    """
    Run NSGA-III multi-objective optimization.

    Parameters
    ----------
    model_list : list of XGBRegressor
        Surrogate models for each objective (order: average_T, Torque_Ripple, Cogging_T).
    con_list   : list of XGBRegressor
        Surrogate models for each inequality constraint (order: Slot_Area).
    settings   : dict, optional
        Custom NSGA3 keyword arguments. If None, defaults are used.

    Returns
    -------
    res : pymoo Result object
        res.X : Pareto-optimal design variable values
        res.F : Pareto-optimal objective values
        res.G : Constraint values at Pareto-optimal solutions
    """
    if not isinstance(model_list, list):
        raise TypeError("Argument 'model_list' must be a list.")
    for ml in model_list:
        if not isinstance(ml, XGBRegressor):
            raise TypeError(f"Expected XGBRegressor, got {type(ml)}.")

    problem = MOO(models=model_list, model_constraints=con_list)

    # Reference directions: das-dennis with n_partitions=40
    # → 861 reference points for 3 objectives, which determines pop_size
    n_obj = len(model_list)
    ref_dirs = get_reference_directions("das-dennis", n_obj, n_partitions=40)

    if settings is not None:
        algorithm = NSGA3(**settings)
    else:
        algorithm = NSGA3(
            ref_dirs=ref_dirs,
            sampling=FloatRandomSampling(),
            crossover=SimulatedBinaryCrossover(prob=0.9, eta=15),
            mutation=PolynomialMutation(eta=20),
            eliminate_duplicates=True,
        )

    termination = DefaultMultiObjectiveTermination()

    res = minimize(
        problem,
        algorithm,
        termination,
        seed=42,
        save_history=True,
        return_least_infeasible=True,
        verbose=True,
    )

    # Approximate ideal / nadir from optimization result
    approx_ideal = res.F.min(axis=0)
    approx_nadir = res.F.max(axis=0)
    print(f"Approximate ideal point : {approx_ideal}")
    print(f"Approximate nadir point : {approx_nadir}")
    print(f"Number of Pareto-optimal solutions: {len(res.F)}")

    with open("models/DV2_nsga3_result.pickle", "wb") as f:
        pickle.dump(res, f)

    return res
