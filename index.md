# 파일 안내

작업 전 [AGENTS.md](AGENTS.md)를 읽고, 기능으로 찾을 때는 [reverse_index.md](reverse_index.md)를 사용한다. 계획과 완료 여부는 아래 문서를 기준으로 한다.

| 파일 | 역할 |
| --- | --- |
| [README.md](README.md) | 환경 설치, 비공개 표본 복원, 실행 안내 |
| [docs/a1_1_detailed_plan.md](docs/a1_1_detailed_plan.md) | 통합 구현 계획·계산 정의·평가 매핑·QA |
| [docs/a1_1_checklist.md](docs/a1_1_checklist.md) | 완료 여부와 검증 증거 |
| [docs/a1_1_mission.md](docs/a1_1_mission.md) | 미션 원문 |
| [docs/a1_1_eval.md](docs/a1_1_eval.md) | 평가 원문 |
| [docs/ai1_1_mission.pdf](docs/ai1_1_mission.pdf) · [docs/a1_1_eval.pdf](docs/a1_1_eval.pdf) | 원본 PDF |
| [src/pipeline.py](src/pipeline.py) | DataAnalyzer 상태·로드·조인·피처·정제·RFM 및 CLI |
| [utils/__init__.py](utils/__init__.py) | 공용 도구 패키지 |
| [utils/image_features.py](utils/image_features.py) | 픽셀 정규화·상품별 이미지 배치 통계 |
| [utils/run_checks.py](utils/run_checks.py) | 가상 입력 검증·선택적 새 커널 노트북 실행 |
| [tests/test_pipeline.py](tests/test_pipeline.py) | B1~B4 회귀 검증, 실제 데이터 불필요 |
| [notebooks/analysis_report.ipynb](notebooks/analysis_report.ipynb) | 실제 분석의 설정·클래스 호출·해석, 공개본 출력 비움 |
| [notebooks/prepare_hm_sample.ipynb](notebooks/prepare_hm_sample.ipynb) | Kaggle에서 필요한 거래·상품·이미지만 추출 |
| [scripts/restore_hm_sample.py](scripts/restore_hm_sample.py) | 비공개 표본 ZIP 검사·안전한 로컬 복원 |
| [requirements.txt](requirements.txt) | 분석용 의존성 |
| [.gitignore](.gitignore) | 데이터·환경·인증 설정·임시 출력 제외 |

`data/raw/hm/`의 표본, `data/drive_source.json`의 개인 연결 정보, `data/processed/`의 실행 결과는 로컬 전용이며 Git에 없다. 검증 명령은 [AGENTS.md](AGENTS.md), 다음 작업은 [체크표](docs/a1_1_checklist.md)에서 확인한다.
