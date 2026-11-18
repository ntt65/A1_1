"""E-commerce multimodal data analysis pipeline."""

from __future__ import annotations	# 타입 힌트 전방 참조 활성화

import argparse	# 명령줄 인자 파싱용 표준 라이브러리
import sys	# 모듈 탐색 경로 조정용
from pathlib import Path	# 파일 시스템 경로 처리용
from typing import Optional	# 선택적 타입 힌트 표기용

import numpy as np	# 수치·배열 연산 라이브러리
import pandas as pd	# 표 형식 데이터 처리 라이브러리

# 기존 python src/pipeline.py 실행도 저장소 루트의 utils를 찾게 한다.
if __package__ in (None, ""):	# 패키지 컨텍스트 없이 직접 실행된 경우
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))	# 저장소 루트 경로를 sys.path 최상단에 추가
from utils.image_features import extract_product_image_features	# 상품 이미지 배치 피처 추출 함수 임포트
from utils.analytics import clean_transactions, impute_features, iqr_limits, calculate_customer_rfm, segment_profile	# 정제·대치·IQR·RFM 공용 함수 임포트


class DataAnalyzer:
    """Object-oriented data analysis pipeline for e-commerce data."""

    def __init__(self, data_path: str):
        """CSV 경로와 분석 상태를 준비한다. 파일은 load_data()에서 읽는다."""
        self.data_path = data_path	# 입력 거래 CSV 파일 경로 저장
        self.df: Optional[pd.DataFrame] = None	# 주 거래 DataFrame 상태 초기화
        self.products: Optional[pd.DataFrame] = None	# 조인된 상품 DataFrame 상태 초기화
        self.product_key: Optional[str] = None	# 상품 조인 키 열 이름 초기화
        self.join_summary: dict = {}	# 상품 조인 검증 요약 초기화
        self.image_batch_info: dict = {}	# 이미지 배치 처리 진단 정보 초기화
        self.transaction_audit: dict = {}	# 거래 정제 건수 감사 초기화
        self.missing_audit: dict = {}	# 결측 대치 감사 초기화
        self.outlier_audit: dict = {}	# 이상치 탐지·보정 감사 초기화
        self.rfm_audit: dict = {}	# RFM 계산 기준 감사 초기화

    def load_data(self, *, required_columns=(), date_columns=(), dtype=None) -> pd.DataFrame:
        """검증한 CSV를 self.df에 저장해 반환하고 이전 분석 상태를 초기화한다.

        required_columns는 필수 열, date_columns는 YYYY-MM-DD 날짜 열이다.
        알려진 ID는 문자열로 읽어 선행 0을 보존한다. dtype으로 다른 열의
        자료형도 지정할 수 있다. 날짜 변환 실패는 NaT로 남겨 정제 단계에서
        집계하며, 로드 실패 시 기존 분석 상태를 유지한다.
        """
        types = dict.fromkeys(("customer_id", "article_id", "sales_channel_id"), "string")	# 선행 0 보존을 위해 ID 열을 string으로 지정
        types.update(dtype or {})	# 사용자 지정 dtype으로 덮어쓰기·병합
        try:	# 빈 파일 등 CSV 파싱 예외 처리 시작
            loaded = pd.read_csv(self.data_path, dtype=types)	# 지정된 dtype으로 거래 CSV 로드
        except pd.errors.EmptyDataError as error:	# 헤더조차 없는 빈 CSV 예외 포착
            raise ValueError(f"Empty CSV: {self.data_path}") from error	# 통일된 ValueError로 변환해 발생
        missing = set(required_columns).union(date_columns) - set(loaded.columns)	# 필수 열 및 날짜 열 누락 여부 계산
        if missing:	# 누락된 열이 하나라도 있으면 중단
            raise ValueError(f"Missing columns in {self.data_path}: {sorted(missing)}")	# 누락 열 목록을 담아 예외 발생
        if loaded.empty:	# 헤더만 있고 데이터 행이 없는 경우
            raise ValueError(f"Empty CSV: {self.data_path}")	# 빈 데이터셋 예외 발생
        for column in ("customer_id", "article_id", "sales_channel_id"):	# 알려진 ID 열 순회 정규화
            if column in loaded:	# 해당 ID 열이 존재할 때만 처리
                loaded[column] = loaded[column].astype("string").str.strip().replace("", pd.NA)	# 공백 제거 및 빈 문자열을 결측(NA)으로 변환
        for column in date_columns:	# 지정된 날짜 열 순회
            loaded[column] = pd.to_datetime(loaded[column], format="%Y-%m-%d", errors="coerce")	# YYYY-MM-DD 파싱 실패 값은 NaT로 유지
        self.df = loaded	# 검증된 DataFrame으로 상태 갱신
        self.products = None	# 새 데이터 로드 시 기존 상품 표 초기화
        self.product_key = None	# 기존 조인 키 초기화
        self.join_summary = {}	# 기존 조인 감사 기록 초기화
        self.image_batch_info = {}	# 기존 이미지 배치 정보 초기화
        self.transaction_audit = {}	# 기존 거래 정제 기록 초기화
        self.missing_audit = {}	# 기존 결측 대치 기록 초기화
        self.outlier_audit = {}	# 기존 이상치 기록 초기화
        self.rfm_audit = {}	# 기존 RFM 감사 기록 초기화
        return self.df	# 로드된 거래 DataFrame 반환

    def join_products(self, product_path: str, *, key="article_id", amount_col="price") -> pd.DataFrame:
        """상품 CSV를 다대일 왼쪽 조인하고 self.df와 self.products를 갱신한다.

        빈 상품 키는 제외하고 중복 키와 겹치는 메타데이터 열은 오류로 알린다.
        거래 순서·행 수·금액 합계를 보존하며, 미매칭과 제외 건수는
        join_summary에 기록한다. 실패하면 기존 데이터는 변경하지 않는다.
        """
        if self.df is None:	# 거래 데이터 로드 여부 확인
            raise ValueError("Data is not loaded. Call load_data() first.")	# 미로드 시 예외 발생
        if key not in self.df:	# 거래 표에 조인 키 열이 있는지 확인
            raise ValueError(f"Column '{key}' not found in transactions.")	# 키 누락 시 예외 발생
        try:	# 상품 CSV 읽기 예외 처리 시작
            products = pd.read_csv(product_path, dtype={key: "string"})	# 상품 키를 문자열로 유지하며 CSV 로드
        except pd.errors.EmptyDataError as error:	# 빈 상품 CSV 예외 포착
            raise ValueError(f"Empty product CSV: {product_path}") from error	# ValueError로 변환해 발생
        if key not in products:	# 상품 표에 조인 키 열이 있는지 확인
            raise ValueError(f"Column '{key}' not found in {product_path}.")	# 키 누락 시 예외 발생
        products[key] = products[key].str.strip().replace("", pd.NA)	# 상품 키 공백 제거 및 빈 문자열 결측 처리
        missing_keys = int(products[key].isna().sum())	# 제외될 빈 상품 키 건수 집계
        # Pandas는 null 키끼리도 연결하므로, 상품 쪽 null을 먼저 제외한다.
        products = products.dropna(subset=[key]).copy()	# null 키 행 제거 후 독립 사본 생성
        if products.empty:	# 유효한 상품 키가 하나도 남지 않은 경우
            raise ValueError(f"No usable product keys in {product_path}.")	# 사용 가능한 키 없음 예외 발생
        if products[key].duplicated().any():	# 다대일 조인 보장을 위해 상품 키 중복 검사
            raise ValueError(f"Duplicate product keys in {product_path}: {key}")	# 중복 키 발견 시 예외 발생
        overlap = (set(products) & set(self.df)) - {key}	# 키 외에 겹치는 열 이름 확인
        if overlap:	# 열 충돌 시 기존 거래 열 보호를 위해 중단
            raise ValueError(f"Product columns already exist in transactions: {sorted(overlap)}")	# 겹치는 열 목록 예외 발생
        working = self.df.copy()	# 실패 시 원본 유지를 위해 작업 사본 생성
        working[key] = working[key].astype("string").str.strip().replace("", pd.NA)	# 거래 쪽 조인 키 정규화
        matched = working[key].isin(products[key])	# 상품 메타데이터와 매칭되는 거래 마스크
        joined = working.merge(products, on=key, how="left", sort=False, validate="many_to_one")	# 행 순서 유지하며 다대일 왼쪽 조인 수행
        joined.index = self.df.index	# 기존 거래 DataFrame 인덱스 복원
        before = after = None	# 금액 합계 비교 변수 초기화
        if amount_col in working:	# 금액 열이 존재하면 조인 전후 합계 검증
            before = float(pd.to_numeric(working[amount_col], errors="coerce").sum())	# 조인 전 금액 합계 계산
            after = float(pd.to_numeric(joined[amount_col], errors="coerce").sum())	# 조인 후 금액 합계 계산
            if not np.isclose(before, after, rtol=1e-12, atol=1e-10, equal_nan=True):	# 부동소수 오차 범위 내 금액 보존 확인
                raise ValueError("Product join changed the transaction amount sum.")	# 금액 합계 변동 시 예외 발생
        if len(joined) != len(working):	# 조인 후 행 수 변동 여부 확인
            raise ValueError("Product join changed the transaction row count.")	# 행 수 변동 시 예외 발생
        self.join_summary = {	# 조인 검증 결과 요약 기록
            "rows_before": len(working), "rows_after": len(joined),	# 조인 전후 행 수 기록
            "amount_before": before, "amount_after": after,	# 조인 전후 금액 합계 기록
            "matched_rows": int(matched.sum()), "unmatched_rows": int((~matched).sum()),	# 매칭·미매칭 거래 행 수 기록
            "excluded_empty_product_keys": missing_keys,	# 제외된 빈 상품 키 수 기록
        }
        self.df, self.products, self.product_key = joined, products, key	# 검증 통과 후 인스턴스 상태 일괄 갱신
        return self.df	# 조인된 거래 DataFrame 반환

    def validate_transactions(self, customer_col="customer_id", date_col="t_dat", amount_col="price", **settings):
        """유효 거래로 self.df를 교체하고 제외 사유를 transaction_audit에 기록한다."""
        if self.df is None:	# 데이터 로드 여부 확인
            raise ValueError("Data is not loaded. Call load_data() first.")	# 미로드 시 예외 발생
        valid, audit = clean_transactions(self.df, customer_col, date_col, amount_col, **settings)	# 공용 정제 함수로 유효 거래·감사 로그 산출
        self.df, self.transaction_audit = valid, audit	# 정제된 DataFrame과 감사 기록 저장
        return self.df	# 정제된 거래 DataFrame 반환

    def handle_missing_values(self, strategy="group_mean", group_col=None, *, columns=None, eligible=None):
        """지정한 수치 피처의 결측만 처리하고 대치 집계를 missing_audit에 남긴다.

        eligible=False인 행과 기존 관측값을 보존한다. 실패하면 self.df를 바꾸지
        않는다. 그룹 평균이 없을 때 대치 전 전체 관측값의 평균을 사용한다.
        """
        if self.df is None:	# 데이터 로드 여부 확인
            raise ValueError("Data is not loaded. Call load_data() first.")	# 미로드 시 예외 발생
        result, audit = impute_features(self.df, strategy, group_col, columns, eligible)	# 공용 결측 대치 함수 호출
        self.df, self.missing_audit = result, audit	# 대치된 DataFrame과 감사 로그 저장
        return self.df	# 대치 완료된 DataFrame 반환

    def handle_missing(self, strategy="group_mean", group_col=None, *, columns=None, eligible=None):
        """피처 대치를 위임해 self.df·missing_audit를 갱신하고 대치 표를 반환한다."""
        return self.handle_missing_values(strategy, group_col, columns=columns, eligible=eligible)	# 호환 별칭 메서드 위임 호출

    def detect_outliers(self, column, threshold=1.5):
        """원본을 바꾸지 않고 IQR 경계 밖 마스크를 반환하고 경계를 기록한다."""
        if self.df is None:	# 데이터 로드 여부 확인
            raise ValueError("Data is not loaded. Call load_data() first.")	# 미로드 시 예외 발생
        if column not in self.df:	# 대상 수치 열 존재 확인
            raise ValueError(f"Column '{column}' not found in data.")	# 열 누락 시 예외 발생
        lower, upper = iqr_limits(self.df[column], threshold)	# IQR 기반 하한·상한 경계 계산
        mask = (self.df[column] < lower) | (self.df[column] > upper)	# 경계 밖 이상치 불리언 마스크 생성
        self.outlier_audit[column] = {"lower": lower, "upper": upper, "count": int(mask.sum()), "threshold": threshold}	# 열별 이상치 경계·건수 기록
        return mask	# 이상치 마스크 반환

    def clip_outliers(self, column, threshold=1.5):
        """EDA용 보정 Series를 반환한다. self.df의 원본 금액은 보존한다."""
        self.detect_outliers(column, threshold)	# 경계 계산 및 outlier_audit 갱신
        limits = self.outlier_audit[column]	# 계산된 하한·상한 조회
        return self.df[column].clip(limits["lower"], limits["upper"])	# 원본을 변경하지 않고 경계로 clip한 사본 Series 반환

    def calculate_rfm(self, customer_col, date_col, amount_col, *, reference_date=None,
                      frequency_unit="purchase_day", order_col=None, split_inactive=False):
        """원본 거래를 보존하며 고객별 RFM 표와 계산 기준 rfm_audit를 만든다.

        기준일 구매의 Recency는 0, 기본 Frequency는 고유 구매일 수다.
        같은 값은 평균 순위로 같은 점수를 받는다. 그룹 규칙은 통합 계획 C5다.
        """
        if self.df is None:	# 데이터 로드 여부 확인
            raise ValueError("Data is not loaded. Call load_data() first.")	# 미로드 시 예외 발생
        result, audit = calculate_customer_rfm(self.df, customer_col, date_col, amount_col,	# 공용 RFM 계산 함수 호출
            reference_date=reference_date, frequency_unit=frequency_unit,	# 기준일 및 빈도 단위 전달
            order_col=order_col, split_inactive=split_inactive)	# 주문 열 및 비활성 분리 옵션 전달
        self.rfm_audit = audit	# RFM 계산 기준 감사 로그 저장
        return result	# 고객별 RFM DataFrame 반환

    def summarize(self, columns=None):
        """수치 열의 건수·평균·중앙값·표준편차·사분위수 표를 반환한다."""
        if self.df is None:	# 데이터 로드 여부 확인
            raise ValueError("Data is not loaded. Call load_data() first.")	# 미로드 시 예외 발생
        frame = self.df[columns] if columns is not None else self.df.select_dtypes(include="number")	# 지정 열 또는 전체 수치 열 선택
        return frame.describe().T.rename(columns={"25%": "Q1", "50%": "median", "75%": "Q3"})	# 전치된 기술통계 표의 사분위 열 이름 정리

    @staticmethod
    def profile_segments(rfm):
        """고객 단위 표를 받아 세그먼트별 건수·중앙값·구매금액 비중을 반환한다."""
        return segment_profile(rfm)	# 공용 세그먼트 요약 함수 호출

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
        if self.df is None:	# 데이터 로드 여부 확인
            raise ValueError("Data is not loaded. Call load_data() first.")	# 미로드 시 예외 발생
        if image_dir is not None:	# 디스크 이미지 폴더 경로가 주어진 경우
            return self._extract_image_files(Path(image_dir), image_column, image_size, batch_size,	# 상품별 배치 이미지 피처 추출 경로로 분기
                                             advanced, histogram_bins)	# 고급 피처 옵션 및 히스토그램 구간 수 전달
        if advanced:	# 인메모리 배열 경로에서 고급 피처 요청 시
            raise ValueError("Advanced image features require image_dir.")	# image_dir 필수 안내 예외 발생
        if image_column not in self.df.columns:	# 인메모리 이미지 열 존재 여부 확인
            raise ValueError(f"Column '{image_column}' not found in data.")	# 열 누락 시 예외 발생

        image_data = np.asarray(self.df[image_column].tolist(), dtype=float)	# 배열 열을 NumPy 실수 다차원 배열로 변환
        if image_data.ndim < 2:	# 최소 2차원(배치+픽셀) 이상인지 검증
            raise ValueError("image_column must contain same-shaped array-like values.")	# 동일 형태 배열 요건 위반 예외

        reduce_axes = tuple(range(1, image_data.ndim))	# 첫 번째 배치 축(0)을 제외한 축 목록 생성
        self.df[f"{image_column}_mean"] = image_data.mean(axis=reduce_axes)	# 이미지별 픽셀 평균 계산 및 열 추가
        self.df[f"{image_column}_std"] = image_data.std(axis=reduce_axes)	# 이미지별 픽셀 표준편차(ddof=0) 계산 및 열 추가

        return self.df	# 이미지 피처가 추가된 DataFrame 반환

    def _extract_image_files(self, directory, prefix, image_size, batch_size, advanced=False, histogram_bins=8):
        """재사용 도구의 상품 피처를 거래에 매핑하고 배치 진단을 기록한다."""
        if self.products is None:	# 상품 조인 선행 여부 확인
            raise ValueError("Call join_products() before extracting image files.")	# 미조인 시 예외 발생
        features, batch_info = extract_product_image_features(	# 공용 도구로 고유 상품별 이미지 피처 배치 계산
            self.products, self.product_key, directory, prefix, image_size, batch_size,	# 상품 표·키·폴더·크기·배치 상한 전달
            advanced, histogram_bins)	# 고급 피처 및 히스토그램 구간 수 전달
        keys = self.products[self.product_key]	# 상품 표의 조인 키 Series 참조
        # 거래별 이미지 배열 대신 상품별로 계산한 작은 피처만 연결한다.
        for column in features:	# 계산된 각 이미지 피처 열 순회
            self.df[column] = self.df[self.product_key].map(features[column])	# 상품 키 기준으로 거래 표에 피처 매핑
            self.products[column] = keys.map(features[column])	# 상품 표에도 동일 피처 매핑
        self.df[f"{prefix}_status"] = self.df[f"{prefix}_status"].fillna("unmatched_product")	# 상품 미매칭 거래의 이미지 상태 보완
        self.image_batch_info = batch_info	# 최대 실제 배치 및 픽셀 버퍼 진단 정보 기록
        return self.df	# 이미지 피처가 연결된 거래 DataFrame 반환

    def extract_text_features(self, text_column: str) -> pd.DataFrame:
        """원문은 보존하고 문자 수·공백 기준 단어 수를 self.df에 추가한다.

        상품 조인이 있으면 상품별 한 번 계산해 거래에 매핑한다. 결측 상품명은
        계산할 때만 빈 문자열로 취급한다. 미매칭 거래의 피처는 결측으로 둔다.
        """
        if self.df is None:	# 데이터 로드 여부 확인
            raise ValueError("Data is not loaded. Call load_data() first.")	# 미로드 시 예외 발생
        if text_column not in self.df.columns:	# 대상 텍스트 열 존재 여부 확인
            raise ValueError(f"Column '{text_column}' not found in data.")	# 열 누락 시 예외 발생

        source = self.products if self.products is not None and text_column in self.products else self.df	# 상품 조인 시 상품 표 기준으로 중복 계산 방지
        text_series = source[text_column].fillna("").astype(str)	# 원문 보존한 채 결측만 빈 문자열로 변환
        for suffix, values in (("length", text_series.str.len()),	# 문자열 길이 계산 쌍
                               ("word_count", text_series.str.split().str.len())):	# 공백 기준 단어 수 계산 쌍
            column = f"{text_column}_{suffix}"	# 파생 피처 열 이름 생성
            if source is self.products:	# 상품 표에서 계산한 경우
                self.products[column] = values	# 상품 표에 텍스트 피처 저장
                self.df[column] = self.df[self.product_key].map(self.products.set_index(self.product_key)[column])	# 상품 키 기준으로 거래 표에 매핑
            else:	# 거래 표에서 직접 계산한 경우
                self.df[column] = values	# 거래 표에 바로 열 추가

        return self.df	# 텍스트 피처가 추가된 DataFrame 반환


def main() -> None:
    """CSV 로드와 선택적인 상품 조인을 명령줄에서 확인한다."""
    parser = argparse.ArgumentParser(description="Run e-commerce data analysis pipeline.")	# CLI 인자 파서 생성
    parser.add_argument("--data", required=True, help="Path to CSV data file")	# 필수 거래 CSV 경로 인자 등록
    parser.add_argument("--products", help="Optional product CSV, joined on article_id")	# 선택적 상품 CSV 경로 인자 등록
    args = parser.parse_args()	# 명령줄 인자 파싱

    analyzer = DataAnalyzer(args.data)	# 입력 경로로 분석기 인스턴스 생성
    df = analyzer.load_data()	# 거래 CSV 로드 실행
    if args.products:	# 상품 CSV 경로가 함께 전달된 경우
        df = analyzer.join_products(args.products)	# 상품 조인 실행
        print(f"Join audit: {analyzer.join_summary}")	# 조인 검증 요약 출력
    print(f"Loaded dataset shape: {df.shape}")	# 로드된 데이터셋 행·열 크기 출력


if __name__ == "__main__":	# 스크립트로 직접 실행될 때만 진입
    main()	# CLI 진입점 함수 호출
