"""분석 표에서 상관·월별 집계·차트·인사이트를 만들며 입력 보존과 저장 부작용을 함수별로 명시한다."""

from pathlib import Path
import numpy as np
import pandas as pd


def pair_correlation(frame, left, right):
    """표와 두 열 이름을 받아 유한한 완전 관측 쌍의 수와 피어슨 계수를 반환한다.

    입력은 변경하지 않는다. 두 관측 미만 또는 상수 열은 계수를 NaN으로 남겨 해석에서 제외한다.
    """
    pairs = frame[[left, right]].replace([np.inf, -np.inf], np.nan).dropna()	# 각 쌍의 결측·무한대를 함께 제외해 서로 다른 관측으로 상관을 계산하지 않는다.
    valid = len(pairs) >= 2 and pairs.nunique().min() > 1	# 표본 부족과 분산 0에서는 피어슨 계수의 의미가 없으므로 계산하지 않는다.
    return {"left": left, "right": right, "n": len(pairs),
            "pearson": float(pairs[left].corr(pairs[right])) if valid else float("nan")}	# 계수와 유효 관측 수를 함께 제공해 분석 범위와 해석의 근거를 남긴다.


def monthly_amount(frame, date_col, amount_col, start, end):
    """거래 표·열·시작/종료일로 완전 월별 금액 Series를 반환하고 합계를 검증하며 입력은 보존한다."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start.day != 1 or end.day != 1 or end <= start:	# 부분 월끼리 합계를 비교해 생기는 왜곡을 막기 위해 월초 경계를 요구한다.
        raise ValueError("Monthly reporting requires complete months, start < end.")
    dates = pd.to_datetime(frame[date_col])
    if not dates.between(start, end, inclusive="left").all():	# 요청 범위 밖 거래를 조용히 버리지 않고 입력 불일치를 알린다.
        raise ValueError("Transactions fall outside the requested monthly scope.")
    months = pd.period_range(start, end - pd.Timedelta(days=1), freq="M")	# 종료일은 제외하므로 하루 전이 포함되는 마지막 월을 결정한다.
    result = frame.groupby(dates.dt.to_period("M"))[amount_col].sum().reindex(months, fill_value=0)	# 관측 범위 안에서 거래 없는 월도 0으로 표시해 시간축의 연속성을 지킨다.
    if not np.isclose(result.sum(), frame[amount_col].sum(), rtol=1e-12, atol=1e-10):	# 월별 집계가 유효 거래의 원금액 총합을 보존하는지 확인한다.
        raise ValueError("Monthly totals differ from transaction totals.")
    result.index = result.index.astype(str)	# 저장·표시 시 월을 명확히 읽을 수 있도록 문자열 라벨을 만든다.
    return result.rename("Amount")


def make_figures(transactions, clipped_amount, products, rfm, profile, monthly):
    """거래·보정값·상품·RFM·그룹·월별 표로 6개 Figure 사전을 반환하며 입력은 보존하고 전역 테마를 설정한다."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", font="DejaVu Sans")	# 공통 가독성을 위해 전역 Matplotlib·Seaborn 테마를 바꾼다.
    figures = {}
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(transactions["price"], bins=35, color="#306b9b", edgecolor="white")	# 거래 행 단위 원금액의 꼬리와 집중 구간을 본다.
    ax.set(title="Purchase amount distribution", xlabel="Amount (source units)", ylabel="Transaction rows")	# 확인되지 않은 통화 대신 데이터 원본 단위를 명시한다.
    figures["01_histogram"] = fig
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot([transactions["price"].to_numpy(), clipped_amount.to_numpy()], tick_labels=["Raw", "IQR clipped"])	# 원본과 EDA 보정 사본을 같은 축에 놓아 분포 변화를 직접 비교한다.
    ax.set(title="Amount before and after IQR clipping", xlabel="EDA treatment", ylabel="Amount (source units)")
    figures["02_boxplot"] = fig
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(profile.index, profile.Customers, color="#306b9b")	# 반복 거래 수가 아닌 세그먼트별 고유 고객 수를 비교한다.
    ax.set(title="Customers by RFM segment", xlabel="Segment", ylabel="Customers")
    figures["03_bar"] = fig
    fig, ax = plt.subplots(figsize=(6, 5))
    corr = rfm[["Recency", "Frequency", "Monetary"]].corr()	# 고객 단위 RFM 표로 계산해 거래 빈도에 따른 중복 가중을 피한다.
    sns.heatmap(corr, annot=True, fmt=".2f", vmin=-1, vmax=1, cmap="vlag", ax=ax)	# 상관 범위를 −1~1로 고정해 색의 의미가 결과마다 바뀌지 않게 한다.
    ax.set(title="Customer-level RFM correlations", xlabel="RFM metric", ylabel="RFM metric")
    figures["04_heatmap"] = fig
    fig, ax = plt.subplots(figsize=(7, 4))
    observed = products.loc[products.image_status == "ok"]	# 대치값과 미표본을 제외하고 실제 관측 상품의 관계만 표시한다.
    ax.scatter(observed.image_mean, observed.image_std, alpha=.65, s=20, color="#306b9b")	# 상품당 한 점으로 픽셀 요약 관계를 보며 인과나 의미 인식으로 해석하지 않는다.
    ax.set(title="Observed product image features", xlabel="Pixel mean (0–1)", ylabel="Pixel standard deviation (0–1)")
    figures["05_scatter"] = fig
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(monthly.index, monthly.to_numpy(), marker="o", color="#306b9b")	# 사전에 검증한 완전 월별 원금액 합계를 연결한다.
    ax.set(title="Monthly purchase amount in the sample", xlabel="Complete month", ylabel="Amount (source units)")
    figures["06_line"] = fig
    for fig in figures.values():
        fig.tight_layout()	# 그림별 제목·축 라벨이 잘리지 않도록 배치를 조정한다.
    return figures	# 저장과 닫기는 호출자가 담당하도록 Figure 객체들을 반환한다.


