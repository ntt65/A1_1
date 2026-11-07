# 파일 안내

작업 전 [AGENTS.md](AGENTS.md)를 읽고, 기능으로 찾을 때는 [reverse_index.md](reverse_index.md)를 사용한다. 계획과 완료 여부는 아래 문서를 기준으로 한다.

| 파일 | 역할 |
| --- | --- |
| [README.md](README.md) | 환경·표본·실행·결과 안내와 하단 파일 트리·클래스 구조·실행 Mermaid 차트 |
| [docs/a1_1_detailed_plan.md](docs/a1_1_detailed_plan.md) | 통합 구현 계획·계산 정의·평가 매핑·QA |
| [docs/a1_1_checklist.md](docs/a1_1_checklist.md) | 완료 여부와 검증 증거 |
| [docs/a1_1_mission.md](docs/a1_1_mission.md) | 미션 원문 |
| [docs/a1_1_eval.md](docs/a1_1_eval.md) | 평가 기준 Markdown 원본 |
| [2차 네이토 평가](docs/naito_eval_result2.md) · [최종 네이토 평가](docs/naito_eval_result.md) | 17/19에서 19/19로 변경. 1차 이력과 대응은 [통합 계획](docs/a1_1_detailed_plan.md#네이토-평가-보완-계획), 권고 반영은 [체크표](docs/a1_1_checklist.md#최종-권고와-자체-점검) |
| [docs/a1_1_eval_review.md](docs/a1_1_eval_review.md) | PDF·Markdown 자료 대조와 검토 의견 |
| [docs/a1_1_evaluation_qa.md](docs/a1_1_evaluation_qa.md) | 평가 문항 19개 Q&A·SRC·시연·준비 계획 |
| [docs/presentation/a1_1_eval_technical_final.pptx](docs/presentation/a1_1_eval_technical_final.pptx) | 질문별 기술 발표31장·실제 결과·보너스·발표자 노트 |
| [docs/presentation/README.md](docs/presentation/README.md) | 질문-페이지 매핑·발표·PPT 재생성 안내 |
| [utils/build_eval_presentation.mjs](utils/build_eval_presentation.mjs) · [utils/eval_presentation_content.mjs](utils/eval_presentation_content.mjs) | 현재 실행 결과를 활용한 재사용 PPT 작성·검증과 질문별 원고 |
| [docs/tech_study.md](docs/tech_study.md) | 미션·평가 용어와 기술 원리·예시·구현 위치 |
| [docs/ai1_1_mission.pdf](docs/ai1_1_mission.pdf) · [docs/a1_1_eval.pdf](docs/a1_1_eval.pdf) | 원본 PDF |
| [src/pipeline.py](src/pipeline.py) | DataAnalyzer 상태·로드·조인·피처·정제·RFM 및 CLI |
| [utils/__init__.py](utils/__init__.py) | 공용 도구 패키지 |
| [utils/image_features.py](utils/image_features.py) | 픽셀 정규화·상품별 이미지 배치 통계·JPEG 읽기/디코딩/전처리 계측 |
| [utils/run_checks.py](utils/run_checks.py) | 가상 입력 검증·선택적 새 커널 노트북 실행 |
| [tests/test_pipeline.py](tests/test_pipeline.py) | B1~B4 회귀 검증, 실제 데이터 불필요 |
| [notebooks/analysis_report.ipynb](notebooks/analysis_report.ipynb) | 실제 데이터·ID·이미지·통계·RFM과 원본 실행 출력 |
| [notebooks/prepare_hm_sample.ipynb](notebooks/prepare_hm_sample.ipynb) | Kaggle에서 필요한 거래·상품·이미지만 추출 |
| [scripts/restore_hm_sample.py](scripts/restore_hm_sample.py) | 비공개 표본 ZIP 검사·안전한 로컬 복원 |
| [utils/analytics.py](utils/analytics.py) | 거래 정제·결측·IQR·RFM·세그먼트 프로파일 |
| [utils/reporting.py](utils/reporting.py) | 상관·월별 집계·필수 차트·인사이트 |
| [utils/reproducibility.py](utils/reproducibility.py) | 새 복제본·새 환경의 전체 결과 대조 |
| [utils/repository_checks.py](utils/repository_checks.py) | 제출 파일·링크·출력·공개 데이터 제외 검사 |
| [tests/test_repository_checks.py](tests/test_repository_checks.py) | Markdown 인용 코드·정상 링크·깨진 상대 링크의 회귀 검증 |
| [tests/test_analytics.py](tests/test_analytics.py) · [tests/test_reporting.py](tests/test_reporting.py) | 손계산·원본 보존·월 누락·상관 경계 검증 |
| [requirements.txt](requirements.txt) | 검증 버전으로 고정한 분석용 의존성 |
| [requirements-notebook.txt](requirements-notebook.txt) | 별도 노트북 실행 의존성 |
| [.gitignore](.gitignore) | 데이터·환경·인증 설정·임시 출력 제외 |

`data/raw/hm/`의 표본, `data/drive_source.json`의 개인 연결 정보, `data/processed/`의 실행 결과는 로컬 전용이며 Git에 없다. 검증 명령은 [AGENTS.md](AGENTS.md), 다음 작업은 [체크표](docs/a1_1_checklist.md)에서 확인한다.

| 추가 파일 | 역할 |
| --- | --- |
| [utils/publish_report.py](utils/publish_report.py) | 원본 실행본·차트 보존과 보조 집계 보고서 생성 |
| [tests/test_publication.py](tests/test_publication.py) | 원본 필드·실행본 바이트 보존과 오류 실행 거부 검증 |
| [docs/results/analysis_report.md](docs/results/analysis_report.md) | 원본·노트북 stdout 없이 집계 구조에서 생성한 정적 보고서 |
| [docs/results/analysis_aggregates.json](docs/results/analysis_aggregates.json) | 설정·집계·통계·검증 결과 |
| [docs/results/segment_profile.csv](docs/results/segment_profile.csv) · [docs/results/monthly_amount.csv](docs/results/monthly_amount.csv) | 공개 고객 그룹·월별 집계 |

공개 차트 6종은 `docs/results/figures/`에 있고 README 본문에서 볼 수 있다. 원본 표본·개인 연결 설정은 계속 로컬 전용이다.

| 보너스 파일 | 역할 |
| --- | --- |
| [utils/bonus.py](utils/bonus.py) | 첫 관찰 구매월 코호트·히트맵·Plotly RFM |
| [tests/test_bonus.py](tests/test_bonus.py) | 히스토그램·엣지·분모·미관측·원본 관측 보존 |
| [requirements-bonus.txt](requirements-bonus.txt) | 보너스 전용 고정 의존성 |
| [docs/results/bonus/rfm_interactive.html](docs/results/bonus/rfm_interactive.html) | 원본1000고객의 독립 실행 Plotly HTML |
| [docs/results/bonus/cohort_retention.csv](docs/results/bonus/cohort_retention.csv) | 첫 구매월 코호트 월별 활동 비율 |
