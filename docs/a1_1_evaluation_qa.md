# A1 1 평가 대비 Q&A와 시연 순서

기준: [평가 PDF](a1_1_eval.pdf) 15~17페이지와 [평가 Markdown](a1_1_eval.md)의 평가 문항. 자료 대조 의견은 [검토 문서](a1_1_eval_review.md), 용어 해설은 [tech_study.md](tech_study.md)다. 이슈 #6에서 관리한다.

## 연습과 증거 준비

답변은 **핵심 설명 → SRC 지목 → 검증 결과 → 한계** 순서로 말한다. 아래 19개 질문을 먼저 혼자 설명하고 꼬리 질문을 연습한다. 실제 계산 결과는 로컬 `data/processed/analysis_report.executed.ipynb`와 `analysis_verification.json`, 새 환경 비교는 `reproduction_verification.json`에서 확인한다. 평가 노트북은 원본 데이터·ID·이미지 예시와 실행 출력을 그대로 보존한다. 실제 집계 출력·검토한 차트는 `docs/results/analysis_report.md`와 `docs/results/analysis_aggregates.json`에서도 확인할 수 있다. 사용자 지시에 따라 평가 실행 결과는 마스킹하지 않는다. 실행과 제출 요약은 [README](../README.md)에서 확인한다.

```powershell
.venv\Scripts\python.exe -B -m utils.run_checks --with-sample
.venv\Scripts\python.exe -B -m utils.reproducibility
```

실데이터 접근 전에 환경·표본 준비가 필요하다. 원본을 공유하지 않는 자리에서는 아래 가상 입력과 공개 소스를 사용하고 실제 검증 여부를 구분해 말한다.

## 항목 1 · 구현과 실행 증거 8개

### 1-1. 필수 클래스와 메서드를 구현했나?

**답변:** DataAnalyzer가 거래와 상품의 분석 상태를 관리한다. load_data는 CSV와 자료형, handle_missing_values는 지정 피처 결측, detect_outliers는 IQR 마스크, calculate_rfm은 고객 집계를 담당한다. 조인·요약 통계·피처 메서드도 제공한다.

**SRC/증거:** [src/pipeline.py](../src/pipeline.py)의 `DataAnalyzer`, [노트북](../notebooks/analysis_report.ipynb)의 NB_LOAD·NB_CLEAN·NB_RFM, [테스트](../tests/test_analytics.py).

**꼬리 질문:** self.df를 바꾸는 메서드와 새 표를 반환하는 메서드는? 로드·정제·조인·대치는 상태를 바꾸고 RFM과 EDA 보정 Series는 원본 거래를 보존해 반환한다.

### 1-2. 처음부터 끝까지 실행되나?

**답변:** 현재 가상환경의 새 커널에서 전체 노트북을 실행한다. 새 복제본에는 원본을 넣지 않고 허가된 ZIP을 복원한 뒤 새 환경에서 같은 결과를 대조한다. 성공의 근거는 오류가 없다는 사실과 주요 집계 전체의 일치다.

**SRC/증거:** [utils/run_checks.py](../utils/run_checks.py)의 `run_notebook`, [utils/reproducibility.py](../utils/reproducibility.py)의 `verify_reproduction`, NB_REPRO. 회귀 테스트는 15개다.

**꼬리 질문:** 기존 커널로 실행하면 왜 부족한가? 이전 셀의 변수나 순서 의존 오류가 숨을 수 있다.

### 1-3. 행·열·자료형 조건을 충족하나?

**답변:** NB_LOAD에서 거래 행 수·조인 열 수·dtype·head/info/describe를 출력하고 1,000행·8열 이상을 assert한다. 수치 금액, 문자열/범주 정보, 날짜가 있으며 이미지는 상품 배치에서 처리한다. ID를 숫자 피처로 취급하지 않는다.

**SRC/증거:** [파이프라인](../src/pipeline.py)의 `load_data`, `join_products`; NB_LOAD; 로컬 기록의 transaction_rows/joined_columns.

**꼬리 질문:** 상품 조인으로 거래 수가 늘어나면? 상품 키 중복 가능성을 확인하고 many_to_one 검증으로 중단한다.

### 1-4. 이미지·텍스트 파생 열이 있는가?

**답변:** image_mean/image_std와 prod_name_length/prod_name_word_count를 상품별 계산 후 거래에 연결한다. RGB 전체 픽셀 평균과 ddof=0 표준편차이며, 원래 상품명은 보존한다.

