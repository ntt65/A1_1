"""이미지 기대값·코호트 분모/미관측·인터랙티브 원본 관측 보존을 검증한다."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from utils.bonus import cohort_retention, interactive_rfm
from utils.image_features import advanced_image_statistics


class BonusTests(unittest.TestCase):
    """원본 데이터 없이 보너스의 계산 정의와 실패 경계를 확인한다."""

    def test_histogram_edges_known_images(self):
        checker = np.array([[0, 1], [1, 0]], dtype=np.float32)
        gray = np.stack([np.zeros((2, 2)), np.ones((2, 2)), checker])
        rgb = np.repeat(gray[..., None], 3, axis=3)
        histogram, edge = advanced_image_statistics(rgb)
        np.testing.assert_allclose(histogram.sum(axis=1), 1)
        np.testing.assert_allclose(histogram[:, 0], [1, 0, .5])
        np.testing.assert_allclose(histogram[:, -1], [0, 1, .5])
        np.testing.assert_allclose(edge, [0, 0, 1])
        np.testing.assert_allclose(advanced_image_statistics(np.ones((1, 1, 1, 3)))[1], 0)

    def test_histogram_rejects_invalid_pixels_and_bins(self):
        for batch in [np.ones((2, 2)), np.full((1, 2, 2, 3), np.nan), np.full((1, 2, 2, 3), 2)]:
            with self.assertRaises(ValueError):
                advanced_image_statistics(batch)
        for bins in [0, True, 2.5]:
            with self.assertRaises(ValueError):
                advanced_image_statistics(np.zeros((1, 2, 2, 3)), bins)

    def test_cohort_denominators_zero_and_future_nan(self):
        frame = pd.DataFrame({"customer": ["A", "A", "A", "B", "B", "C"],
            "date": ["2020-06-01", "2020-06-01", "2020-08-01", "2020-06-02", "2020-07-01", "2020-07-02"]})
        before = frame.copy(deep=True)
        counts, retention, sizes = cohort_retention(frame, "customer", "date", "2020-06-01", "2020-09-01")
        self.assertEqual(sizes.tolist(), [2, 1])
        np.testing.assert_allclose(counts.loc["2020-06"], [2, 1, 1])
        np.testing.assert_allclose(retention.loc["2020-06"], [1, .5, .5])
        self.assertEqual(retention.loc["2020-07", 1], 0)
        self.assertTrue(np.isnan(retention.loc["2020-07", 2]))
        pd.testing.assert_frame_equal(before, frame)

    def test_cohort_rejects_incomplete_or_invalid_scope(self):
        frame = pd.DataFrame({"customer": ["A"], "date": ["2020-06-01"]})
        for start, end in [("2020-06-02", "2020-09-01"), ("2020-07-01", "2020-09-01")]:
            with self.assertRaises(ValueError):
                cohort_retention(frame, "customer", "date", start, end)
        frame.loc[0, "date"] = "bad"
        with self.assertRaises(ValueError):
            cohort_retention(frame, "customer", "date", "2020-06-01", "2020-09-01")

    @unittest.skipUnless(importlib.util.find_spec("plotly"), "Install requirements-bonus.txt for the Plotly check")
    def test_plotly_preserves_points_ids_and_embeds_runtime(self):
        frame = pd.DataFrame({"customer_id": ["alpha", "beta"], "Recency": [0, 2],
            "Frequency": [2, 1], "Monetary": [60, 5], "Segment": ["VIP", "New"]})
        before = frame.copy(deep=True)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "rfm.html"
            figure = interactive_rfm(frame, path)
            self.assertEqual(sum(len(trace.x) for trace in figure.data), 2)
            self.assertEqual({name for trace in figure.data for name in trace.hovertext}, {"alpha", "beta"})
            html = path.read_text(encoding="utf-8")
            self.assertIn("alpha", html)
            self.assertNotIn('<script src="https://cdn.plot.ly', html)
        pd.testing.assert_frame_equal(before, frame)


if __name__ == "__main__":
    unittest.main()
