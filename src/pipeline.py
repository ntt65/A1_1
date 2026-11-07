"""E-commerce multimodal data analysis pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# 기존 python src/pipeline.py 실행도 저장소 루트의 utils를 찾게 한다.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils.image_features import extract_product_image_features
from utils.analytics import clean_transactions, impute_features, iqr_limits, calculate_customer_rfm, segment_profile


class DataAnalyzer:
    """Object-oriented data analysis pipeline for e-commerce data."""

    def __init__(self, data_path: str):
        """CSV 경로와 분석 상태를 준비한다. 파일은 load_data()에서 읽는다."""
        self.data_path = data_path
        self.df: Optional[pd.DataFrame] = None
        self.products: Optional[pd.DataFrame] = None
        self.product_key: Optional[str] = None
        self.join_summary: dict = {}
        self.image_batch_info: dict = {}
        self.transaction_audit: dict = {}
        self.missing_audit: dict = {}
        self.outlier_audit: dict = {}
        self.rfm_audit: dict = {}

    def load_data(self, *, required_columns=(), date_columns=(), dtype=None) -> pd.DataFrame:
        """CSV를 읽어 self.df를 교체하고 반환한다.

        required_columns는 필수 열, date_columns는 YYYY-MM-DD 날짜 열이다.
        알려진 ID는 문자열로 읽어 선행 0을 보존한다. dtype으로 다른 열의
        자료형도 지정할 수 있다. 날짜 변환 실패는 NaT로 남겨 정제 단계에서
        집계하며, 로드 실패 시 기존 분석 상태를 유지한다.
        """
        types = dict.fromkeys(("customer_id", "article_id", "sales_channel_id"), "string")
        types.update(dtype or {})
        try:
            loaded = pd.read_csv(self.data_path, dtype=types)
        except pd.errors.EmptyDataError as error:
            raise ValueError(f"Empty CSV: {self.data_path}") from error
        missing = set(required_columns).union(date_columns) - set(loaded.columns)
        if missing:
            raise ValueError(f"Missing columns in {self.data_path}: {sorted(missing)}")
        if loaded.empty:
            raise ValueError(f"Empty CSV: {self.data_path}")
        for column in ("customer_id", "article_id", "sales_channel_id"):
            if column in loaded:
                loaded[column] = loaded[column].astype("string").str.strip().replace("", pd.NA)
        for column in date_columns:
            loaded[column] = pd.to_datetime(loaded[column], format="%Y-%m-%d", errors="coerce")
        self.df = loaded
        self.products = None
        self.product_key = None
        self.join_summary = {}
        self.image_batch_info = {}
        self.transaction_audit = {}
        self.missing_audit = {}
        self.outlier_audit = {}
        self.rfm_audit = {}
        return self.df

    def join_products(self, product_path: str, *, key="article_id", amount_col="price") -> pd.DataFrame:
        """상품 CSV를 다대일 왼쪽 조인하고 self.df와 self.products를 갱신한다.

        빈 상품 키는 제외하고 중복 키와 겹치는 메타데이터 열은 오류로 알린다.
        거래 순서·행 수·금액 합계를 보존하며, 미매칭과 제외 건수는
        join_summary에 기록한다. 실패하면 기존 데이터는 변경하지 않는다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if key not in self.df:
            raise ValueError(f"Column '{key}' not found in transactions.")
        try:
            products = pd.read_csv(product_path, dtype={key: "string"})
        except pd.errors.EmptyDataError as error:
            raise ValueError(f"Empty product CSV: {product_path}") from error
        if key not in products:
            raise ValueError(f"Column '{key}' not found in {product_path}.")
        products[key] = products[key].str.strip().replace("", pd.NA)
        missing_keys = int(products[key].isna().sum())
        # Pandas는 null 키끼리도 연결하므로, 상품 쪽 null을 먼저 제외한다.
        products = products.dropna(subset=[key]).copy()
        if products.empty:
            raise ValueError(f"No usable product keys in {product_path}.")
        if products[key].duplicated().any():
            raise ValueError(f"Duplicate product keys in {product_path}: {key}")
        overlap = (set(products) & set(self.df)) - {key}
        if overlap:
            raise ValueError(f"Product columns already exist in transactions: {sorted(overlap)}")
        working = self.df.copy()
        working[key] = working[key].astype("string").str.strip().replace("", pd.NA)
        matched = working[key].isin(products[key])
        joined = working.merge(products, on=key, how="left", sort=False, validate="many_to_one")
        joined.index = self.df.index
        before = after = None
        if amount_col in working:
            before = float(pd.to_numeric(working[amount_col], errors="coerce").sum())
            after = float(pd.to_numeric(joined[amount_col], errors="coerce").sum())
            if not np.isclose(before, after, rtol=1e-12, atol=1e-10, equal_nan=True):
                raise ValueError("Product join changed the transaction amount sum.")
        if len(joined) != len(working):
            raise ValueError("Product join changed the transaction row count.")
        self.join_summary = {
            "rows_before": len(working), "rows_after": len(joined),
            "amount_before": before, "amount_after": after,
            "matched_rows": int(matched.sum()), "unmatched_rows": int((~matched).sum()),
            "excluded_empty_product_keys": missing_keys,
        }
        self.df, self.products, self.product_key = joined, products, key
        return self.df

    def validate_transactions(self, customer_col="customer_id", date_col="t_dat", amount_col="price", **settings):
        """유효 거래로 self.df를 교체하고 제외 사유를 transaction_audit에 기록한다."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        valid, audit = clean_transactions(self.df, customer_col, date_col, amount_col, **settings)
        self.df, self.transaction_audit = valid, audit
        return self.df

    def handle_missing_values(self, strategy="group_mean", group_col=None, *, columns=None, eligible=None):
        """지정한 수치 피처의 결측만 처리하고 대치 집계를 missing_audit에 남긴다.

        eligible=False인 행과 기존 관측값을 보존한다. 실패하면 self.df를 바꾸지
        않는다. 그룹 평균이 없을 때 대치 전 전체 관측값의 평균을 사용한다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        result, audit = impute_features(self.df, strategy, group_col, columns, eligible)
        self.df, self.missing_audit = result, audit
        return self.df

    def detect_outliers(self, column, threshold=1.5):
        """원본을 바꾸지 않고 IQR 경계 밖 마스크를 반환하고 경계를 기록한다."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if column not in self.df:
            raise ValueError(f"Column '{column}' not found in data.")
        lower, upper = iqr_limits(self.df[column], threshold)
        mask = (self.df[column] < lower) | (self.df[column] > upper)
        self.outlier_audit[column] = {"lower": lower, "upper": upper, "count": int(mask.sum()), "threshold": threshold}
        return mask

    def clip_outliers(self, column, threshold=1.5):
        """EDA용 보정 Series를 반환한다. self.df의 원본 금액은 보존한다."""
        self.detect_outliers(column, threshold)
        limits = self.outlier_audit[column]
        return self.df[column].clip(limits["lower"], limits["upper"])

    def calculate_rfm(self, customer_col, date_col, amount_col, *, reference_date=None,
                      frequency_unit="purchase_day", order_col=None, split_inactive=False):
        """원본 거래를 보존하며 고객별 RFM 표와 계산 기준 rfm_audit를 만든다.

        기준일 구매의 Recency는 0, 기본 Frequency는 고유 구매일 수다.
        같은 값은 평균 순위로 같은 점수를 받는다. 그룹 규칙은 통합 계획 C5다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        result, audit = calculate_customer_rfm(self.df, customer_col, date_col, amount_col,
            reference_date=reference_date, frequency_unit=frequency_unit,
            order_col=order_col, split_inactive=split_inactive)
        self.rfm_audit = audit
        return result

    def summarize(self, columns=None):
        """수치 열의 건수·평균·중앙값·표준편차·사분위수 표를 반환한다."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        frame = self.df[columns] if columns is not None else self.df.select_dtypes(include="number")
        return frame.describe().T.rename(columns={"25%": "Q1", "50%": "median", "75%": "Q3"})

    @staticmethod
    def profile_segments(rfm):
        """고객 단위 표를 받아 세그먼트별 건수·중앙값·구매금액 비중을 반환한다."""
        return segment_profile(rfm)

    def extract_image_features(self, image_column: str = "image", *, image_dir=None,
                               image_size: int = 32, batch_size: int = 32,
                               advanced=False, histogram_bins=8) -> pd.DataFrame:
        """이미지 평균·표준편차를 self.df에 추가하고 같은 표를 반환한다.

        image_dir가 없으면 기존처럼 image_column의 같은 모양 배열을 계산한다.
        파일 입력은 join_products() 후 상품별 한 번 읽는다. 0~1 RGB 픽셀을
        image_size 정사각형으로 줄여 batch_size장씩 계산한다. 실패 피처는
        NaN으로, 이유는 <image_column>_status 열에 남긴다.
        파일 입력의 advanced=True는 같은 배치에서 히스토그램·엣지를 추가한다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if image_dir is not None:
            return self._extract_image_files(Path(image_dir), image_column, image_size, batch_size,
                                             advanced, histogram_bins)
        if advanced:
            raise ValueError("Advanced image features require image_dir.")
        if image_column not in self.df.columns:
            raise ValueError(f"Column '{image_column}' not found in data.")

        image_data = np.asarray(self.df[image_column].tolist(), dtype=float)
        if image_data.ndim < 2:
            raise ValueError("image_column must contain same-shaped array-like values.")

        reduce_axes = tuple(range(1, image_data.ndim))
        self.df[f"{image_column}_mean"] = image_data.mean(axis=reduce_axes)
        self.df[f"{image_column}_std"] = image_data.std(axis=reduce_axes)

        return self.df

    def _extract_image_files(self, directory, prefix, image_size, batch_size, advanced=False, histogram_bins=8):
        """재사용 도구의 상품 피처를 거래에 매핑하고 배치 진단을 기록한다."""
        if self.products is None:
            raise ValueError("Call join_products() before extracting image files.")
        features, batch_info = extract_product_image_features(
            self.products, self.product_key, directory, prefix, image_size, batch_size,
            advanced, histogram_bins)
        keys = self.products[self.product_key]
        # 거래별 이미지 배열 대신 상품별로 계산한 작은 피처만 연결한다.
        for column in features:
            self.df[column] = self.df[self.product_key].map(features[column])
            self.products[column] = keys.map(features[column])
        self.df[f"{prefix}_status"] = self.df[f"{prefix}_status"].fillna("unmatched_product")
        self.image_batch_info = batch_info
        return self.df

    def extract_text_features(self, text_column: str) -> pd.DataFrame:
        """원문은 보존하고 문자 수·공백 기준 단어 수를 self.df에 추가한다.

        상품 조인이 있으면 상품별 한 번 계산해 거래에 매핑한다. 결측 상품명은
        계산할 때만 빈 문자열로 취급한다. 미매칭 거래의 피처는 결측으로 둔다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if text_column not in self.df.columns:
            raise ValueError(f"Column '{text_column}' not found in data.")

        source = self.products if self.products is not None and text_column in self.products else self.df
        text_series = source[text_column].fillna("").astype(str)
        for suffix, values in (("length", text_series.str.len()),
                               ("word_count", text_series.str.split().str.len())):
            column = f"{text_column}_{suffix}"
            if source is self.products:
                self.products[column] = values
                self.df[column] = self.df[self.product_key].map(self.products.set_index(self.product_key)[column])
            else:
                self.df[column] = values

        return self.df


def main() -> None:
    """CSV 로드와 선택적인 상품 조인을 명령줄에서 확인한다."""
    parser = argparse.ArgumentParser(description="Run e-commerce data analysis pipeline.")
    parser.add_argument("--data", required=True, help="Path to CSV data file")
    parser.add_argument("--products", help="Optional product CSV, joined on article_id")
    args = parser.parse_args()

    analyzer = DataAnalyzer(args.data)
    df = analyzer.load_data()
    if args.products:
        df = analyzer.join_products(args.products)
        print(f"Join audit: {analyzer.join_summary}")
    print(f"Loaded dataset shape: {df.shape}")


if __name__ == "__main__":
    main()