**SRC/증거:** [이미지 도구](../utils/image_features.py)의 `extract_product_image_features`, [파이프라인](../src/pipeline.py)의 피처 메서드, NB_FEATURES. `Blue cotton shirt`는 17자·3단어, 절반 0/1 배열은 평균·표준편차 각각 0.5다.

**꼬리 질문:** 이미지가 없으면 0인가? 실패값은 결측이고 image_status로 누락·표본 미포함·손상 등을 구분한다.

### 1-5. 이상치 처리 전후를 비교했나?

**답변:** IQR 경계 밖을 표시하고 EDA용 금액 사본만 clip한다. 같은 축의 원값·보정 사본 박스플롯을 비교한다. RFM과 월별 금액은 원값을 유지한다.

**SRC/증거:** [파이프라인](../src/pipeline.py)의 `detect_outliers`, `clip_outliers`; [보고 도구](../utils/reporting.py)의 `make_figures`; NB_CLEAN·NB_PLOTS.

**꼬리 질문:** 고액이면 오류인가? 유효 구매일 수 있어 탐지만으로 오류를 확정하지 않는다.

### 1-6. 필수 차트 6종과 제목·축이 있는가?

**답변:** 거래 히스토그램·전후 박스플롯, 고객 그룹 막대·RFM 상관 히트맵, 관측 상품 이미지 산점도, 완전한 월의 금액 라인차트가 있다. 제목과 두 축 레이블을 assert한다.

**SRC/증거:** [utils/reporting.py](../utils/reporting.py)의 `make_figures`; NB_PLOTS; 로컬 figures의 01~06 PNG.

**꼬리 질문:** 거래가 없는 달은? 범위가 확인된 완전한 달은 0으로 표시하고 월 합계를 거래 합계와 대조한다.

### 1-7. 기술통계와 상관 2쌍을 해석했나?

**답변:** 금액과 텍스트 피처의 평균·중앙값·표준편차·사분위수를 구한다. 상품의 관측 이미지 평균–표준편차, 고객의 Frequency–Monetary 상관을 쌍별 표본 수와 함께 계산한다. 각 결과에 수치와 분석 단위에 맞는 시사점을 붙인다.

**SRC/증거:** [파이프라인](../src/pipeline.py)의 `summarize`, [보고 도구](../utils/reporting.py)의 `pair_correlation`, NB_STATS.

**꼬리 질문:** 상수 열·결측은? 유한 완전 관측 쌍만 사용하고 관측 부족·분산 0이면 계수를 해석하지 않는다. 상관은 인과가 아니다.

### 1-8. 4개 그룹과 인사이트 3개가 있는가?

**답변:** 우선순위 규칙으로 고객당 한 그룹을 배정하고 비어 있지 않은 그룹이 최소 4개인지 assert한다. 그룹별 고객 수·비중, 대표 RFM과 금액 기여를 비교한다. 인사이트는 VIP 유지, 최근 한 구매일 고객의 다음 구매, 낮은 최근성 고객의 재활성화를 근거·실행·검증으로 설명한다.

**SRC/증거:** [utils/analytics.py](../utils/analytics.py)의 `calculate_customer_rfm`, `segment_profile`; [utils/reporting.py](../utils/reporting.py)의 `write_insights`; NB_RFM·README의 인사이트.

**꼬리 질문:** 네 그룹을 만들려고 동점을 임의로 나눴나? 아니다. 같은 값에는 같은 점수다. 그룹 부족 시 관측 범위·표본·사업상 분류 이유를 재검토한다.

## 항목 2 · 설계 설명 4개

### 2-1. 메서드를 왜 분리했나?

**답변:** 데이터 상태·단계를 관리하는 클래스와 공통 계산을 구분했다. 노트북은 설정과 해석을 담당한다. 로드·조인·정제·피처·고객 집계의 단위와 부작용을 분리하면 작은 입력으로 검증하고 다른 입력에 재사용하기 쉽다.

**SRC/증거:** [src/pipeline.py](../src/pipeline.py), [utils/analytics.py](../utils/analytics.py), [utils/image_features.py](../utils/image_features.py). 독스트링의 입력·출력·변경 상태를 보여준다.

**꼬리 질문:** 전부 utils로 옮기면 클래스는 필요 없나? 클래스가 입력·현재 상태·감사 집계와 작업 순서를 관리하고 도구는 독립 계산을 재사용한다.

### 2-2. 벡터 연산 부분을 직접 지목해 달라.

**답변:** `batch.mean(axis=(1,2,3))`, `batch.std(axis=(1,2,3), ddof=0)`이 이미지마다 값 하나를 구한다. Python으로 픽셀을 하나씩 방문하는 대신 같은 dtype의 배열 축을 NumPy 내부 연산으로 축소한다.

