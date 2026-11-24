# A1 1 미션 원문과 구현 대조

미션 원문을 그대로 옮기고, 요구사항마다 이 저장소에서 어떻게 구현했는지 덧붙였다.

## 읽는 방법

- 일반 글머리표는 **미션 원문**이다. 원문 문장은 고치지 않았다.
- 들여쓴 **구현** 항목은 이 저장소의 대응 내용이다. 먼저 무엇을 했는지 설명하고, 이어서 코드·노트북·결과 파일 링크를 붙였다.
- ✅는 구현과 검증을 마친 요구사항이다. 평가 문항별 답변과 시연 순서는 [평가 Q&A](a1_1_evaluation_qa.md), 용어 해설은 [tech_study.md](tech_study.md)에서 볼 수 있다.

| 항목 | 내용 |
| --- | --- |
| 분야 | AI/SW 심화 |
| 구분 | 데이터 분석 |
| 학습시간 | 60시간 |
| 필수/선택 | 필수 |
| 한 줄 요약 | 쇼핑몰에서 누가 자주 오고 많이 사는지 분석해서 단골 찾기 |

## 1. 미션 소개

이 미션에서는 이커머스 플랫폼의 상품 데이터를 분석한다. 상품명(텍스트), 가격(수치), 카테고리(범주), 등록일(날짜), 상품 이미지(배열) 등 서로 다른 유형의 멀티모달 데이터를 다룬다. NumPy의 벡터 연산을 활용해 이미지 데이터를 직접 수치화하고, Pandas로 탐색적 데이터 분석(EDA)과 통계 분석을 수행하며, 시각화를 통해 비즈니스 인사이트를 도출하는 전 과정을 경험한다. 나아가 고객의 구매 패턴을 분석하는 RFM(Recency, Frequency, Monetary) 기법을 적용하여 고객을 세분화하고 비즈니스 전략을 제안하는 과정까지 수행한다.

이 경험은 이후 컴퓨터 비전, 자연어 처리, 머신러닝 미션에서 데이터 전처리와 특성 공학을 수행하기 위한 필수 기반이 된다.

이번 미션에서 반드시 수행하는 핵심 과제 3가지:

1. 멀티모달 데이터(수치 + 텍스트 + 이미지 배열)를 NumPy 벡터 연산으로 통합 처리하는 파이프라인을 Class로 구축한다.
2. IQR 이상치 탐지, 그룹별 결측치 대치, 6종 시각화를 포함한 완전한 탐색적 데이터 분석(EDA)을 수행한다.
3. RFM 분석으로 고객을 4개 이상 세그먼트로 분류하고, 데이터 근거에 기반한 비즈니스 전략을 제안한다.

## 2. 최종 결과물

다음 내용이 모두 포함된 GitHub 레포지토리(Repository) URL을 제출한다.

