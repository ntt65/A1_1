# A1 1 평가 대비 Q&A와 시연 순서

기준: [평가 PDF](a1_1_eval.pdf) 15~17페이지와 [평가 Markdown](a1_1_eval.md)의 평가 문항. 자료 대조 의견은 [검토 문서](a1_1_eval_review.md), 용어 해설은 [tech_study.md](tech_study.md)다. 이슈 #6에서 관리한다.

## 연습과 증거 준비

각 답변은 실제 구현과 실행 결과를 함께 읽을 수 있도록 해당 위치를 연결했다. 노트북 링크의 `In [번호]`는 노트북 화면에서 확인할 실행 셀이고, 줄 번호는 저장된 소스와 출력의 위치를 가리킨다. 실제 계산 결과는 로컬 `data/processed/analysis_report.executed.ipynb`와 `analysis_verification.json`, 새 환경 비교는 `reproduction_verification.json`에서 확인한다. 평가 노트북은 원본 데이터·ID·이미지 예시와 실행 출력을 그대로 보존한다. 실제 집계 출력·검토한 차트는 `docs/results/analysis_report.md`와 `docs/results/analysis_aggregates.json`에서도 확인할 수 있다. 사용자 지시에 따라 평가 실행 결과는 마스킹하지 않는다. 실행과 제출 요약은 [README](../README.md)에서 확인한다.

```powershell
.venv\Scripts\python.exe -B -m utils.run_checks --with-sample
.venv\Scripts\python.exe -B -m utils.reproducibility
```

실데이터 접근 전에 환경·표본 준비가 필요하다. 원본을 공유하지 않는 자리에서는 아래 가상 입력과 공개 소스를 사용하고 실제 검증 여부를 구분해 말한다.

## 5. 평가문항

### 항목 1

#### 1-1

- src/pipeline.py 파일에 DataAnalyzer Class가 정의되어 있고, load_data(), handle_missing_values(), detect_outliers(), calculate_rfm() 메서드가 모두 포함되어 있는가?

**답변**

