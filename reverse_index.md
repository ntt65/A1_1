# 기능에서 수정 위치 찾기

파일 목록은 [index.md](index.md), 작업 규칙은 [AGENTS.md](AGENTS.md), 구현 정의는 [통합 계획](docs/a1_1_detailed_plan.md)을 참고한다. 이 문서는 계획이나 완료 기록을 중복 관리하지 않는다.

| 필요하거나 바꿀 기능 | 시작 위치 | 함께 확인할 영향 |
| --- | --- | --- |
| 표본 기간·채널·시드·이미지 수 변경 | `notebooks/prepare_hm_sample.ipynb` 설정 | 분석 노트북 설정·manifest 대조·A3~A4 |
| Drive ZIP 복원·무결성·기존 파일 충돌 | `scripts/restore_hm_sample.py::restore_sample/main` | README 복원 안내·로컬 Drive 설정 |
| CSV 필수 열·ID 선행 0·날짜 변환 | `src/pipeline.py::DataAnalyzer.load_data` | `tests/test_pipeline.py`·`NB_LOAD` |
| 상품 키·다대일 조인·행 수·금액 보존 | `src/pipeline.py::DataAnalyzer.join_products` | 조인 회귀 검증·`NB_LOAD`·B2 |
| 회색조·RGB·RGBA·정규화·축소 | `utils/image_features.py::prepare_image` | 이미지 회귀 검증·B3~B4 |
| 이미지 상태·배치 크기·평균/표준편차 | `utils/image_features.py::extract_product_image_features` | `DataAnalyzer._extract_image_files`·`NB_FEATURES` |
| 배열 열의 기존 이미지 API | `src/pipeline.py::DataAnalyzer.extract_image_features` | 가상 배열 기대값·기존 호출 호환성 |
| 상품명 길이·단어 수 | `src/pipeline.py::DataAnalyzer.extract_text_features` | 상품별 계산·거래 매핑·B4 |
| 결측 대치·IQR·RFM | `src/pipeline.py::handle_missing_values/detect_outliers/calculate_rfm` | 계획 C1~C5·QA Q5~Q7·후속 회귀 검증 |
| 실제 분석 호출·설정·차트·해석 | `notebooks/analysis_report.ipynb`의 `NB_*` 구간 | 파이프라인 공용 API·체크표 D·출력 공개 범위 |
| 검증 실행·현재 가상환경 커널·출력 위치 | `utils/run_checks.py::main/run_notebook` | 회귀 검증·실행된 로컬 노트북·README |
| 허용 라이브러리·설치 환경 | `requirements.txt`·README | 미션 원문·평가 원문·P0 |
| 데이터 공개·Git 제외 | `.gitignore`·`AGENTS.md` | A1·F2·README·Git 노트북 출력 |
| 작업 순서·계산 기준·평가·QA 변경 | `docs/a1_1_detailed_plan.md` | 체크표·원문과의 일치 |
| 완료 상태·실행 증거 확인 | `docs/a1_1_checklist.md` | 로컬 `data/processed/` 기록 |
| 토큰 절약·수정과 검증 반복 절차 | `AGENTS.md` | 인덱스 최신성·관련 파일만 읽기 |

호출 흐름은 `분석 노트북 → DataAnalyzer → utils.image_features`다. 검증 흐름은 `utils.run_checks → tests`이며, `--with-sample`을 지정하면 `분석 노트북 → data/processed/`까지 실행한다. 로컬 기록에는 실제 표본 수·금액·이미지 상태와 배치 메모리 정보가 있으며, 공개 문서에는 합격 여부와 가상 입력의 기대값을 기록한다.
