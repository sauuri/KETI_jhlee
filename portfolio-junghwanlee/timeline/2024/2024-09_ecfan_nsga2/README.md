# EC Fan Optimization with NSGA-III

This repository implements a **surrogate-based multi-objective optimization workflow** for EC Fan design variables.  
It combines **XGBoost regressors** with **NSGA-III** (via pymoo) to optimize multiple objectives under design constraints.

---

## 📑 Research Note: October — NSGA-III Optimization & Surrogate Modeling

### 🔹 Process
1. **Design Variables & Constraints**
   - 6 design variables (`V_rotor_r1`, `V_Opening_A`, …, `V_Tooth_W`).
   - Constraint: `Slot_Area ≥ 270`.
   - Bounds defined in [`model.py`](model.py).

2. **Surrogate Modeling**
   - Surrogates built using **XGBoostRegressor** (`base_leaner`).
   - Evaluated R² for each objective: `average_T`, `Torque_Ripple`, `Cogging_T`.
   - Feature importance plots automatically saved (`figure/DV2_{tdv}.png`).
   - Compared performance with full DV=6 vs reduced DV=2.

3. **Optimization (NSGA-III)**
   - Objectives:  
     - Maximize `average_T`  
     - Minimize `Torque_Ripple`  
     - Minimize `Cogging_T`
   - Implemented with pymoo’s NSGA-III algorithm.
   - Results saved to `models/DV2_nsga3_result.pickle`.

4. **Visualization**
   - `plot_convergence`: generations vs feasibility/hypervolume.
   - `plot_pareto_optimal_solutions`: Pareto front in 3D space.
   - `Editing_plot_pareto_optimal_solutions`: compares final population vs Pareto front.
   - Step-like surface plotting under development.

---

### 🔹 Results — Strengths ✅
- **Clear modularization**: bounds, optimizer, workflow, visualization separated.  
- **Surrogates trained** with reasonable R²-scores; feature importance clarifies dominant DVs.  
- **Optimization runs successfully** with feasible Pareto sets.  
- **Visualization** identifies first feasible generations and shows trade-offs.  
- **Reproducibility**: Pickle-based result saving/loading.

---

### 🔹 Limitations / Bugs ⚠️
- Constraints: only one supported, hardcoded offset (`-270`).  
- Surrogates: currently only XGBRegressor supported (SVM/GPR not modularized).  
- Visualization: convergence mislabeled (CV vs Hypervolume); step plots incomplete.  
- Cross-validation toggle only partially implemented.  
- Reduced-DV experiments tested manually (not automated).  
- Debugging comments remain in code.

---

### 🔹 Next Steps
1. **Constraints**
   - Generalize `_evaluate()` for multiple constraints.
   - Normalize constraint scaling.

2. **Surrogates**
   - Expand `base_leaner` to support GPR, SVR, SVM.
   - Automate R²-comparison across models.

3. **Visualization**
   - Correct convergence labels.
   - Implement true 3D surface plots (instead of scatter).
   - Automate batch plotting of Pareto and populations.

4. **Automation**
   - Automate reduced-DV vs full-DV experiments.
   - Automate experiments with different sample sizes (n=5000, 1000, 500…).

5. **Code Quality**
   - Remove debug prints, add complete docstrings.
   - Organize outputs (`models/`, `figure/`, `logs/`) with timestamps.

---

## 📚 References
- [`optimizer.py`](optimizer.py): NSGA-III implementation.  
- [`model.py`](model.py): Design variable bounds & constraints.  
- [`main.py`](main.py): Workflow for surrogate + optimization.  
- [`NSGA3_res_Visualization.py`](NSGA3_res_Visualization.py): Visualization utilities.  
- [Slides: ECFan Optimization 1008 Update](./ECFan1008_Updated.pptx).  

---
