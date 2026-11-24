"""월 누락·상수 열 등 보고서 계산의 경계 조건을 검증한다."""
import unittest
import numpy as np
import pandas as pd
from utils.reporting import monthly_amount, pair_correlation


class ReportingTests(unittest.TestCase):
    """보고서의 합계 보존과 유효 상관 표본 기준을 확인한다."""

    def test_monthly_totals_include_zero_month(self):
        """가상 월별 거래로 누락 월의 0 보충과 완전한 월 범위 검증을 확인한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        frame = pd.DataFrame({"date": pd.to_datetime(["2020-01-03", "2020-03-01"]), "amount": [10, 20]})
        monthly = monthly_amount(frame, "date", "amount", "2020-01-01", "2020-04-01")
        self.assertEqual(monthly.tolist(), [10, 0, 20])	# 거래 없는 2월도 누락하지 않고 관측값 0으로 표시한다.
        self.assertEqual(monthly.index.tolist(), ["2020-01", "2020-02", "2020-03"])
        with self.assertRaisesRegex(ValueError, "complete months"):
            monthly_amount(frame, "date", "amount", "2020-01-02", "2020-04-01")
        with self.assertRaisesRegex(ValueError, "outside"):
            monthly_amount(frame, "date", "amount", "2020-01-01", "2020-03-01")

    def test_correlation_uses_finite_pairs_and_rejects_constant(self):
        """가상 열로 유한 쌍만의 상관 계산과 상수 열의 미정의 처리를 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        frame = pd.DataFrame({"x": [1, 2, np.inf, np.nan], "y": [2, 4, 5, 6]})
        result = pair_correlation(frame, "x", "y")
        self.assertEqual(result["n"], 2)	# 무한대·결측이 없는 두 쌍만 유효 관측 수에 포함한다.
        self.assertAlmostEqual(result["pearson"], 1)
        frame["x"] = 1
        self.assertTrue(np.isnan(pair_correlation(frame, "x", "y")["pearson"]))	# 상수 열의 상관을 임의의 0으로 해석하지 않는다.


if __name__ == "__main__":
    unittest.main()	# 파일을 직접 실행했을 때 이 모듈의 회귀 검사를 수행한다.