def write_insights(profile, reference_date, path):
    """그룹 집계·기준일·경로로 인사이트 문서를 저장하고 같은 문자열을 반환한다.

    입력 표는 보존하고 대상 폴더를 만들며 파일이 있으면 덮어쓴다. 고객·상품 ID와 원본 행은 받지 않는다.
    관측 밖 가입 시점·실제 이탈을 단정하지 않고 금액을 확인되지 않은 통화로 환산하지 않는다.
    """
    required = {"VIP", "New", "Churned"}
    if not required.issubset(profile.index):	# 현재 인사이트 문안이 요구하는 그룹이 없으면 잘못된 해석을 만들지 않는다.
        raise ValueError("Expected VIP, New and Churned groups for these insight templates.")
    vip, recent, inactive = (profile.loc[name] for name in ("VIP", "New", "Churned"))	# 개인 행 대신 세그먼트 집계만 문안의 수치 근거로 사용한다.
    text = f'''# 실제 표본 기반 인사이트

기준일 {reference_date}. 2020년 6~8월의 선택 고객·전체 판매 채널 표본에 한정한 관측이다. 금액은 H&M 원본 단위이며 통화를 추정하지 않는다. 아래 비중은 고객별 RFM에서 집계했고 원본 행·식별자는 포함하지 않는다. 표 위치는 노트북 `NB_RFM`의 세그먼트 프로파일이다.

## 1. VIP 유지 실험

- **근거:** VIP는 고객의 {vip.Customer_share:.1%}이며 관측 구매금액의 {vip.Monetary_share:.1%}를 차지한다. 고액·반복 구매 그룹의 유지 성과를 따로 관찰할 이유가 있다.
- **실행:** VIP에 재입고·신상품 우선 알림을 시험하고, 불필요한 상시 할인 없이 재구매를 유지할 수 있는지 확인한다. 효과는 가설이다.
- **검증:** 발송군과 무작위 미발송군의 이후 구매율·고객당 마진을 비교한다. 반응 이력·마진·추가 관찰 기간이 필요하며 차이가 없으면 가설을 기각한다.

## 2. 최근 1개 구매일 고객의 다음 구매 유도

- **근거:** New 그룹은 고객의 {recent.Customer_share:.1%}이고 고유 구매일 수 중앙값은 {recent.Frequency_median:.0f}일이다. 관찰 기간 내 한 구매일만 확인된 그룹이며 실제 신규 가입 고객을 뜻하지 않는다.
- **실행:** 이 그룹에 구매 상품군을 고려한 후속 안내를 시험해 두 번째 구매일이 생기는 비율을 높이는 것을 목표로 한다.
- **검증:** 미발송군 대비 30일 내 추가 구매일 발생률과 마진을 비교한다. 연락 동의·상품 반응·향후 거래가 필요하며 자연 재구매와 계절성의 영향을 통제한다.

## 3. 낮은 최근성 그룹의 재활성화 타당성 확인

- **근거:** Churned는 고객의 {inactive.Customer_share:.1%}이고 최근 구매 이후 일수 중앙값은 {inactive.Recency_median:.0f}일이다. 표본 내 상대적으로 낮은 최근성 그룹이며 실제 이탈 확정값은 아니다.
- **실행:** 이 그룹의 과거 반복 구매 여부를 나눠 재입고 안내나 제한된 혜택을 소규모로 실험한다. 재활성화 효과와 비용을 함께 확인한다.
- **검증:** 무작위 대조군과 순증 구매율·혜택 비용 차감 후 마진을 비교한다. 비용·상품 재고·후속 거래가 필요하며 수익이 늘지 않으면 확대하지 않는다.

세 인사이트의 우선순위와 ROI는 현재 데이터만으로 확정하지 않는다. 이미지 평균·표준편차는 밝기·배경·색상 요약이며 상품 패턴이나 구매 원인을 직접 설명하지 않는다.
'''	# 관측 사실·실행 가설·추가 검증을 구분한 문안을 유지한다.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)	# 호출자가 지정한 문서 경로의 상위 폴더만 준비한다.
    path.write_text(text, encoding="utf-8")	# UTF-8로 저장하며 같은 경로의 기존 문서는 교체된다.
    return text
