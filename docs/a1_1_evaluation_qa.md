# A1 1 평가 대비 Q&A와 시연 순서

기준: [평가 PDF](a1_1_eval.pdf) 15~17페이지와 [평가 Markdown](a1_1_eval.md)의 평가 문항. 자료 대조 의견은 [검토 문서](a1_1_eval_review.md), 용어 해설은 [tech_study.md](tech_study.md)다. 이슈 #6에서 관리한다.

[실행 증거](#평가용-실행-증거) · [미션·평가 대응표](#미션-요구사항과-평가문항-대응표) · [네이토 평가](#네이토-평가) · [발표자료](#평가-기술-발표자료) · [평가 문항별 Q&A](#5-평가문항)

## 이 문서 읽는 법

평가 문항 순서 그대로 답변을 정리했다. 처음 보는 사람도 읽고 바로 말할 수 있도록 모든 답변을 같은 틀로 썼다.

| 순서 | 내용 |
| --- | --- |
| **한 줄 답** | 질문에 대한 답을 먼저 말한다. |
| **용어** | 처음 나오는 말을 한 줄로 풀이한다. |
| **작은 예** | 손으로 계산할 수 있는 예제다. 대부분 회귀 테스트로 확인한 값이며 README의 [검증을 직접 재현할 작은 입력](../README.md#검증을-직접-재현할-작은-입력)에도 있다. |
| **실제 결과** | 이 프로젝트의 H&M 표본에서 나온 수치다. |
| **왜 이렇게** | 설계 이유다. 평가자가 이어서 물을 가능성이 큰 부분이다. |
| **보여줄 곳** | 코드·노트북·그림 링크를 여기에만 모았다. |

답변은 말로 하는 상황을 생각해 존댓말로 썼다. 같은 주제가 여러 문항에 나오면 뒤 문항에서 앞 문항을 가리키며 이어 간다.

## 연습과 증거 준비

노트북 링크의 `In [번호]`는 노트북 화면에서 확인할 실행 셀이고, 줄 번호는 저장된 소스와 출력의 위치를 가리킨다. 실제 계산 결과는 로컬 `data/processed/analysis_report.executed.ipynb`와 `analysis_verification.json`, 새 환경 비교는 `reproduction_verification.json`에서 확인한다. 평가 노트북은 원본 데이터·ID·이미지 예시와 실행 출력을 그대로 보존한다. 실제 집계 출력·검토한 차트는 `docs/results/analysis_report.md`와 `docs/results/analysis_aggregates.json`에서도 확인할 수 있다. 사용자 지시에 따라 평가 실행 결과는 마스킹하지 않는다. 실행과 제출 요약은 [README](../README.md)에서 확인한다.

```powershell
.venv\Scripts\python.exe -B -m utils.run_checks --with-sample
.venv\Scripts\python.exe -B -m utils.reproducibility
```

실데이터 접근 전에 환경·표본 준비가 필요하다. 원본을 공유하지 않는 자리에서는 아래 작은 예와 공개 소스를 사용하고 실제 검증 여부를 구분해 말한다.

## 평가용 실행 증거

### 평가 문항별 결과 위치

아래 번호는 네이토 평가 항목 #1~#19를 가리킨다.

| 항목 | 실제 결과와 확인 위치 | SRC |
| --- | --- | --- |
| 1–3 · 클래스·실행·입력 | 결측 처리 두 이름은 같은 구현을 호출한다. `NB_LOAD` (`1196c1cf`)에 `head()`, `info()`, `describe()`와 조인 후 8,084행·9열을 저장했다. `NB_REPRO`까지 실행됐다. | [DataAnalyzer](../src/pipeline.py) · [호환 회귀 테스트](../tests/test_analytics.py) |
| 4 · 파생 피처 | `NB_FEATURES` (`936e811c`)에 `image_mean`, `image_std`, `prod_name_length`, `prod_name_word_count` 및 가상 입력 `Blue cotton shirt`의 17자·3단어가 나온다. 관측 이미지는 상품 200개의 피처다. | [피처 메서드](../src/pipeline.py) · [NumPy 이미지 배치](../utils/image_features.py) |
| 5–6 · IQR·그림 | `NB_CLEAN` (`a32f822f`)에서 212행 탐지, 하한 −0.012729·상한 0.061847. `NB_PLOTS` (`87a953b4`)에서 전후 박스플롯과 나머지 다섯 차트를 출력한다. | [clip_outliers](../src/pipeline.py) · [make_figures](../utils/reporting.py) |
| 7 · 기술통계·상관 | `NB_STATS` (`333254fa`)에서 상품 200쌍 `r=-0.9435`, 고객 1,000쌍 `r=0.6397`을 표본 수 및 해석과 함께 보여준다. | [summarize](../src/pipeline.py) · [pair_correlation](../utils/reporting.py) |
| 8 · 고객군·인사이트 | `NB_RFM` (`b4769e15`)에서 VIP 270명, Churned 499명, New 149명, Loyal 82명. [비즈니스 인사이트](../README.md#비즈니스-인사이트)의 3건은 각 그룹 행을 근거로 삼는다. | [RFM 계산과 분류](../utils/analytics.py) · [인사이트](../README.md#비즈니스-인사이트) |
| 9–12 · 책임·축·설정·판단 근거 | [입력과 계산 기준](../README.md#입력과-계산-기준)과 [분석 흐름](../README.md#분석-흐름과-원본-보존)의 메서드·설정 표에 입력과 상태 변화가 있다. `NB_FEATURES`는 이미지 N을 보존하고 H·W·C만 축약한다. `NB_CLEAN`은 EDA 사본, `NB_RFM`은 유효 원금액을 사용한다. | [클래스](../src/pipeline.py) · [이미지 집계](../utils/image_features.py) · [#11 설정 검토](#설정-기본값과-탐색-범위) · [의사결정 기록](a1_1_detailed_plan.md#q11-분석-의사결정을-노트북에-어떻게-남기는가) |
| 13 · IQR의 통계적 필요성과 한계 | 같은 `1.5×IQR`의 이론 경계 밖 비율은 정규 약 0.70%, 오른쪽 꼬리가 긴 로그정규 예시 약 7.76%다. `NB_CLEAN` (`a32f822f`)의 실제 거래는 상한 초과 212행, 보정 후 분산 −17.21%, 중앙값 동일이다. | [평가 Q&A 3-1](#3-1) · [실제 전후 표](../README.md#iqr의-통계적-필요성과-한계) · [IQR 상세 해설](tech_study.md#사분위수quartile와-iqr-기반-이상치-탐지-및-클리핑) · [iqr_limits](../utils/analytics.py) · [clip_outliers](../src/pipeline.py) |
| 14–16 · 대치·점수·배치 | `NB_CLEAN`의 이미지 평균 대치 전후 분산은 0.010424 → 0.010130이다. RFM 동점 테스트와 `NB_FEATURES`의 NumPy 배치 축 설명도 확인할 수 있다. | [대치·RFM](../utils/analytics.py) · [동점 테스트](../tests/test_analytics.py) · [배치 계산](../utils/image_features.py) |
| 17 · 대규모 이미지 병목과 개선 | 실제 이미지 200장 계측에서 읽기+디코딩이 전체의 약 85%였다. `NB_FEATURES` 설명 셀 `923b9a03`에 상품 피처 캐시, 제한된 병렬 로드, 유한 대기열, 표본 선정과 워커별 검증 설계를 기록했다. | [병목 진단과 확장 설계](#대규모-이미지-처리의-병목과-개선-설계) · [이미지 처리](../utils/image_features.py) |
| 18–19 · 사업 활용과 예측 확장 | 캠페인 대조군과 30일 목표 예시, 기준시점 T까지의 피처와 미래 30일 라벨의 분리 설계를 확인한다. | [캠페인 실험](#4-2) · [예측 확장](#4-3) |

### 미션 요구사항과 평가문항 대응표

미션 구현은 README의 분석 흐름으로 설명하고, 질의응답에서는 아래 표에서 질문에 해당하는 미션 요구사항·코드·결과를 찾는다. 평가 원문의 앞부분에는 미션 요구사항이 반복되며, 평가 문항은 마지막 절에 있다. [미션 요구사항](a1_1_mission.md#4-기능-요구-사항) · [평가 문항](a1_1_eval.md#5-평가문항)

| 평가 | 질문 요지 | 미션 요구사항 | 코드 | 결과 위치 |
| --- | --- | --- | --- | --- |
| 1-1 | DataAnalyzer와 필수 메서드 4개 | 2. 최종 결과물, 4-2 | [pipeline.py](../src/pipeline.py#L20) | `NB_LOAD`~`NB_RFM` |
| 1-2 | 노트북 전체 실행 | 2. 최종 결과물 | [run_checks.py](../utils/run_checks.py) | [실제 실행 확인 기록](#실제-실행-확인-기록) |
| 1-3 | 1,000행·8열·3종 타입 | 4-1 | [load_data·join_products](../src/pipeline.py#L36) | `NB_LOAD` |
| 1-4 | 이미지 Mean/Std·텍스트 피처 열 | 4-3 | [image_features.py](../utils/image_features.py#L64) | `NB_FEATURES` |
| 1-5 | 이상치 전후 분포 시각화 | 4-4, 4-6 | [clip_outliers](../src/pipeline.py#L156) | [IQR 절](../README.md#iqr의-통계적-필요성과-한계) |
| 1-6 | 6종 차트·제목·축 | 4-6 | [make_figures](../utils/reporting.py#L35) | [필수 시각화 6종](../README.md#필수-시각화-6종) |
| 1-7 | 기술통계·상관 2쌍·해석 | 4-5 | [summarize](../src/pipeline.py#L177) · [pair_correlation](../utils/reporting.py#L8) | [실제 실행 결과와 기술통계](../README.md#실제-실행-결과와-기술통계) |
| 1-8 | RFM 4그룹·인사이트 3개 | 4-7 | [calculate_customer_rfm](../utils/analytics.py#L128) | [비즈니스 인사이트](../README.md#비즈니스-인사이트) |
| 2-1 | 메서드 분리 이유와 책임 | 4-2 | [pipeline.py](../src/pipeline.py#L20) | [분석 흐름과 원본 보존](../README.md#분석-흐름과-원본-보존) |
| 2-2 | for 대신 NumPy 연산 지목 | 4-3 | [평균·표준편차 계산](../utils/image_features.py#L128) | `NB_FEATURES` |
| 2-3 | 파라미터를 인자로 받은 이유 | 4-2 | [detect_outliers](../src/pipeline.py#L145) · [calculate_rfm](../src/pipeline.py#L162) | [입력과 계산 기준](../README.md#입력과-계산-기준) |
| 2-4 | 단계별 마크다운·의사결정 기록 | 2. 최종 결과물 | [분석 노트북](../notebooks/analysis_report.ipynb) | `NB_FEATURES`·`NB_CLEAN`·`NB_STATS` 설명 셀 |
| 3-1 | IQR 필요성과 한계 | 4-4 | [iqr_limits](../utils/analytics.py#L117) | [Q&A 3-1](#3-1) |
| 3-2 | 그룹 평균 대치의 이유와 위험 | 4-4 | [impute_features](../utils/analytics.py#L71) | `NB_CLEAN` |
| 3-3 | RFM 점수 기준과 타당성 | 4-7 | [점수 계산](../utils/analytics.py#L151) | [실제 고객 그룹 요약](../README.md#실제-고객-그룹-요약) |
| 3-4 | 벡터화가 빠른 이유 | 4-3 (과제 목표) | [배치 축 연산](../utils/image_features.py#L128) | `NB_FEATURES` stride 출력 |
| 4-1 | 100만 명·1024² 병목 | 없음 (확장) | [순차 이미지 경로](../utils/image_features.py#L96) | [병목과 개선 설계](#대규모-이미지-처리의-병목과-개선-설계) |
| 4-2 | 첫 캠페인 세그먼트·리스크 | 4-7 | [write_insights](../utils/reporting.py#L73) | [1. VIP 유지 실험](../README.md#1-vip-유지-실험) |
| 4-3 | ML 예측 확장 | 없음 (확장) | [calculate_rfm](../src/pipeline.py#L162) | [평가 Q&A 4-3](#4-3) |
| 5 | 보너스 3종 | 5-1~5-3 | [bonus.py](../utils/bonus.py) | [보너스 3개 실제 구현 결과](../README.md#보너스-3개-실제-구현-결과) |

### 실제 실행 확인 기록

2026-11-08 실제 검증의 성공 상태를 기록했다. 아래는 테스트 수·종료 성공·검증 상태 요약이며, 전체 분석 출력은 실행 노트북에서 확인할 수 있다. 이 블록은 실행 결과이며 실행할 명령은 [환경과 실행](../README.md#환경과-실행)의 bash·PowerShell 블록이다.

```text
Validation status summary, 2026-11-08 Asia/Seoul
> .venv/Scripts/python.exe -B -m utils.run_checks --with-sample
Ran 22 tests
OK
Notebook execution: PASS (13 code cells)
> .venv/Scripts/python.exe -B -m utils.repository_checks
Repository checks: PASS
Original stdout is private. No notebook rows or identifiers are copied here.
```

새 복제본·새 가상환경에서는 표본 203파일을 복원하고 입력 체크섬·설정·버전·정제·이미지·월별·RFM·상관 등 기록한 전체 필드를 비교한다. 성공 시 `Fresh-checkout reproduction matched every recorded field.`를 출력한다. 검증 원문은 `data/processed/reproduction_verification.json`에 남는다.

## 네이토 평가

| 회차 | 결과 | 판정과 보완 |
| --- | --- | --- |
| 1차 평가 | 18/19 | #1 결측 처리 호출명에 맞춰 호환 메서드를 연결했다. |
| 2차 평가 | 17/19 | #1은 PASS로 바뀌었고 #13 IQR 분포 비교와 #17 이미지 병목 대응이 FAIL이었다. |
| 최종 평가 | **19/19** | IQR의 이론·실측 비교와 이미지 계측·확장 검증 설계를 보강해 #13·#17이 PASS로 바뀌었다. |

최종 보고서는 2026-11-07 23:50:40에 기록됐으며 평가 대상 커밋은 보고서에 기재되어 있지 않다. 보완 과정은 [네이토 재평가 체크표](a1_1_checklist.md#네이토-재평가-체크표)와 [이슈 #23](https://github.com/ntt65/A1_1/issues/23)에 남아 있다.

### 설정 기본값과 탐색 범위

최종 평가 #11은 PASS였고 아래 보완 의견이 있었다.

> 핵심 설정의 기본값과 권장 범위를 README의 SETTINGS 표에 명확히 기재하세요

표본을 뽑을 때 사용한 기간·시드·채널과 기준일은 `data/raw/hm/sample_manifest.json`에 기록한다. `notebooks/analysis_report.ipynb`의 `SETTINGS`는 분석에 쓸 이름과 값을 모아 둔 설정 딕셔너리다. 분석을 시작할 때 추출 기록과 기간·시드·채널을 대조한다. 아래 범위는 설정을 바꿔 볼 때의 시작점이다. [표본 추출 기록과 분석 설정](../README.md#표본-추출-기록과-분석-설정) · [파라미터 설계 답변](#2-3)

| 설정이 있는 파일과 항목 | 기본 실행값 | 탐색 권장 범위와 변경 영향 |
| --- | --- | --- |
| `data/raw/hm/sample_manifest.json`과 [`notebooks/analysis_report.ipynb`의 `SETTINGS`](../notebooks/analysis_report.ipynb?plain=1#L69) · `start_inclusive`, `end_exclusive`, `seed`, `sales_channel` | `2020-06-01`, `2020-09-01`, `42`, `None` | 시작일 포함, 종료일 제외, 난수 시드 42, 전체 판매 채널이다. 기간·시드·채널이 바뀌면 표본을 다시 추출하고 분석 설정을 맞춘다. |
| [`notebooks/analysis_report.ipynb`의 `SETTINGS`](../notebooks/analysis_report.ipynb?plain=1#L69) · `image_size` | `32` | 계산에 쓸 사진 한 변의 픽셀 수다. 16~64에서 시작한다. 해상도에 따라 통계가 달라질 수 있으며, 원본에서 짧은 변이 지정 크기보다 작은 사진은 계산에서 제외된다. 같은 상품을 비교할 때는 원본들의 최소 변 길이 이하로 고른다. |
| [`notebooks/analysis_report.ipynb`의 `SETTINGS`](../notebooks/analysis_report.ipynb?plain=1#L69) · `batch_size` | `32` | 한 번에 처리할 최대 이미지 수다. 메모리가 빠듯하면 8~32에서 시작해 처리량과 최대 메모리를 함께 측정한다. 입력이 같으면 이미지별 계산 결과는 같다. |
| [`notebooks/analysis_report.ipynb`의 `SETTINGS`](../notebooks/analysis_report.ipynb?plain=1#L69) · `iqr_threshold` | `1.5` | 이상치 경계에 쓰는 IQR 배수다. 1.5~3에서 시작해 경계와 표시 건수를 비교한다. RFM은 원금액을 사용한다. |
| [`notebooks/analysis_report.ipynb`의 `NB_FEATURES` 호출](../notebooks/analysis_report.ipynb?plain=1#L1036) · `histogram_bins` | `8` | 픽셀 밝기를 나눌 구간 수다. 8~16에서 시작하고, 사진 간 비교에서는 구간 수와 이미지 크기를 맞춘다. |
| `data/raw/hm/sample_manifest.json` · `reference_date` | `2020-08-31` | 마지막 구매 후 경과일을 셀 기준일이다. [노트북의 `NB_RFM`에서 기준일 전달](../notebooks/analysis_report.ipynb?plain=1#L1491) |
| [`src/pipeline.py`의 `DataAnalyzer.calculate_rfm()`](../src/pipeline.py#L162-L163) · `frequency_unit` | `purchase_day` | `NB_RFM` 호출에서 생략해 기본값을 사용한다. 주문 ID가 있는 입력은 `order` 모드와 주문 ID 열(`order_col`)을 지정할 수 있다. |


### 네이토 최종 평가 원문

<details>
<summary>2026-11-07 23:50:40 · 19/19 · 원문 펼치기</summary>

```text
AI 사전평가 결과
평가 시각: 2026-11-07 23:50:40

100%
(19 / 19 항목 통과)
종합 평가
대부분의 요구사항이 코드·문서·실행 결과에 근거해 충족되었습니다. 핵심 구현(데이터 로드·결측 대치 API, 이미지·텍스트 파생, IQR 탐지·클리핑, RFM 산정 및 4개 이상 세그먼트 생성)과 노트북 실행 증거가 README·결과 JSON·로그·유틸 코드에 일관되게 기재되어 있습니다. 보완점은 문서 인용을 더 짧은 코드 주석으로 연결하고 일부 설계·한계 설명을 노트북 셀에 다시 요약하는 것입니다.

항목별 평가 (19개)
PASS
평가 항목 #1
근거
src/pipeline.py > 'def load_data(self, *, required_columns=(), date_columns=(), dtype=None) -> pd.DataFrame:' and src/pipeline.py > 'def handle_missing(self, strategy="group_mean", group_col=None, *, columns=None, eligible=None):'
잘한 점
DataAnalyzer에 load/결측 호출이 명확히 구현됨
부족한 점
해당 없음
보완
두 메서드의 의도와 반환/상태 변화를 한 줄씩 더 주석으로 요약하세요
PASS
평가 항목 #2
근거
docs/results/validation_log.txt > 'Notebook execution: PASS'
잘한 점
노트북 전체 실행 결과가 검증 로그에 기록됨
부족한 점
해당 없음
보완
노트북 실행 결과 저장 경로와 실행 시간을 README에 한 줄 덧붙이세요
PASS
평가 항목 #3
근거
docs/results/analysis_aggregates.json > '"transaction_rows": 8084' and docs/results/analysis_aggregates.json > '"joined_columns": 9' and README.md > 'NB_LOAD의 실제 info()는 `bool(2)`, `datetime64[us](1)`, `float64(1)`, `str(2)`, `string(3)`을 표시한다.'
잘한 점
데이터 규모·열수·다중 자료형을 문서·집계에 명확히 기재함
부족한 점
해당 없음
보완
노트북에 types 통계 출력 셀을 바로 링크로 연결하세요
PASS
평가 항목 #4
근거
src/pipeline.py > 'self.df[f"{image_column}_mean"] = image_data.mean(axis=reduce_axes)' and src/pipeline.py > 'for suffix, values in (("length", text_series.str.len()), ("word_count", text_series.str.split().str.len())):'
잘한 점
이미지 평균/표준편차와 텍스트 길이·단어수 파생이 구현됨
부족한 점
해당 없음
보완
파생 컬럼의 null 처리 정책을 노트북에서 한 줄로 요약하세요
PASS
평가 항목 #5
근거
utils/reporting.py > 'ax.boxplot([transactions["price"].to_numpy(), clipped_amount.to_numpy()], tick_labels=["Raw", "IQR clipped"])' and docs/results/analysis_aggregates.json > '"outliers": { "price": { "count": 212'
잘한 점
IQR 탐지 통계와 전후 박스플롯 생성 코드·수치가 모두 존재함
부족한 점
해당 없음
보완
박스플롯에 이상치로 처리된 행수(수치)를 캡션으로 추가하세요
PASS
평가 항목 #6
근거
utils/reporting.py > 'ax.hist(transactions["price"], bins=35' and 'ax.boxplot([transactions["price"].to_numpy(), clipped_amount.to_numpy()]' and 'ax.bar(profile.index, profile.Customers'
잘한 점
필수 차트(히스토그램·박스플롯·막대 등)와 제목/축 라벨이 코드에 설정됨
부족한 점
해당 없음
보완
노트북에서 각 Figure의 파일명·생성 위치를 명시적으로 출력하세요
PASS
평가 항목 #7
근거
docs/results/analysis_aggregates.json > '"statistics": { "price": { "mean": 0.0250139, "median": 0.0220169 } }' and docs/results/analysis_aggregates.json > '"correlations": [{"left":"image_mean","right":"image_std","pearson":-0.9435457970388688},{"left":"Frequency","right":"Monetary","pearson":0.6396637341139406}]'
잘한 점
평균·중앙값과 두 쌍의 상관계수가 집계 JSON에 포함되어 있음
부족한 점
해당 없음
보완
상관 해석의 한 문장 코멘트를 노트북 셀 바로 아래에 추가하세요
PASS
평가 항목 #8
근거
docs/results/analysis_aggregates.json > '"segments": {"Churned": 499, "VIP": 270, "New": 149, "Loyal": 82}' and README.md > '## 비즈니스 인사이트'
잘한 점
RFM으로 4개 그룹이 생성되고 README에 3개 인사이트가 문서화됨
부족한 점
해당 없음
보완
세 인사이트 각각에 대응하는 표(행수·금액)를 노트북에 바로 보여주세요
PASS
평가 항목 #9
근거
README.md > '아래 메서드 및 설정 표에 입력과 상태 변화가 있다.' and src/pipeline.py class docstring > 'Object-oriented data analysis pipeline for e-commerce data.'
잘한 점
메서드 책임과 상태 변화가 README·클래스 docstring에 설명되어 있음
부족한 점
해당 없음
보완
주요 메서드(예:handle_missing)의 입력·출력·부작용을 표로 요약해 두면 더 명확합니다
PASS
평가 항목 #10
근거
src/pipeline.py > 'self.df[f"{image_column}_mean"] = image_data.mean(axis=reduce_axes)' and utils/image_features.py > 'batch.mean(axis=(1, 2, 3))' and utils/image_features.py docstring > '픽셀별 Python 반복 없이'
잘한 점
NumPy의 축 연산을 사용한 벡터 연산 지점과 설계 의도가 명시됨
부족한 점
해당 없음
보완
노트북에 해당 셀에서 사용한 배열 형상 예시를 함께 보여주세요
PASS
평가 항목 #11
근거
README.md > '`SETTINGS["image_size"]`, `SETTINGS["batch_size"]` | `32`, `32`' and src/pipeline.py signatures (image_size, batch_size, histogram_bins)
잘한 점
이미지/처리 관련 파라미터가 인자화되고 README에 설정 위치가 명시됨
부족한 점
해당 없음
보완
핵심 설정의 기본값과 권장 범위를 README의 SETTINGS 표에 명확히 기재하세요
PASS
평가 항목 #12
근거
README.md > 'IQR의 통계적 필요성과 한계' and README.md > '4. `handle_missing_values()`로 이미지 통계의 EDA 사본에만 그룹 평균→대치 전 전체 평균을 적용한다.'
잘한 점
대치 근거와 분석 단계가 Markdown 문서에 근거와 함께 문서화됨
부족한 점
해당 없음
보완
의사결정별 참조 노트(노트북 셀 id)를 각 항목에 링크하면 재검증이 쉬워집니다
PASS
평가 항목 #13
근거
README.md > '사분위수는 극단값이 더 커져도 평균과 표준편차보다 영향을 덜 받으므로, 오염이 섞인 자료에서 중심부를 기준으로 먼 값을 찾는 데 유용하다.'
잘한 점
IQR의 필요성과 꼬리 분포에서의 한계를 문서에 설명함
부족한 점
해당 없음
보완
정규분포·로그정규의 수치 예시(간단 표)를 노트북에 바로 포함하세요
PASS
평가 항목 #14
근거
README.md > '이미지 대치가 분산을 축소할 수 있어 이미지 상관에는 원래 관측값만 사용한다.' and docs/results/analysis_aggregates.json > '"variance_before": 0.010424100859843282, "variance_after": 0.010130025199517102'
잘한 점
그룹별 대치의 분산 축소 위험과 수치적 근거를 문서화함
부족한 점
해당 없음
보완
대치 전에/후의 분포 플롯(예:밀도)을 인사이트 섹션에 추가하세요
PASS
평가 항목 #15
근거
README.md > '(평균 순위−0.5)/고객 수가 0.25/0.50/0.75 이하인지에 따라 1/2/3점' and README.md > 'R은 기준일−최종 구매일(기준일 구매=0일), F는 고유 구매일 수, M은 유효 금액 원값 합계다.'
잘한 점
RFM 점수 산정 규칙(분위수 근거)과 비즈니스 분류 기준이 문서화됨
부족한 점
해당 없음
보완
분위수 기반 임계값이 비즈니스 KPI와 어떻게 연결되는지 사례 한 줄을 추가하세요
PASS
평가 항목 #16
근거
README.md > '배열 축·메모리/Stride/SIMD·RFM 손계산·검증값과 한계를 담았다.' and utils/image_features.py docstring > '픽셀별 Python 반복 없이'
잘한 점
NumPy의 연속 메모리·벡터화(또는 SIMD 친화성)를 다룬 설명과 코드 근거가 있음
부족한 점
해당 없음
보완
노트북에 stride/contiguity 확인 코드 예시를 하나 포함하면 이해가 쉬워집니다
PASS
평가 항목 #17
근거
README.md > '파일 반복 읽기·디코딩 | 상품 ID·파일 버전·피처 설정을 키로 피처를 캐시한다. 캐시 미스만 제한된 워커에서 읽기·디코딩·축소하고, 크기가 제한된 대기열로 다음 NumPy 배치에 넘긴다.'
잘한 점
이미지 처리 병목(읽기+디코딩) 진단과 캐시·병렬화·샘플링 개선 방안이 문서화됨
부족한 점
해당 없음
보완
노트북에 병목 측정(읽기/디코딩/전처리 시간 분해)을 보여주는 간단 계측 셀을 추가하세요
PASS
평가 항목 #18
근거
utils/reporting.py > '## 1. VIP 유지 실험' and utils/reporting.py write_insights() template containing '검증: 발송군과 무작위 미발송군'
잘한 점
우선 액션 대상(VIP 등)과 검증용 대조군 설계가 인사이트 문서에 제시됨
부족한 점
해당 없음
보완
각 캠페인 우선순위에 대응한 단기 KPI(숫자)를 README에 표로 요약하세요
PASS
평가 항목 #19
근거
docs/results/analysis_aggregates.json > '"feature_columns": ["t_dat","customer_id","article_id","price","prod_name","image_mean","image_std",...]' and docs/results/analysis_aggregates.json > '"segments": {"Churned": 499, ...}'
잘한 점
ML 확장용 타깃(예:Churned 그룹)과 사용 가능한 피처 목록이 산출물에 포함되어 있음
부족한 점
해당 없음
보완
예시 타깃(이탈/재구매)별 feature list와 데이터 분리 시점을 노트북에 명확히 보여주세요
```

</details>

### 네이토 2차 평가 원문

<details>
<summary>2026-11-07 23:30:31 · 17/19 · 원문 펼치기</summary>

```text
AI 사전평가 결과
평가 시각: 2026-11-07 23:30:31

89%
(17 / 19 항목 통과)
종합 평가
대체로 제출물은 요구사항을 충실히 구현하고 문서화가 잘 되어 있으며 DataAnalyzer와 관련 유틸이 명확히 역할을 분리한다. 시연·집계·피처 생성·RFM·시각화 등 핵심 산출 근거가 README와 결과 JSON에 명시되어 있어 재현 가능성이 높다. 다만 IQR의 통계적 필요성·비대칭성 한계에 대한 서술이 목표 수준으로는 부족했고, 대규모 이미지 처리 시 병목 완화(병렬화·구성적 개선)의 구체적 개선방안 서술이 미흡하다.

항목별 평가 (19개)
PASS
평가 항목 #1
근거
src/pipeline.py > 'class DataAnalyzer:'; 'def load_data(self, *, required_columns=(), date_columns=(), dtype=None)' ; 'def handle_missing(self, strategy="group_mean", group_col=None, *, columns=None, eligible=None):'
잘한 점
클래스와 두 메서드가 명확히 구현되어 있고 docstring으로 역할을 설명함
부족한 점
추가 보완 포인트: 메서드 예외 경로 사례 문서화가 있으면 유용함
보완
핸들링되는 예외 케이스(예: 빈 입력)에 대한 간단한 사용 예시를 추가하라
PASS
평가 항목 #2
근거
docs/results/validation_log.txt > 'Notebook execution: PASS'
잘한 점
노트북 전체 실행 성공을 검증 로그에 기록함
부족한 점
추가 보완 포인트: 실패시 재현 방법 로그 첨부 권장
보완
실행 환경·셀 번호별 시간 소요 등 간단한 실행 메타를 노트북에 추가하라
PASS
평가 항목 #3
근거
docs/results/analysis_aggregates.json > '"transaction_rows": 8084'; '"joined_columns": 9'; README.md > 'bool(2), `datetime64[us](1)`, `float64(1)`'
잘한 점
행·열 수와 다양한 자료형(문자·숫자·날짜)이 결과 파일에 명시되어 있음
부족한 점
추가 보완 포인트: 컬럼별 타입 표를 자동 생성해 노트북에 포함하면 명확함
보완
데이터 타입 요약 표(summarize dtypes)를 노트북 시작부에 출력하라
PASS
평가 항목 #4
근거
src/pipeline.py > 'self.df[f"{image_column}_mean"] = image_data.mean(axis=reduce_axes)'; 'for suffix, values in (("length", text_series.str.len()), ("word_count", text_series.str.split().str.len())):'
잘한 점
이미지 mean/std와 텍스트 길이·단어수 파생변수가 코드에 직접 생성됨
부족한 점
추가 보완 포인트: 고유값 누락 시 처리 예시(대치/표시)가 문서에 더 필요함
보완
피처 생성 시 결측·비정상 입력의 처리 흐름을 한 문단으로 요약하라
PASS
평가 항목 #5
근거
README.md > 'IQR 전후 박스플롯:'; docs/results/analysis_aggregates.json > '"outliers": {"price": {"lower": -0.01272881355932203, "upper": 0.061847457627118636, "count": 212'
잘한 점
IQR 경계와 탐지 건수 및 전후 박스플롯 생성 근거를 문서화함
부족한 점
추가 보완 포인트: 어떤 축·스케일을 공유했는지 코드 행 단위로 링크하면 재검증이 쉬움
보완
박스플롯을 그리는 코드 셀에 '원본 vs 보정' 축 공유 설정을 주석으로 명시하라
PASS
평가 항목 #6
근거
docs/results/analysis_aggregates.json > '"figures": ["01_histogram","02_boxplot","03_bar","04_heatmap","05_scatter","06_line"]'; README.md > '모든 그림에 제목·축·단위를 표시한다.'
잘한 점
필수 6종 차트 파일 목록과 제목·축 규칙이 README에 명확히 명시됨
부족한 점
추가 보완 포인트: 축 단위와 라벨 규칙 예시(포맷)가 노트북에 표시되면 더 명확함
보완
차트 생성 함수에서 사용하는 제목·축 라벨 포맷 예시를 노트북에 첨부하라
PASS
평가 항목 #7
근거
docs/results/analysis_aggregates.json > '"statistics": {"price": {"mean": 0.025013946779157827, "median": 0.022016949152542376}}'; '"correlations": [{"left": "image_mean", "right": "image_std"'
잘한 점
기술통계(평균·중앙값)과 두 상관쌍이 결과 JSON에 포함되어 해석 근거 제공됨
부족한 점
추가 보완 포인트: 상관 해석을 주석으로 보완하면 비전문가 이해가 쉬움
보완
상관 결과 옆에 '해석 한두문장'을 결과 표에 직접 포함하라
PASS
평가 항목 #8
근거
docs/results/analysis_aggregates.json > '"rfm": {"segments": {"Churned": 499, "VIP": 270, "New": 149, "Loyal": 82}}'; README.md > '비즈니스 인사이트'
잘한 점
RFM에서 4개 이상의 그룹을 생성하고 README에 3개 이상의 인사이트를 제시함
부족한 점
추가 보완 포인트: 세그먼트별 처리 우선순위 표로 요약하면 실행계획에 유용함
보완
README의 인사이트 아래에 세그먼트별 우선순위 표(short list)를 추가하라
PASS
평가 항목 #9
근거
README.md > '아래 메서드 및 설정 표에 입력과 상태 변화가 있다.'; src/pipeline.py > '"Object-oriented data analysis pipeline for e-commerce data."'
잘한 점
메서드 역할과 상태 변화에 대한 문서·설명이 README와 클래스 docstring에 존재함
부족한 점
추가 보완 포인트: 메서드별 입력/출력 예시(샘플 호출)을 더해 테스트 이해를 돕기 바람
보완
각 공개 메서드에 간단한 사용 예제 코드를 노트북에 추가하라
PASS
평가 항목 #10
근거
utils/image_features.py > 'means[positions] = batch.mean(axis=(1, 2, 3))' ; utils/image_features.py > 'histogram, edge = advanced_image_statistics(batch, histogram_bins)'
잘한 점
NumPy 배치 연산(mean/std/histogram/edge) 지점이 코드에 명확히 구현되어 있음
부족한 점
추가 보완 포인트: 벡터화 의도가 노트북에 한 문장으로 적혀있으면 리뷰어 이해가 빨라짐
보완
노트북에서 해당 셀 위에 '이 연산은 벡터화로 의도됨' 한 줄을 추가하라
PASS
평가 항목 #11
근거
src/pipeline.py > 'def load_data(self, *, required_columns=(), date_columns=(), dtype=None)'; utils/image_features.py > 'for name, value in (("image_size", image_size), ("batch_size", batch_size)):'
잘한 점
주요 파라미터(image_size, batch_size 등)가 함수 인자로 노출되어 하드코드가 적음
부족한 점
추가 보완 포인트: 전체 SETTINGS 연동 예시가 노트북에 더 명확하면 이식성 향상됨
보완
노트북 상단에 SETTINGS(dict)를 정의해 함수 인자로 전달하는 예시를 보이라
PASS
평가 항목 #12
근거
README.md > '의사결정 기록' ; README.md > '분석 흐름과 원본 보존'
잘한 점
분석 단계·판단 근거·대치 근거가 README와 관련 문서로 기록되어 있음
부족한 점
추가 보완 포인트: 의사결정 변경 이력(간단한 changelog)이 있으면 추적성이 좋아짐
보완
의사결정 섹션 하단에 변경 이력 링크 또는 간단 타임스탬프를 추가하라
FAIL
평가 항목 #13
근거
README.md > 'IQR 보정도 EDA 사본에만 적용한다.'
잘한 점
IQR을 EDA 전용 보정으로 다루며 보정 전후 수치(경계·건수)를 제공함
부족한 점
판정 불가: IQR의 정규대비 효과와 비대칭(비정규 분포) 한계에 대한 명확한 이론 설명이 부족함
보완
IQR이 정규 대비 언제 유리한지와 비대칭 분포에서의 한계를 사례·수치로 한 문단으로 보완하라
PASS
평가 항목 #14
근거
docs/results/analysis_aggregates.json > '"imputation": {"image_mean_eda": {"variance_before": 0.010424100859843282, "variance_after": 0.010130025199517102}}'
잘한 점
그룹 대치로 분산 축소 위험을 수치로 제시하고 원본 상관은 보존한다고 명시함
부족한 점
추가 보완 포인트: 그룹별 대치가 그룹간 효과를 과장할 수 있다는 예시 제시 권장
보완
그룹 대치 시 분산 축소 영향 예시(간단 표)를 노트북에 추가하라
PASS
평가 항목 #15
근거
README.md > '`(평균 순위−0.5)/고객 수`가 0.25/0.50/0.75 이하인지에 따라 1/2/3점, 나머지는 4점이다.'
잘한 점
RFM 점수 기준(분위수 기반)과 그룹 규칙을 README에서 수식과 함께 근거로 제시함
부족한 점
추가 보완 포인트: 비즈니스 근거(예: KPI에 따른 컷오프 설명)을 한 문단 추가하면 완성도 상승
보완
RFM 컷오프를 뒷받침하는 간단한 비즈니스 가정(목표 KPI)을 README에 덧붙이라
PASS
평가 항목 #16
근거
utils/image_features.py > 'return np.ascontiguousarray(sampled)'; README.md > '메모리/Stride/SIMD·RFM'
잘한 점
연속 메모리(ascontiguousarray)와 stride 정보를 수집해 NumPy 성능 근거를 제시함
부족한 점
추가 보완 포인트: SIMD/벡터화에 대한 간단 그림이나 링크가 있으면 이해에 도움됨
보완
성능 근거로 간단한 메모리·stride 설명과 참고 링크를 노트북에 추가하라
FAIL
평가 항목 #17
근거
utils/image_features.py > 'batch_size는 동시에 계산할 상품 수 상한이다.'
잘한 점
배치 크기와 픽셀 버퍼(nbytes)를 기록해 메모리 병목 가능성을 인지하고 있음
부족한 점
실제 병목 완화(예: 병렬화 전략·구체적 샘플링·I/O 병렬화) 개선방안 서술이 부족함
보완
대규모 시 I/O/디코딩 병목 완화를 위한 병렬화·비동기 로드·샘플링 전략을 설계 제안하라
PASS
평가 항목 #18
근거
README.md > 'VIP 유지 실험' ; README.md > '검증: 발송군과 무작위 미발송군의 이후 구매율·고객당 마진을 비교한다.'
잘한 점
우선 액션 대상(VIP)과 각 실험의 검증용 대조군·측정지표를 구체적으로 제시함
부족한 점
추가 보완 포인트: 검증에 필요한 표본 크기 산정 언급이 있으면 실무 적용이 쉬움
보완
각 실험 검증에 권장하는 최소 표본 크기 또는 효과 크기 기준을 덧붙이라
PASS
평가 항목 #19
근거
README.md > 'Churned(R≤2) → Potential' ; docs/results/analysis_aggregates.json > '"feature_columns": ["t_dat","customer_id","article_id","price","prod_name","image_mean","image_std"]'
잘한 점
예시 타겟(Churned)과 사용 가능한 피처 목록(image/text/transaction)이 문서와 결과 JSON에 포함됨
부족한 점
추가 보완 포인트: ML 확장을 위한 피처 전처리(스케일링·카테고리 인코딩) 예시가 있으면 좋음
보완
모델 입력으로 권장되는 피처 전처리 파이프라인(한두 문장)을 노트북에 추가하라
```

</details>

## 평가 기술 발표자료

평가 Q&A [PPTX](presentation/a1_1_evaluation_qa.pptx)와 [PDF](presentation/a1_1_evaluation_qa.pdf)는 **35장**으로 필수 19문항과 보너스 3개를 다룬다. 문항별 코드·수식·배열 축·메모리·RFM 손계산을 실제 결과에 연결한다. PPTX 발표자 노트에는 상세 설명·시연·꼬리 질문 답변·출처를 담았다. 이전 31장 버전, 페이지 구성과 재생성 방법은 [발표자료 안내](presentation/README.md)에 있다.

## 5. 평가문항

### 항목 1

항목 1은 **미션에서 요구한 것이 실제로 있는지** 확인하는 질문 8개입니다. 답은 모두 "네, 있습니다"이고, 핵심은 **어디를 열어서 보여줄지**입니다. 1-1에서 클래스를 소개한 뒤, 1-2 실행 → 1-3 데이터 → 1-4 피처 → 1-5 이상치 → 1-6 차트 → 1-7 통계 → 1-8 RFM 순서로 분석 흐름을 따라갑니다.

#### 1-1

- src/pipeline.py 파일에 DataAnalyzer Class가 정의되어 있고, load_data(), handle_missing_values(), detect_outliers(), calculate_rfm() 메서드가 모두 포함되어 있는가?

**답변**

**한 줄 답:** 네. `src/pipeline.py`에 `DataAnalyzer` 클래스가 있고, 필수 메서드 4개가 모두 들어 있습니다.

**용어:** 클래스는 데이터(거래 표)와 그 데이터를 다루는 기능(메서드)을 한 덩어리로 묶은 것입니다. `analyzer = DataAnalyzer(경로)`처럼 만든 것을 인스턴스라고 부릅니다.

**사용 흐름:** 노트북은 거래 CSV 경로를 넘겨 `analyzer = DataAnalyzer(DATA / "transactions_sample.csv")`를 만들고, 이 인스턴스 하나로 읽기 → 정제 → RFM까지 진행합니다. 네 메서드는 이 흐름에서 각자 한 단계를 맡습니다.

| 메서드 | 하는 일 | 작은 예 |
| --- | --- | --- |
| `load_data()` | 고객 ID·상품 ID·거래일·금액·판매 채널을 필수 열로 지정해 CSV를 읽고, 거래일 `t_dat`를 날짜형으로 바꿔 `analyzer.df`에 저장합니다. | 고객 ID `"0012"`가 숫자 12로 바뀌지 않도록 문자열로 읽습니다. |
| `handle_missing_values()` | 비어 있는 이미지 피처를 같은 상품 유형의 평균으로 채웁니다. 그룹 평균이 없으면 전체 평균을 씁니다. | 그룹 A의 값이 `10, 30, (빈칸)`이면 빈칸은 둘의 평균인 **20**이 됩니다. |
| `detect_outliers()` | IQR 경계 밖의 값을 찾아 표시(마스크)하고 경계와 건수를 기록합니다. | `[1, 2, 3, 4, 100]`이면 경계가 −1과 7이라 **100만** 표시됩니다 (계산은 1-5). |
| `calculate_rfm()` | 고객마다 마지막 구매 후 경과일(R), 구매한 날 수(F), 구매금액 합계(M)를 계산합니다. | 고객 A가 1/1에 10·20, 1/3에 30을 샀다면 기준일 1/3에 **R=0, F=2, M=60**입니다 (계산은 1-8). |

**실제 결과:** 결측 대치는 이미지 피처 표의 사본을 별도 인스턴스 `imputer`에 넣어 처리하고, 이미지 표본에 포함되지 않은 상품은 채우지 않습니다. 이상치 탐지는 노트북이 `analyzer.clip_outliers("price", ...)`를 부르면 그 안에서 `detect_outliers()`가 실행됩니다. RFM은 고객 1,000명 각각이 한 번씩 집계됐는지, 그룹이 4개 이상인지 노트북에서 확인합니다.

평가 호환 메서드 `handle_missing()`는 `handle_missing_values()`에 인자를 그대로 전달하며 반환값과 대치 기록도 같습니다. [호환 메서드](../src/pipeline.py#L141) · [회귀 테스트](../tests/test_analytics.py)

**왜 이렇게:** 단계마다 메서드를 나누면, 문제가 생겼을 때 어느 단계(읽기·정제·집계)에서 생겼는지 바로 찾을 수 있습니다. 메서드별 분리 이유는 2-1에서 더 설명합니다.

**보여줄 곳:** [DataAnalyzer 정의 (pipeline.py 20행)](../src/pipeline.py#L20) · [인스턴스 생성 (노트북 679행)](../notebooks/analysis_report.ipynb#L679) · [load_data 결과: 거래 표와 자료형 · In [2]](../notebooks/analysis_report.ipynb#L238) · [handle_missing_values 결과: 결측치 대치표 · In [4]](../notebooks/analysis_report.ipynb#L1142) · [detect_outliers 결과: IQR 탐지 · In [4]](../notebooks/analysis_report.ipynb#L1226) · [calculate_rfm 결과: RFM 그룹 요약 · In [5]](../notebooks/analysis_report.ipynb#L1398)

**더 알아보기:** [Python·OOP](tech_study.md#12-pythonoop라이브러리와-실행)

#### 1-2

- 노트북(notebooks/analysis_report.ipynb)이 처음부터 끝까지 에러 없이 실행되는가?

**답변**

**한 줄 답:** 네. 새 커널에서 처음부터 끝까지 실행했고, 코드 셀 13개가 모두 오류 없이 끝난 출력이 저장되어 있습니다.

**용어:** 커널은 노트북의 코드를 실제로 실행하는 Python 프로세스입니다. **새 커널**은 이전에 만든 변수가 하나도 없는 깨끗한 상태입니다.

**작은 예:** 셀 3에서 만든 변수 `x`를 셀 5에서 쓰는데, 작업 중 셀 3을 지웠다고 해 봅시다. 열어 둔 노트북에서는 메모리에 `x`가 남아 있어 셀 5가 그대로 돌아갑니다. 새 커널에서 처음부터 실행하면 셀 5에서 오류가 납니다. 그래서 "처음부터 끝까지 실행된다"는 것은 새 커널로 확인해야 의미가 있습니다.

**실제 결과:** 2026-11-08에 `run_checks --with-sample`로 새 커널 실행을 통과했습니다(코드 셀 13개, 첫 셀 시작부터 마지막 셀 종료까지 8.67초). 끝에서 두 번째 셀 `NB_REPRO`에 결과 저장 완료 메시지가, 마지막 셀 `NB_TIMING`에 단계별 시간표가 남아 있습니다.

**왜 이렇게:** 한 걸음 더 나아가, 저장소를 새로 복제하고 새 가상환경에서 표본 ZIP과 의존성을 복원해 실행한 뒤 집계 결과를 기준 결과와 대조하는 재현 검증도 만들었습니다. "내 컴퓨터에서만 된다"를 막기 위해서입니다.

**보여줄 곳:** [새 커널 실행 코드](../utils/run_checks.py#L17) · [전체 실행 PASS 기록](#실제-실행-확인-기록) · [완료 메시지 · In [12]](../notebooks/analysis_report.ipynb#L4820) · [마지막 셀의 시간표 · In [13]](../notebooks/analysis_report.ipynb#L4901) · [새 환경 재현 코드](../utils/reproducibility.py#L15)

**더 알아보기:** [테스트·재현](tech_study.md#13-테스트재현git-작업-흐름)

#### 1-3

- 데이터셋이 1,000행 이상 / 8컬럼 이상이며, 수치형·범주형·날짜형·이미지(배열) 중 3종 이상의 데이터 타입을 포함하는가?

**답변**

**한 줄 답:** 네. 거래 정제와 상품 정보 연결(조인)을 마친 표가 **8,084행·9열**이고, 수치·범주(문자열)·날짜·이미지 배열을 모두 포함합니다.

**용어:** 조인은 두 표를 공통 키(여기서는 상품 ID)로 붙이는 작업입니다. `many_to_one`은 "거래는 여러 건이 같은 상품을 가리킬 수 있지만, 상품 표에는 상품마다 한 줄만 있어야 한다"는 조건입니다.

**작은 예:** 상품 표에 같은 상품 ID가 실수로 두 줄 있으면, 그 상품을 산 거래 1건이 조인 후 2건으로 불어납니다. 매출이 두 배로 잡히는 셈입니다. `many_to_one` 검증은 이런 경우 조인을 멈추고 오류를 냅니다.

**실제 결과:**

| 유형 | 컬럼 |
| --- | --- |
| 수치 | `price` (거래 금액) |
| 날짜 | `t_dat` (거래일) |
| 범주·문자열 | `product_type_name`, 고객·상품 ID |
| 텍스트 | `prod_name` (상품명) |
| 이미지 배열 | 상품 사진을 NumPy 배열로 읽어 상품 단위로 처리 |

노트북이 1,000행·8열 이상인지 직접 검사하고, `info()` 출력에서 각 열의 자료형을 확인할 수 있습니다.

**왜 이렇게:** 이미지는 거래마다 붙이지 않고 **상품 단위로 한 번만** 처리한 뒤 숫자 피처만 거래에 연결합니다. 같은 상품을 여러 번 산 거래마다 사진 배열을 복사하면 메모리만 낭비되기 때문입니다. ID는 앞자리 0이 사라지지 않게 문자열로 다룹니다.

**보여줄 곳:** [조인 구현](../src/pipeline.py#L71) · [최소 크기 검사](../notebooks/analysis_report.ipynb#L693) · [행·열 요약 · In [2]](../notebooks/analysis_report.ipynb#L587) · [거래 구조와 dtype · In [2]](../notebooks/analysis_report.ipynb#L238) · [이미지 배열 정보 · In [3]](../notebooks/analysis_report.ipynb#L903)

**더 알아보기:** [표와 자료형](tech_study.md#2-표와-자료형) · [분석 단위와 조인](tech_study.md#3-분석-단위와-조인)

#### 1-4

- 이미지 배열에서 추출한 Mean/Std 피처와 텍스트 파생 변수(단어 수 또는 문자열 길이)가 데이터프레임에 새로운 컬럼으로 추가되어 있는가?

**답변**

**한 줄 답:** 네. 이미지 피처 `image_mean`, `image_std`와 텍스트 피처 `prod_name_length`, `prod_name_word_count` 네 개 열을 추가했습니다.

**용어:** 피처는 분석에 쓰려고 원본에서 뽑아낸 숫자입니다. 이미지의 **평균**은 전체적인 밝기, **표준편차**는 밝기가 얼마나 들쭉날쭉한지(대비)를 나타냅니다. 픽셀 값은 0(검정)~1(흰색)로 맞췄습니다.

**작은 예:**

- 픽셀 절반이 0, 절반이 1인 이미지 → 평균 **0.5**, 표준편차 **0.5**
- 상품명 `Blue cotton shirt` → 글자 수 **17**, 단어 수 **3**

**실제 결과:** 이미지를 읽은 상품 200개에 이미지 피처가 들어갔습니다. 이미지가 없거나 읽기에 실패한 상품은 값을 비워 두고 그 이유(상태)를 기록합니다. 상품명은 원문을 지우지 않고 그대로 둔 채 파생 열만 추가했습니다.

**왜 이렇게:** 표준편차는 `ddof=0`(모집단 표준편차)으로 계산합니다. 한 이미지의 픽셀 전체가 표본이 아니라 그 이미지 자체이기 때문입니다. 위 예에서 0.5가 나오는 것도 `ddof=0` 기준입니다.

**보여줄 곳:** [이미지 피처 추출](../utils/image_features.py#L64) · [텍스트 피처 구현](../src/pipeline.py#L236) · [이미지 상태 출력 · In [3]](../notebooks/analysis_report.ipynb#L771) · [네 파생 열의 요약표 · In [3]](../notebooks/analysis_report.ipynb#L817)

**더 알아보기:** [이미지와 텍스트 피처](tech_study.md#5-이미지와-텍스트-피처)

#### 1-5

- 이상치 처리 전후 분포 비교 시각화(박스플롯 등)가 포함되어 있는가?

**답변**

**한 줄 답:** 네. 노트북에 이상치 처리 전과 후를 같은 축에 나란히 그린 박스플롯이 있습니다.

**용어:** 이상치는 다른 값들과 동떨어지게 크거나 작은 값입니다. IQR은 데이터를 크기순으로 세웠을 때 가운데 50%가 차지하는 폭(Q3 − Q1)입니다. 이 폭의 1.5배보다 더 바깥에 있으면 이상치로 봅니다. 박스플롯은 이 가운데 50%를 상자로, 경계 밖 값을 점으로 그린 그림입니다.

**작은 예:** `[1, 2, 3, 4, 100]`에서 Q1 = 2, Q3 = 4이므로 IQR = 2입니다. 경계는 2 − 1.5×2 = **−1**, 4 + 1.5×2 = **7**이라서 7을 넘는 **100만** 이상치입니다.

**실제 결과:** 거래 금액 8,084건 중 **212건(2.62%)**이 상한 0.061847을 넘었습니다. 이 212건을 상한값으로 낮춘 **사본**을 만들어 원본과 같은 금액 축에 그렸습니다. 사본은 분산이 **17.21%** 줄었고 중앙값(0.022017)은 그대로입니다.

**왜 이렇게:** 비싼 거래도 실제로 일어난 구매일 수 있습니다. 원본 금액을 깎으면 고객별 구매액(RFM)과 월별 매출이 틀려지므로, 보정은 그림 비교용 사본에만 하고 원본은 그대로 보존했습니다. IQR을 고른 이유와 한계는 3-1에서 설명합니다.

**보여줄 곳:** [전후 박스플롯](results/figures/02_boxplot.png) · [보정 코드](../src/pipeline.py#L156) · [탐지 건수와 원금액 보존 · In [4]](../notebooks/analysis_report.ipynb#L1226) · [박스플롯 셀 출력 · In [7]](../notebooks/analysis_report.ipynb#L1788)

**더 알아보기:** [IQR 기반 이상치 탐지](tech_study.md#사분위수quartile와-iqr-기반-이상치-탐지-및-클리핑)

#### 1-6

- 히스토그램, 박스플롯, 막대그래프, 히트맵, 산점도, 라인차트 6종 시각화가 모두 존재하고, 각 차트에 제목과 축 레이블이 표기되어 있는가?

**답변**

**한 줄 답:** 네. `make_figures()` 함수 하나가 6종을 모두 그리고, 노트북이 차트 개수와 각 차트의 제목·가로축·세로축 레이블이 있는지 코드로 검사합니다.

**용어:** 축 레이블은 가로축과 세로축이 무엇을 나타내는지 적은 글자입니다. 노트북은 눈으로 확인하는 대신 각 그림 객체에서 제목과 레이블 문자열이 비어 있지 않은지 직접 꺼내 확인합니다.

**실제 결과:** 각 차트가 무엇을 보여주는지는 다음과 같습니다.

| 차트 | 무엇을 보여주나 | 단위 |
| --- | --- | --- |
| 히스토그램 | 거래 금액이 어느 구간에 몰려 있고 꼬리가 얼마나 긴지 | 거래 |
| 박스플롯 | IQR 보정 전후 금액 분포 (1-5) | 거래 |
| 막대그래프 | RFM 그룹별 고객 수 (1-8) | 고객 |
| 히트맵 | R·F·M 세 지표 사이의 상관 | 고객 |
| 산점도 | 상품 이미지의 평균 밝기와 표준편차의 관계 (1-7) | 상품 |
| 라인차트 | 2020년 6~8월 월별 거래 금액 합계 | 월 |

**왜 이렇게:** 차트마다 분석 단위(거래·고객·상품·월)가 다릅니다. 단위를 섞으면 해석이 틀어지므로 표에 함께 적었습니다. 예를 들어 막대그래프의 높이는 거래 건수가 아니라 **고객 수**입니다.

**보여줄 곳:** [차트 생성 함수](../utils/reporting.py#L35) · [6종·제목·축 검사 · In [7]](../notebooks/analysis_report.ipynb#L2000) · [히스토그램](results/figures/01_histogram.png) · [박스플롯](results/figures/02_boxplot.png) · [막대그래프](results/figures/03_bar.png) · [히트맵](results/figures/04_heatmap.png) · [산점도](results/figures/05_scatter.png) · [라인차트](results/figures/06_line.png)

**더 알아보기:** [시각화 6종 읽기](tech_study.md#8-시각화-6종-읽기)

#### 1-7

- 기술통계(평균/중앙값/표준편차/사분위수)와 상관분석(2쌍 이상) 결과가 제시되고, 각각에 수치 근거 + 시사점 해석이 작성되어 있는가?

**답변**

**한 줄 답:** 네. 거래 금액과 상품명 파생 열의 기술통계, 그리고 상관 2쌍(상품 단위 1쌍, 고객 단위 1쌍)을 수치와 해석과 함께 제시했습니다.

**용어:**

- 중앙값은 크기순으로 세웠을 때 한가운데 값입니다. 평균이 중앙값보다 크면 큰 값 몇 개가 평균을 끌어올린, 오른쪽 꼬리가 긴 분포입니다.
- 상관계수 r은 −1~1 사이 값입니다. 1에 가까우면 함께 커지고, −1에 가까우면 하나가 클 때 다른 하나는 작습니다. 0이면 직선 관계가 없습니다.

**작은 예:** 금액이 `1, 2, 3, 4, 100`이면 평균은 22인데 중앙값은 3입니다. 이럴 때 평균 하나만 보면 "보통 22쯤 산다"고 잘못 말하게 됩니다.

**실제 결과:**

| 거래 금액 | 평균 | 중앙값 | 표준편차 | Q1 | Q3 |
| --- | --- | --- | --- | --- | --- |
| `price` | 0.025014 | 0.022017 | 0.014912 | 0.015237 | 0.033881 |

평균이 중앙값보다 크므로 오른쪽 꼬리가 긴 분포입니다(왜도 +1.554). 그래서 금액을 설명할 때 평균과 중앙값을 함께 말합니다.

| 상관 쌍 | 개수 | r | 해석 |
| --- | --- | --- | --- |
| 상품: 이미지 평균–표준편차 | 200 | −0.944 | 밝은 이미지일수록 밝기 차이가 작습니다. 흰 배경처럼 촬영 조건의 영향이 크다고 봅니다. |
| 고객: Frequency–Monetary | 1,000 | 0.640 | 구매한 날이 많은 고객일수록 구매금액도 큽니다. 다만 두 값은 같은 거래에서 나오므로 어느 정도 함께 움직이는 것이 자연스럽습니다. |

**왜 이렇게:** 상관 2쌍은 분석 단위가 다릅니다. 상품 피처는 상품 단위로, RFM은 고객 단위로 계산해야 숫자가 섞이지 않습니다. 상관은 원인을 말해 주지 않으므로 "함께 움직인다"까지만 해석합니다.

**보여줄 곳:** [기술통계 메서드](../src/pipeline.py#L177) · [통계량 출력 · In [6]](../notebooks/analysis_report.ipynb#L1557) · [유효 관측 쌍의 상관 계산](../utils/reporting.py#L8) · [이미지 상관 결과 · In [6]](../notebooks/analysis_report.ipynb#L1648) · [고객 상관 결과 · In [6]](../notebooks/analysis_report.ipynb#L1664)

**더 알아보기:** [통계·이상치·상관](tech_study.md#7-통계이상치상관)

#### 1-8

- RFM 분석 결과로 고객이 4개 이상 그룹으로 세분화되어 있으며, README.md에 비즈니스 인사이트가 3가지 이상 (근거 + 실행 + 검증) 형식으로 정리되어 있는가?

**답변**

**한 줄 답:** 네. 고객 1,000명을 VIP·Loyal·New·Churned 4개 그룹으로 나눴고, README에 근거·실행·검증 형식의 인사이트 3개를 정리했습니다.

**용어:** RFM은 고객을 세 숫자로 요약하는 방법입니다.

- **R (Recency):** 마지막 구매 후 며칠 지났나 (작을수록 최근 고객)
- **F (Frequency):** 구매한 날이 며칠인가
- **M (Monetary):** 구매금액 합계

**작은 예:** 고객 A가 1/1에 10원·20원어치, 1/3에 30원어치를 사고, 고객 B가 1/2에 5원어치를 샀습니다. 기준일 1/3에서 계산하면 다음과 같습니다.

| 고객 | R | F | M |
| --- | --- | --- | --- |
| A | 0일 (1/3에 구매) | 2일 (1/1, 1/3) | 60 |
| B | 1일 | 1일 | 5 |

A는 같은 날 두 번 샀어도 F는 1일로 셉니다.

**실제 결과:** 점수(1~4점)를 매긴 뒤 우선순위 규칙으로 고객 한 명당 한 그룹만 배정했습니다.

| 그룹 | 고객 수 | 특징 |
| --- | --- | --- |
| VIP | 270명 (27.0%) | 구매금액의 52.3%를 차지 |
| Churned | 499명 (49.9%) | 마지막 구매가 상대적으로 오래됨 |
| New | 149명 (14.9%) | 최근 구매했지만 구매일이 하루뿐 |
| Loyal | 82명 (8.2%) | 최근 반복 구매, 금액은 중간 |

README의 인사이트 3개는 VIP 유지, New의 다음 구매 유도, Churned의 재활성화입니다. 예를 들어 VIP는 고객 27.0%가 금액 52.3%를 차지하므로(근거) 유지 안내를 시험하고(실행), 안내를 보내지 않은 무작위 대조군과 구매율을 비교합니다(검증).

**왜 이렇게:** 점수 기준을 왜 이렇게 정했는지는 3-3, 어느 그룹부터 실제 행동에 옮길지는 4-2에서 이어서 설명합니다.

**보여줄 곳:** [점수와 그룹 배정 규칙](../utils/analytics.py#L151) · [고객 그룹 프로파일 · In [5]](../notebooks/analysis_report.ipynb#L1398) · [README 인사이트 3개](../README.md#비즈니스-인사이트) · [노트북 인사이트 출력 · In [8]](../notebooks/analysis_report.ipynb#L2046)

**더 알아보기:** [RFM·점수·세분화](tech_study.md#9-rfm점수세분화)

### 항목 2

항목 2는 항목 1에서 보여준 구현을 **왜 그렇게 설계했는지** 묻습니다. 2-1 클래스 구조 → 2-2 NumPy 연산 → 2-3 인자 설계 → 2-4 노트북 기록 순서로, "무엇이 있다"에서 "왜 이렇게 만들었다"로 넘어갑니다.

#### 2-1

- DataAnalyzer 클래스의 메서드를 왜 현재와 같이 분리했는지, 각 메서드의 책임과 역할을 설명할 수 있는가?

**답변**

**한 줄 답:** 한 메서드가 한 가지 책임만 지도록 나눴습니다. 그래야 문제가 생긴 단계를 바로 찾고, 단계별로 따로 검증할 수 있습니다.

**용어:** 책임은 "이 메서드가 실패하면 무엇이 잘못된 것인가"에 대한 답입니다. 상태는 인스턴스가 들고 있는 거래 표와 감사 기록(무엇을 몇 건 처리했는지)입니다.

**작은 예:** 조인 후 거래가 8,084건에서 9,000건으로 늘었다고 해 봅시다. 읽기와 조인이 한 메서드에 섞여 있으면 CSV가 잘못됐는지 상품 표가 잘못됐는지 알 수 없습니다. 둘을 나눠 두면 "읽기 직후는 8,084건, 조인 후 9,000건"처럼 조인 단계의 문제임이 바로 드러납니다.

**실제 결과:** 메서드는 분석 순서대로 세 묶음입니다.

| 묶음 | 메서드 | 책임 |
| --- | --- | --- |
| 로드와 조인 | `load_data()`, `join_products()` | 거래 CSV를 읽고 자료형을 맞추는 일과, 상품 키를 검증해 상품 정보를 붙이는 일을 나눴습니다. |
| 정제와 피처 | `handle_missing_values()`, `detect_outliers()`, 이미지·텍스트 피처 메서드 | 결측 대치는 대상과 방식을 인자로 받고, 이상치 탐지는 원금액을 그대로 둔 채 표시만 반환합니다. 피처는 상품 단위로 만듭니다. |
| 고객 집계 | `calculate_rfm()` | 거래 표는 그대로 두고, 고객 단위 결과를 새 표로 돌려줍니다. |

**왜 이렇게:** 클래스는 상태(표와 감사 기록)를 관리하고, 상태가 필요 없는 계산(IQR 경계, RFM 점수 등)은 `utils/`의 함수로 뺐습니다. 그래서 계산 함수는 노트북이나 테스트에서도 그대로 다시 쓸 수 있습니다.

**보여줄 곳:** [로드 메서드](../src/pipeline.py#L36) · [조인 메서드](../src/pipeline.py#L71) · [정제 메서드](../src/pipeline.py#L129) · [이미지 피처 메서드](../src/pipeline.py#L189) · [RFM 메서드](../src/pipeline.py#L162) · [거래 표 구조 · In [2]](../notebooks/analysis_report.ipynb#L238) · [대치 결과 · In [4]](../notebooks/analysis_report.ipynb#L1142) · [고객 그룹 표 · In [5]](../notebooks/analysis_report.ipynb#L1398)

**더 알아보기:** [Python·OOP](tech_study.md#12-pythonoop라이브러리와-실행)

#### 2-2

- 이미지 피처 추출 로직에서 Python for loop 대신 NumPy 배열 연산을 사용한 코드 부분을 직접 지목하고, 그렇게 구현한 설계 의도를 설명할 수 있는가?

**답변**

**한 줄 답:** `batch.mean(axis=(1, 2, 3))`와 `batch.std(axis=(1, 2, 3), ddof=0)` 두 줄입니다. 이미지 여러 장의 평균과 표준편차를 반복문 없이 한 번에 계산합니다.

**용어:** 이미지 묶음(배치)은 `(N, H, W, C)` 모양의 4차원 배열입니다. N은 이미지 장수, H·W는 높이·너비, C는 색 채널(RGB 3개)입니다. `axis=(1, 2, 3)`은 "높이·너비·채널 방향은 모두 합쳐서 계산하고, 이미지 장수(N) 방향은 남겨 두라"는 뜻입니다.

**작은 예:** 32×32 RGB 이미지 5장의 배치는 `(5, 32, 32, 3)`입니다. `mean(axis=(1, 2, 3))`을 하면 `(5,)` 모양, 즉 이미지마다 평균 하나씩 5개가 나옵니다. 반복문으로 쓰면 이미지마다 32×32×3 = 3,072개 픽셀을 Python이 하나씩 더해야 합니다.

**실제 결과:** 노트북에서 실제 배치의 모양 `(5, 32, 32, 3)`, 자료형 `float32`, 그리고 결과 열 `image_mean`, `image_std`를 확인할 수 있습니다.

**왜 이렇게:** 반복문은 파일을 읽고 배치를 나누는 곳에만 쓰고, 픽셀 계산은 모두 NumPy에 맡겼습니다. 계산 속도와 메모리 이점은 3-4에서 설명합니다.

**보여줄 곳:** [평균·표준편차 계산](../utils/image_features.py#L128) · [실제 배치 모양과 자료형 · In [3]](../notebooks/analysis_report.ipynb#L903) · [피처 출력 · In [3]](../notebooks/analysis_report.ipynb#L817)

**더 알아보기:** [NumPy 배열·벡터화](tech_study.md#4-numpy-배열벡터화메모리)

#### 2-3

- 주요 파라미터(이상치 임계값, 결측치 대치 전략, RFM 기준일 등)를 하드코딩하지 않고 인자로 설계한 이유와, 이 설계가 다른 데이터셋 적용 시 어떤 이점을 주는지 설명할 수 있는가?

**답변**

**한 줄 답:** 데이터가 바뀌면 이 값들도 바뀌어야 하기 때문입니다. 인자로 받으면 코드를 고치지 않고 호출할 때 값만 바꿔 다른 데이터에 적용할 수 있습니다.

**용어:** 하드코딩은 `1.5`나 `"2020-08-31"` 같은 값을 코드 안에 직접 박아 두는 것입니다. 인자는 메서드를 부를 때 바깥에서 넘겨주는 값입니다.

**작은 예:** RFM 기준일이 코드에 `2020-08-31`로 박혀 있다면, 2021년 데이터를 넣을 때 모든 고객의 R이 음수가 되거나 엉뚱한 값이 나옵니다. 기준일을 인자로 받으면 `calculate_rfm(..., reference_date="2021-12-31")`처럼 호출만 바꾸면 됩니다.

**실제 결과:**

| 인자 | 이 프로젝트의 값 | 다른 데이터에서 바꾸는 경우 |
| --- | --- | --- |
| `threshold` (IQR 배수) | 1.5 | 꼬리가 긴 데이터에서 덜 엄격하게 하려면 3으로 |
| `strategy`, 그룹 열, 대상 마스크 | 상품 유형별 평균 | 분류 체계가 다른 데이터면 그룹 열만 바꿈 |
| `reference_date` | `data/raw/hm/sample_manifest.json`에서 읽은 `2020-08-31`을 노트북에서 전달 | 분석에 맞는 기준일로 지정 |
| `frequency_unit` | 노트북에서 생략해 `src/pipeline.py`의 기본값 `purchase_day`(구매일 수) 적용 | 주문 ID가 있는 데이터면 주문 수로 |

**왜 이렇게:** H&M 표본에는 주문 ID가 없어서 F를 "구매한 날 수"로 셉니다. 주문 ID가 있는 데이터라면 `frequency_unit="order"`와 주문 ID 열 `order_col`을 전달해 주문 수로 셀 수 있습니다.

**보여줄 곳:** [이상치 임계값 인자](../src/pipeline.py#L145) · [대치 전략 인자](../src/pipeline.py#L129) · [기준일·빈도 인자](../src/pipeline.py#L162) · [노트북 대치 인자](../notebooks/analysis_report.ipynb#L1314) · [노트북 기준일 전달](../notebooks/analysis_report.ipynb#L1491) · [탐지 결과 · In [4]](../notebooks/analysis_report.ipynb#L1226) · [대치 결과 · In [4]](../notebooks/analysis_report.ipynb#L1142) · [RFM 결과 · In [5]](../notebooks/analysis_report.ipynb#L1398)

**더 알아보기:** [Python·OOP](tech_study.md#12-pythonoop라이브러리와-실행)

#### 2-4

- 노트북의 마크다운 설명이 분석 단계별로 작성되어 있으며, 코드만으로는 파악하기 어려운 의사결정 (예: 대치 전략 선택 근거) 이 문서화되어 있는가?

**답변**

**한 줄 답:** 네. 피처·정제·통계 단계마다 코드 앞에 "무엇을 왜 이렇게 정했는지"를 마크다운으로 적었습니다.

**용어:** 의사결정은 코드를 봐도 이유가 드러나지 않는 선택입니다. 예를 들어 코드에는 `groupby("product_type_name").mean()`만 보이지, 왜 중앙값이 아니라 평균인지, 왜 상품 유형별인지는 보이지 않습니다.

**실제 결과:**

| 단계 | 노트북에 기록한 의사결정 |
| --- | --- |
| 피처 | 이미지는 200개 상품만 표본으로 읽었고, 나머지 상품은 "표본 미포함" 상태로 따로 관리한다. 이미지 피처는 상품 단위로 한 번만 계산한다. |
| 정제 | 결측은 상품 유형별 평균으로 채운다(이유는 3-2). 대치한 값은 별도 사본에만 쓰고, 상관 분석에는 원래 관측값만 쓴다. IQR 보정 사본은 분포 비교에만 쓴다(1-5). |
| 통계 | 상품 단위 이미지 상관과 고객 단위 RFM 상관을 따로 해석하고, 수치 근거와 한계를 함께 남긴다(1-7). |

**왜 이렇게:** 평가자나 다른 사람이 노트북만 보고도 결과를 같은 방식으로 다시 만들 수 있어야 하기 때문입니다.

**보여줄 곳:** [이미지·텍스트 피처 설명](../notebooks/analysis_report.ipynb#L710) · [결측과 이상치 처리 설명](../notebooks/analysis_report.ipynb#L1080) · [통계 분석 설명](../notebooks/analysis_report.ipynb#L1513) · [이미지 상태 출력 · In [3]](../notebooks/analysis_report.ipynb#L771) · [대치 결과 · In [4]](../notebooks/analysis_report.ipynb#L1142) · [상관 결과 · In [6]](../notebooks/analysis_report.ipynb#L1664)

**더 알아보기:** [EDA 4단계](tech_study.md#eda탐색적-데이터-분석의-4단계-풀이와-코드-연결)

### 항목 3

항목 3은 사용한 **방법의 원리와 한계**를 묻습니다. 1-5의 IQR → 1-1의 결측 대치 → 1-8의 RFM 점수 → 2-2의 NumPy 연산을 하나씩 깊이 들어갑니다.

#### 3-1

- IQR 방식의 이상치 탐지가 왜 필요한지, 어떤 데이터 분포에서 효과적이고 어떤 경우에 한계가 있는지(예: 정규분포 vs 비대칭 분포) 설명하고, 자신의 코드에서 해당 로직을 짚어 보여줄 수 있는가?

**답변**

**한 줄 답:** IQR은 극단값에 휘둘리지 않는 사분위수로 경계를 정하므로, 이상치가 섞인 데이터에서도 경계가 안정적입니다. 다만 꼬리가 긴 분포에서는 정상적인 큰 값까지 이상치로 표시할 수 있습니다.

**용어:** 평균·표준편차로 경계를 정하는 방법(예: 평균 ± 3σ)은 이상치 자체가 평균과 표준편차를 끌어올려 경계가 함께 밀려납니다. 사분위수는 값의 **순서**만 보므로 가장 큰 값이 100이든 10,000이든 Q1과 Q3가 변하지 않습니다.

**작은 예:** 1-5의 `[1, 2, 3, 4, 100]`에서 100을 10,000으로 바꿔도 Q1 = 2, Q3 = 4, 경계 −1·7은 그대로입니다. 반면 평균은 22에서 2,002로 크게 바뀝니다.

**실제 결과:**

| 분포 | 경계 밖 비율 | 해석 |
| --- | --- | --- |
| 표준정규분포 (이론값) | 약 0.70% | 좌우 대칭이면 정말 드문 값만 걸립니다. |
| 오른쪽 꼬리가 긴 `exp(N(0,1))` (이론값) | 약 7.76% | 꼬리 쪽 정상 값까지 많이 걸립니다. |
| 이 프로젝트의 거래 금액 (왜도 +1.554) | 2.62% (212건, 모두 상한 초과) | 오른쪽 꼬리가 있어 큰 금액만 걸렸습니다. |

표준정규분포의 경계는 약 `±2.698σ`입니다. 로그정규 예시의 하한은 음수라 경계 밖 값은 모두 상한 쪽에 있습니다.

경계 보정 사본의 표본분산은 0.000222373에서 0.000184101로 줄었고, 중앙값은 0.022017로 같았습니다.

**왜 이렇게:** 그래서 걸린 212건을 지우지 않고 "검토 대상"으로 표시만 하고, 원래 금액은 RFM에 그대로 썼습니다(1-5). 다른 한계도 있습니다. 가격대가 다른 상품군을 한데 섞으면 전체 경계가 각 상품군을 제대로 반영하지 못하고, 값이 거의 같아 IQR이 0이면 경계가 한 점으로 좁아집니다.

**보여줄 곳:** [IQR 경계 계산](../utils/analytics.py#L117) · [경계 밖 마스크 구현](../src/pipeline.py#L145) · [H&M 표본의 IQR 결과](../README.md#iqr의-통계적-필요성과-한계) · [전후 통계표 · In [4]](../notebooks/analysis_report.ipynb#L1276) · [같은 축의 전후 박스플롯](results/figures/02_boxplot.png)

**더 알아보기:** [IQR 기반 이상치 탐지](tech_study.md#사분위수quartile와-iqr-기반-이상치-탐지-및-클리핑) · [통계·이상치·상관](tech_study.md#7-통계이상치상관)

#### 3-2

- 결측치를 그룹별 평균(또는 중앙값)으로 대치하는 이유와, 이 방식이 데이터 분포에 미치는 잠재적 위험(예: 분산 축소, 그룹 간 차이 과장)을 설명할 수 있는가?

**답변**

**한 줄 답:** 상품 유형마다 이미지 밝기 수준이 다르므로, 전체 평균보다 같은 유형의 평균이 빈칸에 더 그럴듯한 값입니다. 대신 채운 값이 평균 근처에 몰려 분산이 줄어드는 위험이 있습니다.

**용어:** 대치는 빈칸(결측)을 추정값으로 채우는 것입니다. 분산은 값들이 평균에서 얼마나 퍼져 있는지를 나타냅니다.

**작은 예:** 그룹 A의 값이 `10, 30, (빈칸)`입니다.

- 빈칸을 그룹 평균 20으로 채우면 `10, 20, 30`이 됩니다.
- 채우기 전 관측값 `10, 30`의 분산은 100인데, 채운 뒤 `10, 20, 30`의 분산은 약 66.7입니다(둘 다 `ddof=0`).
- 새 정보 없이 평균값만 하나 더해졌는데 데이터가 실제보다 덜 퍼진 것처럼 보이게 됩니다. 이것이 분산 축소입니다.

**실제 결과:** 이미지 평균 피처의 빈칸 9개를 그룹 평균으로 채웠고, 분산은 0.010424에서 0.010130으로 조금 줄었습니다. 그룹에 관측값이 하나도 없으면 전체 관측 평균을 쓰고, 열 전체가 비어 있으면 결측으로 남깁니다. 이미지 표본에 포함되지 않은 상품 4,496개는 "모르는 값"이 아니라 "읽지 않은 값"이므로 채우지 않았습니다.

**왜 이렇게:** 분산 축소 때문에, 이미지 상관(1-7)에는 채운 값을 섞지 않고 원래 관측값만 썼습니다. 또 그룹마다 결측 비율이 다르면 채운 값이 그룹 간 차이를 실제보다 크거나 작게 보이게 할 수 있습니다. 노트북에서 같은 상품 범위의 대치 전후 분포를 그림으로 비교해 이를 확인했습니다.

**보여줄 곳:** [그룹 평균 대치 구현](../utils/analytics.py#L71) · [실제 대치 결과표 · In [4]](../notebooks/analysis_report.ipynb#L1142) · [대치 전후 밀도 출력 · In [8]](../notebooks/analysis_report.ipynb#L2143)

**더 알아보기:** [정제와 결측 대치](tech_study.md#6-정제와-결측-대치)

#### 3-3

- RFM 점수 산정 기준(분위수 구간, 스코어링 방식)을 왜 그렇게 설정했는지, 세분화 결과가 비즈니스적으로 타당한 근거를 데이터에서 뽑아 설명할 수 있는가?

**답변**

**한 줄 답:** 고객을 R·F·M 각각의 순위로 줄 세운 뒤 4등분해 1~4점을 줬습니다. 금액의 절대 크기가 아니라 **상대적인 위치**로 점수를 매기므로 꼬리가 긴 금액 분포에서도 안정적입니다. 그 결과 VIP 27%가 금액의 52%를 차지하는 뚜렷한 차이가 나왔습니다.

**용어:**

- 순위 비율 `p = (평균 순위 − 0.5) / 고객 수`를 계산해, p가 0.25 이하면 1점, 0.50 이하면 2점, 0.75 이하면 3점, 나머지는 4점입니다.
- R은 작을수록(최근일수록), F·M은 클수록 높은 점수입니다.
- 같은 값을 가진 고객은 순위를 평균 내서 같은 점수를 받습니다.

**작은 예:** 고객 4명의 M이 `5, 20, 60, 100`이면 순위 1~4에 대해 p = 0.125, 0.375, 0.625, 0.875이므로 점수는 **1, 2, 3, 4점**입니다. 만약 앞의 두 명이 모두 5라면 둘 다 평균 순위 1.5, p = 0.25가 되어 **둘 다 1점**입니다. 입력 순서를 바꿔도 결과는 같습니다.

**실제 결과:** 점수와 원래 구매일 수로 그룹을 정했습니다. 위에서부터 먼저 맞는 조건 하나만 적용합니다.

| 순서 | 그룹 | 조건 | 고객 수 |
| --- | --- | --- | --- |
| 1 | VIP | R·F·M 모두 3점 이상, 구매일 2일 이상 | 270명 |
| 2 | Loyal | R·F 3점 이상, 구매일 2일 이상 | 82명 |
| 3 | New | R 3점 이상, 구매일 1일 | 149명 |
| 4 | Churned | R 2점 이하 | 499명 |
| 5 | Potential | 위에 해당하지 않음 | 0명 |

VIP는 고객의 27.0%이면서 구매금액의 52.3%를 차지하고, New의 구매일 수 중앙값은 1일입니다.

**왜 이렇게:** 평균·표준편차 기준은 소수의 고액 고객이 기준을 끌어올려 대부분 고객이 낮은 점수로 몰립니다. 순위 기준은 분포 모양과 상관없이 고객을 고르게 나눕니다. 그룹별로 금액 비중과 구매일 수가 확연히 다르다는 점이 이 분류가 실제 행동 차이를 잡아냈다는 근거입니다. 다만 New는 "관찰 기간에 하루만 산 고객"이지 신규 가입 고객이 아니고, Churned는 상대적으로 덜 최근일 뿐 이탈이 확정된 고객이 아닙니다.

VIP의 Monetary 점수 3 이상은 평균 순위 비율이 0.50보다 큰 고객을 우선 검토하는 기준입니다. 이 기준의 타당성은 후보군 크기와 대조군 대비 30일 재구매율·고객당 마진으로 확인합니다.

**보여줄 곳:** [평균 순위와 점수 코드](../utils/analytics.py#L151) · [그룹별 RFM·금액 표 · In [5]](../notebooks/analysis_report.ipynb#L1398) · [그룹 요약과 사업 해석](../README.md#실제-고객-그룹-요약)

**더 알아보기:** [RFM·점수·세분화](tech_study.md#9-rfm점수세분화)

#### 3-4

- NumPy 벡터 연산이 Python for loop보다 빠른 이유를 메모리 구조(연속 메모리 배치)와 연산 방식(SIMD 등) 관점에서 설명할 수 있는가?

**답변**

**한 줄 답:** NumPy는 같은 자료형의 숫자를 메모리에 빈틈없이 이어 붙여 두고, 반복을 Python이 아니라 미리 컴파일된 코드에서 처리합니다. 그래서 숫자 하나마다 드는 Python의 부가 비용이 사라집니다.

**용어:**

- **연속 메모리:** 숫자들이 메모리에 순서대로 붙어 있는 상태입니다. CPU는 메모리를 덩어리(캐시 라인)로 읽어 오므로, 붙어 있으면 한 번에 여러 개를 가져옵니다.
- **stride:** 다음 원소로 가려면 메모리에서 몇 바이트를 건너뛰어야 하는지입니다.
- **SIMD:** 한 명령으로 여러 숫자를 동시에 계산하는 CPU 기능입니다. CPU와 NumPy 빌드, 연산 종류가 지원할 때 쓰입니다.

**작은 예:** Python 리스트 `[0.1, 0.2, 0.3]`의 각 원소는 따로 떨어진 Python 객체이고, 리스트는 그 위치만 들고 있습니다. 더할 때마다 Python은 "이 객체가 숫자인가? 어떤 종류인가?"를 확인합니다. NumPy `float32` 배열은 4바이트 숫자 3개가 12바이트 안에 붙어 있고 자료형도 하나로 정해져 있어, 이런 확인 없이 곧바로 더합니다. 32×32 RGB 이미지 한 장이면 이 차이가 3,072번 반복됩니다.

**실제 결과:** 노트북에서 실제 배치의 stride와 연속성 여부를 출력하고, 슬라이스로 자른 배열은 stride가 바뀌어 연속이 아닐 수 있다는 것도 비교해 보여줍니다. 계산 전에 배열을 연속 배열로 만드는데, 이때 복사가 생길 수 있습니다.

**왜 이렇게:** 2-2에서 픽셀 계산을 모두 배열 연산으로 처리한 이유가 이것입니다. 반대로 파일 읽기처럼 숫자 계산이 아닌 일은 NumPy로 빨라지지 않으므로 반복문으로 둡니다. 실제 병목도 이쪽에 있습니다(4-1).

**보여줄 곳:** [배치 축 연산](../utils/image_features.py#L128) · [샘플 배열 연속화](../utils/image_features.py#L36) · [실제 배치의 stride와 연속성 · In [3]](../notebooks/analysis_report.ipynb#L903) · [슬라이스 비교 코드 · In [3]](../notebooks/analysis_report.ipynb#L1066)

**더 알아보기:** [NumPy 배열·벡터화·메모리](tech_study.md#4-numpy-배열벡터화메모리)

### 항목 4

항목 4는 지금 결과를 **더 크게, 실제로, 다음 단계로** 가져가면 어떻게 할지 묻습니다. 4-1 규모 확장 → 4-2 실제 마케팅 → 4-3 예측 모델 순서입니다. 아직 실행하지 않은 설계이므로, 측정한 사실과 제안을 구분해서 말합니다.

#### 4-1

- 만약 고객 수가 100만 명으로 증가하고 이미지 해상도가 1024×1024로 커진다면, 현재 파이프라인에서 가장 먼저 병목이 발생하는 지점은 어디이며, 이를 어떻게 개선하겠는가?

**답변**

**한 줄 답:** 이미지 **파일을 읽고 압축을 푸는 단계**가 가장 먼저 병목이 됩니다. 지금도 이미지 처리 시간의 약 85%가 이 단계입니다. 피처를 캐시하고, 캐시에 없는 이미지만 제한된 수의 작업자가 나눠 읽게 바꾸겠습니다.

**용어:**

- **병목:** 전체 속도를 결정하는 가장 느린 단계입니다.
- **디코딩:** JPEG처럼 압축된 파일을 픽셀 배열로 푸는 일입니다.
- **캐시:** 한 번 계산한 결과를 저장해 두고 다시 계산하지 않는 것입니다.

**작은 예:** 1024×1024 RGB 이미지 한 장은 픽셀 값이 1024×1024×3 ≈ 315만 개입니다. `float32`(4바이트)면 **12 MiB**, `float64`(8바이트)면 **24 MiB**입니다. 현재 설정의 32×32 `float32` 이미지 32장에 필요한 픽셀 버퍼는 **384 KiB**입니다.

**실제 결과:** `extract_product_image_features()`는 고유 상품마다 `imread()`로 순차 읽기·디코딩하고, 축소·정규화한 배열을 쌓아 NumPy 통계를 계산한다. 2026-11-07 로컬에서 실제 이미지 200장, 출력 32×32 RGB `float32`, 배치 상한 32, 보너스 피처 활성화 조건으로 워밍업 1회 후 3회 계측했다. 전체 중앙값은 **2.115초**, `imread()`의 읽기+디코딩 중앙값은 **1.797초**, 실행별 비중의 중앙값은 **84.9%**였다. 같은 피처·상태가 반환됐다. 이 시간은 해당 PC의 워밍업된 표본 계측이며 `imread()` 내부의 읽기와 디코딩 시간은 합산돼 있다. [순차 처리 경로](../utils/image_features.py#L96)

`NB_TIMING`은 이미지 12장으로 파일 바이트 읽기·메모리 [JPEG (Joint Photographic Experts Group · 이미지 압축 형식)](tech_study.md#5-이미지와-텍스트-피처) 디코딩·픽셀 전처리를 분리했다. 워밍업 후 3회에서 단계별 중앙값은 각각 **7.45 ms**, **124.32 ms**, **3.38 ms**였다. 메모리 디코딩 후 피처 입력이 기존 파일 경로와 일치하는지 검사했다. 이 수치는 파일 캐시가 워밍업된 소규모 실험의 관측값이다. [계측 셀 · `image-timing`](../notebooks/analysis_report.ipynb?plain=1#L4865)

##### 대규모 이미지 처리의 병목과 개선 설계

다음 표는 고객 100만 명·고해상도 이미지에 대응하기 위한 확장안과 검증 방법이다.

| 병목 | 확장 설계 | 확인 방법 |
| --- | --- | --- |
| 파일 반복 읽기·디코딩 | 상품 ID·파일 버전·피처 설정을 키로 피처를 캐시한다. 캐시 미스만 제한된 워커에서 읽기·디코딩·축소하고, 크기가 제한된 대기열로 다음 NumPy 배치에 넘긴다. 상품 위치로 결과를 합친다. | 같은 이미지 목록으로 워커 1·2·4개를 비교한다. 첫 실행과 워밍업 이후를 구분하고 이미지/초, 단계별 시간, 최대 프로세스 메모리, 오류 수를 기록한다. 상품 순서·상태·결측 위치 일치와 수치 허용 오차를 확인한다. |
| 고해상도 메모리 | RGB 1024×1024 한 장은 `float32`로 12 MiB, `float64`로 24 MiB다. 축소 배치 외에 동시 디코딩 배열, 대기 중 축소 배열, `stack` 사본, 통계 임시 배열을 예산에 넣는다. 워커 수와 대기열 용량을 함께 제한한다. | 실제 최대 60 KiB와 32장 설정 상한 384 KiB는 축소 픽셀 버퍼다. 워커 설정별 프로세스 최대 메모리는 별도로 측정한다. |
| 탐색할 이미지 수 | 상품군과 원본 해상도 구간별로 배분하고 고정 시드·선택 목록을 기록한다. | 동일 표본으로 처리량과 결과를 비교하고 이미지 미포함과 읽기 오류를 별도 상태로 유지한다. |
| 고객 100만 명의 거래 | 필요한 열만 청크로 읽는다. 고객별 금액 합계·최종일은 청크별 집계를 병합하고, 구매일 수는 청크 간 중복 `(고객, 구매일)`을 제거한다. 이미지 비용은 고객 수와 별도로 고유 상품 이미지 수로 산정한다. | 전체 고객 수·금액 합계·최종 구매일·고유 구매일 수를 기존 경로와 비교한다. |

**보여줄 곳:** [현재 읽기 위치](../utils/image_features.py#L114) · [노트북 실측 기록](../notebooks/analysis_report.ipynb#L720) · [현재 배치 메모리 정보 · In [3]](../notebooks/analysis_report.ipynb#L903)

**더 알아보기:** [표본·대용량 데이터](tech_study.md#11-표본대용량-데이터공개-범위)

#### 4-2

- 이 RFM 분석 결과를 실제 마케팅 캠페인에 적용한다면, 가장 먼저 액션을 취해야 할 세그먼트는 어디이며 그 이유는 무엇인가? 해당 전략의 리스크와 이를 검증하기 위해 추가로 필요한 데이터는 무엇인가?

**답변**

**한 줄 답:** **VIP**부터 시작하겠습니다. 고객의 27.0%가 구매금액의 52.3%를 차지하므로, 이 그룹을 잃는 것이 가장 큰 손실입니다. 다만 효과는 반드시 대조군 실험으로 확인합니다.

**용어:**

- **대조군:** 캠페인을 보내지 않고 그대로 둔 고객 집단입니다.
- **무작위 배정:** 누가 대조군이 될지 추첨으로 정하는 것입니다. 그래야 두 집단의 차이가 캠페인 때문이라고 말할 수 있습니다.

**작은 예:** VIP 전원에게 안내를 보냈더니 다음 달 구매율이 40%였다고 해 봅시다. 이것만으로는 효과를 알 수 없습니다. 원래 VIP는 안내가 없어도 40%가 다시 사는 고객일 수 있기 때문입니다. 무작위로 고른 미발송군이 35%였다면, 차이 5%p가 캠페인 효과입니다.

**실제 결과:** 1-8과 3-3의 그룹 표가 근거입니다. VIP는 고객 270명(27.0%), 금액 52.3%입니다. README의 세 인사이트를 바탕으로 캠페인마다 대상·대조군과 30일 목표의 예시를 정했습니다. [비즈니스 인사이트](../README.md#비즈니스-인사이트)

| 검토 순서·대상 | 30일 목표의 예시 | 대조군 | 추가 확보할 데이터 |
| --- | --- | --- | --- |
| 1 · VIP 유지 | 구매율 +3%p 이상, 고객당 마진 차이 ≥0 | VIP 내 무작위 미발송 | 배정·발송 시각, 후속 거래, 상품 마진 |
| 2 · New 추가 구매 | 두 번째 구매일 발생률 +2%p 이상, 고객당 마진 차이 ≥0 | New 내 무작위 미발송 | 연락 동의, 후속 거래의 고객 ID·날짜, 마진 |
| 3 · Churned 재활성화 | 구매율 +1%p 이상, 혜택 비용 차감 후 고객당 마진 차이 >0 | 기존 반복 구매 여부 층별 무작위 미발송 | 배정·발송 시각, 후속 거래, 혜택 비용, 재고 |

30일은 배정 시각부터 셉니다. 표의 수치는 대조군 대비 차이의 **사전 목표 예시**입니다. 기준 구매율·표본 크기·비용을 확인한 뒤 목표와 실행 순서를 결정합니다. 대상별 고객 수·거래 행 수·구매금액은 노트북에서 확인할 수 있습니다. [인사이트 출력](../notebooks/analysis_report.ipynb?plain=1#L2031)

**왜 이렇게:**

- **위험:** 원래 다시 살 고객이나 계절 효과가 캠페인 성과처럼 보일 수 있습니다. 할인을 주면 매출은 늘어도 고객당 마진은 줄 수 있습니다.
- **추가로 필요한 데이터:** 발송·반응 기록, 할인 비용, 상품 마진, 연락 수신 동의, 캠페인 이후 기간의 거래 데이터입니다.
- **검증:** 무작위 미발송군과 구매율·고객당 마진·수신 거부율을 비교합니다. 지금의 그룹 분석은 "누구를 실험할지" 고르는 근거이고, 효과 자체는 실험으로 확인합니다.

**보여줄 곳:** [VIP 고객·금액 비중 · In [5]](../notebooks/analysis_report.ipynb#L1480) · [VIP 유지 실험안](../README.md#1-vip-유지-실험) · [노트북 사업 인사이트 · In [8]](../notebooks/analysis_report.ipynb#L2046)

**더 알아보기:** [사업 해석과 검증](tech_study.md#10-사업-해석과-검증)

#### 4-3

- 이 분석 파이프라인을 머신러닝 예측 모델로 확장한다면, 어떤 타겟 변수(예: 이탈 여부, 구매 금액)를 설정하고 현재 파이프라인에서 생성한 피처 중 어떤 것을 활용하겠는가?

**답변**

**한 줄 답:** "기준시점 이후 30일 안에 다시 사는가"를 맞히는 분류 모델을 만들고, 지금 만든 RFM·상품 피처를 입력으로 쓰겠습니다. 가장 중요한 것은 **미래 정보가 입력에 섞이지 않게 시점을 나누는 것**입니다.

**용어:**

- **타겟:** 모델이 맞혀야 하는 값입니다. 예/아니오면 분류, 금액처럼 숫자면 회귀입니다.
- **피처:** 모델에 넣는 입력입니다.
- **데이터 누수:** 예측 시점에는 알 수 없는 미래 정보가 입력에 들어가는 실수입니다. 이러면 시험 점수만 좋고 실제로는 쓸 수 없는 모델이 됩니다.

**작은 예 (설계 예시):** 기준시점 T를 7월 31일로 정합니다. 6~7월 거래로 피처(RFM 등)를 만들고, 8월 1일부터 30일 동안 구매했는지를 타겟으로 씁니다. 만약 8월 거래까지 넣어 RFM을 계산하면, R이 이미 "8월에 샀다"는 답을 담게 되어 누수가 생깁니다.

**실제 결과:** 모델 학습은 아직 하지 않은 확장 설계입니다. 대신 지금 파이프라인에 활용할 수 있는 산출물이 이미 있습니다.

| 후보 피처 | 지금 있는 산출물 |
| --- | --- |
| 고객 R·F·M | `calculate_rfm()` 결과 (1-8) |
| 상품 유형별 구매 비중 | 조인된 거래 표의 `product_type_name` (1-3) |
| 구매 상품의 이미지 평균·표준편차 | `image_mean`, `image_std` (1-4) |
| 구매 상품명 길이·단어 수 | `prod_name_length`, `prod_name_word_count` (1-4) |

상품 단위 피처는 고객 단위로 평균 내서 붙입니다. 예상 지출을 맞히려면 같은 30일의 구매금액을 회귀 타겟으로 씁니다.

**왜 이렇게:** 학습·평가는 기준시점 순서로 나눕니다(과거로 학습, 이후로 평가). 30일을 끝까지 관측한 고객만 쓰고, 결측 대치 기준도 학습 구간 데이터로만 정합니다. 그래야 실제로 미래를 예측하는 상황과 같아집니다.

**보여줄 곳:** [RFM 구현](../src/pipeline.py#L162) · [RFM 결과 · In [5]](../notebooks/analysis_report.ipynb#L1398) · [상품 피처 결과 · In [3]](../notebooks/analysis_report.ipynb#L817) · [예측 시점 분리](../notebooks/analysis_report.ipynb?plain=1#L2195)

**더 알아보기:** [보너스·예측 확장 용어](tech_study.md#14-선택-보너스예측-확장-용어)

### 항목 5

보너스 문제 해결에 따른 크레딧 부여

**답변**

**한 줄 답:** 선택 과제 3개(이미지 고급 피처, 코호트 분석, 인터랙티브 시각화)를 모두 같은 표본으로 구현하고 새 커널 실행까지 확인했습니다.

#### 고급 이미지 피처

- **무엇:** 이미지 밝기를 0~1 구간에서 8칸으로 나눠 각 칸의 픽셀 비율(히스토그램)을 구하고, 옆 픽셀과의 밝기 차이 평균(엣지 강도)을 NumPy로 계산했습니다.
- **작은 예:** 픽셀이 모두 0.9인 이미지는 히스토그램의 마지막 칸만 1.0이고 나머지 칸은 0입니다. 옆 픽셀과 차이가 없으니 엣지 강도도 0입니다.
- **실제 결과:** 상품 200개 모두 히스토그램의 합이 1인지 검증했습니다. 평균 엣지 강도는 0.045633입니다.

#### 코호트 분석

- **무엇:** 고객을 처음 구매한 달(코호트)로 묶고, 각 묶음이 다음 달들에도 다시 사는 비율을 계산했습니다.
- **왜 첫 구매월인가:** 데이터에 가입일이 없어서 관찰 기간 내 첫 구매월로 대신했습니다. 그래서 "신규 가입 고객"이 아니라 "6월부터 관찰된 고객"으로 해석합니다.
- **실제 결과:** 6월·7월·8월 코호트가 각각 550명·288명·162명입니다. 6월 코호트는 7월에 40.7%(224명)가 다시 샀습니다. 아직 오지 않은 달은 0이 아니라 빈칸(`NaN`)으로 두었습니다.

#### 인터랙티브 RFM

- **무엇:** 고객 1,000명의 R·F·M을 3차원 점으로 그린 Plotly 차트를 독립 HTML로 저장했습니다.
- **실제 결과:** 마우스로 돌리고 확대하고, 점에 마우스를 올려 고객 ID와 지표를 보고, 범례로 그룹을 고를 수 있습니다. 인터넷을 끈 상태에서도 동작하는 것을 확인했습니다.

**보여줄 곳:** [이미지 통계 구현](../utils/image_features.py#L38) · [관측 상품 검증 출력 · In [9]](../notebooks/analysis_report.ipynb#L2526) · [밝기 히스토그램](results/bonus/image_histogram.png) · [코호트 계산](../utils/bonus.py#L9) · [코호트별 고객 수 · In [10]](../notebooks/analysis_report.ipynb#L2605) · [코호트 히트맵](results/bonus/cohort_retention.png) · [Plotly 차트 생성](../utils/bonus.py#L59) · [Plotly 실행 출력 · In [11]](../notebooks/analysis_report.ipynb#L2843) · [인터랙티브 HTML](results/bonus/rfm_interactive.html)

**더 알아보기:** [보너스 구현의 계산 기준](tech_study.md#15-실제-보너스-구현의-계산-기준)

## 마지막 연습

모의 평가에서는 아래 순서로 말해 보고, 해당 코드를 직접 열어 수정·재실행할 수 있는지 확인한다.

1. 입력·조인 시연 (1-3)
2. 픽셀 0/1 이미지의 평균·표준편차 0.5 (1-4)
3. 대치 `10, 30, 빈칸` → 20, 분산 100 → 66.7 (3-2)
4. `[1, 2, 3, 4, 100]`의 IQR 경계 −1·7 (1-5, 3-1)
5. 고객 A·B의 RFM 손계산 (1-8)
6. 실제 그룹 표·차트·한계 (3-3, 4-2)
7. 새 환경 재현 (1-2)
