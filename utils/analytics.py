"""거래·피처·고객 표를 정제·대치·RFM 결과와 감사 집계로 변환하며 입력 표를 변경하지 않는다."""

import numpy as np
import pandas as pd


def clean_transactions(frame, customer_col, date_col, amount_col, *, frequency_unit="purchase_day",
                       order_col=None, start=None, end=None, channel_col=None, channel=None):
    """거래 표·열 이름·기간·채널·빈도 설정을 받아 유효 거래 사본과 제외 집계를 반환한다.

    입력은 보존하고 고객→날짜→주문→금액 순으로 상호 배타적인 대표 제외 사유를 배정한다.
    기간은 시작 포함·종료 제외다. 같은 값의 반복 구매 행은 제거하지 않는다.
    frequency_unit=order이면 주문 ID가 필요하며 C로 시작하는 취소 주문을 제외한다.
    """
    if frequency_unit not in ("purchase_day", "order"):	# 구매일과 주문의 빈도 정의를 혼용하지 않도록 허용 모드를 제한한다.
        raise ValueError("frequency_unit must be purchase_day or order.")
    required = {customer_col, date_col, amount_col}
    if frequency_unit == "order":	# 주문 횟수 모드에서만 주문 식별자를 필수로 요구한다.
        if not order_col:
            raise ValueError("order_col is required for order frequency.")
        required.add(order_col)
    if channel is not None:	# 채널 필터를 요청했을 때만 채널 열을 필수 입력에 포함한다.
        if not channel_col:
            raise ValueError("channel_col is required for a channel filter.")
        required.add(channel_col)
    missing = required - set(frame)
    if missing:
        raise ValueError(f"Missing transaction columns: {sorted(missing)}")
    result = frame.copy()	# 자료형 변환과 필터링은 원본이 아닌 사본에서 수행한다.
    result[customer_col] = result[customer_col].astype("string").str.strip().replace("", pd.NA)	# 빈 식별자는 고객별 집계에 포함시키지 않도록 결측으로 통일한다.
    result[date_col] = pd.to_datetime(result[date_col], format="mixed", errors="coerce").dt.normalize()	# 시간을 자정으로 맞춰 같은 날의 구매를 하나의 빈도 단위로 센다.
    result[amount_col] = pd.to_numeric(result[amount_col], errors="coerce").astype(float)	# 변환 실패와 무한대·음수는 뒤의 대표 사유 집계에서 판정한다.
    if frequency_unit == "order":
        result[order_col] = result[order_col].astype("string").str.strip().replace("", pd.NA)
    remaining = np.ones(len(result), dtype=bool)	# 행 위치 기준 마스크를 사용해 중복 인덱스에서도 제외 건수를 일관되게 센다.
    audit = {"source_rows": len(result)}

    def exclude(name, condition):
        """사유명·조건 마스크로 아직 남은 행만 제외한다. 반환값 없이 외부 audit·remaining을 갱신한다."""
        selected = remaining & np.asarray(condition, dtype=bool)	# 앞서 제외한 행을 다시 세지 않아 감사 집계의 합이 원본 건수와 맞게 한다.
        audit[name] = int(selected.sum())
        remaining[selected] = False	# 선행 사유의 우선순위를 이후 판정에도 유지한다.

    exclude("missing_customer_rows", result[customer_col].isna())	# 고객 누락이 다른 오류보다 먼저 대표 사유가 된다.
    exclude("invalid_date_rows", result[date_col].isna())	# 이미 고객 누락으로 센 행은 날짜 오류에 중복 집계하지 않는다.
    if frequency_unit == "order":
        exclude("invalid_order_rows", result[order_col].isna() |
                result[order_col].str.upper().str.startswith("C", na=False))	# 취소 표시는 주문 모드에만 적용하고 대소문자를 통일한다.
    else:
        audit["invalid_order_rows"] = 0
    exclude("invalid_amount_rows", ~np.isfinite(result[amount_col]) | (result[amount_col] <= 0))	# 금액은 유한한 양수만 인정하며 0·음수·변환 실패를 함께 제외한다.
    audit["valid_before_scope"] = int(remaining.sum())	# 데이터 유효성 제외와 기간·채널 범위 제외를 분리해 기록한다.
    in_scope = pd.Series(True, index=result.index)
    if start is not None:
        in_scope &= result[date_col] >= pd.Timestamp(start)	# 시작일의 거래는 관찰 범위에 포함한다.
    if end is not None:
        if start is not None and pd.Timestamp(end) <= pd.Timestamp(start):	# 역전되거나 길이가 없는 기간을 허용하지 않는다.
            raise ValueError("end must be later than start.")
        in_scope &= result[date_col] < pd.Timestamp(end)	# 종료일은 제외해 인접 기간의 거래가 중복되지 않게 한다.
    if channel is not None:
        in_scope &= result[channel_col].astype("string") == str(channel)	# 코드의 표시 자료형 차이 때문에 같은 채널이 누락되지 않게 비교한다.
    exclude("out_of_scope_rows", ~in_scope.fillna(False))	# 채널 결측 등 범위를 판정할 수 없는 행도 범위 밖으로 처리한다.
    result = result.iloc[np.flatnonzero(remaining)].copy()	# 살아남은 위치의 원래 순서를 유지하며 동일 값 반복 거래는 보존한다.
    audit["output_rows"] = len(result)
    audit["amount_sum"] = float(result[amount_col].sum())	# 보정하지 않은 유효 원금액으로 후속 집계의 보존 기준을 남긴다.
    if result.empty:	# 분모가 없는 빈 결과로 후속 통계가 진행되지 않도록 중단한다.
        raise ValueError(f"No valid transactions remain: {audit}")
    return result, audit


