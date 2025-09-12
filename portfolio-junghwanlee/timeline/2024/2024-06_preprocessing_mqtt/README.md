# 📑 Research Note: June — Compressor Data Cleaning, “Triangle” Pattern Detection & MQTT Multiprocessing

---

## 🔹 Process

### 1. Data Loading & Cleaning
- Loaded compressor operation logs (≈86,400 rows/day).  
- Converted units (e.g., °C → K; planned: g/cm² → Pa).  
- Used CSV initially, evaluated Parquet for speed-up  
  → CSV ≈ 20.1s vs Parquet ≈ 0.0s (demo).  

### 2. Exploratory Visualization
- Global & windowed slices (e.g., index **48,000–50,000**) for trend checking.  
- Plotted: **Inlet Flow vs System Pressure**, **Outlet Flow vs Discharge Pressure**.  
- Tried **KDE / heatmap / vector (arrow)** plots to reveal the “triangle” operating-state shape.  

### 3. Modeling & Error Analysis
- Response surfaces with semi-transparent `plot_surface(alpha=…)`.  
- Ground-truth `scatter` with higher alpha; error bars to show **local AE**.  
- **GPR** (Matern/RBF/RQ) with confidence planes.  
- Fixed CI bug → found that `std` must be multiplied into the predicted mean offsets.  

### 4. MQTT Experiments (Multiprocessing)
- Local **Mosquitto broker** on LAN.  
- Publish/subscribe without Paho (CLI tools).  
- Verified **QoS 0/1/2** behavior on Windows & Raspberry Pi.  
- Produced **how-to notes** for setup.  

---

## 🔹 Purpose
- Clean and structure monthly compressor data, then reliably detect the **“triangle” regime shape**.  
- Look beyond global **R²** and quantify **local errors (AE)** with error bars.  
- Validate **confidence intervals (30/60/90/95/99%)** for uncertainty-aware visuals.  
- Prepare **MQTT multi-processing** paths for real-time ingestion.  

---

## 🔹 Results
- **Parquet** proved far faster for reloads on large logs.  
- Triangle shape visible in subsets; dense clusters hide edges unless narrowed.  
- **CI bug fixed**: upper/lower planes now render correctly across confidence levels.  
- Error-bar views (Efficiency/Power) exposed **largest-AE points**, even when global R² was high.  

> ⚠️ Note: Several plots/models were inconsistent this month; many are placeholders for later polishing.  

---

## 🔹 Next Steps

### 🔸 Triangle Detection
- Formalize feature space (x: Inlet Flow, y: Pressure Ratio = Discharge/System).  
- Add density-aware edge detection so the triangle doesn’t collapse when down-sampling.  

### 🔸 Error & CI Automation
- Function to compute AE per point and draw error bars automatically.  
- Batch draw CI planes for 30/60/90/95/99%.  

### 🔸 Model Tuning
- Systematic kernel search for GPR; report **AE/RMSE** (not only R²).  
- Track **max AE locations** to guide data cleaning or sensor checks.  

### 🔸 MQTT Multiprocessing
- Benchmark multi-core publishing/subscribing.  
- Define topic schema & QoS policy.  

---

## 🔹 HW / Notes

**HW #1**  
1. `for i in range(int(1e10))`  
2. Split across 10 cores and compute **Σ log10(x)**.  
3. Decide chunking: contiguous integer ranges per core; reduce partial sums at the end.  

**June Log Snippets**  
- 6/18: cmap/vector plots; global vs 48k–50k windows.  
- 6/19: x = Inlet Flow, y = Pressure Ratio; compare full vs 2k-slice views.  

---

## 📚 References
- MQTT note & local-LAN broker tests, QoS, Mosquitto setup.  
- Compressor EDA slides: CSV→Parquet timing, triangle windows, density/arrow plots.  

---

👉 (Optional) A small Python utility can be added to:  
1. Compute AE + error bars per point  
2. Auto-render CI planes for selected confidence levels