**SRC/증거:** [utils/image_features.py](../utils/image_features.py)의 배치 집계와 NB_FEATURES의 batch_info.

**꼬리 질문:** for가 있는데 요구 위반 아닌가? 파일 I/O와 배치 순회에는 반복이 필요하다. 픽셀별 통계 계산을 배열 연산으로 수행한다.

### 2-3. 파라미터로 받은 이유는?

**답변:** IQR 배수, 대치 대상·그룹·대상 마스크, RFM 기준일·빈도 단위, 이미지 크기·배치를 외부에서 정한다. 다른 데이터의 의미와 자원 제약을 반영하고 한 번의 함수 구현으로 다른 조건을 검증할 수 있다.

**SRC/증거:** [파이프라인](../src/pipeline.py)의 메서드 인자와 [정제 테스트](../tests/test_analytics.py)의 주문 모드·잘못된 기준일·IQR 배수.

**꼬리 질문:** UCI 주문 데이터라면? 취소 주문과 수량·단가를 확인해 유효 금액을 준비하고, 주문 ID 문자열을 보존해 고유 주문 수 모드를 사용한다. H&M의 구매일 빈도와 주문 빈도를 혼동하지 않는다.

### 2-4. 분석 의사결정은 어디에 기록했나?

**답변:** 각 NB 구간의 Markdown에 이유·분석 단위·수치 근거·한계를 둔다. 예를 들어 상품 이미지 중 표본 미포함은 결측 오류와 구분하고 대치에서 제외한다. 관측 이미지와 대치 사본의 용도를 구분한다.

**SRC/증거:** [노트북](../notebooks/analysis_report.ipynb)의 NB_FEATURES·NB_CLEAN·NB_STATS, [통합 계획](a1_1_detailed_plan.md).

**꼬리 질문:** 결측이 실제로 없다면? 별도 가상 입력이나 표시한 시연용 사본에서 전략을 검증하고 실제 입력을 오염시키지 않는다.

## 항목 3 · 통계와 계산 원리 4개

### 3-1. IQR이 왜 필요하고 한계는 무엇인가?

**답변:** Q3−Q1로 가운데 절반의 퍼짐을 요약하고 그 밖의 먼 값을 탐색한다. 정규성 가정이 필수는 아니다. 비대칭·여러 상품군 혼합·IQR=0에서는 정상 꼬리를 과하게 표시하거나 구분력이 약해질 수 있어 도메인 검토가 필요하다.

**SRC/증거:** [utils/analytics.py](../utils/analytics.py)의 `iqr_limits`, [테스트](../tests/test_analytics.py). `[1,2,3,4,100]`은 경계 −1·7로 100만 표시하고 `[-2,1,2,3,6]`의 경계값은 포함한다.

**꼬리 질문:** 제거와 clip의 차이는? 제거는 행을 버리고 clip은 경계로 바꾼다. 현재는 탐지 마스크와 EDA 사본을 만들며 실제 금액 집계는 보존한다.

### 3-2. 그룹 평균 대치의 이유와 위험은?

**답변:** 카테고리별 분포 차이를 고려하려는 선택이다. 결측 위치만 그룹 평균으로 채우고 없으면 원래 관측 전체 평균을 사용한다. 평균 대치는 분산·상관을 바꾸고 그룹 차이를 과장하거나 축소할 수 있으며 결측 발생 원인을 복원하지 않는다.

**SRC/증거:** [utils/analytics.py](../utils/analytics.py)의 `impute_features`, NB_CLEAN. `[10,30,결측]→20`, 그룹 없는 기존 50 보존, fallback=30을 시연한다.

**꼬리 질문:** 그룹 전체가 결측이면? 전체 평균을 쓰고 그 열도 전부 결측이면 그대로 남겨 보고한다. 표본 미포함 이미지는 대치 대상에서 제외한다.

### 3-3. RFM 점수·그룹의 기준은?

**답변:** R은 작을수록, F·M은 클수록 높은 점수가 되도록 평균 순위를 만든다. `p=(평균 순위−0.5)/n`의 0.25·0.50·0.75 경계를 사용한다. 동점으로 점수별 인원이 같지 않을 수 있다. 점수와 원 Frequency를 함께 써 우선순위 그룹을 배정하고 프로파일·합계로 검증한다.

**SRC/증거:** [utils/analytics.py](../utils/analytics.py)의 `calculate_customer_rfm`, NB_RFM과 순서·동점 테스트.

**꼬리 질문:** qcut으로 무조건 4등분하면? 중복 경계로 실패하거나 tie-break로 같은 고객 지표에 다른 점수가 생길 수 있다. 현재 구현은 qcut이 아니다. 동일 값과 규칙의 의미를 우선한다.

