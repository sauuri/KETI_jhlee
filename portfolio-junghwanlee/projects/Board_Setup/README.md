## Board Setup

임베디드 보드(Raspberry Pi, Variscite DART-6UL) 세팅 및 운영환경 구성 과정을 정리한 문서 모음입니다.

---

## 폴더 구조

```
Board_Setup/
├── RaspberryPi/
│   ├── 라즈베리파이 pip list 설치(requirements).pdf
│   ├── 라즈베리파이 메모리 할당 결과 정리.pdf
│   └── RaspberryPi_clock_speed_bashrc.jpg
└── Variscite/
    ├── Variscite 보드 시스템 사양 및 운영환경 정리.pdf
    └── Varisite_보드_pip3_install_numpy_실패.txt
```

---

## Raspberry Pi

### 시스템 환경

| 항목 | 내용 |
|------|------|
| 모델 | Raspberry Pi 5 / 3A+ |
| 아키텍처 | aarch64 (64-bit ARM) |
| Python | 3.11+ |

---

### pip 패키지 오프라인 설치 (`라즈베리파이 pip list 설치(requirements).pdf`)

인터넷이 연결된 Raspberry Pi 5에서 패키지를 다운로드한 뒤, USB를 통해 Raspberry Pi 3A+에 오프라인으로 설치하는 방법을 정리한 문서.

**Step 1. requirements.txt 생성 (Raspberry Pi 5)**
```bash
pip list --format=freeze > requirements.txt
```

**Step 2. 64비트 wheel 파일 다운로드**
```bash
mkdir -p wheelhouse_64bit
pip download --only-binary=:all: --platform manylinux2014_aarch64 \
    -d wheelhouse_64bit -r requirements.txt
```

**Step 3. USB에 복사**
```bash
cp -r wheelhouse_64bit /media/keti/USB_DRIVE_NAME/
sudo umount /media/keti/USB_DRIVE_NAME
```

**Step 4. Raspberry Pi 3A+에서 설치**
```bash
cp -r /media/keti/USB_DRIVE_NAME/wheelhouse_64bit ~/
cd ~/wheelhouse_64bit
pip install *.whl --break-system-packages
```

**Step 5. 설치 확인**
```python
import numpy, pandas, sklearn
print(numpy.__version__, pandas.__version__, sklearn.__version__)
```

---

### 메모리 할당 실험 (`라즈베리파이 메모리 할당 결과 정리.pdf`)

Raspberry Pi 5에서 대용량 데이터 처리 시 메모리 효율을 검토한 실험.

#### 실험 1 — 희소 행렬(Sparse Matrix) 압축 효과 검증

- **데이터**: 광소자 데이터 shape `(5622, 513, 10)` / 코에버 데이터 `(1374534, 114)`
- **방법**: float64 → float32 변환 후 CSR 희소 행렬 변환

| 데이터 | float32 원본 | 희소 행렬 변환 후 | 결과 |
|--------|-------------|-----------------|------|
| 광소자 | 110.59 MB | 232.25 MB | 증가 (0이 적음) |
| 코에버 | 597.75 MB | 402.51 MB | 감소 (0이 많음) |

> 희소 행렬은 0의 비율이 높은 데이터에서만 효과적이며, 적용 전 0의 비율 확인이 필요함

#### 실험 2 — ctypes 3D 배열 동적 할당 및 CPU Governor 성능 비교

- **환경**: Raspberry Pi 5, 메모리 크기 `1000x1000x1000` (float32, 약 3.81 GB)
- **방법**: `np.ctypeslib.as_ctypes()`로 Numpy 메모리를 ctypes에 직접 연결 (기존 방식 대비 속도 대폭 개선)

| 조건 | 평균 데이터 생성 | 메모리 할당 | 값 조회 |
|------|----------------|-----------|---------|
| CPU ondemand | 17.67 초 | 0.000375 초 | 0.000033 초 |
| CPU powersave (400MHz) | 58.46 초 | 0.059617 초 | 0.000347 초 |

> powersave 모드에서 데이터 생성이 약 3배, 값 조회가 약 10배 느려짐

**3D 배열 → 1D 인덱스 변환 공식**
```
index = (x * cols * depth) + (y * depth) + z
element_address = base_address + index * sizeof(c_float)
```

---

## Variscite

### 시스템 사양 (`Variscite 보드 시스템 사양 및 운영환경 정리.pdf`)

| 항목 | 값 |
|------|-----|
| 보드 모델 | Variscite DART-6UL |
| SoC | NXP i.MX6ULL |
| CPU | ARM Cortex-A7, 싱글코어, armv7l |
| 클럭 범위 | 198 ~ 792 MHz (단계: 198 / 396 / 528 / 792 MHz) |
| RAM | ~490 MiB DDR3 |
| 저장장치 | 7.3 GB eMMC |
| OS | NXP i.MX Release Distro 5.4-zeus (Yocto 기반) |
| 커널 | Linux 5.4.3 |
| 기능 | eMMC & WiFi 내장 |
| 베이스 보드 | VAR-6ULCustomBoard |

#### 시리얼 접속 방법 (PuTTY)

```
Connection type : Serial
Serial line     : COM3
Speed           : 115200
```

빈 화면에서 보드 전원 On → `login: root` 입력

#### CPU Governor 설정 확인

```bash
cd /sys/devices/system/cpu/cpu*/cpufreq
cat scaling_governor          # 현재 정책 (기본: ondemand)
cat scaling_available_governors  # conservative powersave ondemand performance
cat scaling_available_frequencies  # 198000 396000 528000 792000
```

#### 시스템 모니터링

```bash
top           # CPU 사용률 확인
free -h       # RAM 상태 확인
df -h         # eMMC 저장 공간 확인
lsblk         # 블록 장치 목록
```

#### 운영 중 CPU 사용 현황

| 항목 | 값 | 비고 |
|------|-----|------|
| us (사용자) | 19.6% | |
| sy (커널) | 71.7% | 백그라운드 데몬 과부하 |
| id (여유) | 8.7% | CPU 거의 풀 사용 |
| 주요 프로세스 | amid, rtud | 각각 CPU 25~28% 점유 |

---

### numpy 설치 실패 로그 (`Varisite_보드_pip3_install_numpy_실패.txt`)

Variscite 보드(armv7l, Python 3.7)에서 `pip3 install numpy` 실패 기록.

**실패 원인**
- BLAS / LAPACK 라이브러리 미설치
- Fortran 컴파일러(`gfortran` 등) 미설치
- 크로스 컴파일러(`arm-poky-linux-gnueabi-gcc`) 없음
- 빌드 툴체인 불완전 → `RuntimeError: Broken toolchain`

**소요 시간**: 약 74분 후 최종 실패

```
ERROR: Failed building wheel for numpy
ERROR: Could not build wheels for numpy, which is required to install pyproject.toml-based projects
```

> armv7l 환경에서는 소스 빌드 대신 사전 빌드된 wheel 파일(`.whl`) 또는
> `opkg` 패키지 매니저를 통한 설치를 권장함