`src/pipeline.py`에 `DataAnalyzer` 클래스와 필수 메서드 4개가 정의되어 있다. [DataAnalyzer 정의 (pipeline.py 20행)](../src/pipeline.py#L20)

노트북의 `NB_LOAD`에서 거래 표본 CSV 경로를 넘겨 `analyzer = DataAnalyzer(DATA / "transactions_sample.csv")`를 만들고, 이 인스턴스를 이후 정제와 RFM 집계에 사용한다. [analysis_report.ipynb (line 679)](../notebooks/analysis_report.ipynb#L679)

- **`load_data()` · `NB_LOAD`** — 바로 다음 줄에서 고객 ID, 상품 ID, 거래일, 금액, 판매 채널을 필수 열로 지정해 CSV를 읽는다. 거래일인 `t_dat`를 날짜형으로 변환하고 읽어 온 거래 표를 `analyzer.df`에 저장한다. [거래 표와 자료형 출력 · In [2]](../notebooks/analysis_report.ipynb#L238)
- **`handle_missing_values()` · `NB_CLEAN`** — 상품 피처 표의 사본을 별도의 `DataAnalyzer` 인스턴스인 `imputer`에 넣는다. `image_mean_eda`와 `image_std_eda`의 결측값을 상품 유형별 평균으로 채우고, 그룹 평균이 없으면 전체 관측 평균을 사용한다. 표본에 포함되지 않은 상품은 대치 대상에서 제외한다. [결측치 대치 결과표 · In [4]](../notebooks/analysis_report.ipynb#L1142)
- **`detect_outliers()` · `NB_CLEAN`** — 노트북이 `analyzer.clip_outliers("price", ...)`를 호출하면, 이 메서드가 내부에서 `detect_outliers()`를 호출한다. IQR 경계 밖 거래를 마스크로 표시하고 경계와 건수를 기록한다. 노트북은 경계로 보정한 사본을 분포 비교에 쓰고 원래 거래 금액은 유지한다. [IQR 이상치 탐지 결과 · In [4]](../notebooks/analysis_report.ipynb#L1226)
- **`calculate_rfm()` · `NB_RFM`** — 고객 ID, 거래일, 원래 거래 금액, 표본 기록의 기준일을 넘겨 고객별 마지막 구매 이후 경과일, 고유 구매일 수, 구매금액 합계를 집계한다. 반환된 고객별 RFM 표로 그룹을 요약하고, 고객이 한 번씩 집계됐는지와 그룹이 4개 이상인지 확인한다. [RFM 그룹 요약표 · In [5]](../notebooks/analysis_report.ipynb#L1398)

#### 1-2

- 노트북(notebooks/analysis_report.ipynb)이 처음부터 끝까지 에러 없이 실행되는가?

**답변**

- **전체 실행** — 새 커널에서 위에서 아래로 실행했고 코드 셀 13개의 출력이 저장되어 있다. 새 커널에서 실행하면 이전 실행의 변수에 의존하는 오류를 확인할 수 있다. [새 커널 실행 코드](../utils/run_checks.py#L17) · [전체 실행 PASS 기록](../README.md#L415)
- **완료와 재현** — `NB_REPRO`에 결과 저장 완료 메시지가 있고 마지막 `NB_TIMING`에 단계별 시간표가 남아 있다. 재현 검증은 새 복제본에서 표본 ZIP과 의존성을 복원해 집계를 기준 결과와 대조한다. [완료 메시지 · In [12]](../notebooks/analysis_report.ipynb#L4820) · [마지막 셀의 시간표 · In [13]](../notebooks/analysis_report.ipynb#L4901) · [새 환경 재현 코드](../utils/reproducibility.py#L15)

#### 1-3

- 데이터셋이 1,000행 이상 / 8컬럼 이상이며, 수치형·범주형·날짜형·이미지(배열) 중 3종 이상의 데이터 타입을 포함하는가?

**답변**

- **행과 열** — 거래 정제와 상품 조인 결과는 8,084행·9열이다. 노트북이 1,000행·8열 이상인지 검사한다. 상품 조인은 `many_to_one`으로 검증해 중복 상품 키 때문에 거래가 불어나는 경우를 차단한다. [조인 구현](../src/pipeline.py#L71) · [최소 크기 검사](../notebooks/analysis_report.ipynb#L693) · [행·열 요약 · In [2]](../notebooks/analysis_report.ipynb#L587)
- **자료형** — 금액은 수치형, `t_dat`는 날짜형, 상품 유형·식별자는 문자열이다. 식별자는 키로 사용하고 이미지는 상품 단위 배열 배치로 처리한다. [거래 구조와 dtype · In [2]](../notebooks/analysis_report.ipynb#L238) · [이미지 배열 정보 · In [3]](../notebooks/analysis_report.ipynb#L903)

#### 1-4

- 이미지 배열에서 추출한 Mean/Std 피처와 텍스트 파생 변수(단어 수 또는 문자열 길이)가 데이터프레임에 새로운 컬럼으로 추가되어 있는가?

**답변**

- **이미지 피처** — 상품별 RGB 픽셀 전체의 평균과 모집단 표준편차(`ddof=0`)를 `image_mean`, `image_std` 열에 기록한다. 이미지가 없거나 읽기에 실패하면 값을 결측으로 두고 상태를 남긴다. [이미지 피처 추출](../utils/image_features.py#L64) · [이미지 상태 출력 · In [3]](../notebooks/analysis_report.ipynb#L771)
- **텍스트 피처** — 상품명을 보존하고 `prod_name_length`와 `prod_name_word_count`를 추가한다. 상품별 피처는 상품 키로 거래에 연결한다. [텍스트 피처 구현](../src/pipeline.py#L236) · [네 파생 열의 요약표 · In [3]](../notebooks/analysis_report.ipynb#L817)

#### 1-5

- 이상치 처리 전후 분포 비교 시각화(박스플롯 등)가 포함되어 있는가?

**답변**

- **처리** — `clip_outliers()`는 IQR 경계 밖 212행을 표시한 뒤 분포 비교용 금액 사본을 경계값으로 보정한다. RFM과 월별 집계에는 원래 금액을 사용한다. [보정 코드](../src/pipeline.py#L156) · [탐지 건수와 원금액 보존 · In [4]](../notebooks/analysis_report.ipynb#L1226)
- **시각화** — 같은 금액 축의 박스플롯에서 보정 전후를 비교한다. 경계를 벗어난 고액 거래도 유효 구매일 수 있으므로 검토 대상으로 해석한다. [박스플롯 셀 출력 · In [7]](../notebooks/analysis_report.ipynb#L1788) · [전후 박스플롯](results/figures/02_boxplot.png)

#### 1-6

- 히스토그램, 박스플롯, 막대그래프, 히트맵, 산점도, 라인차트 6종 시각화가 모두 존재하고, 각 차트에 제목과 축 레이블이 표기되어 있는가?

**답변**

- **생성과 검증** — `make_figures()`가 아래 6종을 생성한다. 노트북에서 차트 수, 제목, 가로축과 세로축의 레이블을 검사한다. [차트 생성 함수](../utils/reporting.py#L35) · [6종·제목·축 검사 · In [7]](../notebooks/analysis_report.ipynb#L2000)
- 거래 금액 분포와 이상치 처리 전후를 보여준다. [히스토그램](results/figures/01_histogram.png) · [박스플롯](results/figures/02_boxplot.png)
- 고객 그룹 규모와 RFM 지표 간 상관을 보여준다. [막대그래프](results/figures/03_bar.png) · [히트맵](results/figures/04_heatmap.png)
- 관측 이미지 피처 간 관계와 완전한 월의 거래 금액 추이를 보여준다. [산점도](results/figures/05_scatter.png) · [라인차트](results/figures/06_line.png)

#### 1-7

- 기술통계(평균/중앙값/표준편차/사분위수)와 상관분석(2쌍 이상) 결과가 제시되고, 각각에 수치 근거 + 시사점 해석이 작성되어 있는가?

**답변**

- **기술통계** — 금액과 상품명 파생 열의 평균·중앙값·표준편차·사분위수를 계산한다. 금액은 평균과 중앙값의 차이와 분포의 꼬리를 함께 해석한다. [기술통계 메서드](../src/pipeline.py#L177) · [통계량 출력 · In [6]](../notebooks/analysis_report.ipynb#L1557)
- **상품 단위 상관** — 관측 이미지 200개에서 이미지 평균과 표준편차의 Pearson r은 −0.944다. 평균이 높은 이미지에서 픽셀 퍼짐이 작은 경향이 있으며 촬영 배경의 영향을 고려한다. [이미지 상관 결과 · In [6]](../notebooks/analysis_report.ipynb#L1648)
- **고객 단위 상관** — 1,000명에서 Frequency와 Monetary의 r은 0.640이다. 구매일이 많은 고객은 관측 구매금액도 큰 경향을 보인다. 두 지표는 같은 거래에서 집계된다. [유효 관측 쌍의 상관 계산](../utils/reporting.py#L8) · [고객 상관 결과 · In [6]](../notebooks/analysis_report.ipynb#L1664)

#### 1-8

- RFM 분석 결과로 고객이 4개 이상 그룹으로 세분화되어 있으며, README.md에 비즈니스 인사이트가 3가지 이상 (근거 + 실행 + 검증) 형식으로 정리되어 있는가?

**답변**

- **그룹 결과** — 우선순위 규칙으로 고객 한 명당 한 그룹을 배정했다. VIP 270명, Churned 499명, New 149명, Loyal 82명이다. 그룹별 고객 수·비중과 금액 기여를 확인할 수 있다. [점수와 그룹 배정 규칙](../utils/analytics.py#L151) · [고객 그룹 프로파일 · In [5]](../notebooks/analysis_report.ipynb#L1398)
- **인사이트 3개** — README는 VIP 유지, 최근 한 구매일 고객의 다음 구매 유도, 낮은 최근성 고객의 재활성화를 각각 근거·실행·검증으로 정리한다. 예를 들어 고객의 27.0%이면서 관측 금액의 52.3%를 차지한 VIP에는 유지 안내를 시험하고 대조군과 성과를 비교하도록 제안한다. [README 인사이트 3개](../README.md#L544) · [노트북 인사이트 출력 · In [8]](../notebooks/analysis_report.ipynb#L2046)

### 항목 2

#### 2-1

- DataAnalyzer 클래스의 메서드를 왜 현재와 같이 분리했는지, 각 메서드의 책임과 역할을 설명할 수 있는가?

**답변**

- **로드와 조인** — 거래 CSV를 읽고 자료형을 준비하는 책임과 상품 키를 검증해 상품 속성을 붙이는 책임을 나눴다. 입력 스키마 오류와 조인 오류를 단계별로 확인할 수 있다. [로드 메서드](../src/pipeline.py#L36) · [조인 메서드](../src/pipeline.py#L71) · [거래 표 구조 · In [2]](../notebooks/analysis_report.ipynb#L238)
- **정제와 피처** — 결측 대치는 적용 대상과 정책을 받고, 이상치 탐지는 원금액을 보존하면서 마스크를 반환한다. 이미지·텍스트 피처는 상품별로 만든다. 클래스가 표와 감사 기록을 관리하고 독립 계산은 도구 함수에서 재사용한다. [정제 메서드](../src/pipeline.py#L129) · [이미지 피처 메서드](../src/pipeline.py#L189) · [대치 결과 · In [4]](../notebooks/analysis_report.ipynb#L1142)
- **고객 집계** — `calculate_rfm()`은 원거래 표를 보존하며 고객 단위 결과를 반환한다. 노트북에서 기준일을 넘기고 고객 그룹과 집계값을 확인한다. [RFM 메서드](../src/pipeline.py#L162) · [고객 그룹 표 · In [5]](../notebooks/analysis_report.ipynb#L1398)

#### 2-2

- 이미지 피처 추출 로직에서 Python for loop 대신 NumPy 배열 연산을 사용한 코드 부분을 직접 지목하고, 그렇게 구현한 설계 의도를 설명할 수 있는가?

**답변**

- **구현 위치** — `batch.mean(axis=(1, 2, 3))`와 `batch.std(axis=(1, 2, 3), ddof=0)`는 높이·너비·채널 축을 한 번에 줄여 이미지마다 평균과 표준편차 하나씩을 반환한다. 파일 읽기와 배치 순회에 반복을 쓰고 픽셀 통계는 NumPy 배열 연산으로 계산한다. [평균·표준편차 계산](../utils/image_features.py#L128) · [실제 배치 모양과 자료형 · In [3]](../notebooks/analysis_report.ipynb#L903) · [피처 출력 · In [3]](../notebooks/analysis_report.ipynb#L817)

#### 2-3

- 주요 파라미터(이상치 임계값, 결측치 대치 전략, RFM 기준일 등)를 하드코딩하지 않고 인자로 설계한 이유와, 이 설계가 다른 데이터셋 적용 시 어떤 이점을 주는지 설명할 수 있는가?

**답변**

- **이상치 임계값** — `threshold`로 IQR 배수를 받으므로 새 데이터의 분포와 분석 목적에 따라 탐지 경계를 조정할 수 있다. [이상치 임계값 인자](../src/pipeline.py#L145) · [탐지 결과 · In [4]](../notebooks/analysis_report.ipynb#L1226)
- **결측 대치 전략** — `strategy`, 그룹, 열, 대상 마스크를 받아 데이터별 분류 체계와 결측 사유에 맞춰 바꿀 수 있다. [대치 전략 인자](../src/pipeline.py#L129) · [노트북 대치 인자](../notebooks/analysis_report.ipynb#L1314) · [대치 결과 · In [4]](../notebooks/analysis_report.ipynb#L1142)
- **RFM 기준** — `reference_date`와 `frequency_unit`으로 비교 시점과 빈도 단위를 지정한다. H&M 표본은 표본 기록의 기준일과 고유 구매일 수를 쓰며, 주문 ID가 있는 데이터는 고유 주문 수를 선택할 수 있다. [기준일·빈도 인자](../src/pipeline.py#L162) · [노트북 기준일 전달](../notebooks/analysis_report.ipynb#L1491) · [RFM 결과 · In [5]](../notebooks/analysis_report.ipynb#L1398)

#### 2-4

- 노트북의 마크다운 설명이 분석 단계별로 작성되어 있으며, 코드만으로는 파악하기 어려운 의사결정 (예: 대치 전략 선택 근거) 이 문서화되어 있는가?

**답변**

- **피처 단계** — 이미지 관측 범위와 상품 단위 계산의 이유를 기록한다. 이미지 표본에 포함되지 않은 상품은 별도 상태로 관리한다. [이미지·텍스트 피처 설명](../notebooks/analysis_report.ipynb#L710) · [이미지 상태 출력 · In [3]](../notebooks/analysis_report.ipynb#L771)
- **정제 단계** — 상품 유형별 평균을 선택한 이유와 적용 범위를 설명하고, 관측값과 대치 사본의 사용처를 구분한다. IQR 보정 사본은 분포 비교에 사용한다. [결측과 이상치 처리 설명](../notebooks/analysis_report.ipynb#L1080) · [대치 결과 · In [4]](../notebooks/analysis_report.ipynb#L1142)
- **통계 단계** — 상품 단위 이미지 상관과 고객 단위 RFM 상관을 각각 해석하고 수치 근거와 한계를 남긴다. [통계 분석 설명](../notebooks/analysis_report.ipynb#L1513) · [상관 결과 · In [6]](../notebooks/analysis_report.ipynb#L1664)

### 항목 3

#### 3-1

- IQR 방식의 이상치 탐지가 왜 필요한지, 어떤 데이터 분포에서 효과적이고 어떤 경우에 한계가 있는지(예: 정규분포 vs 비대칭 분포) 설명하고, 자신의 코드에서 해당 로직을 짚어 보여줄 수 있는가?

**답변**

- **IQR을 쓰는 이유** — `IQR = Q3 − Q1`은 가운데 절반의 퍼짐이다. 극단값의 크기에 덜 민감한 사분위수로 `Q1 − 1.5×IQR`과 `Q3 + 1.5×IQR` 경계를 만든다. [IQR 경계 계산](../utils/analytics.py#L117) · [경계 밖 마스크 구현](../src/pipeline.py#L145)
- **분포에 따른 한계** — 이론상 경계 밖 비율은 표준정규분포에서 약 0.70%, 오른쪽 꼬리가 긴 `exp(N(0,1))` 예시에서 약 7.76%다. 비대칭, 상품군 혼합, IQR이 0인 경우에는 정상 꼬리까지 표시되거나 구분력이 약해질 수 있다. [분포별 IQR 해석](../README.md#L457)
- **실제 표본** — 8,084행에서 왜도는 +1.554, 상한 초과는 212행(2.62%)이었다. EDA 사본의 경계 보정 후 표본분산은 0.000222373에서 0.000184101로 줄었고 중앙값은 0.022017로 같았다. [전후 통계표 · In [4]](../notebooks/analysis_report.ipynb#L1276) · [같은 축의 전후 박스플롯](results/figures/02_boxplot.png)

#### 3-2

- 결측치를 그룹별 평균(또는 중앙값)으로 대치하는 이유와, 이 방식이 데이터 분포에 미치는 잠재적 위험(예: 분산 축소, 그룹 간 차이 과장)을 설명할 수 있는가?

**답변**

- **그룹 평균 대치** — 상품 유형별 피처 수준 차이를 반영한다. 그룹에 관측값이 없으면 전체 관측 평균을 쓰고, 열 전체가 결측이면 결측으로 남긴다. 미표본 이미지는 대치 대상에서 제외한다. [그룹 평균 대치 구현](../utils/analytics.py#L71) · [실제 대치 결과표 · In [4]](../notebooks/analysis_report.ipynb#L1142)
- **분포 변화** — 평균으로 채운 값이 중심에 쌓여 그룹 내 분산이 줄 수 있고, 그룹별 결측률이 다르면 그룹 간 차이와 상관도 달라질 수 있다. 노트북은 동일 상품 범위의 대치 전후 밀도를 비교하고 이미지 상관에는 원래 관측값을 사용한다. [대치 전후 밀도 출력 · In [8]](../notebooks/analysis_report.ipynb#L2143)

#### 3-3

- RFM 점수 산정 기준(분위수 구간, 스코어링 방식)을 왜 그렇게 설정했는지, 세분화 결과가 비즈니스적으로 타당한 근거를 데이터에서 뽑아 설명할 수 있는가?

**답변**

- **점수 산정** — R은 작을수록, F·M은 클수록 높은 점수를 받는다. `p = (평균 순위 − 0.5) / n`의 0.25·0.50·0.75 경계로 1~4점을 부여한다. 같은 값은 같은 점수를 받으므로 구간별 인원은 달라질 수 있다. [평균 순위와 점수 코드](../utils/analytics.py#L151)
- **그룹 근거** — 점수와 원래 구매일 수에 우선순위 규칙을 적용한다. VIP는 고객의 27.0%이면서 관측 금액의 52.3%를 차지하고, New의 구매일 수 중앙값은 1일이다. 이 차이가 VIP 유지와 New의 다음 구매 유도를 각각 검토하는 근거다. [그룹별 RFM·금액 표 · In [5]](../notebooks/analysis_report.ipynb#L1398) · [그룹 요약과 사업 해석](../README.md#L534)

#### 3-4

- NumPy 벡터 연산이 Python for loop보다 빠른 이유를 메모리 구조(연속 메모리 배치)와 연산 방식(SIMD 등) 관점에서 설명할 수 있는가?

**답변**

- **연산 방식** — 같은 dtype의 수치 배열을 컴파일된 NumPy 축 연산으로 처리하면 픽셀마다 Python 객체를 처리하는 비용이 줄어든다. SIMD는 지원하는 CPU·빌드·연산에서 여러 원소를 한 명령으로 처리하는 최적화다. [배치 축 연산](../utils/image_features.py#L128)
- **메모리 구조** — C 연속 배열의 마지막 축은 작은 stride로 연속 접근할 수 있어 캐시 활용에 유리하다. 슬라이스는 stride를 바꿀 수 있고 배열 연속화 과정에서 복사가 생길 수 있다. [샘플 배열 연속화](../utils/image_features.py#L36) · [실제 배치의 stride와 연속성 · In [3]](../notebooks/analysis_report.ipynb#L903) · [슬라이스 비교 코드 · In [3]](../notebooks/analysis_report.ipynb#L1066)

### 항목 4

#### 4-1

- 만약 고객 수가 100만 명으로 증가하고 이미지 해상도가 1024×1024로 커진다면, 현재 파이프라인에서 가장 먼저 병목이 발생하는 지점은 어디이며, 이를 어떻게 개선하겠는가?

**답변**

- **현재 병목** — 이미지 200장을 워밍업한 뒤 3회 계측했을 때 전체 중앙값은 2.115초, 파일 읽기와 디코딩을 합친 `imread()` 중앙값은 1.797초였다. 실행별 비중의 중앙값 84.9%를 근거로 현재 순차 경로에서는 읽기·디코딩을 먼저 검토한다. [현재 읽기 위치](../utils/image_features.py#L114) · [노트북 실측 기록](../notebooks/analysis_report.ipynb#L720)
- **해상도 영향** — 1024×1024 RGB 한 장은 `float32`에서 12 MiB, `float64`에서 24 MiB다. 32×32 `float32` 32장의 축소 배치 상한은 384 KiB이며 디코딩·통계 임시 배열은 별도다. 실제 처리량에는 고객 수 외에도 고유 이미지 수, 스토리지, 압축 형식이 영향을 준다. [현재 배치 메모리 정보 · In [3]](../notebooks/analysis_report.ipynb#L903)
- **개선과 검증** — 상품 ID·파일 버전·피처 설정을 기준으로 캐시하고, 캐시가 없는 파일은 제한된 워커에서 읽고 축소한다. 워커 수별 처리량·최대 메모리·오류와 결과 일치를 확인한다. 거래는 필요한 열을 청크로 집계하고 고객별 구매일 중복을 제거한다. [병목 개선과 검증 설계](../README.md#L471)

#### 4-2

- 이 RFM 분석 결과를 실제 마케팅 캠페인에 적용한다면, 가장 먼저 액션을 취해야 할 세그먼트는 어디이며 그 이유는 무엇인가? 해당 전략의 리스크와 이를 검증하기 위해 추가로 필요한 데이터는 무엇인가?

**답변**

- **우선 세그먼트** — VIP 유지 안내부터 소규모로 시험한다. 관측 표본에서 VIP는 고객의 27.0%이며 구매금액의 52.3%를 차지한다. [VIP 고객·금액 비중 · In [5]](../notebooks/analysis_report.ipynb#L1480) · [VIP 유지 실험안](../README.md#L548)
- **위험과 추가 데이터** — 자연 재구매나 계절성이 캠페인 성과처럼 보일 수 있고 할인 비용이 고객당 마진을 줄일 수 있다. 발송·반응 기록, 할인 비용, 마진, 연락 동의, 추가 관찰 기간의 거래 데이터가 필요하다.
- **검증** — 무작위 미발송군과 구매율·고객당 마진·수신 거부를 비교한다. 현재 그룹 프로파일은 실험 대상을 고른 근거이며 캠페인 효과는 실험으로 확인한다. [노트북 사업 인사이트 · In [8]](../notebooks/analysis_report.ipynb#L2046)

#### 4-3

- 이 분석 파이프라인을 머신러닝 예측 모델로 확장한다면, 어떤 타겟 변수(예: 이탈 여부, 구매 금액)를 설정하고 현재 파이프라인에서 생성한 피처 중 어떤 것을 활용하겠는가?

**답변**

- **타겟** — 기준시점 T 이후 30일 구매 여부를 분류 타겟으로 삼을 수 있다. 예상 지출을 구하려면 같은 기간의 구매금액을 회귀 타겟으로 삼는다.
- **후보 피처** — T까지의 고객 RFM, 상품 유형별 구매 비중, 구매 상품의 이미지 평균·표준편차와 상품명 길이·단어 수를 고객 단위로 집계한다. 아래 결과가 활용할 수 있는 기존 산출물이며 모델 학습은 확장 설계다. [RFM 구현](../src/pipeline.py#L162) · [RFM 결과 · In [5]](../notebooks/analysis_report.ipynb#L1398) · [상품 피처 결과 · In [3]](../notebooks/analysis_report.ipynb#L817)
- **시점 분리** — 타겟 30일을 끝까지 관측한 사례를 쓰고 기준시점 순서로 학습·평가를 나눈다. 학습 구간의 자료로 대치 기준을 정하고 T 이후 거래는 타겟 산출에 사용한다.

### 항목 5

보너스 문제 해결에 따른 크레딧 부여

**답변**

- **고급 이미지 피처** — NumPy로 밝기 8구간 히스토그램과 인접 픽셀의 평균 절대차를 계산했다. 관측 상품 200개의 히스토그램 합이 1인지 검증했다. [이미지 통계 구현](../utils/image_features.py#L38) · [관측 상품 검증 출력 · In [9]](../notebooks/analysis_report.ipynb#L2526) · [밝기 히스토그램](results/bonus/image_histogram.png)
- **코호트 분석** — 가입일이 없어 첫 관찰 구매월로 고객 1,000명을 550명·288명·162명으로 나눴다. 월별 재구매율을 계산하고 미관측 미래 월은 `NaN`으로 표시했다. [코호트 계산](../utils/bonus.py#L9) · [코호트별 고객 수 · In [10]](../notebooks/analysis_report.ipynb#L2605) · [코호트 히트맵](results/bonus/cohort_retention.png)
- **인터랙티브 RFM** — 전체 고객 ID와 RFM 점을 Plotly 차트에 저장했다. 독립 HTML에서 오프라인 필터와 회전을 확인했다. [Plotly 차트 생성](../utils/bonus.py#L59) · [Plotly 실행 출력 · In [11]](../notebooks/analysis_report.ipynb#L2843) · [인터랙티브 HTML](results/bonus/rfm_interactive.html)

## 마지막 연습

모의 평가에서는 ① 입력·조인 시연 ② 픽셀 0/1 평균·표준편차 ③ 대치 20/30/50 ④ IQR 경계 ⑤ 고객 A·B 손계산 ⑥ 실제 그룹 표·차트·한계 ⑦ 새 환경 재현 순으로 연습한다. 말로 답한 뒤 해당 코드를 직접 수정·재실행할 수 있는지 확인한다.
