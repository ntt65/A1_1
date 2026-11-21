[a1_1_mission.md](https://github.com/ntt65/A1_1/blob/main/docs/a1_1_mission.md) · [README.md](https://github.com/ntt65/A1_1/blob/main/README.md#%EC%9D%B4%EC%BB%A4%EB%A8%B8%EC%8A%A4-%EB%A9%80%ED%8B%B0%EB%AA%A8%EB%8B%AC-%EB%B6%84%EC%84%9D--hm-%ED%91%9C%EB%B3%B8)
("이커머스 멀티모달 분석 · H&M 표본")를 초보자 눈높이에 맞춰 강의 순서대로 정리한 스터디 노트입니다. [통합 계획](https://github.com/ntt65/A1_1/blob/main/docs/a1_1_detailed_plan.md), [체크표](https://github.com/ntt65/A1_1/blob/main/docs/a1_1_checklist.md), [평가용 실행 노트북](https://github.com/ntt65/A1_1/blob/main/notebooks/analysis_report.ipynb), [질문별 기술 발표 PPT](https://github.com/ntt65/A1_1/blob/main/docs/presentation/a1_1_eval_technical_final.pptx)의 흐름을 따라가며 **수치·구조·소스코드 위치·주의점**을 순서대로 짚습니다.

---

### Step 1 · 프로젝트 개요 & 평가용 실행 증거 (`README.md` 1~20행)

* **발표 오프닝 한 문장:** 이 프로젝트는 H&M 이커머스 표본 데이터(유효 거래 **8,084행**, 고객 **1,000명**, 상품 **4,705개**, 관측 이미지 **200장**)를 [`DataAnalyzer`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L20) 클래스로 통합해 **정제·멀티모달 피처·결측 대치·IQR 보정·RFM 세분화·시각화 6종·보너스 3종**까지 새 커널에서 오류 없이 재현한 분석 파이프라인입니다.
* **관찰 범위와 기준일:** `2020-06-01` 포함 ~ `2020-09-01` 제외, 전체 판매 채널, 시드 `42`, RFM 기준일 `2020-08-31`.

#### 평가 문항 19개 증거 지도 (발표 시 시연 위치 매핑)

| 문항 묶음 | 노트북 셀(`NB_*`) | 핵심 수치·증거 (발표 키워드) | 코드(SRC) |
| --- | --- | --- | --- |
| **1–3 · 클래스·실행·입력** | `NB_LOAD` (`1196c1cf`) | `DataAnalyzer`, 결측 두 이름(`handle_missing_values`/`handle_missing`) 동일 구현, 조인 후 **8,084행·9열**, `head()`/`info()`/`describe()` 보존 | [`DataAnalyzer`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L20) · [`load_data`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L36) · [test_analytics.py](https://github.com/ntt65/A1_1/blob/main/tests/test_analytics.py) |
| **4 · 파생 피처** | `NB_FEATURES` (`936e811c`) | `image_mean`/`std`, `prod_name_length`/`word_count`, 가상 입력 `"Blue cotton shirt"` → **17자·3단어**, 이미지 관측 **200개** | [`extract_text_features`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L236) · [`extract_product_image_features`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L64) |
| **5–6 · IQR·그림** | `NB_CLEAN` (`a32f822f`), `NB_PLOTS` (`87a953b4`) | `1.5×IQR` **212행** 탐지, 하한 **−0.012729**·상한 **0.061847**, 필수 차트 6종 | [`clip_outliers`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L156) · [`make_figures`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L35) |
| **7 · 기술통계·상관** | `NB_STATS` (`333254fa`) | 상품 200쌍 `r = -0.9435`, 고객 1,000쌍 `r = 0.6397` (분석 단위 분리) | [`summarize`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L177) · [`pair_correlation`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L8) |
| **8 · 고객군·인사이트** | `NB_RFM` (`b4769e15`) | **VIP 270명**, **Churned 499명**, **New 149명**, **Loyal 82명**, 인사이트 3건(근거-실행-검증) | [`calculate_customer_rfm`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L128) · [`write_insights`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L73) |
| **9–12 · 책임·축·설정·근거** | `NB_FEATURES`, `NB_CLEAN`, `NB_RFM` | 이미지 `N` 보존 & `(H,W,C)` 축약(`axis=(1,2,3)`), 대치·IQR은 **EDA 사본**, RFM은 **원금액** | [`extract_image_features`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L189) · [a1_1_detailed_plan.md](https://github.com/ntt65/A1_1/blob/main/docs/a1_1_detailed_plan.md) |
| **13 · IQR 필요성·한계** | `NB_CLEAN` (`a32f822f`) | 이론 경계 밖: 정규 **0.70%** vs 로그정규 **7.76%** / 실제 거래 상한 초과 **212행**, 분산 **−17.21%**, 중앙값 동일 | [`iqr_limits`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L117) · [`clip_outliers`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L156) |
| **14–16 · 대치·점수·배치** | `NB_CLEAN`, `NB_FEATURES` | 이미지 평균 대치 전후 분산 **0.010424 → 0.010130**, RFM 동점 평균 순위 테스트, NumPy 배치 축 | [`impute_features`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L71) · [`prepare_image`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L11) |
| **17 · 대규모 이미지 병목** | `NB_FEATURES` (`923b9a03`) | 200장 계측에서 **읽기+디코딩 약 85%** → 상품 피처 캐시·제한 병렬 로드·유한 대기열 설계 | [`profile_jpeg_stages`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L144) |
| **18–19 · 사업·예측 확장** | 인사이트·예측 셀 | 30일 대조 실험 가설 표, 기준시점 `T` 이전 피처와 미래 30일 라벨 분리(데이터 누수 방지) | [`write_insights`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L73) · [a1_1_evaluation_qa.md](https://github.com/ntt65/A1_1/blob/main/docs/a1_1_evaluation_qa.md) |

#### 발표자가 반드시 짚어야 할 3가지 핵심 원칙
1. **원본 보존과 EDA 사본 분리:** 결측 대치([`handle_missing_values`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L129) → [`impute_features`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L71))와 IQR 클리핑([`clip_outliers`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L156))은 **EDA 사본**에만 적용하고, RFM([`calculate_rfm`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L162))·월별 매출 합계([`monthly_amount`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L19), `202.212746`)에는 **유효 거래 원금액**을 그대로 사용합니다.
2. **분석 단위 혼동 금지:** 상품 단위(`image_mean`–`image_std`, **200쌍**, [`extract_product_image_features`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L64))와 고객 단위(`Frequency`–`Monetary`, **1,000쌍**, [`pair_correlation`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L8)), 거래 행 단위(**8,084행**, [`join_products`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L71))를 명확히 구분해 설명합니다.
3. **관찰 한계 명시:** 이미지는 표본 200장만 관측했고(`image_status == "ok"`), `New`·`Churned`([`calculate_customer_rfm`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L128))는 기간 내 구매 패턴 분류일 뿐 실제 가입·이탈 확정이 아니며, 상관계수는 인과가 아닙니다.
* **보충 · 왜 노트북 안에 클래스를 안 짜고 `src/pipeline.py`와 `utils/`로 나눴을까?**
  * 노트북에 계산 코드를 다 적으면 다른 데이터로 재실행하거나 단위 테스트([`tests/`](https://github.com/ntt65/A1_1/tree/main/tests))를 돌리기 어렵습니다. 그래서 **상태 관리**는 [`DataAnalyzer`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L20)가, **순수 계산 함수**는 `utils/`가, **실행·해석**은 [analysis_report.ipynb](https://github.com/ntt65/A1_1/blob/main/notebooks/analysis_report.ipynb)가 맡도록 책임을 분리했습니다.

---

### Step 2 · 환경과 실행 & 비공개 데이터 준비 (`README.md` 22~80행)

#### 1) 왜 가상환경(`.venv`)과 버전 고정(`requirements*.txt`)을 쓰는가?
* **가상환경(`.venv`):** 내 컴퓨터 전체에 설치된 Python 라이브러리와 이 프로젝트용 라이브러리가 섞여 버전이 충돌하지 않게 **프로젝트 전용 작업실**을 만듭니다(`python3.11 -m venv .venv`).
* **의존성 파일 3개 분리:**
  * [requirements.txt](https://github.com/ntt65/A1_1/blob/main/requirements.txt): 핵심 분석 라이브러리(`NumPy 2.4.6`, `Pandas 3.1.1`, `Matplotlib 3.11.2`, `Seaborn 0.13.2`) 버전 고정
  * [requirements-notebook.txt](https://github.com/ntt65/A1_1/blob/main/requirements-notebook.txt): 노트북 실행 엔진(`Notebook 7.6.4`, `ipykernel 7.4.0`, `nbclient 0.11.0`, `nbformat 5.11.1`) 분리
  * [requirements-bonus.txt](https://github.com/ntt65/A1_1/blob/main/requirements-bonus.txt): 인터랙티브 보너스용(`Plotly 7.1.0`, `narwhals 2.28.0`, `packaging 26.3`) 분리
* **실행 및 검증 명령 순서:**
  1. 설치 직후 점검: `.venv/bin/python -B -m utils.run_checks` → [`run_checks.py`](https://github.com/ntt65/A1_1/blob/main/utils/run_checks.py#L55)가 `tests/` 단위 테스트를 돌려 설치 정상을 확인(`-B`는 `__pycache__` 미생성 옵션).
  2. 표본 복원: `.venv/bin/python scripts/restore_hm_sample.py --archive "$HOME/Downloads/A1_1_hm_sample.zip"` (203개 파일 검증·복원; `data/raw/hm/hm_sample.zip` 보관 시 `--archive` 생략 가능).
  3. 전체 노트북 실행: `.venv/bin/python -B -m utils.run_checks --with-sample` (회귀 테스트 22개 + [analysis_report.ipynb](https://github.com/ntt65/A1_1/blob/main/notebooks/analysis_report.ipynb) 새 커널 13개 코드 셀 실행, 로컬 관측 시간 **8.67초**).
  4. 산출물 보존 및 저장소 검사: `.venv/bin/python -B -m utils.publish_report`([`publish_report.py`](https://github.com/ntt65/A1_1/blob/main/utils/publish_report.py#L32)) 후 `.venv/bin/python -B -m utils.repository_checks`([`repository_checks.py`](https://github.com/ntt65/A1_1/blob/main/utils/repository_checks.py#L39)).
  5. 독립 재현 검증: `.venv/bin/python -B -m utils.reproducibility`([`reproducibility.py`](https://github.com/ntt65/A1_1/blob/main/utils/reproducibility.py), `data/processed/reproduction_verification.json` 생성).

#### 2) 왜 원본 데이터는 Git에 없고 Kaggle → `restore_hm_sample.py` 과정을 거치는가?
* **Git 제외 이유:** H&M 대회 데이터는 규정에 동의한 사용자만 쓸 수 있어 외부 재배포가 금지되어 있습니다. [.gitignore](https://github.com/ntt65/A1_1/blob/main/.gitignore)와 [`check_repository()`](https://github.com/ntt65/A1_1/blob/main/utils/repository_checks.py#L39)로 원본 CSV·이미지·ZIP이 Git에 올라가지 않도록 막습니다.
* **추출 → 복원 2단계 흐름:**
  1. **Kaggle에서 작은 표본만 추출:** [prepare_hm_sample.ipynb](https://github.com/ntt65/A1_1/blob/main/notebooks/prepare_hm_sample.ipynb)가 수천만 행 원본 중 3개월·고객 1,000명·이미지 200장만 골라 `hm_sample.zip`으로 만듭니다.
  2. **로컬 검증 후 복원:** [`restore_sample()`](https://github.com/ntt65/A1_1/blob/main/scripts/restore_hm_sample.py#L30)이 ZIP 내부 파일 목록, `sample_manifest.json`의 이미지 수 일치 여부, 기존 파일 충돌, SHA-256 체크섬을 검사한 뒤 `data/raw/hm/` 폴더에 안전하게 풀어줍니다. (이미 같은 파일이 있으면 건너뛰고, 내용이 다른 기존 파일은 덮어쓰지 않아 데이터 손상을 막습니다.)

#### 3) 보충 · Kaggle 표본 추출 설정 (`prepare_hm_sample.ipynb` In [1])
[prepare_hm_sample.ipynb](https://github.com/ntt65/A1_1/blob/main/notebooks/prepare_hm_sample.ipynb)의 1번 섹션(`In [1]`)은 외부 다운로드가 아니라 비공개 Kaggle 노트북에 연결된 H&M 원본 데이터셋에서 분석용 표본(`hm_sample.zip`)을 추출하기 위한 경로·기간·표본 크기·청크 크기 변수 설정입니다.

1. **경로 변수 (`INPUT_ROOT`, `DATASET_DIR`, `OUTPUT_DIR`)**
   * `INPUT_ROOT = Path("/kaggle/input")`: Kaggle 노트북에 **Add Input**으로 연결한 원본 데이터 루트 경로입니다.
   * `DATASET_DIR = None`: 후보 폴더가 여러 개일 때 수동으로 지정하는 경로이며, `None`이면 `find_dataset()`가 `transactions_train.csv`, `articles.csv`, `images/`가 모두 있는 경로를 자동 탐색합니다.
   * `OUTPUT_DIR = Path("/kaggle/working")`: 추출된 표본 아카이브(`hm_sample.zip`)를 저장하는 작업 출력 경로입니다.
2. **기간·채널·시드·표본 상한 변수**
   * `START_DATE = "2020-06-01"`, `END_DATE = "2020-09-01"`: 시작일 포함 ~ 종료일 미포함으로 2020년 6월 1일 ~ 8월 31일(3개월) 거래를 대상으로 삼습니다.
   * `SALES_CHANNEL = None`: 채널 필터 없이 전체 채널을 포함합니다.
   * `SEED = 42`: 무작위 표본 추출(`np.random.default_rng`)을 재현하기 위한 난수 시드입니다.
   * `MAX_CUSTOMERS = 1_000`: 최대 추출 표본 고객 수 1,000명 기준입니다.
   * `MAX_IMAGES = 200`: 최대 추출 상품 이미지 수 200장 기준입니다.
   * `MIN_TRANSACTIONS = 1_000`: 최소 유효 표본 거래 행 수 1,000건 기준입니다.
3. **청크 크기 변수 (`CHUNK_SIZE = 250_000`)**
   * 약 3,178만 행 규모의 원본 거래 CSV(`transactions_train.csv`)를 한 번에 메모리에 올리지 않고 25만 행 단위로 분할 읽기 위한 설정입니다.

#### 4) 보충 · `transaction_chunks` 및 `prepare_hm_sample` 1차·2차 스캔 동작 (`prepare_hm_sample.ipynb` In [2]·In [3])
1. **`transaction_chunks` 동작 (청크별 정제·기간 필터링·상호 배타 감사)**
   * **읽기 및 정규화:** `pd.read_csv(path, usecols=TRANSACTION_COLUMNS, dtype="string", chunksize=chunk_size)`로 `t_dat`, `customer_id`, `article_id`, `price`, `sales_channel_id`를 문자열로 `250,000`행씩 읽고, `customer_id`와 `article_id`는 앞뒤 공백 제거 후 `""`를 `pd.NA`로 변환합니다. `t_dat`는 `%Y-%m-%d` 형식(`errors="coerce"`), `price`는 실수 배열(`np.isfinite(amounts) & (amounts > 0)`)로 변환합니다.
   * **유효 및 범위 마스크:** `valid = customer_ok & date_ok & amount_ok`, `in_scope = dates.ge(start) & dates.lt(end)` (기본 `2020-06-01` 이상 ~ `2020-09-01` 미만; `sales_channel` 지정 시 채널 일치 조건 추가).
   * **상호 배타적 `audit` 집계:** `missing_customer_rows` (`(~customer_ok).sum()`), `invalid_date_rows` (`(customer_ok & ~date_ok).sum()`), `invalid_amount_rows` (`(customer_ok & date_ok & ~amount_ok).sum()`), `out_of_scope_rows` (`(valid & ~in_scope).sum()`).
   * **반환 값:** `rows.loc[selected, TRANSACTION_COLUMNS]`, `dates.loc[selected]`, `dates.min()`, `dates.max()`, `audit`를 `yield`합니다.
2. **`prepare_hm_sample` 1차 스캔 (모수 점검·기준일 산출·고객 선정)**
   * **사전 조건 검사:** `start`와 `end`가 월초(`is_month_start`)이고 최소 3개월 이상(`start + pd.DateOffset(months=3) <= end`)인지, `max_customers`, `max_images`, `min_transactions`, `chunk_size`가 모두 `1` 이상인지 확인합니다.
   * **1차 스캔 누적:** `transaction_chunks`를 순회하며 `counts.update(audit)`로 전체 청크 제외·원본 행 수를 누적하고, `raw_start`·`raw_end`로 `source_start`·`source_end`를 갱신합니다.
   * **범위 내 유효 행 집계:** `rows`가 비어 있지 않으면 `customers`에 고유 `customer_id`, `covered_months`에 `dates.dt.to_period("M")`을 추가하고, `reference_date`를 `dates.max()` 최댓값(`2020-08-31`)으로 갱신하며 `counts["eligible_rows"]`에 `len(rows)`를 더합니다.
   * **기간 커버리지 검증 및 고객 추출:** `source_start <= start`, `source_end >= end - 1일`, `covered_months == expected_months`를 확인한 뒤, `choose(customers, max_customers, seed)`로 정렬된 고객 목록에서 `np.random.default_rng(seed)` 비복원 추출로 최대 1,000명을 뽑고 `population_size = len(customers)`를 기록한 뒤 `customers`를 삭제합니다.
3. **`prepare_hm_sample` 2차 스캔 (거래 저장·상품/이미지 매칭·정합성 검증·ZIP 생성)**
   * **2차 스캔 및 거래 저장:** `transaction_chunks`를 다시 순회하며 `rows["customer_id"].isin(chosen_customers)`인 행만 골라 `TemporaryDirectory` 안의 `transactions_sample.csv`에 `mode="a"`로 이어 쓰고 `transaction_count`와 `article_ids`를 누적합니다(`transaction_count < min_transactions`이면 예외).
   * **상품 메타데이터 및 이미지 매칭:** `articles.csv`에서 `ARTICLE_COLUMNS`를 읽어 `article_ids`에 해당하는 행만 필터링하고 중복 상품 ID를 검사합니다. ASCII 숫자 `article_id`에 대해 `dataset_dir / "images" / article_id[:3] / f"{article_id}.jpg"` 존재 여부를 확인한 뒤 `choose(image_paths, max_images, seed)`로 최대 200장을 선정하고, `source_image_available`과 `image_sampled` 열을 붙여 `articles_sample.csv`로 저장합니다.
   * **행 수 정합성 검증 및 패키징:** `counts["sampled_rows"] = transaction_count`, `counts["sample_excluded_rows"] = counts["eligible_rows"] - transaction_count`를 계산하고, 제외 5항목 합계 + `transaction_count == counts["source_rows"]`를 검증합니다. `sample_manifest.json`을 기록한 뒤 `ZipFile`로 CSV·JSON은 `ZIP_DEFLATED`, 표본 이미지는 `images/<앞3자리>/<파일명>` 경로로 `ZIP_STORED` 압축해 저장하고 `archive_path.replace(destination)`로 원자적 이동을 마칩니다.

---

### Step 3 · 입력과 계산 기준 & 분석 흐름과 원본 보존 (`README.md` 90~138행)

#### 1) 입력 데이터와 자료형을 지키는 이유
* **ID 열은 반드시 문자열(`string`):** `customer_id`, `article_id`, `sales_channel_id`를 숫자로 읽으면 `"0706016002"`의 앞자리 `0`이 사라져 이미지 경로 매칭이 깨집니다. 그래서 [`DataAnalyzer.load_data`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L36)에서 처음부터 `string`으로 읽고 공백을 제거합니다.
* **금액(`price`)은 원값 보존:** 통화나 환율을 임의로 추정해 곱하지 않고, 유효한 양수인지(`np.isfinite` & `> 0`)만 검사합니다.
* **정제 순서(상호 배타적 집계):** [`clean_transactions`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L7)는 **고객 누락 → 날짜 오류 → (주문 모드 시 주문/취소 오류) → 금액 오류** 순서로 검사해, 한 행이 여러 사유로 중복 카운트되지 않도록 합니다. H&M에는 주문 ID가 없어 같은 날·같은 금액의 중복 구매 행도 정상 거래로 유지합니다.

#### 2) 상품 조인과 이미지·텍스트 피처 규칙
* **다대일 왼쪽 조인(`many_to_one`):** [`DataAnalyzer.join_products`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L71)는 상품 표의 null 키를 먼저 빼고, 중복 키나 열 충돌을 검사한 뒤, **조인 전후 거래 행 수(8,084행)와 총 금액 합계(202.212746)가 그대로 유지**되는지 검증합니다.
* **이미지 배치 축약 `(N, H, W, C)` → `axis=(1, 2, 3)`:** [`extract_product_image_features`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L64)는 상품별로 이미지를 한 번만 읽어 `32×32` RGB `float32`(`0~1`)로 맞춘 뒤, 최대 `batch_size=32`장씩 묶어 **배치 축 `0(N)`만 남기고 높이·너비·채널 축 `(1, 2, 3)`을 평균·표준편차(`ddof=0`)로 축약**합니다. 원본 이미지 배열을 8,084행 거래마다 복제하지 않고 요약 숫자만 매핑합니다.
* **보충 · 텍스트 피처와 `ddof=0` vs `ddof=1` 차이:**
  * [`extract_text_features`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L236)는 `prod_name` 원문은 보존하고 계산 시에만 결측을 `""`로 취급해 글자 수·단어 수를 구합니다(예: `"Blue cotton shirt"` → **17자·3단어**).
  * 이미지 한 장의 픽셀 표준편차는 픽셀 전체를 하나로 보는 **모표준편차(`ddof=0`, NumPy 기본)**를 쓰고, 거래금액 기술통계나 IQR 전후 분산은 표본을 비교하는 **표본표준편차/표본분산(`ddof=1`, Pandas 기본)**을 사용합니다.

#### 3) 원본 보존 vs EDA 사본 분리 규칙
* **결측 대치:** [`handle_missing_values`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L129)(호환 별칭 [`handle_missing`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L141)) → [`impute_features`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L71)는 별도 `imputer`의 **EDA 사본**에만 적용합니다. `not_sampled`(4,496개)와 기존 관측값(200개)은 건드리지 않고, 누락 9건만 `product_type_name` 그룹 평균 → 전체 평균 순으로 채웁니다.
* **IQR 이상치 보정:** [`detect_outliers`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L145)와 [`clip_outliers`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L156) → [`iqr_limits`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L117)는 `Q1 − 1.5×IQR`, `Q3 + 1.5×IQR` 경계 밖 **212행**을 찾아 보정된 별도 `Series`만 반환하므로, `analyzer.df["price"]` 원금액은 그대로 보존됩니다.

#### 4) RFM 점수 및 세그먼트 계산 규칙
* **지표 정의([`calculate_customer_rfm`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L128)):** 기준일(`2020-08-31`) 기준 **R** = `기준일 − 최종 구매일`(당일 구매=0), **F** = 고유 구매일 수, **M** = 유효 원금액 합계.
* **동점 처리 점수화:** R은 내림차순, F·M은 오름차순 **평균 순위**를 매긴 뒤 `(평균 순위 − 0.5) / 고객 수` 비율이 `0.25 / 0.50 / 0.75` 이하인지에 따라 `1 / 2 / 3 / 4`점을 부여합니다(같은 값은 같은 점수를 받음).
* **5대 세그먼트 우선순위:** `VIP(R·F·M ≥ 3, F원값 ≥ 2)` → `Loyal(R·F ≥ 3, F원값 ≥ 2)` → `New(R ≥ 3, F원값 = 1)` → `Churned(R ≤ 2)` → `Potential` 순서로 배정합니다.
* **보충 Q&A · 왜 코사인 유사도·정규분포 대신 '순위 사분위수 + 규칙'을 썼는가?** ([`calculate_customer_rfm`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L149-L164))
  * 이커머스 금액·빈도는 오른쪽 꼬리가 긴 비대칭 분포(`price` 왜도 `+1.554`)이므로, 평균·표준편차(`Z-score`) 기준은 소수 고액 고객에 의해 왜곡됩니다. **순위 백분위(`25% / 50% / 75%`)**는 분포 모양과 무관하게 상대적 위치를 안정적으로 나눕니다.
  * 코사인 유사도는 벡터 방향(비율)만 보고 절대 규모를 잃기 쉽고, 군집화는 매 실행마다 경계와 해석이 달라집니다. 반면 규칙 기반 RFM(`np.select`)은 *"왜 VIP인지"* 기준이 투명하며, 컷오프 타당성은 대조군 대비 30일 재구매율·마진으로 사후 검증합니다([README.md](https://github.com/ntt65/A1_1/blob/main/README.md#L118)).

---

### Step 4 · 실제 실행 결과 · 기술통계 · IQR 한계 · 이미지 병목 (`README.md` 150~230행)

#### 1) 표본 실행 규모와 메모리 버퍼 ([`NB_LOAD`](https://github.com/ntt65/A1_1/blob/main/notebooks/analysis_report.ipynb) · [`NB_FEATURES`](https://github.com/ntt65/A1_1/blob/main/notebooks/analysis_report.ipynb))
* **실행 규모:** 유효 거래 **8,084행**, 고객 **1,000명**, 상품 **4,705개**, 조인 후 **9열**. 이미지 읽기 성공(`ok`) **200개**, 표본 미포함(`not_sampled`) **4,496개**, 원본 누락(`missing`) **9개**.
* **픽셀 버퍼 크기(`N×H×W×C×dtype`):** 실제 최대 배치 `(5, 32, 32, 3)` `float32`는 **61,440 B(60 KiB)**, 32장 상한은 **384 KiB**입니다. 반면 `1024×1024` RGB `float64`는 1장에 **24 MiB**로 크기·자료형에 따라 메모리가 급증합니다([`prepare_image`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L11)).

#### 2) 기술통계와 상관관계 2쌍 ([`summarize`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L177) · [`pair_correlation`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L8))
* **거래금액(`price`) 분포:** 평균 **0.025014** > 중앙값 **0.022017** (표준편차 **0.014912**, Q1 **0.015237**, Q3 **0.033881**). 평균이 중앙값보다 큰 오른쪽 꼬리 분포이므로 평균 하나만으로 대표하지 않습니다.
* **상관관계 2쌍 (분석 단위 분리 & 인과 금지):**
  * **상품 단위 (`image_mean`–`image_std`, 200쌍):** `r = -0.9435` → 밝은 배경 등 평균이 높은 이미지에서 픽셀 퍼짐이 낮아지는 경향(대치 전 원래 관측값만 사용; 대치 후 분산은 `0.010424 → 0.010130`으로 축소).
  * **고객 단위 (`Frequency`–`Monetary`, 1,000쌍):** `r = 0.6397` → 구매일이 많은 고객의 관측 금액 합계도 큰 경향(같은 거래에서 집계되는 구조 고려).

#### 3) IQR의 통계적 필요성과 한계 ([`iqr_limits`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L117) · [`clip_outliers`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L156))
* **왜 쓰는가?** `IQR = Q3 − Q1`은 가운데 50% 퍼짐이므로 극단값 몇 개가 아무리 커져도 평균·표준편차보다 흔들리지 않습니다.
* **한계는 무엇인가?** 같은 `1.5×IQR` 규칙이라도 **표준정규분포**에서는 약 **0.70%**만 경계 밖이지만, 오른쪽 꼬리가 긴 **로그정규 예시 `exp(N(0,1))`**에서는 약 **7.76%**가 상한을 넘습니다. 즉, 긴 꼬리 분포에서는 오류가 아닌 **유효한 고액 거래**도 이상치로 표시될 수 있고, 서로 다른 가격대 상품군을 합치면 경계가 왜곡될 수 있습니다.
* **실제 8,084행 결과:** 하한(**−0.012729**) 미만 **0행**, 상한(**0.061847**) 초과 **212행(2.62%)**, 왜도 **+1.554**. EDA 사본 보정 시 중앙값(**0.022017**)은 그대로이고 표본분산(`ddof=1`)은 **0.000222373 → 0.000184101(−17.21%)**로 줄었으며, 원금액 합계(**202.212746**)는 RFM에 보존했습니다.

#### 4) 대규모 이미지 처리 병목과 개선 설계 ([`extract_product_image_features`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L64) · [`profile_jpeg_stages`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L144))
* **실측 병목:** 실제 200장 계측(워밍업 1회 후 3회 중앙값) 결과, 전체 **2.115초** 중 `imread()` 읽기+디코딩이 **1.797초(84.9%)**를 차지했습니다.
* **단계 분리 계측(`NB_TIMING`, 12장):** 파일 바이트 읽기 **7.45 ms**, 메모리 JPEG 디코딩 **124.32 ms**, 픽셀 전처리 **3.38 ms** → 즉, 계산보다 **JPEG 디코딩·I/O**가 핵심 병목입니다.
* **확장 설계:** 상품 ID·버전·설정 키 기반 **피처 캐시**, 캐시 미스만 처리하는 **제한된 병렬 워커 + 유한 대기열**, 고객 100만 명 거래는 **필요 열만 청크 집계 병합**으로 확장합니다.

---

### Step 5 · 필수 시각화 6종 · 고객 그룹 · 비즈니스 인사이트 · 보너스 3종 (`README.md` 230~360행)

#### 1) 필수 시각화 6종과 분석 단위 ([`make_figures`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L35) · [`monthly_amount`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L19))
1. **`01_histogram.png` (거래 행 단위):** 원금액 집중 구간과 오른쪽 긴 꼬리 확인.
2. **`02_boxplot.png` (거래 행 단위):** IQR 보정 전 원금액 vs 보정 후 EDA 사본을 **동일 금액 축**으로 비교.
3. **`03_bar.png` (고객 단위):** 세그먼트별 고객 인원 비교(거래 행 수와 구분).
4. **`04_heatmap.png` (고객 단위):** RFM 지표 간 선형 상관 요약(인과 증명 아님).
5. **`05_scatter.png` (상품 단위):** 관측 이미지 200개의 `image_mean`–`image_std` 점 분포(임의 구간화·점 제거 없음).
6. **`06_line.png` (월 단위):** 완전한 세 달(`2020-06` **80.766000** → `2020-07` **62.779373** → `2020-08` **58.667373**, **−27.4%**) 추이. 세 달 합계 **202.212746**은 RFM 원금액 합계와 일치합니다.

#### 2) 실제 고객 그룹 요약 & 비즈니스 인사이트 3건 ([`segment_profile`](https://github.com/ntt65/A1_1/blob/main/utils/analytics.py#L171) · [`write_insights`](https://github.com/ntt65/A1_1/blob/main/utils/reporting.py#L73))
* **VIP (270명 · 27.0%):** R 중앙값 12.5일 · F 중앙값 3.0일 · 평균 M 0.391468 · **금액 비중 52.3%** → *유지 실험*: 상시 할인 없이 재입고·신상품 우선 알림 시험(대조군 대비 30일 구매율 +3%p, 마진 ≥ 0 목표 예시).
* **Churned (499명 · 49.9%):** R 중앙값 60.0일 · F 중앙값 1.0일 · 평균 M 0.149389 · **금액 비중 36.9%** → *재활성화 타당성*: 실제 이탈 확정이 아니며, 과거 반복 구매 여부로 층화해 소규모 실험 후 혜택 비용 차감 순증 마진(> 0) 검증.
* **New (149명 · 14.9%):** R 중앙값 18.0일 · F 중앙값 1.0일 · 평균 M 0.101617 · **금액 비중 7.5%** → *두 번째 구매 유도*: 신규 가입이 아닌 기간 내 1회 구매 고객이며, 구매 상품군 기반 후속 안내로 30일 내 2번째 구매일 발생률(+2%p 목표 예시) 비교.
* **Loyal (82명 · 8.2%):** R 중앙값 16.0일 · F 중앙값 2.0일 · 평균 M 0.083296 · **금액 비중 3.4%**.

#### 3) 보너스 3종 실제 구현 결과
1. **이미지 히스토그램·엣지 피처 ([`advanced_image_statistics`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L38)):** `image_hist_0~7`(가중 밝기 `0.2126R+0.7152G+0.0722B` 근사, 이미지별 합 `1`) 및 `image_edge_mean`(200개 평균 **0.045633**, 범위 **0.004035~0.162338**).
2. **첫 관찰 구매월 코호트 ([`cohort_retention`](https://github.com/ntt65/A1_1/blob/main/utils/bonus.py#L9) · [`cohort_figure`](https://github.com/ntt65/A1_1/blob/main/utils/bonus.py#L44)):** 가입일이 없어 관찰 기간 첫 구매월 기준. `2020-06` **550명**(M1 **40.7%**, M2 **38.7%**), `2020-07` **288명**(M1 **28.5%**), `2020-08` **162명**. 미래 미관측 칸은 0이 아닌 빈칸(`NaN`)으로 남깁니다.
3. **Plotly 3D 인터랙티브 RFM ([`interactive_rfm`](https://github.com/ntt65/A1_1/blob/main/utils/bonus.py#L59) · [rfm_interactive.html](https://github.com/ntt65/A1_1/blob/main/docs/results/bonus/rfm_interactive.html)):** 고객 1,000명·4개 그룹·원본 ID hover 포함, Plotly JS 내장으로 오프라인 브라우저에서도 회전·확대·범례 필터가 동작합니다.

---

### Step 6 · 범위·한계 · 재현성 검증 · 발표 단골 질문(FAQ) (`README.md` 360행~끝)

#### 1) 이 분석으로 말할 수 있는 것 vs 말할 수 없는 것
* **말할 수 있는 것:** 2020년 6~8월 선택 표본(고객 1,000명, 거래 8,084행, 관측 이미지 200장)에서 확인된 분포·상관·세그먼트 규모와, 이를 바탕으로 한 **검증 가능한 대조 실험 가설**.
* **말할 수 없는 것:** 전체 H&M 고객·매출로의 일반화, 실제 신규 가입(`New`)·영구 이탈(`Churned`) 판정, 상품 마진/LTV 확정, 이미지 평균·표준편차만으로의 질감/구매 원인 단정.

#### 2) 4단계 검증·보존 체계 (누가 돌려도 같은 결과가 나오는 이유)
1. **가상 입력 단위 테스트:** [`run_checks.py`](https://github.com/ntt65/A1_1/blob/main/utils/run_checks.py#L55)가 작은 손계산 입력으로 정제·대치·IQR·RFM·이미지 배치 로직을 검증합니다.
2. **새 커널 전체 실행:** `--with-sample` 옵션으로 [analysis_report.ipynb](https://github.com/ntt65/A1_1/blob/main/notebooks/analysis_report.ipynb)를 깨끗한 커널에서 처음부터 끝까지 실행합니다.
3. **실행본 보존 & 저장소 검사:** [`publish_report.py`](https://github.com/ntt65/A1_1/blob/main/utils/publish_report.py#L17)가 오류 없는 실행본을 바이트 그대로 보존하고, [`repository_checks.py`](https://github.com/ntt65/A1_1/blob/main/utils/repository_checks.py#L39)가 링크·허용 라이브러리·비공개 데이터 Git 제외를 검사합니다.
4. **독립 새 환경 재현:** [`reproducibility.py`](https://github.com/ntt65/A1_1/blob/main/utils/reproducibility.py)가 새 복제본·새 가상환경에서도 `analysis_verification.json` 전체 필드가 일치하는지 대조합니다.

#### 3) 발표장 단골 질문 5선 (15초 답변 가이드)
1. **Q. 왜 `handle_missing_values()`와 `handle_missing()` 두 개가 있나요?**
   * A. 기존 API 호환성과 평가 호출명(`handle_missing`)을 모두 지원하기 위해 [`handle_missing()`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L141)이 내부적으로 [`handle_missing_values()`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L129)를 그대로 호출하도록 묶어 두었습니다.
2. **Q. 왜 표본에 없는 이미지 4,496개는 결측 대치를 안 했나요?**
   * A. 애초에 표본으로 뽑지 않은 이미지를 평균으로 채우면 사실과 다른 가짜 데이터가 대량 생성되므로, `eligible=False`(`not_sampled`)로 제외하고 누락 9건만 EDA 사본에서 대치했습니다([`NB_CLEAN`](https://github.com/ntt65/A1_1/blob/main/notebooks/analysis_report.ipynb)).
3. **Q. 이상치 212행을 왜 삭제하지 않고 사본에만 clip했나요?**
   * A. 긴 꼬리 분포에서는 정상적인 고액 구매도 `1.5×IQR` 밖으로 잡힐 수 있습니다. 원금액 합계(`202.212746`)를 지킨 채 RFM을 계산하고, 분포 비교 시각화에서만 [`clip_outliers()`](https://github.com/ntt65/A1_1/blob/main/src/pipeline.py#L156) 사본을 쓰기 위함입니다.
4. **Q. 이미지 처리 속도를 높이려면 무엇을 고쳐야 하나요?**
   * A. 실제 계측에서 전체의 **84.9%**가 파일 읽기+JPEG 디코딩([`profile_jpeg_stages`](https://github.com/ntt65/A1_1/blob/main/utils/image_features.py#L144) 기준 디코딩 `124.32 ms`)이었으므로, 상품 ID 기준 **피처 캐시 + 제한된 병렬 워커 + 유한 대기열**이 핵심 개선책입니다.
5. **Q. 만약 예측 모델을 만든다면 어떻게 데이터 누수를 막나요?**
   * A. 기준시점 `T` 이전 거래·피처만 입력(`X`)으로 사용하고, `T` 이후 30일 구간의 구매 여부·금액만 타겟(`y`)으로 분리해 미래 정보가 과거 피처·대치에 섞이지 않게 합니다([a1_1_evaluation_qa.md](https://github.com/ntt65/A1_1/blob/main/docs/a1_1_evaluation_qa.md)).