1. ✅ 데이터 분석 파이프라인 모듈 (`src/pipeline.py`)
   - 원본 데이터를 입력받아 전처리, 피처 엔지니어링, 요약 통계를 수행하는 Python Class 파일
   - 절차 지향 스크립트가 아닌 객체 지향(OOP) 구조로 설계
   - **구현** — `DataAnalyzer` 클래스 하나가 로드·조인·정제·피처·통계·RFM을 메서드로 나눠 맡는다. 상태가 필요 없는 계산은 `utils/`의 함수로 분리해 재사용한다. [파이프라인 모듈](../src/pipeline.py) · [DataAnalyzer 클래스 정의 (20행)](../src/pipeline.py#L20)
2. ✅ 분석 리포트 노트북 (`notebooks/analysis_report.ipynb`)
   - 전처리 결과 시각화, 통계 분석, RFM 기반 고객 세분화 결과 포함
   - 주요 분석 단계마다 마크다운 설명 작성
   - **구현** — 데이터 로드(`NB_LOAD`)부터 단계별 시간 측정(`NB_TIMING`)까지 코드 셀 13개를 새 커널에서 처음부터 끝까지 실행해 통과했다. 각 단계 앞에 결정 이유와 해석을 마크다운으로 적었다. [분석 리포트 노트북](../notebooks/analysis_report.ipynb)
3. ✅ `README.md`
   - 프로젝트 개요, 데이터 설명, 비즈니스 인사이트 3가지 이상, 실행 방법
   - **구현** — 프로젝트 개요, H&M 표본 설명, 실행 방법, 실제 실행 결과, 근거·실행·검증 형식의 비즈니스 인사이트 3개를 담았다. [README](../README.md)

## 3. 과제 목표

이 과제를 마친 후, 학습자는 아래를 스스로 설명할 수 있어야 한다.

- ✅ NumPy의 벡터 연산(Vectorization)을 활용하여 반복문 없이 배열 데이터를 처리하는 방법을 설명할 수 있다.
  - **구현** — 이미지 여러 장을 `(N, H, W, C)` 배치 하나로 쌓고, 축 연산 한 번으로 이미지마다 평균과 표준편차를 구한다. [개념: NumPy 배열·벡터화](tech_study.md#4-numpy-배열벡터화메모리) · [코드: 이미지 배치 피처 추출](../utils/image_features.py#L64)
- ✅ 이미지 데이터에서 평균, 표준편차 등 통계적 특성을 추출하여 수치형 피처로 변환하는 원리를 이해한다.
  - **구현** — RGB 픽셀 전체의 평균은 밝기, 표준편차는 밝기의 퍼짐(대비)을 나타내는 숫자 열 `image_mean`, `image_std`가 된다. [개념: 이미지·텍스트 피처](tech_study.md#5-이미지와-텍스트-피처) · [코드: 이미지 피처 메서드](../src/pipeline.py#L189)
- ✅ IQR 방식을 활용한 이상치 탐지 로직을 직접 구현하고 그 원리를 설명할 수 있다.
  - **구현** — 사분위수로 `Q1 − 1.5×IQR`, `Q3 + 1.5×IQR` 경계를 직접 계산하고, 경계 밖 거래를 표시한다. [개념: IQR 상세 해설](tech_study.md#사분위수quartile와-iqr-기반-이상치-탐지-및-클리핑) · [코드: IQR 경계 계산](../utils/analytics.py#L117)
- ✅ RFM 분석을 통해 고객을 세분화하고, 데이터 기반의 비즈니스 전략을 제안할 수 있다.
  - **구현** — 고객별 최근성·빈도·금액을 1~4점으로 매기고, 4개 그룹으로 나눈 뒤 그룹 수치를 근거로 전략 3가지를 제안했다. [개념: RFM 점수와 세분화](tech_study.md#9-rfm점수세분화) · [코드: RFM 계산](../utils/analytics.py#L128) · [코드: 인사이트 작성](../utils/reporting.py#L73)
- ✅ 분석 로직을 Class로 구조화하여 재사용 가능한 코드를 설계하는 방법을 이해한다.
  - **구현** — 임계값·대치 전략·기준일 같은 값을 메서드 인자로 받아, 다른 데이터셋에도 코드 수정 없이 적용할 수 있게 했다. [코드: DataAnalyzer 클래스](../src/pipeline.py#L20) · [설계 검토: 코드 리뷰](code_review.md)

## 4. 기능 요구 사항

다음 요구사항을 모두 만족해야 한다.

### 4-1. ✅ 데이터 로드 및 기본 탐색

- 최소 1,000건 이상, 8개 이상의 컬럼을 가진 이커머스 데이터셋을 사용한다.
  - **구현** — 거래를 정제하고 상품 정보를 붙인 결과는 **8,084행 · 9열**이다. 상품 키가 중복되면 거래가 불어나므로 조인할 때 `many_to_one`으로 검증한다. [코드: 데이터 로드](../src/pipeline.py#L36) · [코드: 상품 조인](../src/pipeline.py#L71) · [노트북: 행·열 요약 출력](../notebooks/analysis_report.ipynb#L587)
- 수치형, 범주형, 날짜형, 이미지(배열) 중 최소 3가지 이상의 데이터 유형이 포함되어야 한다.
  - **구현** — 다섯 유형을 모두 포함한다.

    | 유형 | 컬럼 |
    | --- | --- |
    | 날짜 | `t_dat` (거래일) |
    | 수치 | `price` (거래 금액) |
    | 범주/문자열 | `product_type_name`, 고객·상품 ID |
    | 텍스트 | `prod_name` (상품명) |
    | 이미지 배열 | `images/*.jpg` → NumPy 배열 |

    [노트북: 거래 표 구조와 dtype](../notebooks/analysis_report.ipynb#L238) · [노트북: 이미지 배열 정보](../notebooks/analysis_report.ipynb#L903)
- `info()`, `describe()`, `head()`를 활용하여 데이터 구조를 파악하고 마크다운으로 해석을 작성한다.
  - **구현** — 노트북 `NB_LOAD` 셀(`1196c1cf`)에서 세 함수의 출력을 보여주고 바로 아래 마크다운에 해석을 적었다. [분석 리포트 노트북](../notebooks/analysis_report.ipynb)
- RFM 계산용 거래 데이터는 최소 `customer_id`, `order_date`, `amount`(또는 `price * qty`) 컬럼을 포함해야 한다.
  - **구현** — 이 데이터의 컬럼명은 `customer_id`, `t_dat`(= `order_date`), `price`(= `amount`)다. 한 행이 상품 하나의 구매이므로 `price`를 금액으로 쓴다.
- Recency 기준일은 데이터의 최종 거래일(또는 분석 기준일)로 정의한다.
  - **구현** — 기준일은 **2020-08-31**이며, 표본 기록 파일 `sample_manifest.json`의 `reference_date` 값을 읽어 넘긴다. [노트북: 기준일 전달 코드](../notebooks/analysis_report.ipynb#L1491)
- 해석은 수치 근거 1개 이상 + 시사점 1문장 이상을 포함해야 한다.
  - **구현** — `NB_LOAD` 마크다운과 README에 행 수·기간·금액 통계를 근거로 한 해석을 적었다. [README: 실제 실행 결과와 기술통계](../README.md#실제-실행-결과와-기술통계)

### 4-2. ✅ 분석 파이프라인 모듈화 (OOP)

- 분석 로직을 `DataAnalyzer`라는 Class로 구현한다.
  - **구현** — `src/pipeline.py`에 정의했다. [코드: DataAnalyzer 클래스](../src/pipeline.py#L20)
- 최소 다음 메서드를 포함한다: `load_data()`, `handle_missing_values()`, `detect_outliers()`, `calculate_rfm()`
  - **구현** — 필수 메서드 4개와 역할은 다음과 같다.

    | 메서드 | 하는 일 |
    | --- | --- |
    | [`load_data()`](../src/pipeline.py#L36) | 필수 열을 지정해 거래 CSV를 읽고, 거래일을 날짜형으로 바꾼다. |
    | [`handle_missing_values()`](../src/pipeline.py#L129) | 지정한 열의 결측값을 그룹 평균으로 채운다. 같은 기능의 호환 이름 [`handle_missing()`](../src/pipeline.py#L141)도 있다. |
    | [`detect_outliers()`](../src/pipeline.py#L145) | IQR 경계 밖 행을 마스크로 표시한다. 보정은 [`clip_outliers()`](../src/pipeline.py#L156)가 맡는다. |
    | [`calculate_rfm()`](../src/pipeline.py#L162) | 고객별 최근성·빈도·금액을 집계한 표를 반환한다. |
- 주요 파라미터(예: 이상치 임계값, 결측치 대치 전략)는 메서드의 인자로 받도록 설계한다.
  - **구현** — 이상치 배수 `threshold=1.5`, 대치 전략 `strategy="group_mean"`, 그룹 열 `group_col`, RFM 기준일 `reference_date`, 이미지 크기 `image_size`, 배치 크기 `batch_size` 등을 모두 인자로 받는다.

### 4-3. ✅ 멀티모달 데이터 피처 엔지니어링

- 이미지 데이터: NumPy를 활용하여 각 이미지의 평균(Mean)과 표준편차(Std)를 계산하고 새로운 컬럼으로 추가한다.
  - **구현** — 이미지가 있는 상품 200개에 `image_mean`, `image_std` 열을 추가했다. 이미지가 없거나 읽기에 실패하면 값을 비워 두고 상태를 기록한다. [코드: 이미지 피처 메서드](../src/pipeline.py#L189) · [코드: 배치 추출 함수](../utils/image_features.py#L64) · [노트북: 피처 요약표](../notebooks/analysis_report.ipynb#L817)
- 반복문(`for` loop) 대신 배열 연산을 사용한다.
  - **구현** — `(N, H, W, C)` 배치에서 `mean(axis=(1, 2, 3))`, `std(axis=(1, 2, 3), ddof=0)`로 이미지마다 값 하나를 한 번에 계산한다. 반복은 파일 읽기와 배치 순회에만 쓴다. [코드: 평균·표준편차 계산 줄](../utils/image_features.py#L128)
- 텍스트 데이터: 상품명에서 단어 수(Word Count) 또는 문자열 길이를 계산하여 파생 변수로 추가한다.
  - **구현** — 두 가지를 모두 추가했다. 상품명 글자 수 `prod_name_length`, 단어 수 `prod_name_word_count`. [코드: 텍스트 피처 메서드](../src/pipeline.py#L236)

### 4-4. ✅ 결측치 및 이상치 처리

- 결측치 현황을 파악하고, 그룹별(GroupBy) 통계를 활용한 대치 로직을 1가지 이상 적용한다.
  - **구현** — 이미지 피처 결측을 상품 유형(`product_type_name`)별 평균으로 채우고, 그룹에 값이 없으면 전체 평균을 쓴다. 대치는 EDA용 사본에만 적용한다. 이미지 표본에 포함되지 않은 상품 4,496개(`not_sampled`)는 채우지 않고 그대로 둔다. [코드: 그룹 평균 대치](../utils/analytics.py#L71) · [노트북: 대치 결과표](../notebooks/analysis_report.ipynb#L1142)
- IQR 방식의 이상치 탐지 로직을 직접 함수로 구현하고, 처리 전후의 분포 변화를 시각화한다.
  - **구현** — 거래 금액에서 상한 초과 **212행(2.62%)**을 찾아 경계값으로 보정했다. 보정 후 분산은 **17.21% 감소**했고 중앙값은 그대로다. 원래 금액은 RFM 계산용으로 보존한다. [코드: IQR 경계](../utils/analytics.py#L117) · [코드: 경계 보정](../src/pipeline.py#L156) · [그림: 처리 전후 박스플롯](results/figures/02_boxplot.png)

### 4-5. ✅ 통계 분석

- 주요 수치형 변수에 대해 평균, 중앙값, 표준편차, 사분위수를 계산하고 해석한다.
  - **구현** — 거래 금액(`price`)과 상품명 길이·단어 수에 대해 계산했다. 금액은 왜도가 +1.554로 오른쪽 꼬리가 긴 분포임을 해석했다. [코드: 기술통계 메서드](../src/pipeline.py#L177) · [노트북: 통계량 출력](../notebooks/analysis_report.ipynb#L1557)
- 최소 2쌍 이상의 변수에 대해 상관계수를 계산하고 해석한다.
  - **구현** — 두 쌍을 계산했다.

    | 단위 | 변수 쌍 | 상관계수 r | 해석 |
    | --- | --- | --- | --- |
    | 상품 (200개) | `image_mean`–`image_std` | −0.9435 | 밝은 이미지일수록 픽셀 퍼짐이 작다 (촬영 배경 영향 고려) |
    | 고객 (1,000명) | `Frequency`–`Monetary` | 0.6397 | 자주 사는 고객일수록 구매금액도 크다 |

    [코드: 상관 계산](../utils/reporting.py#L8) · [노트북: 상관 결과](../notebooks/analysis_report.ipynb#L1648)
- 모든 해석은 수치 근거 1개 이상을 포함하고 시사점 1문장 이상을 기술한다.
  - **구현** — 노트북 `NB_STATS` 셀과 README에 수치와 시사점을 함께 적었다. [README: 통계·상관 해석](../README.md#실제-실행-결과와-기술통계)

### 4-6. ✅ 시각화

다음 6가지 유형의 차트를 각각 1개 이상 작성한다.

| 차트 | 미션 원문 | 구현 내용 | 결과 그림 |
| --- | --- | --- | --- |
| ✅ 히스토그램 | 수치형 변수의 분포 | 거래 금액 분포 | [01_histogram.png](results/figures/01_histogram.png) |
| ✅ 박스플롯 | 이상치 처리 전후 비교 | 같은 축에서 IQR 보정 전후 금액 비교 | [02_boxplot.png](results/figures/02_boxplot.png) |
| ✅ 막대그래프 | 범주형 변수의 빈도 또는 RFM 세그먼트별 고객 수 | RFM 그룹별 고객 수 | [03_bar.png](results/figures/03_bar.png) |
| ✅ 히트맵 | 상관행렬 또는 RFM 세그먼트 분포 | RFM 지표 간 상관행렬 | [04_heatmap.png](results/figures/04_heatmap.png) |
| ✅ 산점도 | 두 수치형 변수의 관계 | 이미지 평균과 표준편차의 관계 | [05_scatter.png](results/figures/05_scatter.png) |
| ✅ 라인차트 | 시계열 추세 (예: 월별 매출 추이) | 완전한 월의 월별 거래 금액 추이 | [06_line.png](results/figures/06_line.png) |

모든 차트에는 제목과 축 레이블을 포함한다.

- **구현** — `make_figures()` 하나가 6종을 그리고, 노트북 `NB_PLOTS`에서 차트 수와 각 차트의 제목·가로축·세로축 레이블이 있는지 자동으로 검사한다. [코드: 차트 생성 함수](../utils/reporting.py#L35) · [README: 필수 시각화 6종](../README.md#필수-시각화-6종)

### 4-7. ✅ RFM 기반 고객 세분화

- 거래 데이터를 바탕으로 고객별 Recency, Frequency, Monetary 점수를 계산한다.
  - **구현** — R은 마지막 구매 후 경과일, F는 고유 구매일 수, M은 구매금액 합계다. 각 지표를 평균 순위 기준 4구간으로 나눠 1~4점을 준다. 같은 값은 같은 점수를 받는다. [코드: RFM 점수 계산](../utils/analytics.py#L128)
- 고객을 최소 4개 그룹(예: VIP, Loyal, New, Churned)으로 세분화하고 각 그룹의 특징을 분석한다.
  - **구현** — 우선순위 규칙(VIP → Loyal → New → Churned 순으로 먼저 맞는 조건)으로 고객 1,000명을 한 그룹씩 배정했다.

    | 그룹 | 고객 수 | 특징 |
    | --- | --- | --- |
    | VIP | 270명 | R·F·M 점수 모두 3점 이상이고 2일 이상 구매. 고객의 27.0%이지만 구매금액의 52.3%를 차지 |
    | Churned | 499명 | R 점수 2점 이하. 다른 고객보다 마지막 구매가 오래됨 (실제 이탈 확정은 아님) |
    | New | 149명 | R 점수 3점 이상이지만 구매일이 하루뿐 (신규 가입을 뜻하지는 않음) |
    | Loyal | 82명 | 최근에 2일 이상 반복 구매했지만 금액 점수는 VIP에 못 미침 |

    [코드: 그룹 프로파일](../utils/analytics.py#L171) · [노트북: 그룹 요약표](../notebooks/analysis_report.ipynb#L1398)
- 세분화 결과를 바탕으로 비즈니스 관점의 인사이트를 `README.md`에 정리한다.
  - **구현** — VIP 유지, New의 다음 구매 유도, 최근성이 낮은 고객 재활성화의 3가지 인사이트를 README에 정리했다. [코드: 인사이트 작성](../utils/reporting.py#L73) · [README: 비즈니스 인사이트](../README.md#비즈니스-인사이트)
- `README.md`에 작성하는 비즈니스 인사이트는 각각 다음 3가지 요소를 포함해야 한다.
  - (근거) 인사이트를 뒷받침하는 수치/그래프 1개 이상
  - (실행) 제안 액션의 대상 세그먼트 + 실행 방법 + 기대 효과
  - (검증) "추가로 필요한 데이터" 또는 "반증 가능성" 1문장
  - **구현** — 인사이트 3개 모두 근거·실행·검증 세 요소를 갖췄다. 예: VIP가 구매금액의 52.3%를 차지한다는 근거로 유지 안내를 제안하고, 무작위 미발송군과 비교해 효과를 검증하도록 했다.

## 5. 보너스 과제 (선택)

### 5-1. ✅ 이미지 고급 피처 추출

- 이미지의 히스토그램 분포나 간단한 엣지 특성을 NumPy로 직접 계산하여 피처로 추가한다.
- 이미지 데이터의 심층적인 수치화 방법을 경험한다.
- **구현** — 밝기를 8구간으로 나눈 히스토그램(`image_hist_0`~`7`)과, 인접 픽셀 밝기 차이의 평균인 엣지 강도(`image_edge_mean`)를 NumPy로 계산했다. 상품 200개 모두 히스토그램 합이 1인지 검증했다. [코드: 고급 이미지 통계](../utils/image_features.py#L38) · [그림: 밝기 히스토그램](results/bonus/image_histogram.png)

### 5-2. ✅ 코호트 분석 (Cohort Analysis)

- 가입 월별 고객의 재구매율(Retention Rate)을 계산하고 히트맵으로 시각화한다.
- 시간에 따른 고객 행동 변화를 추적하는 분석 기법을 경험한다.
- **구현** — 데이터에 가입일이 없어 **첫 관찰 구매월**을 가입 월 대신 사용했다. 고객 1,000명을 550명·288명·162명의 세 코호트로 나눠 월별 재구매율을 계산했고, 아직 관측되지 않은 미래 월은 빈칸(`NaN`)으로 두었다. [코드: 코호트 계산](../utils/bonus.py#L9) · [코드: 코호트 히트맵](../utils/bonus.py#L44) · [그림: 코호트 히트맵](results/bonus/cohort_retention.png)

### 5-3. ✅ 인터랙티브 시각화

- Plotly를 활용하여 RFM 세분화 결과를 인터랙티브 차트로 시각화한다.
- 이 보너스 과제에 한하여 Plotly 사용을 허용한다.
- 동적 시각화의 장점을 경험한다.
- **구현** — 고객별 R·F·M을 3D 산점도로 그려 독립 HTML로 저장했다. 인터넷 없이 열어도 그룹 필터와 회전이 동작한다. [코드: Plotly 차트 생성](../utils/bonus.py#L59) · [결과: 3D RFM HTML](results/bonus/rfm_interactive.html)

## 6. ✅ 개발 환경

- Python 3.8 이상
  - **구현** — Python 3.11.4에서 검증했다. [requirements.txt](../requirements.txt)
- 허용 라이브러리: NumPy, Pandas, Matplotlib, Seaborn
  - **구현** — 검증 스크립트가 허용 목록 밖의 라이브러리 import를 찾아 실패로 처리한다. [코드: 저장소 검사](../utils/repository_checks.py#L39)
- 보너스 과제 3에 한하여 Plotly 사용을 예외적으로 허용한다.
  - **구현** — Plotly는 보너스 전용 파일로 분리해 필수 환경과 섞이지 않게 했다. [requirements-bonus.txt](../requirements-bonus.txt)

## 7. ✅ 제약 사항

### 금지 사항

- ✅ OpenCV, Pillow 등 이미지 처리 전용 라이브러리 사용 금지
- ✅ NumPy 배열 연산으로 직접 구현한다.
- ✅ Scikit-learn, NLTK 등 머신러닝/자연어처리 라이브러리 사용 금지
- ✅ 자동 EDA 라이브러리(pandas-profiling, sweetviz 등) 사용 금지
- **구현** — 위 라이브러리는 사용하지 않으며, [저장소 검사](../utils/repository_checks.py#L39)가 import를 자동으로 막는다.

### 이미지 처리 허용 범위 가이드

- ✅ 이미지 입력/변환: `imread()` 사용 가능. 반환되는 NumPy 배열을 직접 조작한다.
  - **구현** — `imread()`로 읽은 배열을 NumPy로 직접 축소하고 통계를 계산한다. [코드: 이미지 배치 피처 추출](../utils/image_features.py#L64)
- ✅ 저장/복구: CSV에 배열이 문자열로 저장되는 경우 `fromstring()` 또는 `ast.literal_eval()`로 복구한다.
- ✅ 리사이즈: NumPy 슬라이싱(`arr[::n, ::n]`)으로 단순 다운샘플링을 수행한다.
  - **구현** — 슬라이싱으로 이미지를 `32×32`로 줄인다. [코드: 이미지 준비 함수](../utils/image_features.py#L11)

## 8. 데이터셋

- Kaggle, AI Hub 등에서 이커머스/상품 관련 데이터를 수집하거나 제공된 샘플을 사용한다.
- 이미지 데이터는 NumPy 배열 형태로 변환하여 사용한다.
- 공개 라이선스(CC-BY, MIT 등) 데이터를 우선 사용하고, 출처를 반드시 명시한다.

## 9. Test Case

### 결과 예시

아래는 정답이 아니라 참고 예시다. 실제 문구와 구조는 달라도 된다.

#### Class 구조 예시

```python
class DataAnalyzer:
    def __init__(self, data_path):
        self.df = None
        self.data_path = data_path

    def load_data(self):
        # 데이터 로드 로직
        pass

    def handle_missing_values(self, strategy='group_mean', group_col=None):
        # 결측치 처리 로직
        pass

    def detect_outliers(self, column, threshold=1.5):
        # IQR 기반 이상치 탐지
        q1 = self.df[column].quantile(0.25)
        q3 = self.df[column].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        return self.df[(self.df[column] < lower) | (self.df[column] > upper)]

    def calculate_rfm(self, customer_col, date_col, amount_col):
        # RFM 점수 계산
        pass
```

#### RFM 세분화 결과 예시

| 세그먼트 | 고객 수 | 평균 구매금액 | 특징 |
| --- | --- | --- | --- |
| VIP | 120명 | 450,000원 | 최근 구매, 높은 빈도, 높은 금액 |
| Loyal | 350명 | 180,000원 | 꾸준한 구매, 중간 금액 |
| New | 230명 | 85,000원 | 최근 첫 구매, 낮은 빈도 |
| Churned | 300명 | 120,000원 | 오래전 마지막 구매, 이탈 위험 |

#### 인사이트 예시

- **[인사이트 1]**
  - (근거) Churned 그룹이 전체 고객의 30%를 차지하며, 평균 이탈 기간은 90일임.
  - (실행) Churned 대상 → 할인 쿠폰 발송 캠페인 → 재구매율 10% 향상 기대.
  - (검증) 이탈 원인(가격/품질/경쟁사)을 파악하려면 이탈 사유 설문 데이터가 추가로 필요함.
- **[인사이트 2]**
  - (근거) VIP 그룹의 평균 구매 빈도는 월 4.2회로, 전체 매출의 45%를 차지함.
  - (실행) VIP 대상 → 전용 멤버십 혜택 강화 → 이탈 방지 전략 실행.
  - (검증) VIP 이탈 시 매출 감소 규모 시뮬레이션이 필요하며, 현재 데이터만으로는 정확한 LTV 산출이 어려움.