def impute_features(frame, strategy="group_mean", group_col=None, columns=None, eligible=None):
    """표·전략·그룹·대상 열·마스크를 받아 처리 사본과 열별 감사 집계를 반환한다.

    입력은 보존한다. 대치는 결측이며 eligible인 위치만 채우고 그룹 평균이 없으면 원래 전체 평균을 쓴다.
    columns=None은 그룹 외 수치 열을 고른다. drop은 대상 결측 행을 제거하며 eligible을 쓰지 않는다.
    """
    if strategy not in ("group_mean", "mean", "median", "drop"):	# 구현되지 않은 전략을 암묵적으로 다른 방식으로 대체하지 않는다.
        raise ValueError("Unsupported missing-value strategy.")
    if strategy == "group_mean" and (group_col is None or group_col not in frame):	# 상품군 평균을 구하려면 실제 그룹 열이 있어야 한다.
        raise ValueError("A valid group_col is required for group_mean.")
    selected = list(columns) if columns is not None else [
        column for column in frame.select_dtypes(include="number") if column != group_col]	# 그룹을 나타내는 수치 코드가 대치 대상에 섞이지 않게 한다.
    missing = set(selected) - set(frame)
    if missing:
        raise ValueError(f"Missing feature columns: {sorted(missing)}")
    result, audit = frame.copy(), {}	# 실패하거나 일부 열을 처리하더라도 입력 원본은 바뀌지 않는다.
    if strategy == "drop":	# 행 삭제는 대치와 별도 경로이며 eligible 마스크를 사용하지 않는다.
        subset = selected if columns is not None else None
        return result.dropna(subset=subset), {"dropped_rows": int(frame.isna().any(axis=1).sum()) if subset is None
                                            else int(frame[subset].isna().any(axis=1).sum())}	# 대상 열의 결측 때문에 실제 제거되는 행 수를 함께 반환한다.
    mask = pd.Series(True, index=frame.index) if eligible is None else pd.Series(eligible, index=frame.index).fillna(False).astype(bool)	# 대치 허용 여부가 결측이면 허용하지 않는 것으로 해석한다.
    for column in selected:
        if not pd.api.types.is_numeric_dtype(frame[column]):	# 평균·중앙값을 정의한 수치형 피처만 대치한다.
            raise ValueError(f"Feature '{column}' must be numeric.")
        original = frame[column].astype(float)
        if np.isinf(original).any():	# 무한대가 평균을 오염시키거나 대치값으로 전파되지 않게 거부한다.
            raise ValueError(f"Feature '{column}' contains infinity.")
        values = original.copy()
        target = original.isna() & mask	# 기존 관측값과 표본 미포함 위치를 덮어쓰지 않도록 대상을 제한한다.
        group_count = 0
        if strategy == "group_mean":
            means = frame.groupby(group_col, observed=True)[column].transform("mean")	# 대치 전 원래 표로 그룹 평균을 구하며 eligible은 평균 산출 행을 제한하지 않는다.
            group_target = target & means.notna()	# 그룹 평균이 실제 존재하는 대상 결측만 먼저 채운다.
            values.loc[group_target] = means.loc[group_target]
            group_count = int(group_target.sum())
        fallback = original.median() if strategy == "median" else original.mean()	# 대치한 값이 다시 평균에 섞이지 않도록 원래 관측값으로 보완값을 구한다.
        fallback_target = values.isna() & target & pd.notna(fallback)	# 전체 열이 결측이면 보완값도 없어 그대로 결측으로 남긴다.
        values.loc[fallback_target] = fallback
        result[column] = values
        audit[column] = {"missing_before": int(original.isna().sum()),
                         "group_filled": group_count, "global_filled": int(fallback_target.sum()),
                         "missing_after": int(values.isna().sum()),
                         "variance_before": float(original.var()), "variance_after": float(values.var())}	# 분산은 표본분산이며 전후 관측 수가 달라질 수 있어 해석에 주의한다.
    return result, audit


