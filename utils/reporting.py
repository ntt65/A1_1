"""상관·월별 집계·필수 차트와 비식별 세그먼트 인사이트를 재사용한다."""

from pathlib import Path
import numpy as np
import pandas as pd


def pair_correlation(frame, left, right):
    """유한한 완전 관측 쌍의 수와 피어슨 계수를 반환한다.

    두 관측 미만 또는 상수 열에서는 계수를 NaN으로 남겨 해석에서 제외한다.
    """
    pairs = frame[[left, right]].replace([np.inf, -np.inf], np.nan).dropna()
    valid = len(pairs) >= 2 and pairs.nunique().min() > 1
    return {"left": left, "right": right, "n": len(pairs),
            "pearson": float(pairs[left].corr(pairs[right])) if valid else float("nan")}


def monthly_amount(frame, date_col, amount_col, start, end):
    """시작 포함·종료 제외의 완전한 월을 빠짐없이 표시하고 합계를 검증한다."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start.day != 1 or end.day != 1 or end <= start:
        raise ValueError("Monthly reporting requires complete months, start < end.")
    dates = pd.to_datetime(frame[date_col])
    if not dates.between(start, end, inclusive="left").all():
        raise ValueError("Transactions fall outside the requested monthly scope.")
    months = pd.period_range(start, end - pd.Timedelta(days=1), freq="M")
    result = frame.groupby(dates.dt.to_period("M"))[amount_col].sum().reindex(months, fill_value=0)
    if not np.isclose(result.sum(), frame[amount_col].sum(), rtol=1e-12, atol=1e-10):
        raise ValueError("Monthly totals differ from transaction totals.")
    result.index = result.index.astype(str)
    return result.rename("Amount")


def make_figures(transactions, clipped_amount, products, rfm, profile, monthly):
    """거래·상품·고객의 분석 단위를 구분해 필수 차트 6개의 Figure를 반환한다."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="whitegrid", font="DejaVu Sans")
    figures = {}
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(transactions["price"], bins=35, color="#306b9b", edgecolor="white")
    ax.set(title="Purchase amount distribution", xlabel="Amount (source units)", ylabel="Transaction rows")
    figures["01_histogram"] = fig
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot([transactions["price"].to_numpy(), clipped_amount.to_numpy()], tick_labels=["Raw", "IQR clipped"])
    ax.set(title="Amount before and after IQR clipping", xlabel="EDA treatment", ylabel="Amount (source units)")
    figures["02_boxplot"] = fig
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(profile.index, profile.Customers, color="#306b9b")
    ax.set(title="Customers by RFM segment", xlabel="Segment", ylabel="Customers")
    figures["03_bar"] = fig
    fig, ax = plt.subplots(figsize=(6, 5))
    corr = rfm[["Recency", "Frequency", "Monetary"]].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", vmin=-1, vmax=1, cmap="vlag", ax=ax)
    ax.set(title="Customer-level RFM correlations", xlabel="RFM metric", ylabel="RFM metric")
    figures["04_heatmap"] = fig
    fig, ax = plt.subplots(figsize=(7, 4))
    observed = products.loc[products.image_status == "ok"]
    ax.scatter(observed.image_mean, observed.image_std, alpha=.65, s=20, color="#306b9b")
    ax.set(title="Observed product image features", xlabel="Pixel mean (0–1)", ylabel="Pixel standard deviation (0–1)")
    figures["05_scatter"] = fig
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(monthly.index, monthly.to_numpy(), marker="o", color="#306b9b")
    ax.set(title="Monthly purchase amount in the sample", xlabel="Complete month", ylabel="Amount (source units)")
    figures["06_line"] = fig
    for fig in figures.values():
        fig.tight_layout()
    return figures


def write_insights(profile, reference_date, path):
    """그룹 집계만으로 근거·실행·검증이 있는 인사이트 문서를 저장한다.

    고객·상품 ID와 원본 거래 행은 받지 않는다. 관측 범위 밖 가입 시점이나
    실제 이탈 여부를 단정하지 않으며, 금액을 확인되지 않은 통화로 환산하지 않는다.
    """
    required = {"VIP", "New", "Churned"}
    if not required.issubset(profile.index):
        raise ValueError("Expected VIP, New and Churned groups for these insight templates.")
    vip, recent, inactive = (profile.loc[name] for name in ("VIP", "New", "Churned"))
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
'''
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text
