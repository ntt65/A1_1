전체 문서 원문 복사

분야 AI/SW 심화 구분
데이터 분석
학습시간 60시간
필수/선택 필수

쇼핑몰에서 누가 자주 오고 많이 사는지 분석해서 단골 찾기

문제기술 기술적 설명

## 1. 미션 소개

이 미션에서는 이커머스 플랫폼의 상품 데이터를 분석한다. 상품명(텍스트), 가격(수치), 카테고리(범주), 등록일(날짜), 상품 이미지(배열) 등 서로 다른 유형의 멀티모달 데이터를 다룬다. NumPy의 벡터 연산을 활용해 이미지 데이터를 직접 수치화하고, Pandas로 탐색적 데이터 분석(EDA)과 통계 분석을 수행하며, 시각화를 통해 비즈니스 인사이트를 도출하는 전 과정을 경험한다. 나아가 고객의 구매 패턴을 분석하는 RFM(Recency, Frequency, Monetary) 기법을 적용하여 고객을 세분화하고 비즈니스 전략을 제안하는 과정까지 수행한다.

이 경험은 이후 컴퓨터 비전, 자연어 처리, 머신러닝 미션에서 데이터 전처리와 특성 공학을 수행하기 위한 필수 기반이 된다.

이번 미션에서 반드시 수행하는 핵심 과제 3가지:

- 멀티모달 데이터(수치 + 텍스트 + 이미지 배열)를 NumPy 벡터 연산으로 통합 처리하는 파이프라인을 Class로 구축한다.
- IQR 이상치 탐지, 그룹별 결측치 대치, 6종 시각화를 포함한 완전한 탐색적 데이터 분석(EDA)을 수행한다.
- RFM 분석으로 고객을 4개 이상 세그먼트로 분류하고, 데이터 근거에 기반한 비즈니스 전략을 제안한다.

## 2. 최종 결과물

다음 내용이 모두 포함된 GitHub 레포지토리(Repository) URL을 제출한다.

