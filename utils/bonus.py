"""보너스 코호트 분석과 Plotly 시각화. 핵심 분석에는 Plotly를 요구하지 않는다."""

from pathlib import Path

import numpy as np
import pandas as pd


def cohort_retention(frame, customer_col, date_col, start, end):
    """첫 관찰 구매월 코호트의 고객 수·활동 고객 비율·분모를 반환한다.

    start 포함/end 제외의 완전한 월만 받는다. 가입일 코호트가 아니며 기간 전
    구매는 알 수 없다. 관측된 무구매 월은 0, 아직 관측하지 않은 월은 NaN이다.
    같은 고객의 같은 달 거래는 한 번만 센다. 원본 표는 변경하지 않는다.
    """
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start.day != 1 or end.day != 1 or end <= start:
        raise ValueError("Cohort reporting requires complete months, start < end.")
    dates = pd.to_datetime(frame[date_col], errors="coerce")
    if frame.empty or frame[customer_col].isna().any() or dates.isna().any():
        raise ValueError("Cohort input requires valid customers and dates.")
    if not dates.between(start, end, inclusive="left").all():
        raise ValueError("Cohort transactions fall outside the observation window.")
    months = dates.dt.to_period("M")
    work = pd.DataFrame({"customer": frame[customer_col].to_numpy(), "month": months.to_numpy()})
    first = work.groupby("customer")["month"].min()
    work["cohort"] = work.customer.map(first)
    sizes = first.value_counts().sort_index().rename("Customers")
    all_months = pd.period_range(start, end - pd.Timedelta(days=1), freq="M")
    counts = pd.DataFrame(np.nan, index=sizes.index, columns=range(len(all_months)))
    active = work.groupby(["cohort", "month"]).customer.nunique()
    for cohort in sizes.index:
        for age in range(len(all_months)):
            month = cohort + age
            if month <= all_months[-1]:
                counts.loc[cohort, age] = active.get((cohort, month), 0)
    retention = counts.div(sizes, axis=0)
    counts.index = retention.index = sizes.index = sizes.index.astype(str)
    counts.index.name = retention.index.name = sizes.index.name = "First_observed_purchase_month"
    counts.columns.name = retention.columns.name = "Months_since_first_observed_purchase"
    return counts, retention, sizes


def cohort_figure(retention, sizes):
    """미관측 NaN을 가린 코호트 활동 비율 히트맵 Figure를 반환한다."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(retention, mask=retention.isna(), annot=True, fmt=".1%", vmin=0, vmax=1,
                cmap="Blues", ax=ax, cbar_kws={"label": "Active customer share"})
    ax.set(title="First observed purchase cohorts (not signup)",
           xlabel="Months since first observed purchase", ylabel="First observed purchase month")
    ax.set_yticklabels([f"{month} (n={int(sizes[month])})" for month in retention.index], rotation=0)
    fig.tight_layout()
    return fig


def interactive_rfm(rfm, path):
    """고객 RFM 3D Figure와 Plotly JS를 포함한 독립 HTML을 저장한다.

    Plotly는 이 보너스 함수에서만 불러온다. 고객 ID·전체 관측값을 유지하고
    마우스 회전·확대·세그먼트 범례 선택·hover로 탐색한다. 입력은 변경하지 않는다.
    """
    import plotly.express as px

    required = {"customer_id", "Recency", "Frequency", "Monetary", "Segment"}
    if not required.issubset(rfm) or rfm.empty or not rfm.customer_id.is_unique:
        raise ValueError("Interactive RFM requires unique customers and RFM/Segment columns.")
    if not np.isfinite(rfm[["Recency", "Frequency", "Monetary"]].to_numpy()).all():
        raise ValueError("Interactive RFM metrics must be finite.")
    figure = px.scatter_3d(rfm, x="Recency", y="Frequency", z="Monetary", color="Segment",
        hover_name="customer_id", hover_data={"Recency": True, "Frequency": True, "Monetary": ":.6f"},
        labels={"Recency": "Days since last purchase", "Frequency": "Unique purchase days",
                "Monetary": "Amount (source units)"}, title="Customer RFM exploration")
    figure.update_traces(marker={"size": 4, "opacity": .7})
    figure.update_layout(meta={"customers": len(rfm), "frequency_unit": "purchase_day"})
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(figure.to_html(include_plotlyjs=True, full_html=True).encode("utf-8"))
    return figure
