<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/b2900715-4097-4dd7-8df5-93a9a60c94eb" />

# 광섬유 온도센서 교체 및 데이터 1:1 매핑(호환) 적용

## 개요
XXX 설비에서 기존 온도센서를 **광섬유 온도센서(Fiber Optic Temperature Sensor)** 로 교체하는 과제를 수행했습니다.
핵심 요구사항은 기존 운영 시스템(로그/모니터링/알람 등)을 수정하지 않고도 센서를 **즉시 대체 가능**하도록, 신규 센서 데이터를 기존 데이터 형태로 **1:1 매핑(Compatibility Layer)** 하는 것이었습니다.

---

## 접근 방법
- 초기에는 선형 보정(일차 변환)으로 스케일을 맞추는 방식을 검토했으나, 실측 비교 결과 온도 구간에 따라 **비선형 오차(곡률)** 가 나타났습니다.
- 따라서 기존 시스템이 기대하는 데이터 스케일/형태를 유지하면서도 구간별 편차를 줄이기 위해 **곡률을 반영한 보정 모델(비선형 캘리브레이션)** 을 적용했습니다.
- 적용한 변환식은 선형식에 **2차 항(곡률)** 을 추가한 형태로 구성했습니다.

### 변환식(호환 값 생성)
$$T_{mapped} = a \cdot T_{fiber} + b + c \cdot T_{fiber}^{2}$$

- **$T_{fiber}$**: 광섬유 센서 측정값
- **$T_{mapped}$**: 기존 시스템 호환 값
- **$a, b, c$**: 실측 데이터 기반으로 추정한 보정 계수(기울기/오프셋/곡률)

> 참고: 비선형성이 특정 구간에서만 커지는 경우, 동일 목표를 **구간별 선형(piecewise)** 또는 **스플라인(spline)** 으로 구현할 수도 있습니다.
> 본 과제의 핵심은 **기존 시스템 입력 포맷을 유지하면서 비선형 편차를 보정**하는 것이었습니다.

---

## 결과
- 기존 시스템의 데이터 포맷/스케일을 유지하면서 광섬유 센서로 **무중단/최소 변경** 교체가 가능하도록 했습니다.
- 선형 보정만 적용했을 때 발생하던 **온도 구간별 편차**를 곡률 보정으로 완화하여, 센서 교체 후에도 기존 데이터와 **연속성**을 유지했습니다.
- 운영/분석/알람 로직을 그대로 활용할 수 있어, 시스템 변경 비용과 리스크를 최소화했습니다.

---

## 데이터 처리 파이프라인

본 프로젝트의 데이터 처리는 아래 흐름으로 구성되며, `scripts/` 폴더에 단계별 스크립트가 정리되어 있습니다.

```
RAW 데이터
    │
    ▼
[1단계] 데이터 정제 (01~05)
  - HN 센서(누적 소비전력) CSV 로드 및 컬럼 선택
  - 결측치 보간 / 타입 변환 / 운전 구간 필터링
    │
    ▼
[2단계] 데이터 병합 (06~08)
  - 광소자(Photo) 데이터 ↔ HN(Coever) 데이터를 시간 기준으로 1:1 병합
  - 누락 타임스탬프 보완 및 선형 보간
    │
    ▼
[3단계] 오프셋 보정 (09~10)
  - 누적 소비전력 역전(감소) 구간 감지 → 오프셋 누산 보정
    │
    ▼
[4단계] 슬라이싱 & 평활화 (11~12)
  - 운전 구간을 하드코딩 인덱스 기준으로 슬라이스
  - GAM(Generalized Additive Model) 스플라인 평활화
    │
    ▼
[5단계] 운전 경계 탐지 (13~14)
  - 소비전력 diff 임계값 기반으로 운전 시작/종료 자동 감지
  - 구간별 선형 보간 및 다항 커브 피팅(Quadratic)
    │
    ▼
[6단계] 주파수 분석 FFT (15~18)
  - 전체 데이터 / 슬라이스별 / 단일 슬라이스 FFT
  - 노이즈 분석 및 상위 주파수 성분 추출
    │
    ▼
[7단계] 회귀 모델(1:1 매핑) (19~21)
  - scipy curve_fit 예제
  - SVR(Support Vector Regression) + GridSearchCV 하이퍼파라미터 탐색
  - 병렬 처리(multiprocessing) SVR
    │
    ▼
[8단계] 결과 시각화 (22~26)
  - SVR 예측 결과 플롯 (원본/스케일링)
  - 운전 데이터 / 전처리 데이터 분포 시각화
  - 데이터 탐색(소비전력 diff 분포)
```

