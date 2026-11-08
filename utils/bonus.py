"""거래·RFM 입력으로 코호트·탐색 시각화를 제공하며 Plotly는 선택 기능에서만 불러온다."""

from pathlib import Path

import numpy as np
import pandas as pd


def cohort_retention(frame, customer_col, date_col, start, end):
    """거래 표·고객/날짜 열·기간으로 코호트별 활동 고객 수·활동 비율·분모를 반환한다.

    시작 포함·종료 제외의 완전한 월만 받는다. 가입일 코호트가 아니며 기간 전 구매는 알 수 없다.
    관측된 무구매 월은 0, 아직 관측하지 않은 월은 NaN이다. 같은 고객의 같은 달은 한 번만 센다.
    반환값은 counts·retention 표와 sizes Series이며 입력 표를 변경하거나 파일을 저장하지 않는다.
    """
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start.day != 1 or end.day != 1 or end <= start:	# 부분 월과 역전 기간을 거부해 코호트 간 관측 길이 비교를 명확히 한다.
        raise ValueError("Cohort reporting requires complete months, start < end.")
    dates = pd.to_datetime(frame[date_col], errors="coerce")
    if frame.empty or frame[customer_col].isna().any() or dates.isna().any():	# 고객·날짜가 없는 행을 암묵적으로 누락시키면 분모가 달라지므로 거부한다.
        raise ValueError("Cohort input requires valid customers and dates.")
    if not dates.between(start, end, inclusive="left").all():	# 관찰 창 밖 거래는 잘라내지 않고 호출 입력 오류로 알린다.
        raise ValueError("Cohort transactions fall outside the observation window.")
    months = dates.dt.to_period("M")	# 일자가 아닌 구매 월을 활동 단위로 사용한다.
    work = pd.DataFrame({"customer": frame[customer_col].to_numpy(), "month": months.to_numpy()})	# 작업용 표를 별도로 만들어 거래 원본에 코호트 열을 덮어쓰지 않는다.
    first = work.groupby("customer")["month"].min()	# 현재 관찰 범위에서의 첫 구매월이며 생애 첫 구매나 가입월이 아니다.
    work["cohort"] = work.customer.map(first)
    sizes = first.value_counts().sort_index().rename("Customers")	# 고객당 하나의 첫 구매월로 분모를 구해 반복 거래를 중복 집계하지 않는다.
    all_months = pd.period_range(start, end - pd.Timedelta(days=1), freq="M")	# 종료일 직전까지의 완전한 월을 관측 가능한 시간축으로 만든다.
    counts = pd.DataFrame(np.nan, index=sizes.index, columns=range(len(all_months)))	# 아직 도달하지 않은 미래 월을 무구매 0과 구별하려고 NaN으로 초기화한다.
    active = work.groupby(["cohort", "month"]).customer.nunique()	# 같은 고객의 같은 월 반복 거래는 활동 고객 한 명으로 센다.
    for cohort in sizes.index:
        for age in range(len(all_months)):
            month = cohort + age	# 각 코호트의 시작월을 기준으로 상대 월차를 실제 달력 월에 대응시킨다.
            if month <= all_months[-1]:	# 관찰이 끝난 월까지만 값을 채워 미래 칸을 그대로 남긴다.
                counts.loc[cohort, age] = active.get((cohort, month), 0)	# 관측 가능한 달에 기록이 없으면 실제 활동 고객 수를 0으로 둔다.
    retention = counts.div(sizes, axis=0)	# 행별 M0 고객 수가 분모이므로 연속 생존율이 아닌 해당 월 활동 비율이다.
    counts.index = retention.index = sizes.index = sizes.index.astype(str)	# 표와 분모의 라벨 형식을 함께 맞춰 후속 연결을 유지한다.
    counts.index.name = retention.index.name = sizes.index.name = "First_observed_purchase_month"
    counts.columns.name = retention.columns.name = "Months_since_first_observed_purchase"
    return counts, retention, sizes


def cohort_figure(retention, sizes):
    """활동 비율 표·고객 수를 받아 미관측을 가린 히트맵 Figure를 만들며 입력 보존·파일 미저장을 지킨다."""
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(retention, mask=retention.isna(), annot=True, fmt=".1%", vmin=0, vmax=1,	# 미관측 미래 칸은 색과 수치에서 가려 0퍼센트로 오해하지 않게 한다.
                cmap="Blues", ax=ax, cbar_kws={"label": "Active customer share"})	# 비율 색 범위를 0~1로 고정해 코호트 사이 비교를 유지한다.
    ax.set(title="First observed purchase cohorts (not signup)",
           xlabel="Months since first observed purchase", ylabel="First observed purchase month")
    ax.set_yticklabels([f"{month} (n={int(sizes[month])})" for month in retention.index], rotation=0)	# 각 행의 분모를 함께 표시해 같은 비율의 표본 규모 차이를 알린다.
    fig.tight_layout()	# 축 라벨과 고객 수 표시가 그림 밖으로 잘리지 않게 조정한다.
    return fig


def interactive_rfm(rfm, path):
    """고객 RFM 표·출력 경로로 3D Figure를 반환하고 Plotly JS를 포함한 독립 HTML을 저장한다.

    입력 표와 고객 ID·전체 관측값을 보존한다. 대상 폴더를 만들고 기존 HTML이 있으면 덮어쓴다.
    Plotly는 이 함수에서만 불러오며 회전·확대·범례 선택·hover 탐색을 제공한다.
    """
    import plotly.express as px	# 보너스를 호출하지 않는 핵심 분석은 Plotly 설치 없이 실행할 수 있다.

    required = {"customer_id", "Recency", "Frequency", "Monetary", "Segment"}
    if not required.issubset(rfm) or rfm.empty or not rfm.customer_id.is_unique:	# 고객당 한 점과 필수 RFM·분류 정보가 있는 입력만 허용한다.
        raise ValueError("Interactive RFM requires unique customers and RFM/Segment columns.")
    if not np.isfinite(rfm[["Recency", "Frequency", "Monetary"]].to_numpy()).all():	# 비유한 좌표가 시각화에서 사라져 관측 수를 왜곡하지 않도록 거부한다.
        raise ValueError("Interactive RFM metrics must be finite.")
    figure = px.scatter_3d(rfm, x="Recency", y="Frequency", z="Monetary", color="Segment",
        hover_name="customer_id", hover_data={"Recency": True, "Frequency": True, "Monetary": ":.6f"},	# 원본 고객 ID와 실제 지표를 마우스 상세 정보에서 확인할 수 있게 보존한다.
        labels={"Recency": "Days since last purchase", "Frequency": "Unique purchase days",
                "Monetary": "Amount (source units)"}, title="Customer RFM exploration")	# 축에 구매일 빈도와 원본 금액 단위를 명시한다.
    figure.update_traces(marker={"size": 4, "opacity": .7})	# 겹친 점을 살펴볼 수 있도록 크기와 투명도를 고정한다.
    figure.update_layout(meta={"customers": len(rfm), "frequency_unit": "purchase_day"})	# 실제 좌표 수와 빈도 단위를 결과 검증용 메타데이터에 남긴다.
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)	# 지정한 HTML의 상위 폴더를 준비하고 입력 표는 변경하지 않는다.
    path.write_bytes(figure.to_html(include_plotlyjs=True, full_html=True).encode("utf-8"))	# Plotly JS를 내장해 외부 CDN 없이 열 수 있으며 기존 파일은 교체한다.
    return figure	# 저장 결과와 별개로 Figure를 반환해 노트북에서도 그대로 표시할 수 있게 한다.