def iqr_limits(series, threshold=1.5):
    """수치 Series와 배수로 IQR 하한·상한을 반환한다. 입력은 보존하며 경계값은 정상 범위다."""
    if not np.isfinite(threshold) or threshold < 0:	# 음수나 비유한 배수로 뒤집히거나 무의미한 경계가 생기는 것을 막는다.
        raise ValueError("threshold must be finite and non-negative.")
    values = pd.to_numeric(series, errors="raise")
    if np.isinf(values).any() or not values.notna().any():	# 결측은 사분위수에서 제외되지만 무한대나 관측값 없는 입력은 거부한다.
        raise ValueError("IQR needs finite observations.")
    q1, q3 = values.quantile([.25, .75])	# 가운데 50퍼센트의 퍼짐을 사용해 극단값의 크기 영향을 줄인다.
    return float(q1 - threshold * (q3 - q1)), float(q3 + threshold * (q3 - q1))	# 정규성 가정은 없으며 경계 밖 여부 자체가 데이터 오류를 뜻하지는 않는다.


def calculate_customer_rfm(frame, customer_col, date_col, amount_col, *, reference_date=None,
                           frequency_unit="purchase_day", order_col=None, split_inactive=False):
    """거래 표·열·기준일·빈도 설정을 받아 고객 RFM 표와 계산 기준을 반환한다.

    입력은 보존하며 잘못된 거래는 암묵적으로 버리지 않고 정제 호출을 요구한다.
    R은 기준일−최종 구매일, F는 고유 구매일 또는 주문 수, M은 유효 금액 원값 합계다.
    split_inactive=True이면 낮은 최근성 고객을 반복 구매 여부로 나누며 동점 점수는 같다.
    """
    valid, audit = clean_transactions(frame, customer_col, date_col, amount_col,
                                      frequency_unit=frequency_unit, order_col=order_col)
    if len(valid) != len(frame):	# RFM 내부에서 거래를 몰래 제거해 합계가 바뀌지 않도록 정제를 선행하게 한다.
        raise ValueError("Invalid RFM input. Call validate_transactions() first.")
    latest = valid[date_col].max()
    reference = latest if reference_date is None else pd.Timestamp(reference_date).normalize()	# 미지정 시 마지막 거래일을 쓰며 기준일 구매의 최근일수는 0이 된다.
    if pd.isna(reference) or reference < latest:	# 음수 최근일수나 무효 기준일을 방지한다.
        raise ValueError("reference_date must be on or after the latest transaction date.")
    frequency_col = date_col if frequency_unit == "purchase_day" else order_col	# 동일 날짜의 여러 거래를 주문 여러 건으로 해석하지 않는다.
    grouped = valid.groupby(customer_col, sort=True)
    rfm = grouped.agg(last_purchase=(date_col, "max"), Frequency=(frequency_col, "nunique"),
                      Monetary=(amount_col, "sum")).reset_index()	# F는 고유 단위 수이고 M은 삭제·클리핑하지 않은 유효 원금액의 합이다.
    rfm["Recency"] = (reference - rfm.pop("last_purchase")).dt.days	# 임시 마지막 구매일 열을 제거하고 고객별 일수 차이를 계산한다.
    for metric, ascending, score in (("Recency", False, "R_Score"),
                                     ("Frequency", True, "F_Score"), ("Monetary", True, "M_Score")):	# 최근일수는 작을수록, 빈도·금액은 클수록 높은 점수를 받게 한다.
        percentile = (rfm[metric].rank(method="average", ascending=ascending) - .5) / len(rfm)	# 평균 순위는 동점과 입력 순서 독립성을 보존하므로 강제 사등분을 하지 않는다.
        rfm[score] = np.select([percentile <= .25, percentile <= .5, percentile <= .75], [1, 2, 3], default=4)	# 경계는 포함하며 동점 때문에 각 점수에 정확히 25퍼센트가 배정되지는 않는다.
    repeat = rfm["Frequency"] >= 2	# 반복 여부는 상대 점수와 별개로 원래 빈도에서 판정한다.
    conditions = [(rfm.R_Score >= 3) & (rfm.F_Score >= 3) & (rfm.M_Score >= 3) & repeat,	# 고액·최근·반복 조건을 모두 만족하는 고객을 가장 먼저 VIP로 선택한다.
                  (rfm.R_Score >= 3) & (rfm.F_Score >= 3) & repeat,	# VIP와 겹치는 조건은 앞선 규칙이 우선하므로 Loyal로 중복 배정되지 않는다.
                  (rfm.R_Score >= 3) & ~repeat]	# New는 최근 관측 구매 단위가 하나인 그룹이며 신규 가입을 의미하지 않는다.
    labels = ["VIP", "Loyal", "New"]
    if split_inactive:	# 선택한 경우에만 비활성 그룹을 과거 반복 여부로 세분한다.
        conditions += [(rfm.R_Score <= 2) & repeat, (rfm.R_Score <= 2) & ~repeat]
        labels += ["Inactive_repeat", "Inactive_oneoff"]
    else:
        conditions += [rfm.R_Score <= 2]	# 기본 분류의 Churned는 낮은 상대 최근성이며 실제 이탈 확정값은 아니다.
        labels += ["Churned"]
    rfm["Segment"] = np.select(conditions, labels, default="Potential")	# 첫 일치 조건을 적용해 고객마다 정확히 하나의 그룹을 부여한다.
    metadata = {"reference_date": str(reference.date()), "frequency_unit": frequency_unit,
                "split_inactive": split_inactive, "customers": len(rfm),
                "amount_sum": audit["amount_sum"], "segments": rfm.Segment.value_counts().to_dict()}	# 고객 수·원금액 합계·분류 건수를 재현과 결과 검증에 사용할 수 있게 남긴다.
    return rfm, metadata


def segment_profile(rfm):
    """고객 RFM 표를 받아 그룹별 고객 수·중앙값·금액·구성비 표를 반환하며 입력을 변경하지 않는다."""
    profile = rfm.groupby("Segment", observed=True).agg(	# 실제로 관측된 그룹만 요약해 비어 있는 범주가 해석에 섞이지 않게 한다.
        Customers=("Monetary", "size"), Recency_median=("Recency", "median"),
        Frequency_median=("Frequency", "median"), Monetary_mean=("Monetary", "mean"),
        Monetary_total=("Monetary", "sum"))
    profile["Customer_share"] = profile.Customers / profile.Customers.sum()	# 거래 행 수가 아닌 고객 수를 분모로 그룹 규모를 비교한다.
    profile["Monetary_share"] = profile.Monetary_total / profile.Monetary_total.sum()	# 고객 비중과 금액 기여도를 분리해 캠페인 후보의 근거를 보여준다.
    return profile.sort_values("Monetary_total", ascending=False)	# 금액 기여 순으로 정렬하되 계산에 쓴 고객 표는 변경하지 않는다.
