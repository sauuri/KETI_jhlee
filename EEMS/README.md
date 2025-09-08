# EEMS Data Processing Pipeline (TORAY Project)
## Overview
This project is part of the **EEMS (Energy Efficiency Management System)** at KETI, focusing on analyzing Toray motor power consumption data.  
The pipeline converts raw CSV files into structured, cleaned, and analyzed dataset with visualization outputs.  
The workflow is divided into multiple steps, each producing intermediate results and logs for reproducibility.  

## Data Processing Flow
"""
EEMS Original Data (CSV)
   ↓ step1_data_filter.py
      Filtered Data (Parquet)
   ↓ step2_data_decomposed.py
      Decomposed Data (by motor)
   ↓ step3_data_split_chunk.py
      24h Valid Segment Extraction + Operating Section Visualization
   ↓ step3-2_data_split_chunk_operating_visualization.py
      Operating Segment Detection + Calculated Value Plot
   ↓ step4_select_max_diffrate_date.py
      Motor Pairwise Max diff_rate Date Comparison
"""



## 📝 Step Descriptions

### **Step 1: Filtering & Format Conversion**
- **Input**: `original/*.csv`  
- **Process**:
  - Select key columns (`collect_time`, `machine_code`, `Load_Total_Power_Consumption`, etc.)
  - Convert numeric types to reduce file size
  - Save as `.parquet`
- **Output**: `filtered/*.parquet`  
- **Logs**: `step1_csv_vs_parquet_size_comparision.txt`  
- **Compression Rate**: ~97% (Inner), ~96% (Outer)  

---

### **Step 2: Data Decomposition (by Motor)**
- **Input**: `filtered/*.parquet`  
- **Process**:
  - Split into motor-specific datasets (e.g., `P1730A`, `P7412A_EXT`)
  - Save each motor’s data separately (`.parquet` + `.png`)  
- **Output**: `decomposed/TORAY_*_filtered_decomposed.parquet`  
- **Logs**: `step2_device_motor_decomposition_log.txt`  

---

### **Step 3-1: 24h Chunk Split & Visualization**
- **Process**:
  - Split decomposed motor data into **24h segments**
  - Filter out invalid data (missing hours, >1h gaps, almost zero variation)
  - Compute total energy change (`delta_E`), duration (`delta_t`), and average `Wh/h`
- **Output**:
  - `chunked/{motor}/24h/parquets/*.parquet`
  - `plots/*.png` (shifted power plots)
  - `missing_24h_summary.csv`, `saved_24h_summary.csv`

---

### **Step 3-2: Operating Section Detection**
- **Process**:
  - Detect operating segments within valid 24h chunks (`diff > 1`)
  - Highlight operating ranges in **orange** on plots
  - Compare total vs operating consumption
- **Output**: `well plots/*.png` (with operating sections highlighted)

---

### **Step 4: Maximum Difference Date Selection**
- **Process**:
  - Compare motor pairs (`P1730A vs P1730B`, `P7412A_EXT vs P7412B_EXT`, etc.)
  - Normalize `diff` and `diff_rate` using Min-Max scaling
  - Compute pairwise scores across dates (combinations)
  - Select date range with maximum difference rate
- **Output**:
  - `max_diff_rate_dates_{motor1}_{motor2}.csv`
  - `step4_max_diff_rate_date.txt`  
⚠️ **Limitations**: Results may capture large variations unrelated to actual equipment/construction changes, limiting generalization and decision-making reliability.

---

## 📂 Project Directory Structure
"""
data/
├─ original/ # Raw CSV files
├─ filtered/ # Step1 outputs (parquet)
├─ decomposed/ # Step2 outputs (by motor)
├─ chunked/ # Step3 outputs (24h parquets, plots, well plots)
└─ preprocessing_results/
├─ missing_24h_summary.csv
├─ saved_24h_summary.csv
├─ max_diff_rate_dates_*.csv
└─ preprocessing_logs/
├─ step1_csv_vs_parquet_size_comparision.txt
├─ step2_device_motor_decomposition_log.txt
└─ step4_max_diff_rate_date.txt
"""

---

## 👤 Author
**Jeonghwan Lee (이정환)**  
Researcher, Intelligent Mechatronics Research Center, KETI  

📅 *Document last updated: 2025.08.14*


