# Junghwan Lee – Portfolio (2024.04 ~ 2025.09)

Signal Processing × Edge AI × Optimization  
실제 산업 데이터(EEMS, 모터/팬) 기반의 분석·시각화·최적화 프로젝트를 정리했습니다.

---

## 🌟 Highlighted Projects
이 레포지토리에서 **가장 정리 잘 된 대표 과제**들입니다.

- ⭐ [Motor FFT & Anomaly Detection](projects/motor-fft/)  
  - 산업 모터 진동 데이터 → FFT 기반 특징 추출 및 이상 탐지  
  - 전처리 → 스펙트럼 분석 → 이상 구간 시각화까지 풀 파이프라인  
  - [코드 보기](projects/motor-fft/src/) | [플롯](projects/motor-fft/plots/)

- ⭐ [EC Fan Multi-objective Optimization (NSGA-II)](projects/ec-fan-nsga2/)  
  - EC Fan 성능 ↔ 소비전력 간 Pareto Frontier 최적화  
  - NSGA-II 기반 다목적 최적화 실험 → 운영점 추천  
  - [코드 보기](projects/ec-fan-nsga2/src/) | [슬라이드](presentations/2024-09_ecfan_nsga2.pdf)

---

## 📂 Other Projects
- [MQTT Multiprocessing](projects/mqtt-multiprocessing/)  
  Python multiprocessing + MQTT 성능 비교 및 QoS 테스트  

- [Symbolic Regression (PySR)](projects/symbolic-regression/)  
  데이터 기반 수식 추출(Symbolic Regressor) 실험  

- [Edge Motor Sensing (Raspberry Pi)](projects/edge-motor-sensing/)  
  라즈베리파이 기반 모터 센서 데이터 수집 및 Edge ML 적용  

---

## 🗓️ Timeline Highlights
- **2024.04** — [모터 진동 분석(FFT)](timeline/2024/2024-04_fft_motor.md)  
- **2024.09** — EC Fan NSGA-II 다목적 최적화 · [슬라이드](presentations/2024-09_ecfan_nsga2.pdf)  
- **2024.12** — 광소자 데이터: SVM · LinearGAM · FFT 스무딩  
- **2025.06** — Edge Device 모터 센서 분석  
- **2025.07** — EEMS Toray 데이터 분석  
- **2025.09** — EEMS 프로젝트 마무리 / 결과 정리 & 인수인계 · [슬라이드](presentations/2025-09_eems_final.pdf)

👉 전체 월별 기록은 [`timeline/`](timeline/) 폴더 참고

---

## ⚙️ Tech Stack
- Python (NumPy, Pandas, Matplotlib, scikit-learn, PySR)  
- Optimization (SciPy, NSGA-II)  
- Signal Processing (FFT, Filtering, GPR, Curve Fitting)  
- Edge/IoT (MQTT, Raspberry Pi)  
- Visualization (Matplotlib, Seaborn, PPT Reports)

---

## 📄 License
코드는 MIT License를 따릅니다.  
Plot, 보고서, 발표자료는 별도 고지된 라이선스를 따릅니다.
