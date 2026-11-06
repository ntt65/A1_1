"""거래 정제·결측 대치·RFM의 재사용 계산. 입력 표를 직접 변경하지 않는다."""

import numpy as np
import pandas as pd


def clean_transactions(frame, customer_col, date_col, amount_col, *, frequency_unit="purchase_day",
                       order_col=None, start=None, end=None, channel_col=None, channel=None):
    """유효 거래 사본과 상호 배타적인 제외 집계를 반환한다.

    고객→날짜→주문→금액 순으로 대표 제외 사유를 배정한다. 기간은 시작 포함,
    종료 제외다. 동일 상품의 반복 구매 행은 제거하지 않는다. frequency_unit이
    order이면 주문 ID가 필요하고 C로 시작하는 취소 주문을 제외한다.
    """
    if frequency_unit not in ("purchase_day", "order"):
        raise ValueError("frequency_unit must be purchase_day or order.")
    required = {customer_col, date_col, amount_col}
    if frequency_unit == "order":
        if not order_col:
            raise ValueError("order_col is required for order frequency.")
        required.add(order_col)
    if channel is not None:
        if not channel_col:
            raise ValueError("channel_col is required for a channel filter.")
        required.add(channel_col)
    missing = required - set(frame)
    if missing:
        raise ValueError(f"Missing transaction columns: {sorted(missing)}")
    result = frame.copy()
    result[customer_col] = result[customer_col].astype("string").str.strip().replace("", pd.NA)
    result[date_col] = pd.to_datetime(result[date_col], format="mixed", errors="coerce").dt.normalize()
    result[amount_col] = pd.to_numeric(result[amount_col], errors="coerce").astype(float)
    if frequency_unit == "order":
        result[order_col] = result[order_col].astype("string").str.strip().replace("", pd.NA)
    remaining = np.ones(len(result), dtype=bool)
    audit = {"source_rows": len(result)}

    def exclude(name, condition):
        """선행 사유로 제외하지 않은 행만 현재 사유에 배정한다."""
        selected = remaining & np.asarray(condition, dtype=bool)
        audit[name] = int(selected.sum())
        remaining[selected] = False

    exclude("missing_customer_rows", result[customer_col].isna())
    exclude("invalid_date_rows", result[date_col].isna())
    if frequency_unit == "order":
        exclude("invalid_order_rows", result[order_col].isna() |
                result[order_col].str.upper().str.startswith("C", na=False))
    else:
        audit["invalid_order_rows"] = 0
    exclude("invalid_amount_rows", ~np.isfinite(result[amount_col]) | (result[amount_col] <= 0))
    audit["valid_before_scope"] = int(remaining.sum())
    in_scope = pd.Series(True, index=result.index)
    if start is not None:
        in_scope &= result[date_col] >= pd.Timestamp(start)
    if end is not None:
        if start is not None and pd.Timestamp(end) <= pd.Timestamp(start):
            raise ValueError("end must be later than start.")
        in_scope &= result[date_col] < pd.Timestamp(end)
    if channel is not None:
        in_scope &= result[channel_col].astype("string") == str(channel)
    exclude("out_of_scope_rows", ~in_scope.fillna(False))
    result = result.iloc[np.flatnonzero(remaining)].copy()
    audit["output_rows"] = len(result)
    audit["amount_sum"] = float(result[amount_col].sum())
    if result.empty:
        raise ValueError(f"No valid transactions remain: {audit}")
    return result, audit


def impute_features(frame, strategy="group_mean", group_col=None, columns=None, eligible=None):
    """결측 위치만 채운 사본과 열별 대치 집계를 반환한다.

    그룹 평균이 없으면 대치 전 관측값의 전체 평균을 사용한다. eligible=False인
    행은 채우지 않는다. columns=None은 수치 열을 선택하며 그룹 열은 제외한다.
    """
    if strategy not in ("group_mean", "mean", "median", "drop"):
        raise ValueError("Unsupported missing-value strategy.")
    if strategy == "group_mean" and (group_col is None or group_col not in frame):
        raise ValueError("A valid group_col is required for group_mean.")
    selected = list(columns) if columns is not None else [
        column for column in frame.select_dtypes(include="number") if column != group_col]
    missing = set(selected) - set(frame)
    if missing:
        raise ValueError(f"Missing feature columns: {sorted(missing)}")
    result, audit = frame.copy(), {}
    if strategy == "drop":
        subset = selected if columns is not None else None
        return result.dropna(subset=subset), {"dropped_rows": int(frame.isna().any(axis=1).sum()) if subset is None
                                            else int(frame[subset].isna().any(axis=1).sum())}
    mask = pd.Series(True, index=frame.index) if eligible is None else pd.Series(eligible, index=frame.index).fillna(False).astype(bool)
    for column in selected:
        if not pd.api.types.is_numeric_dtype(frame[column]):
            raise ValueError(f"Feature '{column}' must be numeric.")
        original = frame[column].astype(float)
        if np.isinf(original).any():
            raise ValueError(f"Feature '{column}' contains infinity.")
        values = original.copy()
        target = original.isna() & mask
        group_count = 0
        if strategy == "group_mean":
            means = frame.groupby(group_col, observed=True)[column].transform("mean")
            group_target = target & means.notna()
            values.loc[group_target] = means.loc[group_target]
            group_count = int(group_target.sum())
        fallback = original.median() if strategy == "median" else original.mean()
        fallback_target = values.isna() & target & pd.notna(fallback)
        values.loc[fallback_target] = fallback
        result[column] = values
        audit[column] = {"missing_before": int(original.isna().sum()),
                         "group_filled": group_count, "global_filled": int(fallback_target.sum()),
                         "missing_after": int(values.isna().sum()),
                         "variance_before": float(original.var()), "variance_after": float(values.var())}
    return result, audit


