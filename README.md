# 이커머스 멀티모달 데이터 분석 프로젝트

## 프로젝트 개요
이 프로젝트는 이커머스 멀티모달 데이터(수치, 텍스트, 범주, 이미지 배열)를 활용해
고객 세분화(RFM)와 분석 파이프라인을 구축하는 것을 목표로 합니다.

구현 순서와 평가·QA 준비는 [통합 상세 계획](docs/a1_1_detailed_plan.md), 완료 여부와 검증 기록은 [작업 체크표](docs/a1_1_checklist.md)에서 관리합니다.

파일 안내는 [index.md](index.md), 기능별 수정 위치는 [reverse_index.md](reverse_index.md)에 있습니다. 재사용·주석·검증 반복 절차와 필요한 파일만 읽는 방법은 [AGENTS.md](AGENTS.md)에 정리했습니다.

## 실행 방법
1. Python 환경을 준비합니다. 현재 검증 환경은 Python 3.11.4입니다. Windows에서는 `py -3.11 -m venv .venv`로 가상환경을 만듭니다.
2. 의존성 설치:
   ```powershell
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
3. 아래 절차로 H&M 표본을 준비한 뒤 거래 로드와 상품 조인을 확인합니다.
   ```powershell
   .venv\Scripts\python.exe src/pipeline.py --data data/raw/hm/transactions_sample.csv --products data/raw/hm/articles_sample.csv
   ```

## B1~B4 실행과 검증

현재 거래·상품 연결, 이미지 평균·표준편차, 상품명 길이·단어 수를 구현했습니다. 공용 이미지 처리는 `utils/image_features.py`에서 재사용하고 `DataAnalyzer`가 피처를 거래에 연결합니다. ID의 선행 0을 보존하며, 상품 키가 중복이면 조인을 중단합니다.

가상 입력 검증에는 실제 표본과 Jupyter가 필요하지 않습니다.

```powershell
.venv\Scripts\python.exe -B -m utils.run_checks
```

실제 표본이 복원되어 있으면 노트북 실행 도구를 별도로 설치하고 검증합니다.

```powershell
.venv\Scripts\python.exe -m pip install notebook ipykernel
.venv\Scripts\python.exe -B -m utils.run_checks --with-sample
```

이 명령은 현재 가상환경의 새 커널에서 `notebooks/analysis_report.ipynb`를 실행합니다. 출력이 포함된 노트북은 `data/processed/analysis_report.executed.ipynb`, 조인·이미지 상태·배치 정보는 `data/processed/b1_b4_verification.json`에 저장합니다. 공개 저장소의 노트북은 실제 데이터 출력을 비웁니다. 직접 열려면 저장소 루트에서 `.venv\Scripts\python.exe -m notebook notebooks/analysis_report.ipynb`를 실행합니다.

정제·RFM 정의 보완과 최종 통계·차트·인사이트는 통합 계획 C~F에서 이어서 구현합니다. 현재 노트북의 가상 RFM 호출은 메서드 연결만 점검합니다.

## H&M 표본 준비

접근 권한이 있는 Google Drive 계정에서 `A1_1_hm_sample.zip`을 내려받아 아래 명령을 실행합니다. 명령의 ZIP 경로는 실제 다운로드 위치로 바꿉니다.

```powershell
python scripts/restore_hm_sample.py --archive "C:\Downloads\A1_1_hm_sample.zip"
```

복원 도구는 ZIP의 파일 구성과 추출 기록을 검사한 뒤 `data/raw/hm/`에 거래 CSV, 상품 CSV와 이미지 표본을 준비합니다. 같은 파일로 재실행할 수 있으며, 내용이 다른 기존 파일이 있으면 해당 경로를 표시합니다. `data/raw/hm/hm_sample.zip`에 ZIP을 보관한 경우 `--archive`를 생략할 수 있습니다.

연결된 작업 환경에서는 비공개 Drive 주소와 SHA-256을 Git에서 제외된 `data/drive_source.json`에 보관합니다. 설정이 있으면 복원 전에 ZIP의 SHA-256을 대조합니다. 다른 환경에서 표본을 직접 만들려면 대회 데이터 접근 권한을 확보한 뒤 [표본 추출 노트북](notebooks/prepare_hm_sample.ipynb)을 사용합니다. [H&M 대회 규정](https://www.kaggle.com/c/h-and-m-personalized-fashion-recommendations/rules)

표본의 크기와 관계없이 ZIP·CSV·이미지는 공개 Git에 넣지 않고 본인만 접근하는 Drive와 로컬에서 관리합니다. 대회 규정 7절은 비상업·교육 목적의 사용을 허용하며 비참가자에게 데이터를 제공하는 행위를 제한합니다. 실제 집계 수치와 차트의 제출 범위는 체크표 A1·F2에서 별도로 확인합니다.

## 데이터 설명
- **수치형 데이터**: 구매 금액, 수량 등
- **텍스트 데이터**: 상품명, 상품 설명 등
- **범주형 데이터**: 고객 등급, 카테고리 등
- **이미지 배열 데이터**: NumPy 배열 형태의 이미지 피처

## 비즈니스 인사이트 템플릿
아래 형식으로 분석 결과를 정리하세요.

- **(근거)**: 데이터/지표/시각화로 확인한 핵심 사실
- **(실행)**: 비즈니스에서 수행할 액션 아이템
- **(검증)**: 실행 후 성과를 측정할 KPI 및 검증 방법
