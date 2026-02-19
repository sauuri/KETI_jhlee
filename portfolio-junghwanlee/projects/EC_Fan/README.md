<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/03e36c80-8000-43e6-a373-cdc42298109a" />

# EC-Fan 모터 3목적 다목적 최적화 (NSGA-III)

## 개요
본 프로젝트는 **EC-Fan용 모터**의 성능을 개선하기 위해 **NSGA-III 기반 다목적 유전알고리즘**으로 최적화를 수행했다.  
서로 상충하는 3개의 목적함수를 동시에 고려하여, 단일 최적해가 아닌 **Pareto 최적해 집합(Pareto Front)**을 도출하고 그 중 우선순위에 맞는 후보를 선택하는 방식으로 진행했다.

## 목적함수 (3)
- **토크 리플(Torque Ripple) 최소화**
- **코깅 토크(Cogging Torque) 최소화**
- **효율(Efficiency) 최대화**

## 방법
- **Algorithm:** NSGA-III (Multi-objective Genetic Algorithm)
- **Selection:** Pareto 기반 비지배 정렬 + 다목적 분산 유지를 위한 참조점(Reference Points) 활용
- **Output:** Pareto Front 및 최종 후보 솔루션

## 결과 요약
- 토크 품질(리플/코깅)과 효율 간 **트레이드오프**를 반영한 Pareto 해 집합을 확보했다.
- Pareto Front 상에서 요구 성능 우선순위에 맞춰 **최적 후보 해를 선택**할 수 있다.

## 키워드
EC-Fan, Motor Optimization, Multi-objective Optimization, Genetic Algorithm, NSGA-III, Pareto Front, Torque Ripple, Cogging Torque, Efficiency

