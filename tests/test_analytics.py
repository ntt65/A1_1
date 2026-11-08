"""정제·대치·IQR·RFM의 손계산 결과와 원본 보존을 검증한다."""

import unittest
import numpy as np
import pandas as pd
from src.pipeline import DataAnalyzer


class AnalyticsTests(unittest.TestCase):
    """원본 데이터 없이 계산 정책과 실패 조건을 재현한다."""

    def analyzer(self, frame):
        """파일 로드와 독립적으로 계산할 작은 분석 객체를 만든다."""
        analyzer = DataAnalyzer("fixture.csv")
        analyzer.df = frame.copy()
        return analyzer

    def test_cleaning_priority_scope_and_duplicate_purchases(self):
        """가상 거래로 제외 사유의 우선순위와 유효 반복 구매 보존을 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        analyzer = self.analyzer(pd.DataFrame({
            "customer_id": [None, "A", "A", "A", "A", "A", "A"],
            "t_dat": ["bad", "bad", "2020-01-01", "2020-01-02", "2020-01-02", "2020-01-03", "2020-01-04"],
            "price": [-1, -1, np.inf, 5, 5, 6, 7]}))
        result = analyzer.validate_transactions(start="2020-01-02", end="2020-01-04")
        self.assertEqual(result.price.tolist(), [5, 5, 6])
        audit = analyzer.transaction_audit
        self.assertEqual([audit[k] for k in ("missing_customer_rows", "invalid_date_rows", "invalid_amount_rows", "out_of_scope_rows")], [1, 1, 1, 1])
        self.assertEqual(audit["source_rows"], sum(audit[k] for k in ("missing_customer_rows", "invalid_date_rows", "invalid_order_rows", "invalid_amount_rows", "out_of_scope_rows", "output_rows")))

    def test_missing_group_fallback_and_observed_value_preservation(self):
        """가상 결측 피처로 그룹 평균·전체 평균 대치와 관측값 보존을 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        analyzer = self.analyzer(pd.DataFrame({"category": ["A", "A", "A", None, None, "B"],
                                               "feature": [10, 30, np.nan, 50, np.nan, np.nan],
                                               "price": [1, 2, 3, 4, 5, 6]}))
        analyzer.handle_missing_values(group_col="category", columns=["feature"],
                                        eligible=[True, True, True, True, True, False])
        np.testing.assert_allclose(analyzer.df.feature.iloc[:5], [10, 30, 20, 50, 30])	# 그룹 평균 20·전체 평균 30과 기존 관측값 50을 함께 대조한다.
        self.assertTrue(pd.isna(analyzer.df.feature.iloc[5]))	# 대치 대상에서 제외한 행은 결측을 그대로 유지한다.
        self.assertEqual(analyzer.df.price.tolist(), [1, 2, 3, 4, 5, 6])
        self.assertEqual(analyzer.missing_audit["feature"]["group_filled"], 1)
        self.assertEqual(analyzer.missing_audit["feature"]["global_filled"], 1)

    def test_all_missing_feature_stays_missing(self):
        """전부 결측인 가상 열을 대치하지 않고 잘못된 그룹 열을 거부하는지 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        analyzer = self.analyzer(pd.DataFrame({"category": ["A", "B"], "x": [np.nan, np.nan]}))
        analyzer.handle_missing_values(group_col="category", columns=["x"])
        self.assertTrue(analyzer.df.x.isna().all())
        with self.assertRaisesRegex(ValueError, "group_col"):
            analyzer.handle_missing_values(group_col="absent", columns=["x"])

    def test_naito_missing_alias_preserves_result_and_audit(self):
        """두 이름의 반환값과 집계를 대조하고 관측·제외 행의 보존을 확인한다."""
        frame = pd.DataFrame({"category": ["A", "A", "B"], "feature": [10.0, np.nan, np.nan],
                              "other": [1.0, np.nan, 3.0]})
        canonical, compatible = self.analyzer(frame), self.analyzer(frame)
        options = {"columns": ["feature"], "eligible": [True, True, False]}
        expected = canonical.handle_missing_values("group_mean", "category", **options)
        actual = compatible.handle_missing("group_mean", "category", **options)
        pd.testing.assert_frame_equal(actual, expected)
        self.assertIs(actual, compatible.df)
        pd.testing.assert_frame_equal(pd.DataFrame(compatible.missing_audit),
                                      pd.DataFrame(canonical.missing_audit))
        np.testing.assert_allclose(actual.feature, [10.0, 10.0, np.nan])
        pd.testing.assert_series_equal(actual.other, frame.other)

    def test_iqr_bounds_clip_copy_and_boundaries(self):
        """손계산 배열로 IQR 경계·사본 보정·경계값 포함·원금액 보존을 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        analyzer = self.analyzer(pd.DataFrame({"price": [1, 2, 3, 4, 100]}))
        self.assertEqual(analyzer.detect_outliers("price").tolist(), [False] * 4 + [True])
        self.assertEqual((analyzer.outlier_audit["price"]["lower"], analyzer.outlier_audit["price"]["upper"]), (-1, 7))
        self.assertEqual(analyzer.clip_outliers("price").tolist(), [1, 2, 3, 4, 7])
        self.assertEqual(analyzer.df.price.sum(), 110)	# 보정 사본을 만들더라도 RFM에 사용할 원금액 합은 유지한다.
        analyzer.df.price = [-2, 1, 2, 3, 6]
        self.assertFalse(analyzer.detect_outliers("price").any())
        with self.assertRaisesRegex(ValueError, "threshold"):
            analyzer.detect_outliers("price", -1)

    def test_rfm_hand_calculation_and_reference_date(self):
        """가상 고객 두 명의 RFM 손계산·합계 보존·유효 기준일을 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        frame = pd.DataFrame({"customer_id": ["A", "A", "A", "B"],
                              "t_dat": ["2020-01-01", "2020-01-01", "2020-01-03", "2020-01-02"],
                              "price": [10, 20, 30, 5]})
        analyzer = self.analyzer(frame)
        result = analyzer.calculate_rfm("customer_id", "t_dat", "price", reference_date="2020-01-03").set_index("customer_id")
        self.assertEqual(result.loc["A", ["Recency", "Frequency", "Monetary"]].tolist(), [0, 2, 60])
        self.assertEqual(result.loc["B", ["Recency", "Frequency", "Monetary"]].tolist(), [1, 1, 5])
        self.assertEqual(result.Monetary.sum(), 65)	# 상품 행을 고객 단위로 합쳐도 전체 금액은 동일해야 한다.
        pd.testing.assert_frame_equal(analyzer.df, frame)
        profile = analyzer.profile_segments(result.reset_index())
        self.assertEqual(profile.Customers.sum(), 2)
        self.assertEqual(profile.Monetary_total.sum(), 65)
        with self.assertRaisesRegex(ValueError, "reference_date"):
            analyzer.calculate_rfm("customer_id", "t_dat", "price", reference_date="2020-01-02")

    def test_ties_and_order_independence(self):
        """동일 행동값을 가진 가상 고객의 점수가 입력 순서에 독립적인지 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        frame = pd.DataFrame({"customer_id": list("ABCD"), "t_dat": ["2020-01-01"] * 4, "price": [10] * 4})
        analyzer = self.analyzer(frame)
        expected = analyzer.calculate_rfm("customer_id", "t_dat", "price")
        self.assertTrue((expected[["R_Score", "F_Score", "M_Score"]].nunique() == 1).all())
        analyzer.df = frame.sample(frac=1, random_state=42)	# 시드를 고정한 순서 교란으로 동점 처리의 입력 순서 의존을 탐지한다.
        pd.testing.assert_frame_equal(expected, analyzer.calculate_rfm("customer_id", "t_dat", "price"))

    def test_order_mode_and_invalid_input(self):
        """가상 주문으로 주문 수 집계·취소 제외·미정제 입력 거부를 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        analyzer = self.analyzer(pd.DataFrame({"customer_id": ["A"] * 5, "t_dat": ["2020-01-01"] * 5,
                                               "price": [1, 2, 3, -4, 5], "order": ["001", "001", "002", "C003", None]}))
        analyzer.validate_transactions(frequency_unit="order", order_col="order")
        rfm = analyzer.calculate_rfm("customer_id", "t_dat", "price", frequency_unit="order", order_col="order")
        self.assertEqual(rfm.Frequency.iloc[0], 2)
        self.assertEqual(rfm.Monetary.iloc[0], 6)
        self.assertEqual(analyzer.transaction_audit["invalid_order_rows"], 2)
        analyzer.df.loc[0, "price"] = 0
        with self.assertRaisesRegex(ValueError, "validate_transactions"):
            analyzer.calculate_rfm("customer_id", "t_dat", "price")


if __name__ == "__main__":
    unittest.main()	# 파일을 직접 실행했을 때 이 모듈의 회귀 검사를 수행한다.
