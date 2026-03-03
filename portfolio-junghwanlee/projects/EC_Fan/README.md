<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/03e36c80-8000-43e6-a373-cdc42298109a" />

# EC-Fan Multi-Objective Optimization (Surrogate + NSGA-III)

EC-Fan 설계에서 **상충되는 3개 목적함수**를 동시에 최적화하기 위해  
**Surrogate Model(SVR)** 기반으로 목적함수/제약조건을 근사하고,  
**NSGA-III**를 적용해 **Pareto-optimal 해집합**을 도출한 프로젝트입니다. :contentReference[oaicite:1]{index=1}

---

## 1. Problem Definition

### Objectives (3)
- **average_T** : 평균 토크 (**Maximize**) → 최적화에서는 **부호 반전(-average_T)**로 최소화 형태로 변환 :contentReference[oaicite:2]{index=2}  
- **Torque_Ripple** : 토크 리플 (**Minimize**) :contentReference[oaicite:3]{index=3}  
- **Cogging_T** : 코깅 토크 (**Minimize**) :contentReference[oaicite:4]{index=4}  

### Constraint (1)
- **Slot_Area ≥ 270** :contentReference[oaicite:5]{index=5}  

> 최적화 구현에서는 보통 제약식을 `G(x) ≤ 0`로 두므로 예:  
> `G = 270 - Slot_Area` (Slot_Area가 270 이상이면 G≤0 만족)

### Design Variables
- `n_var = 6` (총 6개 설계변수 사용) :contentReference[oaicite:6]{index=6}

---

## 2. Motivation: Why Surrogate Model?

NSGA-III는 세대별로 많은 해를 평가해야 하므로,  
목적함수/제약 평가 비용이 큰 경우 최적화가 비효율적일 수 있습니다.  
이를 보완하기 위해 **회귀 기반 Surrogate Model**로 목적함수 값을 근사하여 최적화를 수행했습니다. :contentReference[oaicite:7]{index=7}

---

## 3. Surrogate Models

목적함수별로 독립적인 회귀 모델을 학습했습니다. 

- Surrogate Model 1 : `average_T`
- Surrogate Model 2 : `Torque_Ripple`
- Surrogate Model 3 : `Cogging_T`
- Surrogate Model 4 (constraint) : `Slot_Area` :contentReference[oaicite:9]{index=9}

NSGA-III 평가 단계에서
- `out['F']` : 3개 목적함수 값을 저장
- `out['G']` : 제약조건 위반 정도(Constraint violation) 값을 저장 :contentReference[oaicite:10]{index=10}

---

## 4. Model Training (SVR) + Hyperparameter Search

### Libraries
- `scikit-learn` (SVR, RandomizedSearchCV) :contentReference[oaicite:11]{index=11}

### Hyperparameter Search
- 모델: **SVR**
- 탐색: **RandomizedSearchCV**
- 설정: `n_iter=5`, `cv=5`, `scoring='neg_mean_squared_error'` :contentReference[oaicite:12]{index=12}

### Best SVR Parameters
최종 도출된 최적 SVR 파라미터: :contentReference[oaicite:13]{index=13}  
- `SVR(C=10, kernel='rbf', epsilon=0.01, gamma=1)`

### Test Performance (per target)
학습 후 테스트 데이터 예측 성능(슬라이드 표기 값): :contentReference[oaicite:14]{index=14}  
- `Average_T` : 0.9970  
- `Torque_Ripple` : 0.9952  
- `Cogging_T` : 0.9958  
- `Slot_Area` : 0.9907  

> ※ README에는 위 값이 **R²인지 / (1-Error)인지** 지표명을 함께 명시하는 것을 권장합니다.

---

## 5. Feature Importance (Permutation Importance)

각 대리모델에서 변수 영향도를 보기 위해 `Permutation_importance`를 적용했습니다. :contentReference[oaicite:15]{index=15}

### Key Findings
- `average_T` : **V_rotor_r1** 중요 :contentReference[oaicite:16]{index=16}  
- `Torque_Ripple` : **V_rotor_r1**, **V_Opening_W** 중요 :contentReference[oaicite:17]{index=17}  
- `Cogging_T` : **V_Opening_W** 중요 :contentReference[oaicite:18]{index=18}  
- `Slot_Area` : **V_Tooth_W**, **V_Shoe_A** 중요 :contentReference[oaicite:19]{index=19}  

(슬라이드 표: Permutation importance 값) :contentReference[oaicite:20]{index=20}  
- V_rotor_r1 / V_Opening_A / V_Opening_W / V_Shoe_A / V_Shoe_W / V_Tooth_W

> 음수(0 근처)는 “섞어도 성능이 거의 안 떨어짐(잡음 수준)”으로 해석 가능.

---

## 6. NSGA-III Optimization Setup

최적화 설정 요약: :contentReference[oaicite:21]{index=21}

- **Problem**
  - `n_var=6`, `n_obj=3`, `n_constr=1`
  - bounds: `xl, xu`는 모델 조건 사용 :contentReference[oaicite:22]{index=22}

- **Reference Directions**
  - method: `"das-dennis"`
  - `n_partitions = 40`
  - `pop_size = 861` :contentReference[oaicite:23]{index=23}

- **Crossover**
  - SBX (Simulated Binary Crossover)
  - `prob=0.9`, `eta=15` :contentReference[oaicite:24]{index=24}

- **Mutation**
  - PolynomialMutation :contentReference[oaicite:25]{index=25}

- **Termination**
  - `xtol=1e-8`, `ftol=0.0025`, `cvtol=1e-6`
  - up to **3000 generations** :contentReference[oaicite:26]{index=26}

---

## 7. Results: Pareto Front Analysis

Pareto Front 시각화 결과:
- 파란색: 최종 population
- 빨간색: Pareto Front (비지배해) :contentReference[oaicite:27]{index=27}  

관찰:
- Pareto Front가 **명확한 경계**를 형성
- 비지배해가 **고르게 분포** → 다양한 트레이드오프 확보
- 일부 **계단식(step-like) 패턴** → 목표 간 트레이드오프 반영 :contentReference[oaicite:28]{index=28}  

---

## 8. Conclusion

- Surrogate(SVR)로 3개 목적함수 + 1개 제약을 근사하고 NSGA-III로 최적화를 수행하여,
  제약을 만족하는 후보군에서 **다양한 Pareto-optimal 해집합**을 도출했습니다. 

### Future Work (optional)
- Pareto 후보 해를 원 시뮬레이션/실험으로 재검증하여 surrogate bias 보정
- 불확실도 기반 샘플링(Active Learning)으로 데이터 효율 개선

---

## References
- NSGA-III (Non-dominated Sorting Genetic Algorithm III)
- scikit-learn SVR / RandomizedSearchCV
- pymoo (NSGA-III implementation)
