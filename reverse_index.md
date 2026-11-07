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
| 거래 유효성·결측·IQR·RFM 계산 정책 | `utils/analytics.py`·`DataAnalyzer` 대응 메서드 | `tests/test_analytics.py`·NB_CLEAN·NB_RFM |
| 월별 합계·상관·차트·실제 인사이트 | `utils/reporting.py` | `tests/test_reporting.py`·NB_STATS·NB_PLOTS·README |
| 새 복제본·새 가상환경 비교 | `utils/reproducibility.py` | 고정 의존성·로컬 입력·NB_REPRO |
| 제출 파일·링크·Git 제외 검사 | `utils/repository_checks.py` | `tests/test_repository_checks.py`·README·공개 노트북·data 제외 |
| PDF 평가 기준과 현재 Markdown 내용 검토 | `docs/a1_1_eval_review.md` | 원본 PDF·평가 문항·가상 참고 예시 구분 |
| 네이토 판정 대조·다음 제출 | `docs/a1_1_detailed_plan.md`의 네이토 평가 보완 계획 | `docs/naito_eval_result.md`·`docs/naito_eval_result2.md`·재평가 체크표·README 평가 증거 |
| 네이토 #13 IQR 이론·표본 전후 비교 / #17 이미지 병목 설계 | 통합 계획 R1·R2 | README·`NB_CLEAN`·`NB_FEATURES`·평가 Q&A 3-1·4-1·`utils/analytics.py`·`utils/image_features.py` |
| 평가 예상 질문·답변·시연 | `docs/a1_1_evaluation_qa.md` | 19개 문항·SRC·실행 기록·이슈 #6 |
| 평가 PPT·질문별 원고·발표자 노트·도식 | `utils/eval_presentation_content.mjs`·`utils/build_eval_presentation.mjs` | docs/presentation·실제 분석 JSON/그림·질문별 페이지·이슈 #17 |
| 기술·용어·원리 학습 | `docs/tech_study.md` | 미션 필수·선택·제약·코드·QA |
| 토큰 절약·수정과 검증 반복 절차 | `AGENTS.md` | 인덱스 최신성·관련 파일만 읽기 |

호출 흐름은 `분석 노트북 → DataAnalyzer → utils.image_features`다. 검증 흐름은 `utils.run_checks → tests`이며, `--with-sample`을 지정하면 `분석 노트북 → data/processed/`까지 실행한다. `utils.publish_report`는 성공한 실행본을 제출 노트북에 바이트 그대로 복사하고 원본 차트·집계를 보존한다.

| 공개 결과 작업 | 수정 위치 | 함께 확인 |
| --- | --- | --- |
| 원본 실행본·차트·집계 보존 | `utils/publish_report.py` | `tests/test_publication.py`·notebooks·docs/results·README |
| 제출 보고서·실행 오류·그림 검사 | `utils/repository_checks.py` | 실행 노트북·보조 집계·차트6개·data 제외 |
| 최종 실행 설명·성공 로그·SRC | `README.md` | 이슈 #11·집계·실제 명령 |
| 소스 파일 트리·클래스 구조·분석/검증 Mermaid 차트 | `README.md`의 소스 구조와 실행 흐름 | `src/pipeline.py`의 실제 속성·메서드·노트북 NB 순서·utils 호출·이슈 #14 |

| 보너스 변경 | 시작 위치 | 함께 확인 |
| --- | --- | --- |
| 이미지 히스토그램·인접 절대차 | `utils/image_features.py::advanced_image_statistics` | DataAnalyzer advanced 옵션·NB_BONUS_IMAGES·test_bonus |
| 코호트 분모·관측 기간·미래NaN | `utils/bonus.py::cohort_retention` | NB_BONUS_COHORT·CSV·히트맵·README 기준 |
| Plotly 3D·원본ID hover·독립 HTML | `utils/bonus.py::interactive_rfm` | NB_BONUS_PLOTLY·requirements-bonus·원본 결과 보존 |