def iqr_limits(series, threshold=1.5):
    """유한 관측값의 IQR 하한·상한을 반환한다. 경계값은 정상 범위다."""
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and non-negative.")
    values = pd.to_numeric(series, errors="raise")
    if np.isinf(values).any() or not values.notna().any():
        raise ValueError("IQR needs finite observations.")
    q1, q3 = values.quantile([.25, .75])
    return float(q1 - threshold * (q3 - q1)), float(q3 + threshold * (q3 - q1))


def calculate_customer_rfm(frame, customer_col, date_col, amount_col, *, reference_date=None,
                           frequency_unit="purchase_day", order_col=None, split_inactive=False):
    """고객별 RFM·동점 일관 점수·단일 그룹과 계산 기준을 반환한다.

    잘못된 거래는 암묵적으로 버리지 않고 정제 호출을 요구한다. R은 기준일과
    최종 구매일의 차이, F는 고유 구매일 또는 주문 수, M은 유효 금액 원값 합계다.
    split_inactive=True는 낮은 최근성 고객을 과거 반복 구매 여부로 구분한다.
    """
    valid, audit = clean_transactions(frame, customer_col, date_col, amount_col,
                                      frequency_unit=frequency_unit, order_col=order_col)
    if len(valid) != len(frame):
        raise ValueError("Invalid RFM input. Call validate_transactions() first.")
    latest = valid[date_col].max()
    reference = latest if reference_date is None else pd.Timestamp(reference_date).normalize()
    if pd.isna(reference) or reference < latest:
        raise ValueError("reference_date must be on or after the latest transaction date.")
    frequency_col = date_col if frequency_unit == "purchase_day" else order_col
    grouped = valid.groupby(customer_col, sort=True)
    rfm = grouped.agg(last_purchase=(date_col, "max"), Frequency=(frequency_col, "nunique"),
                      Monetary=(amount_col, "sum")).reset_index()
    rfm["Recency"] = (reference - rfm.pop("last_purchase")).dt.days
    for metric, ascending, score in (("Recency", False, "R_Score"),
                                     ("Frequency", True, "F_Score"), ("Monetary", True, "M_Score")):
        percentile = (rfm[metric].rank(method="average", ascending=ascending) - .5) / len(rfm)
        rfm[score] = np.select([percentile <= .25, percentile <= .5, percentile <= .75], [1, 2, 3], default=4)
    repeat = rfm["Frequency"] >= 2
    conditions = [(rfm.R_Score >= 3) & (rfm.F_Score >= 3) & (rfm.M_Score >= 3) & repeat,
                  (rfm.R_Score >= 3) & (rfm.F_Score >= 3) & repeat,
                  (rfm.R_Score >= 3) & ~repeat]
    labels = ["VIP", "Loyal", "New"]
    if split_inactive:
        conditions += [(rfm.R_Score <= 2) & repeat, (rfm.R_Score <= 2) & ~repeat]
        labels += ["Inactive_repeat", "Inactive_oneoff"]
    else:
        conditions += [rfm.R_Score <= 2]
        labels += ["Churned"]
    rfm["Segment"] = np.select(conditions, labels, default="Potential")
    metadata = {"reference_date": str(reference.date()), "frequency_unit": frequency_unit,
                "split_inactive": split_inactive, "customers": len(rfm),
                "amount_sum": audit["amount_sum"], "segments": rfm.Segment.value_counts().to_dict()}
    return rfm, metadata


def segment_profile(rfm):
    """고객 표에서 그룹별 건수·중앙값·금액과 구성비를 반환한다."""
    profile = rfm.groupby("Segment", observed=True).agg(
        Customers=("Monetary", "size"), Recency_median=("Recency", "median"),
        Frequency_median=("Frequency", "median"), Monetary_mean=("Monetary", "mean"),
        Monetary_total=("Monetary", "sum"))
    profile["Customer_share"] = profile.Customers / profile.Customers.sum()
    profile["Monetary_share"] = profile.Monetary_total / profile.Monetary_total.sum()
    return profile.sort_values("Monetary_total", ascending=False)