### 3-4. NumPy가 빠른 이유와 SIMD는?

**답변:** 같은 dtype 배열에 대한 내부 컴파일 연산으로 Python 호출·객체 처리 비용을 줄일 수 있다. 연속 메모리와 접근 순서는 캐시 효율에 영향을 준다. SIMD는 CPU·빌드·연산에 따라 여러 원소를 한 명령으로 처리하는 최적화이며 항상 선택되거나 모든 연산이 같은 배수로 빨라지는 것은 아니다.

**SRC/증거:** [이미지 도구](../utils/image_features.py)의 stack·축 연산·ascontiguousarray와 NB_FEATURES의 shape/dtype/strides/nbytes/c_contiguous.

**꼬리 질문:** 슬라이스도 항상 연속인가? 아니다. view의 strides가 달라질 수 있다. 고급 인덱싱·stack 등은 복사도 만들 수 있고 총 메모리는 배치 배열 크기보다 크다.

## 항목 4 · 확장과 사업 검증 3개

### 4-1. 고객 100만 명·1024×1024 이미지라면 병목은?

**답변:** 고객 수와 고유 이미지 수를 구분해야 한다. RGB 1024×1024 float64 한 장은 24MiB, float32는 12MiB다. 전체 원본 배열을 모으기 전에 상품 중복 제거, 파일 읽기·디코딩, 축소와 배치 메모리를 점검한다. 현재 배치 32×32×3×float32×32의 픽셀 배열 자체는 384KiB다.

**SRC/증거:** [utils/image_features.py](../utils/image_features.py)의 상품 단위 배치, [추출 노트북](../notebooks/prepare_hm_sample.ipynb)의 청크 읽기.

**꼬리 질문:** 개선 순서는? 고유 상품 피처 캐시·원본 읽기 최소화·축소·배치 조절·거래 usecols/chunksize·집계 순서 개선을 측정하며 선택한다. 측정 없이 첫 병목이나 속도 배수를 확정하지 않는다.

### 4-2. 어떤 캠페인을 우선할 것인가?

**답변:** 현재 그룹별 고객·금액 비중과 기존 고객 가치에 근거해 VIP 유지 안내 같은 작은 실험부터 검토한다. 금액 기여는 관측이고 캠페인 성과는 가설이다. 할인 비용·마진·반응 데이터가 없어 ROI 순위를 확정하지 않는다.

**SRC/증거:** NB_RFM 프로파일, [utils/reporting.py](../utils/reporting.py)의 `write_insights`, [README](../README.md)의 근거·실행·검증.

**꼬리 질문:** 검증 지표와 위험은? 무작위 대조군 대비 순증 구매율·고객당 마진·혜택 비용·수신 거부를 본다. 자연 재구매·계절성·할인 잠식을 고려하고 연락 동의를 확인한다.

### 4-3. 예측 모델로 확장하면?

**답변:** 기준시점 T까지의 고객 RFM·상품 선호·이미지/텍스트 집계를 피처로, T 이후 30일 구매 여부나 구매금액을 타겟으로 삼을 수 있다. 타겟 기간이 끝까지 관측된 사례만 학습·평가에 사용하고 시간순으로 분리한다.

**SRC/증거:** 현재 파이프라인은 분석·피처 생성까지만 구현했다. 실제 모델 학습은 미구현이다. SRC 후보는 [파이프라인](../src/pipeline.py)의 RFM과 상품 피처다.

**꼬리 질문:** 누수는 어떻게 막나? T 이후 거래를 피처에 넣지 않고 학습 구간으로 대치 기준을 산출한다. 향후 구매금액을 LTV로 부르지 않고 신규/미관측 고객 처리와 계절성을 별도로 설계한다.

## 선택 보너스와 마지막 연습

이미지 히스토그램·엣지, 가입일 기반 코호트, Plotly 인터랙션은 선택 항목이다. 현재 필수 구현과 구분하며 미구현 보너스를 완료로 설명하지 않는다. 가입일이 없으면 첫 관측 구매월은 대체 기준이고 진짜 가입 코호트가 아니다.

모의 평가에서는 ① 입력·조인 시연 ② 픽셀 0/1 평균·표준편차 ③ 대치 20/30/50 ④ IQR 경계 ⑤ 고객 A·B 손계산 ⑥ 실제 그룹 표·차트·한계 ⑦ 새 환경 재현 순으로 연습한다. 말로 답한 뒤 해당 코드를 직접 수정·재실행할 수 있는지 확인한다.
