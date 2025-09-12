📑 **Research Note: Response Surface Visualization & Error Analysis (Blower/Pump Data)**  

---

### 🔹 Process  
1. **CSV Data Loading**  
   - `pandas.read_csv()` (`low_memory=False`, UTF-8 / cp949)  
   - Remove missing values with `dropna()`  

2. **Visualization**  
   - `matplotlib.plot_surface()` for response surfaces (with `alpha` transparency)  
   - `scatter()` for ground truth points (higher alpha for emphasis)  
   - `errorbar()` for local error ranges  

3. **Modeling & Evaluation**  
   - Compute **R² Score** (global fit)  
   - Compute **Absolute Error (AE)** for each point (local fit)  
   - Train **Gaussian Process Regressor (GPR)** with kernels (Matern, RBF, RationalQuadratic)  
   - Plot **95% confidence interval bounds** (upper/lower planes)  

4. **Comparison**  
   - Before/after filtering errors  
   - Local vs global performance differences  

---

### 🔹 Purpose  
- To visualize and compare model predictions with ground truth data  
- To check not only global R² but also **local Absolute Errors**  
- To highlight uncertain regions using **confidence intervals**  
- To build a more reliable basis for future optimization  

---

### 🔹 Results  
- High R² (≈0.99) observed globally, but **large local errors** in specific regions  
- Error bars revealed where predictions diverge most  
- Confidence interval planes (±95%) showed uncertainty zones around predictions  

---

### 🔹 Next Steps  
- Add multiple confidence levels (90%, 95%, 99%) for deeper comparison  
- Automate AE + error bar calculation and plotting  
- Develop optimization routine to minimize variance of local errors  
- Summarize full workflow as a flowchart:  
  **Data → Model → Visualization → Error Analysis**  