1. ✅ 데이터 분석 파이프라인 모듈 ([`src/pipeline.py`](../src/pipeline.py))
   - 원본 데이터를 입력받아 전처리, 피처 엔지니어링, 요약 통계를 수행하는 Python Class 파일
   - 절차 지향 스크립트가 아닌 객체 지향(OOP) 구조로 설계 → [`DataAnalyzer`](../src/pipeline.py#L20)
2. ✅ 분석 리포트 노트북 ([`notebooks/analysis_report.ipynb`](../notebooks/analysis_report.ipynb))
   - 전처리 결과 시각화, 통계 분석, RFM 기반 고객 세분화 결과 포함
   - 주요 분석 단계마다 마크다운 설명 작성 (`NB_LOAD`~`NB_TIMING` 13개 코드 셀 새 커널 PASS)
3. ✅ [`README.md`](../README.md)
   - 프로젝트 개요, 데이터 설명, 비즈니스 인사이트 3가지 이상, 실행 방법

## 3. 과제 목표

이 과제를 마친 후, 학습자는 아래를 스스로 설명할 수 있어야 한다.

- ✅ NumPy의 벡터 연산(Vectorization)을 활용하여 반복문 없이 배열 데이터를 처리하는 방법을 설명할 수 있다. → [NumPy 배열·벡터화](tech_study.md#4-numpy-배열벡터화메모리) · [`extract_product_image_features`](../utils/image_features.py#L64)
- ✅ 이미지 데이터에서 평균, 표준편차 등 통계적 특성을 추출하여 수치형 피처로 변환하는 원리를 이해한다. → [이미지·텍스트 피처](tech_study.md#5-이미지와-텍스트-피처) · [`extract_image_features`](../src/pipeline.py#L189)
- ✅ IQR 방식을 활용한 이상치 탐지 로직을 직접 구현하고 그 원리를 설명할 수 있다. → [IQR 상세 해설](tech_study.md#사분위수quartile와-iqr-기반-이상치-탐지-및-클리핑) · [`iqr_limits`](../utils/analytics.py#L117)
- ✅ RFM 분석을 통해 고객을 세분화하고, 데이터 기반의 비즈니스 전략을 제안할 수 있다. → [RFM·세분화](tech_study.md#9-rfm점수세분화) · [`calculate_customer_rfm`](../utils/analytics.py#L128) · [`write_insights`](../utils/reporting.py#L73)
- ✅ 분석 로직을 Class로 구조화하여 재사용 가능한 코드를 설계하는 방법을 이해한다. → [`DataAnalyzer`](../src/pipeline.py#L20) · [코드 리뷰](code_review.md)

## 4. 기능 요구 사항

다음 요구사항을 모두 만족해야 한다.

### 1. ✅ 데이터 로드 및 기본 탐색

- 최소 1,000건 이상, 8개 이상의 컬럼을 가진 이커머스 데이터셋을 사용한다. → **구현:** 유효 거래 **8,084행 · 9열** ([`load_data`](../src/pipeline.py#L36), [`join_products`](../src/pipeline.py#L71))
- 수치형, 범주형, 날짜형, 이미지(배열) 중 최소 3가지 이상의 데이터 유형이 포함되어야 한다. → **구현:** `t_dat`(날짜), `price`(수치), `product_type_name`·ID(범주/문자열), `prod_name`(텍스트), `images/*.jpg`(이미지 배열)
- `info()`, `describe()`, `head()`를 활용하여 데이터 구조를 파악하고 마크다운으로 해석을 작성한다. → **구현:** [`analysis_report.ipynb`](../notebooks/analysis_report.ipynb) `NB_LOAD` (`1196c1cf`)
- RFM 계산용 거래 데이터는 최소 `customer_id`, `order_date`, `amount`(또는 `price * qty`) 컬럼을 포함해야 한다. → **구현:** `customer_id`, `t_dat`(=`order_date`), `price`(=`amount`)
- Recency 기준일은 데이터의 최종 거래일(또는 분석 기준일)로 정의한다. → **구현:** `2020-08-31` (`sample_manifest.json`의 `reference_date`)
- 해석은 수치 근거 1개 이상 + 시사점 1문장 이상을 포함해야 한다. → **구현:** `NB_LOAD` 마크다운 해석 및 [README 실행 결과](../README.md#실제-실행-결과와-기술통계)

### 2. ✅ 분석 파이프라인 모듈화 (OOP)

- 분석 로직을 `DataAnalyzer`라는 Class로 구현한다. → **구현:** [`DataAnalyzer`](../src/pipeline.py#L20)
- 최소 다음 메서드를 포함한다: `load_data()`, `handle_missing_values()`, `detect_outliers()`, `calculate_rfm()` → **구현:** [`load_data`](../src/pipeline.py#L36), [`handle_missing_values`](../src/pipeline.py#L129)(호환 별칭 [`handle_missing`](../src/pipeline.py#L141)), [`detect_outliers`](../src/pipeline.py#L145) · [`clip_outliers`](../src/pipeline.py#L156), [`calculate_rfm`](../src/pipeline.py#L162)
- 주요 파라미터(예: 이상치 임계값, 결측치 대치 전략)는 메서드의 인자로 받도록 설계한다. → **구현:** `threshold=1.5`, `strategy="group_mean"`, `group_col`, `reference_date`, `image_size`, `batch_size` 등 인자화 완료

### 3. ✅ 멀티모달 데이터 피처 엔지니어링

- 이미지 데이터: NumPy를 활용하여 각 이미지의 평균(Mean)과 표준편차(Std)를 계산하고 새로운 컬럼으로 추가한다. → **구현:** [`extract_image_features`](../src/pipeline.py#L189) · [`extract_product_image_features`](../utils/image_features.py#L64) (`image_mean`, `image_std`, 관측 200상품)
- 반복문(`for` loop) 대신 배열 연산을 사용한다. → **구현:** `(N, H, W, C)` 배치에서 `axis=(1, 2, 3)` 벡터 연산 (`ddof=0`)
- 텍스트 데이터: 상품명에서 단어 수(Word Count) 또는 문자열 길이를 계산하여 파생 변수로 추가한다. → **구현:** [`extract_text_features`](../src/pipeline.py#L236) (`prod_name_length`, `prod_name_word_count`)

### 4. ✅ 결측치 및 이상치 처리

- 결측치 현황을 파악하고, 그룹별(GroupBy) 통계를 활용한 대치 로직을 1가지 이상 적용한다. → **구현:** [`impute_features`](../utils/analytics.py#L71) (`product_type_name` 그룹 평균 → 전체 평균 fallback, EDA 사본에만 적용해 `not_sampled` 4,496개 보존)
- IQR 방식의 이상치 탐지 로직을 직접 함수로 구현하고, 처리 전후의 분포 변화를 시각화한다. → **구현:** [`iqr_limits`](../utils/analytics.py#L117) · [`clip_outliers`](../src/pipeline.py#L156) (212행 탐지, 분산 `-17.21%`, [전후 박스플롯](../README.md#필수-시각화-6종))

### 5. ✅ 통계 분석

- 주요 수치형 변수에 대해 평균, 중앙값, 표준편차, 사분위수를 계산하고 해석한다. → **구현:** [`summarize`](../src/pipeline.py#L177) (`price`, `prod_name_length`, `prod_name_word_count`)
- 최소 2쌍 이상의 변수에 대해 상관계수를 계산하고 해석한다. → **구현:** [`pair_correlation`](../utils/reporting.py#L8) (상품 `image_mean`–`image_std` `r=-0.9435`, 고객 `Frequency`–`Monetary` `r=0.6397`)
- 모든 해석은 수치 근거 1개 이상을 포함하고 시사점 1문장 이상을 기술한다. → **구현:** `NB_STATS` 셀 및 [README 통계·상관](../README.md#실제-실행-결과와-기술통계)

### 6. ✅ 시각화

다음 6가지 유형의 차트를 각각 1개 이상 작성한다. → **구현:** [`make_figures`](../utils/reporting.py#L35) · [README 필수 시각화 6종](../README.md#필수-시각화-6종)

- ✅ 히스토그램: 수치형 변수의 분포 → [`01_histogram.png`](results/figures/01_histogram.png)
- ✅ 박스플롯: 이상치 처리 전후 비교 → [`02_boxplot.png`](results/figures/02_boxplot.png)
- ✅ 막대그래프: 범주형 변수의 빈도 또는 RFM 세그먼트별 고객 수 → [`03_bar.png`](results/figures/03_bar.png)
- ✅ 히트맵: 상관행렬 또는 RFM 세그먼트 분포 → [`04_heatmap.png`](results/figures/04_heatmap.png)
- ✅ 산점도: 두 수치형 변수의 관계 → [`05_scatter.png`](results/figures/05_scatter.png)
- ✅ 라인차트: 시계열 추세 (예: 월별 매출 추이) → [`06_line.png`](results/figures/06_line.png)

모든 차트에는 제목과 축 레이블을 포함한다. → **구현:** 6종 모두 `title`, `xlabel`, `ylabel` 검증 통과 (`NB_PLOTS`)

### 7. ✅ RFM 기반 고객 세분화

- 거래 데이터를 바탕으로 고객별 Recency, Frequency, Monetary 점수를 계산한다. → **구현:** [`calculate_customer_rfm`](../utils/analytics.py#L128) (평균 순위 기반 1~4점)
- 고객을 최소 4개 그룹(예: VIP, Loyal, New, Churned)으로 세분화하고 각 그룹의 특징을 분석한다. → **구현:** [`segment_profile`](../utils/analytics.py#L171) (`VIP` 270명, `Churned` 499명, `New` 149명, `Loyal` 82명)
- 세분화 결과를 바탕으로 비즈니스 관점의 인사이트를 `README.md`에 정리한다. → **구현:** [`write_insights`](../utils/reporting.py#L73) · [README 비즈니스 인사이트](../README.md#비즈니스-인사이트)
- `README.md`에 작성하는 비즈니스 인사이트는 각각 다음 3가지 요소를 포함해야 한다.
  - (근거) 인사이트를 뒷받침하는 수치/그래프 1개 이상
  - (실행) 제안 액션의 대상 세그먼트 + 실행 방법 + 기대 효과
  - (검증) "추가로 필요한 데이터" 또는 "반증 가능성" 1문장

## 5. 보너스 과제 (선택)

### 1) ✅ 이미지 고급 피처 추출

- 이미지의 히스토그램 분포나 간단한 엣지 특성을 NumPy로 직접 계산하여 피처로 추가한다. → **구현:** [`advanced_image_statistics`](../utils/image_features.py#L38) (`image_hist_0`~`7`, `image_edge_mean`), [밝기 히스토그램](results/bonus/image_histogram.png)
- 이미지 데이터의 심층적인 수치화 방법을 경험한다.

### 2) ✅ 코호트 분석 (Cohort Analysis)

- 가입 월별 고객의 재구매율(Retention Rate)을 계산하고 히트맵으로 시각화한다. → **구현:** [`cohort_retention`](../utils/bonus.py#L9) · [`cohort_figure`](../utils/bonus.py#L44) (가입일 부재로 첫 관찰 구매월 기준 대체, [코호트 히트맵](results/bonus/cohort_retention.png))
- 시간에 따른 고객 행동 변화를 추적하는 분석 기법을 경험한다.

### 3) ✅ 인터랙티브 시각화

- Plotly를 활용하여 RFM 세분화 결과를 인터랙티브 차트로 시각화한다. → **구현:** [`interactive_rfm`](../utils/bonus.py#L59) · [3D RFM HTML](results/bonus/rfm_interactive.html)
- 이 보너스 과제에 한하여 Plotly 사용을 허용한다.
- 동적 시각화의 장점을 경험한다.

## 6. ✅ 개발 환경

- Python 3.8 이상 → **구현:** Python `3.11.4` 검증 ([requirements.txt](../requirements.txt))
- 허용 라이브러리: NumPy, Pandas, Matplotlib, Seaborn → **구현:** [`check_repository`](../utils/repository_checks.py#L39)로 허용 외 라이브러리 import 차단
- 보너스 과제 3에 한하여 Plotly 사용을 예외적으로 허용한다. → **구현:** [requirements-bonus.txt](../requirements-bonus.txt) 분리

## 7. ✅ 제약 사항

### 금지 사항

- ✅ OpenCV, Pillow 등 이미지 처리 전용 라이브러리 사용 금지
- ✅ NumPy 배열 연산으로 직접 구현한다.
- ✅ Scikit-learn, NLTK 등 머신러닝/자연어처리 라이브러리 사용 금지
- ✅ 자동 EDA 라이브러리(pandas-profiling, sweetviz 등) 사용 금지

### 이미지 처리 허용 범위 가이드

- ✅ 이미지 입력/변환: `imread()` 사용 가능. 반환되는 NumPy 배열을 직접 조작한다. → [`extract_product_image_features`](../utils/image_features.py#L64)
- ✅ 저장/복구: CSV에 배열이 문자열로 저장되는 경우 `fromstring()` 또는 `ast.literal_eval()`로 복구한다.
- ✅ 리사이즈: NumPy 슬라이싱(`arr[::n, ::n]`)으로 단순 다운샘플링을 수행한다. → [`prepare_image`](../utils/image_features.py#L11) (`32×32` 다운샘플링)

## 8. 데이터셋

- Kaggle, AI Hub 등에서 이커머스/상품 관련 데이터를 수집하거나 제공된 샘플을 사용한다.
- 이미지 데이터는 NumPy 배열 형태로 변환하여 사용한다.
- 공개 라이선스(CC-BY, MIT 등) 데이터를 우선 사용하고, 출처를 반드시 명시한다.

## 9. Test Case

### 8. 결과 예시

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

- 세그먼트 고객 수 평균 구매금액 특징
- VIP: 120명, 450,000원, 최근 구매, 높은 빈도, 높은 금액
- Loyal: 350명, 180,000원, 꾸준한 구매, 중간 금액
- New: 230명, 85,000원, 최근 첫 구매, 낮은 빈도
- Churned: 300명, 120,000원, 오래전 마지막 구매, 이탈 위험

#### 인사이트 예시

- [인사이트 1] (근거) Churned 그룹이 전체 고객의 30%를 차지하며, 평균 이탈 기간은 90일임. (실행) Churned 대상 → 할인 쿠폰 발송 캠페인 → 재구매율 10% 향상 기대. (검증) 이탈 원인(가격/품질/경쟁사)을 파악하려면 이탈 사유 설문 데이터가 추가로 필요함.
- [인사이트 2] (근거) VIP 그룹의 평균 구매 빈도는 월 4.2회로, 전체 매출의 45%를 차지함. (실행) VIP 대상 → 전용 멤버십 혜택 강화 → 이탈 방지 전략 실행. (검증) VIP 이탈 시 매출 감소 규모 시뮬레이션이 필요하며, 현재 데이터만으로는 정확한 LTV 산출이 어려움.
