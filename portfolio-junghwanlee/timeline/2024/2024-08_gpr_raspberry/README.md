# 📑 Research Note: 8월 — Raspberry Pi 저전력 테스트 & 모델 검증

---

## 🔹 Process

### 1. 시스템 세팅
- Raspberry Pi **이미지 재설치** 후 대부분 기본 설정 유지.  
- `commandline.txt`에서 **활성 코어 수**만 제한.  
- `apt`, `pip` 패키지 설치 및 가상환경에서 `requirements.txt` 기반 의존성 세팅.  

### 2. 하드웨어 확인
- 실험 전 보드별 정격 전원 확인:  
  - Raspberry Pi Zero W: 5V / 2.5A  
  - Raspberry Pi 3A+: 5V / 2.5A (micro USB)  
  - Raspberry Pi 5: 5V / 5A (USB-C, PD 지원)  
- M.2 HAT+ 구매처 조사 및 필요 케이블/어댑터 리스트업.  

### 3. 엣지 환경 유사 테스트
- **CPU 코어 수**와 **클록 속도**를 제한하여 **저전력 임베디드 보드 환경** 근사.  
- 해당 조건에서 학습/추론 스크립트를 실행하고 처리 속도 측정.  
- 실행 시간 약 **6초/회** 확인, 저전력 조건에서도 안정적으로 동작.  

### 4. 모델링 및 평가
- **Gaussian Process Regression (GPR)** 구현, Matern/RBF/RQ/WhiteKernel 조합 사용.  
- **GridSearchCV (cv=5)**로 하이퍼파라미터 탐색.  
- 주요 지표 계산:  
  - Global **R² Score**  
  - 각 포인트별 **절대 오차(Absolute Error, AE)**  
  - GPR 기반 **신뢰구간(평균 ± 표준편차)**  
- `train_test_split`으로 학습/검증 분리 후 Efficiency & Power 성능 평가.  

---

## 🔹 Purpose
- **자원 제약 하드웨어 환경**에서 압축기 데이터 모델 검증.  
- CPU 주파수 및 코어 수 제한이 처리 속도에 미치는 영향 확인.  
- R², AE, CI 기반의 모델 성능을 **실제 엣지 장치 근사 환경**에서 평가.  
- 저전력 하드웨어에서도 분석 파이프라인 실행 가능성 확보.  

---

## 🔹 Results
- Raspberry Pi 환경에서 **저전력 AI 엣지 테스트베드**를 성공적으로 재현.  
- 코어/클록 제한 시 실행 시간 증가 확인, 그러나 모델 실행에는 문제 없음.  
- GPR 모델은 의미 있는 R² 점수를 보였으며, **오차가 큰 포인트**도 확인 가능.  
- 신뢰구간 평면이 정상적으로 계산되어 **불확실성 시각화** 가능.  
- 전체 파이프라인이 제한된 환경에서도 실행 가능한 것을 검증.  

---

## 🔹 Next Steps
- 보드별 성능 비교 (Zero W, 3A+, 5).  
- Raspberry Pi 기반 **TLS/SSL MQTT 클라이언트** 추가 → 보안 데이터 전송 테스트.  
- 오차 분석 자동화 (AE 분포 계산, 분산 최소화 평면 구성).  
- **전력 소모 vs 실행 시간** 트레이드오프 프로파일링.  

---

## 📚 References
- Raspberry Pi 공식 문서 (전원 사양, 기본 OS 세팅).  
- 7월 MQTT 브로커 실험 노트.  
- scikit-learn GPR & GridSearchCV 문서.  
