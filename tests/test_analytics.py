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
        analyzer = self.analyzer(pd.DataFrame({"category": ["A", "A", "A", None, None, "B"],
                                               "feature": [10, 30, np.nan, 50, np.nan, np.nan],
                                               "price": [1, 2, 3, 4, 5, 6]}))
        analyzer.handle_missing_values(group_col="category", columns=["feature"],
                                        eligible=[True, True, True, True, True, False])
        np.testing.assert_allclose(analyzer.df.feature.iloc[:5], [10, 30, 20, 50, 30])
        self.assertTrue(pd.isna(analyzer.df.feature.iloc[5]))
        self.assertEqual(analyzer.df.price.tolist(), [1, 2, 3, 4, 5, 6])
        self.assertEqual(analyzer.missing_audit["feature"]["group_filled"], 1)
        self.assertEqual(analyzer.missing_audit["feature"]["global_filled"], 1)

    def test_all_missing_feature_stays_missing(self):
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
        analyzer = self.analyzer(pd.DataFrame({"price": [1, 2, 3, 4, 100]}))
        self.assertEqual(analyzer.detect_outliers("price").tolist(), [False] * 4 + [True])
        self.assertEqual((analyzer.outlier_audit["price"]["lower"], analyzer.outlier_audit["price"]["upper"]), (-1, 7))
        self.assertEqual(analyzer.clip_outliers("price").tolist(), [1, 2, 3, 4, 7])
        self.assertEqual(analyzer.df.price.sum(), 110)
        analyzer.df.price = [-2, 1, 2, 3, 6]
        self.assertFalse(analyzer.detect_outliers("price").any())
        with self.assertRaisesRegex(ValueError, "threshold"):
            analyzer.detect_outliers("price", -1)

    def test_rfm_hand_calculation_and_reference_date(self):
        frame = pd.DataFrame({"customer_id": ["A", "A", "A", "B"],
                              "t_dat": ["2020-01-01", "2020-01-01", "2020-01-03", "2020-01-02"],
                              "price": [10, 20, 30, 5]})
        analyzer = self.analyzer(frame)
        result = analyzer.calculate_rfm("customer_id", "t_dat", "price", reference_date="2020-01-03").set_index("customer_id")
        self.assertEqual(result.loc["A", ["Recency", "Frequency", "Monetary"]].tolist(), [0, 2, 60])
        self.assertEqual(result.loc["B", ["Recency", "Frequency", "Monetary"]].tolist(), [1, 1, 5])
        self.assertEqual(result.Monetary.sum(), 65)
        pd.testing.assert_frame_equal(analyzer.df, frame)
        profile = analyzer.profile_segments(result.reset_index())
        self.assertEqual(profile.Customers.sum(), 2)
        self.assertEqual(profile.Monetary_total.sum(), 65)
        with self.assertRaisesRegex(ValueError, "reference_date"):
            analyzer.calculate_rfm("customer_id", "t_dat", "price", reference_date="2020-01-02")

    def test_ties_and_order_independence(self):
        frame = pd.DataFrame({"customer_id": list("ABCD"), "t_dat": ["2020-01-01"] * 4, "price": [10] * 4})
        analyzer = self.analyzer(frame)
        expected = analyzer.calculate_rfm("customer_id", "t_dat", "price")
        self.assertTrue((expected[["R_Score", "F_Score", "M_Score"]].nunique() == 1).all())
        analyzer.df = frame.sample(frac=1, random_state=42)
        pd.testing.assert_frame_equal(expected, analyzer.calculate_rfm("customer_id", "t_dat", "price"))

    def test_order_mode_and_invalid_input(self):
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
    unittest.main()
