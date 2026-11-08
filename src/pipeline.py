"""거래·상품 입력을 분석 표와 RFM으로 변환하며 인스턴스 상태와 처리 근거를 관리한다."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


if __package__ in (None, ""):	# 직접 파일 실행일 때만 저장소 모듈의 검색 경로를 보완한다.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))	# 현재 파일 기준으로 루트를 찾아 실행 디렉터리 의존성을 줄인다.
from utils.image_features import extract_product_image_features
from utils.analytics import clean_transactions, impute_features, iqr_limits, calculate_customer_rfm, segment_profile


class DataAnalyzer:
    """CSV 경로를 받아 거래·상품 표와 감사 기록을 관리하고 메서드별 분석 결과를 반환한다."""

    def __init__(self, data_path: str):
        """입력 CSV 경로로 빈 분석 상태를 초기화한다. 반환값은 없고 파일은 읽지 않는다."""
        self.data_path = data_path	# 초기화 단계에서는 경로만 보관하고 실제 읽기는 지연한다.
        self.df: Optional[pd.DataFrame] = None	# 미로드 상태와 빈 분석 결과를 구분한다.
        self.products: Optional[pd.DataFrame] = None	# 상품 단위 피처를 거래 빈도로 중복 계산하지 않도록 별도 표를 둔다.
        self.product_key: Optional[str] = None
        self.join_summary: dict = {}	# 행 수·금액 보존과 미매칭의 근거를 후속 단계에 전달한다.
        self.image_batch_info: dict = {}
        self.transaction_audit: dict = {}
        self.missing_audit: dict = {}
        self.outlier_audit: dict = {}
        self.rfm_audit: dict = {}

    def load_data(self, *, required_columns=(), date_columns=(), dtype=None) -> pd.DataFrame:
        """필수 열·날짜 열·자료형 설정으로 CSV를 읽어 self.df에 저장하고 반환한다.

        입력은 인스턴스의 CSV 경로와 required_columns·date_columns·dtype이다.
        ID는 문자열로 읽어 선행 0을 보존하고 지정 날짜는 YYYY-MM-DD로 변환한다.
        날짜 변환 실패는 NaT로 남겨 후속 정제에서 집계한다. 성공하면 상품 표와
        기존 감사 상태를 초기화하며 파일은 변경하지 않고 실패 시 기존 상태를 유지한다.
        """
        types = dict.fromkeys(("customer_id", "article_id", "sales_channel_id"), "string")	# 숫자처럼 보이는 식별자의 선행 0을 잃지 않게 한다.
        types.update(dtype or {})	# 다른 스키마의 자료형은 호출자가 명시적으로 덮어쓸 수 있다.
        try:
            loaded = pd.read_csv(self.data_path, dtype=types)	# 검증이 끝나기 전에는 인스턴스의 기존 표를 바꾸지 않는다.
        except pd.errors.EmptyDataError as error:
            raise ValueError(f"Empty CSV: {self.data_path}") from error
        missing = set(required_columns).union(date_columns) - set(loaded.columns)	# 날짜 변환 대상도 실제로 존재해야 하므로 필수 열과 함께 검사한다.
        if missing:
            raise ValueError(f"Missing columns in {self.data_path}: {sorted(missing)}")
        if loaded.empty:	# 열만 있고 행이 없는 파일도 분석 입력으로 거부한다.
            raise ValueError(f"Empty CSV: {self.data_path}")
        for column in ("customer_id", "article_id", "sales_channel_id"):
            if column in loaded:
                loaded[column] = loaded[column].astype("string").str.strip().replace("", pd.NA)	# 공백 키를 결측으로 통일해 조인과 유효성 판정 기준을 맞춘다.
        for column in date_columns:
            loaded[column] = pd.to_datetime(loaded[column], format="%Y-%m-%d", errors="coerce")	# 해석할 수 없는 날짜는 정제 감사에서 셀 수 있도록 NaT로 남긴다.
        self.df = loaded	# 모든 로드 검증을 통과한 뒤 새 분석 상태를 확정한다.
        self.products = None	# 이전 데이터에 연결된 상품·감사 정보를 재사용하지 않게 초기화한다.
        self.product_key = None
        self.join_summary = {}
        self.image_batch_info = {}
        self.transaction_audit = {}
        self.missing_audit = {}
        self.outlier_audit = {}
        self.rfm_audit = {}
        return self.df

    def join_products(self, product_path: str, *, key="article_id", amount_col="price") -> pd.DataFrame:
        """상품 CSV 경로·조인 키·금액 열을 받아 다대일 왼쪽 조인 표를 반환한다.

        빈 상품 키는 제외하고 중복 키와 겹치는 메타데이터 열은 오류로 알린다.
        거래 순서·행 수·금액을 보존하며 self.df·self.products·product_key와
        join_summary를 갱신한다. 입력 파일은 변경하지 않고 실패 시 기존 상태를 유지한다.
        """
        if self.df is None:	# 거래 표가 준비되지 않은 순서 오류를 즉시 알린다.
            raise ValueError("Data is not loaded. Call load_data() first.")
        if key not in self.df:
            raise ValueError(f"Column '{key}' not found in transactions.")
        try:
            products = pd.read_csv(product_path, dtype={key: "string"})	# 상품 식별자도 거래와 동일한 문자열 기준으로 읽는다.
        except pd.errors.EmptyDataError as error:
            raise ValueError(f"Empty product CSV: {product_path}") from error
        if key not in products:
            raise ValueError(f"Column '{key}' not found in {product_path}.")
        products[key] = products[key].str.strip().replace("", pd.NA)	# 키의 주변 공백과 빈 문자열을 거래 쪽과 같은 규칙으로 정규화한다.
        missing_keys = int(products[key].isna().sum())

        products = products.dropna(subset=[key]).copy()	# Pandas의 결측 키 간 연결을 막기 위해 상품 쪽 결측 키를 먼저 제외한다.
        if products.empty:
            raise ValueError(f"No usable product keys in {product_path}.")
        if products[key].duplicated().any():	# 상품 키가 유일해야 거래가 조인으로 증식하지 않는다.
            raise ValueError(f"Duplicate product keys in {product_path}: {key}")
        overlap = (set(products) & set(self.df)) - {key}
        if overlap:	# 동명 열의 접미사 생성과 기존 메타데이터 덮어쓰기를 방지한다.
            raise ValueError(f"Product columns already exist in transactions: {sorted(overlap)}")
        working = self.df.copy()
        working[key] = working[key].astype("string").str.strip().replace("", pd.NA)
        matched = working[key].isin(products[key])	# 조인 여부를 별도로 집계해 누락 상품이 거래 삭제로 이어지지 않게 한다.
        joined = working.merge(products, on=key, how="left", sort=False, validate="many_to_one")	# 왼쪽 거래를 보존하고 상품 키의 다대일 관계를 라이브러리에서도 검증한다.
        joined.index = self.df.index	# 원래 거래 인덱스를 복원해 후속 Series 정렬과 연결을 유지한다.
        before = after = None
        if amount_col in working:
            before = float(pd.to_numeric(working[amount_col], errors="coerce").sum())
            after = float(pd.to_numeric(joined[amount_col], errors="coerce").sum())
            if not np.isclose(before, after, rtol=1e-12, atol=1e-10, equal_nan=True):	# 부동소수 합계의 작은 오차를 허용하면서 금액 증식을 탐지한다.
                raise ValueError("Product join changed the transaction amount sum.")
        if len(joined) != len(working):	# 조인 과정에서 거래 행이 늘거나 줄지 않았는지 독립적으로 확인한다.
            raise ValueError("Product join changed the transaction row count.")
        self.join_summary = {
            "rows_before": len(working), "rows_after": len(joined),
            "amount_before": before, "amount_after": after,
            "matched_rows": int(matched.sum()), "unmatched_rows": int((~matched).sum()),
            "excluded_empty_product_keys": missing_keys,
        }
        self.df, self.products, self.product_key = joined, products, key	# 보존 검증이 끝난 결과만 인스턴스 상태에 반영한다.
        return self.df

    def validate_transactions(self, customer_col="customer_id", date_col="t_dat", amount_col="price", **settings):
        """열 이름·정제 설정으로 유효 거래 표를 반환하고 self.df·transaction_audit를 갱신한다."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        valid, audit = clean_transactions(self.df, customer_col, date_col, amount_col, **settings)	# 재사용 가능한 정제 함수에서 대표 제외 사유와 유효 거래를 함께 얻는다.
        self.df, self.transaction_audit = valid, audit	# 정제 성공 시에만 거래 표와 감사 기록을 같은 실행 결과로 교체한다.
        return self.df

    def handle_missing_values(self, strategy="group_mean", group_col=None, *, columns=None, eligible=None):
        """전략·그룹·대상 열·eligible을 받아 처리 표를 반환하고 self.df·missing_audit를 갱신한다.

        대치 전략은 기존 관측값과 eligible=False 위치를 보존하며 그룹 평균이 없으면
        대치 전 전체 관측 평균을 쓴다. drop은 대상 결측 행을 제거하며 실패 시 상태를 유지한다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        result, audit = impute_features(self.df, strategy, group_col, columns, eligible)	# 입력 사본을 계산하는 도구에 맡겨 실패 시 기존 상태를 지킨다.
        self.df, self.missing_audit = result, audit
        return self.df

    def handle_missing(self, strategy="group_mean", group_col=None, *, columns=None, eligible=None):
        """전략·그룹·열·대상 마스크를 대치 메서드로 위임해 표를 반환하고 동일한 상태를 갱신한다."""
        return self.handle_missing_values(strategy, group_col, columns=columns, eligible=eligible)	# 호환 이름에서도 별도 계산을 만들지 않아 대치 정책이 갈라지지 않는다.

    def detect_outliers(self, column, threshold=1.5):
        """열·IQR 배수로 경계 밖 마스크를 반환한다. 원본 표는 보존하고 outlier_audit만 갱신한다."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if column not in self.df:
            raise ValueError(f"Column '{column}' not found in data.")
        lower, upper = iqr_limits(self.df[column], threshold)	# 탐지와 보정이 동일한 사분위수 경계를 사용하도록 공용 계산을 호출한다.
        mask = (self.df[column] < lower) | (self.df[column] > upper)	# 경계와 같은 값은 정상에 포함하고 바깥 값만 표시한다.
        self.outlier_audit[column] = {"lower": lower, "upper": upper, "count": int(mask.sum()), "threshold": threshold}	# 마스크와 함께 경계·건수를 남겨 결과를 설명하고 재확인할 수 있게 한다.
        return mask

    def clip_outliers(self, column, threshold=1.5):
        """열·IQR 배수로 보정 Series를 반환한다. 원금액은 보존하고 탐지 감사 기록은 갱신한다."""
        self.detect_outliers(column, threshold)	# 탐지와 보정의 경계가 일치하도록 같은 감사 기록을 사용한다.
        limits = self.outlier_audit[column]
        return self.df[column].clip(limits["lower"], limits["upper"])	# 새 Series만 반환하므로 RFM과 월별 집계용 원금액은 변하지 않는다.

    def calculate_rfm(self, customer_col, date_col, amount_col, *, reference_date=None,
                      frequency_unit="purchase_day", order_col=None, split_inactive=False):
        """고객·날짜·금액 열과 기준일·빈도 설정으로 고객 RFM 표를 반환한다.

        self.df는 보존하고 계산 기준을 rfm_audit에 기록한다. 기준일 구매의 R은 0,
        기본 F는 고유 구매일 수다. 평균 순위는 동점을 보존하며 그룹 규칙은 통합 계획 C5다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        result, audit = calculate_customer_rfm(self.df, customer_col, date_col, amount_col,
            reference_date=reference_date, frequency_unit=frequency_unit,
            order_col=order_col, split_inactive=split_inactive)
        self.rfm_audit = audit	# 거래 표 대신 계산 정의와 고객 집계의 감사 정보만 상태에 남긴다.
        return result

    def summarize(self, columns=None):
        """선택 열 또는 전체 수치 열의 건수·평균·표준편차·사분위수 표를 반환하며 상태를 보존한다."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        frame = self.df[columns] if columns is not None else self.df.select_dtypes(include="number")	# 명시한 열이 없으면 수치형 열만 통계 대상으로 삼는다.
        return frame.describe().T.rename(columns={"25%": "Q1", "50%": "median", "75%": "Q3"})	# 표준 기술통계를 변수별 행으로 바꾸고 사분위수 이름을 명확히 한다.

    @staticmethod
    def profile_segments(rfm):
        """고객 RFM 표를 받아 그룹별 건수·중앙값·금액 비중 표를 반환하며 입력과 상태를 보존한다."""
        return segment_profile(rfm)

    def extract_image_features(self, image_column: str = "image", *, image_dir=None,
                               image_size: int = 32, batch_size: int = 32,
                               advanced=False, histogram_bins=8) -> pd.DataFrame:
        """배열 열 또는 이미지 경로·크기·배치 설정으로 피처를 추가한 self.df를 반환한다.

        image_dir가 없으면 image_column의 같은 모양 배열을 집계하며 원문 배열은 보존한다.
        파일 입력은 상품 조인 후 상품별 한 번 읽고 상품 표·배치 진단도 갱신한다.
        픽셀을 0~1 RGB로 정규화하고 image_size 격자 표본을 batch_size 상품 창에서 계산한다.
        실패 피처는 NaN, 원인은 <image_column>_status로 기록하며 이미지 파일은 변경하지 않는다.
        파일 입력의 advanced=True이면 같은 배치에서 히스토그램·인접 절대차도 추가한다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if image_dir is not None:	# 파일 경로와 기존 배열 열 입력의 호출 방식을 함께 지원한다.
            return self._extract_image_files(Path(image_dir), image_column, image_size, batch_size,
                                             advanced, histogram_bins)
        if advanced:	# 고급 피처의 전처리 계약은 파일 경로에서만 제공한다.
            raise ValueError("Advanced image features require image_dir.")
        if image_column not in self.df.columns:
            raise ValueError(f"Column '{image_column}' not found in data.")

        image_data = np.asarray(self.df[image_column].tolist(), dtype=float)	# 같은 모양의 배열을 모아 첫 축이 거래 관측을 나타내게 한다.
        if image_data.ndim < 2:
            raise ValueError("image_column must contain same-shaped array-like values.")

        reduce_axes = tuple(range(1, image_data.ndim))	# 첫 관측 축을 남기고 각 관측 내부의 모든 픽셀 축을 축약한다.
        self.df[f"{image_column}_mean"] = image_data.mean(axis=reduce_axes)	# 관측마다 하나의 평균을 얻어 행 수를 유지한다.
        self.df[f"{image_column}_std"] = image_data.std(axis=reduce_axes)	# 주어진 픽셀 전체의 퍼짐이므로 기본 ddof=0을 사용한다.

        return self.df

    def _extract_image_files(self, directory, prefix, image_size, batch_size, advanced=False, histogram_bins=8):
        """경로·접두사·배치 설정으로 상품 피처를 추출해 거래 표를 반환하고 상품 표·배치 진단을 갱신한다."""
        if self.products is None:	# 상품별 한 번만 계산하려면 먼저 유일 키를 가진 상품 표가 필요하다.
            raise ValueError("Call join_products() before extracting image files.")
        features, batch_info = extract_product_image_features(
            self.products, self.product_key, directory, prefix, image_size, batch_size,
            advanced, histogram_bins)
        keys = self.products[self.product_key]

        for column in features:
            self.df[column] = self.df[self.product_key].map(features[column])	# 거래마다 이미지 배열을 복제하지 않고 상품별 수치 피처만 연결한다.
            self.products[column] = keys.map(features[column])	# 상품 단위 분석에도 같은 피처를 재사용하도록 상품 표를 함께 갱신한다.
        self.df[f"{prefix}_status"] = self.df[f"{prefix}_status"].fillna("unmatched_product")	# 상품 미매칭과 상품 이미지 자체의 누락 원인을 구분한다.
        self.image_batch_info = batch_info	# 배치 버퍼 정보는 전체 프로세스 메모리와 구별해 보관한다.
        return self.df

    def extract_text_features(self, text_column: str) -> pd.DataFrame:
        """텍스트 열 이름을 받아 문자 수·단어 수를 추가한 self.df를 반환한다.

        상품 조인이 있으면 상품별 한 번 계산해 상품 표와 거래 표를 함께 갱신한다.
        원문은 보존하고 결측은 계산 시에만 빈 문자열로 취급하며 미매칭 피처는 결측으로 둔다.
        """
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if text_column not in self.df.columns:
            raise ValueError(f"Column '{text_column}' not found in data.")

        source = self.products if self.products is not None and text_column in self.products else self.df	# 상품 원문이 있으면 반복 거래보다 고유 상품에서 먼저 계산한다.
        text_series = source[text_column].fillna("").astype(str)	# 결측 치환은 임시 Series에만 적용해 원문을 덮어쓰지 않는다.
        for suffix, values in (("length", text_series.str.len()),
                               ("word_count", text_series.str.split().str.len())):	# 공백 기준 단어 수이며 형태소나 의미 단위 분석은 아니다.
            column = f"{text_column}_{suffix}"
            if source is self.products:
                self.products[column] = values
                self.df[column] = self.df[self.product_key].map(self.products.set_index(self.product_key)[column])	# 상품 키로 매핑하므로 미매칭 거래의 파생값은 결측으로 남는다.
            else:
                self.df[column] = values

        return self.df


def main() -> None:
    """명령줄 CSV 경로를 읽어 로드·선택 조인을 실행하고 요약을 출력한다. 반환값과 파일 변경은 없다."""
    parser = argparse.ArgumentParser(description="Run e-commerce data analysis pipeline.")
    parser.add_argument("--data", required=True, help="Path to CSV data file")
    parser.add_argument("--products", help="Optional product CSV, joined on article_id")	# 상품 경로가 주어진 경우에만 추가 조인을 수행한다.
    args = parser.parse_args()

    analyzer = DataAnalyzer(args.data)
    df = analyzer.load_data()
    if args.products:
        df = analyzer.join_products(args.products)
        print(f"Join audit: {analyzer.join_summary}")	# 명령줄에서도 보존·미매칭 집계를 확인할 수 있게 출력한다.
    print(f"Loaded dataset shape: {df.shape}")


if __name__ == "__main__":	# 모듈을 가져올 때는 명령줄 처리를 실행하지 않는다.
    main()
