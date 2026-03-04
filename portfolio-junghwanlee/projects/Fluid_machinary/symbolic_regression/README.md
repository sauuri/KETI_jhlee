# Symbolic Regression — Fluid Machinery P-Q Curve

P-Q 곡선의 닫힌 수식(closed-form expression)을 도출하기 위해 **gplearn** 및 **PySR** 기반 Symbolic Regression을 적용한 실험 기록.

---

## 목표

각 stroke 조건에서 **Flowrate → Head(압력)** 관계를 수식으로 표현

```
f(x) = a·x + b·cos(c + d·x) + e
```

- 기존 GPR 모델 대비 **해석 가능성(interpretability)** 확보
- 보드 탑재를 위한 **경량 수식** 도출

---

## 도구 비교

| 항목 | gplearn | PySR |
|------|---------|------|
| 언어 | Python | Python + Julia |
| 속도 | 보통 | 빠름 (Julia 가속) |
| 설치 | 간단 | Julia 환경 필요 |
| 수식 품질 | 기본 | 더 높은 정밀도 |

---

## 실험 결과 요약

### 실험 1 — 순수 다항식 (0409)

`docs/이정환_PySR_0409_실험_결과.pdf`

- 사용 함수: `pow2`, `pow3`, `pow4`
- 결과: 중간 비선형 곡률 표현 실패 → sin/cos 오퍼레이터 추가 필요
- RMSE: 0.45682, R²: 0.98685

### 실험 2 — Polynomial + cos (0410)

`docs/0410 실험 계획 및 결과.pdf`

목표 수식 구조:
```
f(x) = a·x + b·cos(c + d·x) + e
```

**PySR 설정:**
```python
niterations = 1000
populations = 50
population_size = 300
binary_operators = ["+", "-", "*", "^"]
unary_operators = ["cos"]
constraints = {"^": (-1, 0), "cos": (-1, 2)}
nested_constraints = {"cos": {"cos": 0}, "^": {"^": 0}}
maxsize = 15
```

**sin vs cos 비교:**

| 실험 | unary_operator | RMSE | R² |
|------|---------------|------|----|
| Polynomial + sin | sin | 0.16228 | 0.99834 |
| Polynomial + cos | cos | 0.15927 | 0.99840 |

→ cos만으로 충분

---

## 7개 Stroke 실험 결과

![per-stroke](plots/flowrate_head_visualization_per_stroke.png)

| Stroke | a | b | c | d | e | RMSE | R² |
|--------|---|---|---|---|---|------|----|
| 15.85 | -1.7189 | 1.4502 | 0.3792 | 1.0000 | 17.3617 | 0.16761 | 0.99822 |
| 45.8  | -1.6842 | 1.8793 | 0.6620 | 0.8985 | 18.1442 | 0.18892 | 0.99761 |
| 69.3  | -1.8760 | 2.5816 | 1.1242 | 0.7696 | 19.7656 | 0.22449 | 0.99621 |
| 74.8  | -2.0467 | 3.0558 | 1.3807 | 0.7094 | 20.7355 | 0.25090 | 0.99620 |
| 82.7  | -2.1508 | 3.3970 | -1.4442 | -0.6881 | 21.5265 | 0.24653 | 0.99625 |
| 93.95 | -2.0008 | 3.4008 | 1.3160 | 0.7041 | 21.5050 | 0.26476 | 0.99558 |
| 104.35| -1.6076 | 2.6261 | -0.8185 | -0.6879 | 20.0742 | 0.29490 | 0.99388 |

> 전체 stroke에서 **R² > 0.993** 달성

---

## 계수 예측 모델 (Stroke → a, b, c, d, e)

stroke → 수식 계수 예측 모델 구축 실험

| 모델 | Parameter | RMSE | R² |
|------|-----------|------|----|
| LinearRegression | a | 0.1814 | 0.0909 |
| LinearRegression | b | 0.3806 | 0.6947 |
| LinearRegression | e | 0.7671 | 0.7341 |
| LR + PolynomialFeatures(2) | b | 0.3344 | 0.7644 |
| LR + PolynomialFeatures(2) | e | 0.6964 | 0.7808 |

### 향후 계획
- `Polynomial + SVR` 조합 시도
- `maxsize` 20~25로 늘려 수식 복잡도 향상

---

## gplearn 기본 테스트

`src/gplearn_test.py`

임의 생성 함수 `sin(x)·log(|x|+1) + tanh(x²-3)` 를 gplearn으로 근사하는 테스트 스크립트.
결과 수식 트리는 `best_program_tree.dot` (Graphviz DOT 형식)에 저장됨.

```bash
pip install -r requirements_gplearn.txt
python src/gplearn_test.py
```

---

## 파일 구조

```
symbolic_regression/
├── src/
│   └── gplearn_test.py          # gplearn 기본 테스트 스크립트
├── docs/
│   ├── 0328_gplearn+PySR_업무_조사.hwpx
│   ├── 0410 실험 계획 및 결과.pdf
│   └── 이정환_PySR_0409_실험_결과.pdf
├── plots/
│   ├── flowrate_head_visualization_per_stroke.png
│   ├── PySR_early_stopping_qkey_enter_result.png
│   ├── 2D_P-Q_Curve+Power+Optimal_Stroke.png
│   ├── 3D_P-Q_Curve+Power+Optimal_Storke.png
│   ├── Find_intersect_points_in_2D_P_Q_curve.png
│   └── flowrate_to_stroke_flowchart.drawio.png
├── gplearn_result.md            # gplearn 실험 결과 이미지
├── best_program_tree.dot        # gplearn 최적 수식 트리 (Graphviz)
├── requirements_gplearn.txt     # gplearn 의존성
├── requirements_pysr.txt        # PySR 의존성
└── README.md
```
