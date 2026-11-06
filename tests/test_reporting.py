"""월 누락·상수 열 등 보고서 계산의 경계 조건을 검증한다."""
import unittest
import numpy as np
import pandas as pd
from utils.reporting import monthly_amount, pair_correlation


class ReportingTests(unittest.TestCase):
    """보고서의 합계 보존과 유효 상관 표본 기준을 확인한다."""

    def test_monthly_totals_include_zero_month(self):
        frame = pd.DataFrame({"date": pd.to_datetime(["2020-01-03", "2020-03-01"]), "amount": [10, 20]})
        monthly = monthly_amount(frame, "date", "amount", "2020-01-01", "2020-04-01")
        self.assertEqual(monthly.tolist(), [10, 0, 20])
        self.assertEqual(monthly.index.tolist(), ["2020-01", "2020-02", "2020-03"])
        with self.assertRaisesRegex(ValueError, "complete months"):
            monthly_amount(frame, "date", "amount", "2020-01-02", "2020-04-01")
        with self.assertRaisesRegex(ValueError, "outside"):
            monthly_amount(frame, "date", "amount", "2020-01-01", "2020-03-01")

    def test_correlation_uses_finite_pairs_and_rejects_constant(self):
        frame = pd.DataFrame({"x": [1, 2, np.inf, np.nan], "y": [2, 4, 5, 6]})
        result = pair_correlation(frame, "x", "y")
        self.assertEqual(result["n"], 2)
        self.assertAlmostEqual(result["pearson"], 1)
        frame["x"] = 1
        self.assertTrue(np.isnan(pair_correlation(frame, "x", "y")["pearson"]))


if __name__ == "__main__":
    unittest.main()