---

## 스크립트 목록 (`scripts/`)

| 파일 | 역할 |
|------|------|
| `01_raw_data_refiner.py` | HN 소비전력 CSV 로드 → 컬럼 선택 → 정제 저장 |
| `02_data_refiner_extended.py` | Photo/Coever 양측 데이터 동시 정제 |
| `03_power_preprocessor.py` | 누적 소비전력 전처리 + 운전 구간 필터링 v1 |
| `04_power_preprocessor_with_instant.py` | 전처리 v2 (Instant Power 컬럼 포함) |
| `05_power_preprocessor_time_specific.py` | 전처리 v3 (08/30~09/10 특정 시간대 데이터) |
| `06_data_normalizer.py` | StandardScaler 적용 후 산점도 시각화 |
| `07_datetime_data_merger.py` | Photo ↔ HN 데이터 datetime 기준 병합 v1 |
| `08_datetime_data_merger_v2.py` | 병합 v2 (경로 변수 분리, 코드 정리) |
| `09_power_offset_corrector.py` | 소비전력 오프셋 보정 (역전 구간 누산 처리) v1 |
| `10_power_offset_corrector_v2.py` | 오프셋 보정 v2 (함수화 + CSV 저장) |
| `11_data_slicer.py` | 하드코딩 인덱스 기반 운전 구간 슬라이스 |
| `12_gam_smoother.py` | GAM 스플라인 평활화 (7개 슬라이스 처리) |
| `13_operation_boundary_detector.py` | diff 임계값 기반 운전 시작/종료 경계 탐지 |
| `14_operation_curve_analyzer.py` | 운전 구간 선형 보간 + 다항 커브 피팅 + R² 평가 |
| `15_fft_full_data.py` | 전체 Operating 데이터에 FFT 적용 (상위 N 성분 IFFT) |
| `16_fft_all_slices.py` | 7개 슬라이스 전체 FFT 결과 subplot 시각화 |
| `17_fft_single_slice.py` | 단일 슬라이스 FFT + IFFT 4패널 분석 |
| `18_fft_noise_analysis.py` | 단일 슬라이스 상위 1/5/25%/50%/75%/100% 주파수 성분 분석 |
| `19_curve_fitting_example.py` | scipy curve_fit 사용법 예제 (2차 함수 피팅) |
| `20_svr_regression.py` | SVR + GridSearchCV로 temp → WATER_IN_TEMP 회귀 |
| `21_svr_regression_parallel.py` | SVR 병렬 처리 (multiprocessing Pool, 20분할) |
| `22_svr_result_plotter.py` | SVR 예측 결과 + Standard/MinMax 스케일 비교 플롯 |
| `23_svr_result_plotter_scaled.py` | SVR 예측 결과 단순 플롯 (스케일링 전) |
| `24_operating_data_plotter.py` | 운전 데이터(Operating) StandardScaler 적용 산점도 |
| `25_processed_data_plotter.py` | IFFT 결과 Cross-Correlation 분석 및 시프트 시각화 |
| `26_data_explorer.py` | 전처리 데이터 소비전력 diff 분포 탐색 |

---

## 공통 설정

모든 스크립트는 `pathlib.Path` 기반의 공통 경로 변수를 사용합니다.

```python
from pathlib import Path

BASE_PATH = Path("/Volumes/jhlee/jhlee/Active_Photo_device")
DATA_PATH = BASE_PATH / "data"
FIGURE_PATH = BASE_PATH / "figures"
```

---

## 사용 기술

- **Python**: pandas, numpy, matplotlib, scipy
- **Machine Learning**: scikit-learn (SVR, GridSearchCV, StandardScaler, MinMaxScaler)
- **Signal Processing**: FFT / IFFT (numpy.fft, scipy.fft)
- **Smoothing**: pyGAM (LinearGAM + spline)
- **Parallel Processing**: multiprocessing.Pool

---

## 키워드
- Fiber Optic Temperature Sensor
- Sensor Replacement / Data Mapping
- Nonlinear Calibration / Quadratic Correction
- Compatibility Layer
- SVR Regression / GridSearchCV
- FFT / IFFT Signal Processing
- GAM Smoothing
