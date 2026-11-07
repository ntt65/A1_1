"""B1~B4의 조인 불변 조건과 알려진 피처 값을 작은 가상 입력으로 검증한다."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.pipeline import DataAnalyzer


class PipelineTests(unittest.TestCase):
    """실제 H&M 데이터 없이 로드·상품 매핑·이미지 실패 경로를 확인한다."""

    def setUp(self):
        """테스트마다 독립된 입력 폴더를 만들어 기존 데이터를 보호한다."""
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def csv(self, name, rows):
        """가상 행을 CSV로 저장하고 경로를 반환한다."""
        path = self.root / name
        pd.DataFrame(rows).to_csv(path, index=False)
        return path

    def test_load_ids_dates_and_failed_reload(self):
        analyzer = DataAnalyzer(self.csv("tx.csv", {
            "article_id": ["00123", "  "], "customer_id": ["0001", "0002"],
            "t_dat": ["2020-06-01", "bad"], "price": [1.0, 2.0]}))
        loaded = analyzer.load_data(required_columns=["price"], date_columns=["t_dat"])
        self.assertEqual(loaded.article_id.iloc[0], "00123")
        self.assertTrue(pd.isna(loaded.article_id.iloc[1]))
        self.assertTrue(pd.isna(loaded.t_dat.iloc[1]))
        with self.assertRaisesRegex(ValueError, "missing_column"):
            analyzer.load_data(required_columns=["missing_column"])
        self.assertIs(analyzer.df, loaded)
        analyzer.data_path = self.csv("empty.csv", {"price": []})
        with self.assertRaisesRegex(ValueError, "Empty CSV"):
            analyzer.load_data()

    def test_join_preserves_rows_order_sum_and_rejects_duplicates(self):
        analyzer = DataAnalyzer(self.csv("tx.csv", {
            "article_id": ["00123", "00999", "00123", None], "price": [2, 3, 4, 5]}))
        analyzer.load_data()
        analyzer.df.index = [5, 2, 8, 1]
        joined = analyzer.join_products(self.csv("products.csv", {
            "article_id": ["00123", None], "prod_name": ["Blue cotton shirt", "unused"]}))
        self.assertEqual(joined.index.tolist(), [5, 2, 8, 1])
        self.assertEqual(joined.price.tolist(), [2, 3, 4, 5])
        self.assertEqual(analyzer.join_summary["unmatched_rows"], 2)
        self.assertEqual(analyzer.join_summary["amount_after"], 14)
        self.assertEqual(analyzer.join_summary["excluded_empty_product_keys"], 1)
        duplicate = self.csv("duplicate.csv", {"article_id": ["00123", "00123"]})
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            analyzer.join_products(duplicate)
        self.assertIs(analyzer.df, joined)
        with self.assertRaisesRegex(ValueError, "already exist"):
            analyzer.join_products(self.root / "products.csv")
        analyzer.extract_text_features("prod_name")
        self.assertEqual(joined.prod_name_length.iloc[0], 17)
        self.assertEqual(joined.prod_name_word_count.iloc[2], 3)
        self.assertTrue(pd.isna(joined.prod_name_length.iloc[1]))
        self.assertEqual(analyzer.products.prod_name.iloc[0], "Blue cotton shirt")

    def test_array_features_and_missing_text_keep_existing_api(self):
        analyzer = DataAnalyzer("unused.csv")
        analyzer.df = pd.DataFrame({"pixels": [np.array([[0, 0], [1, 1]])], "name": [None]})
        original = analyzer.df
        analyzer.extract_image_features("pixels")
        analyzer.extract_text_features("name")
        self.assertIs(analyzer.df, original)
        self.assertEqual(original.pixels_mean.iloc[0], .5)
        self.assertEqual(original.pixels_std.iloc[0], .5)
        self.assertEqual(original.name_word_count.iloc[0], 0)
        self.assertTrue(pd.isna(original.name.iloc[0]))

    def test_file_statuses_batching_and_color_normalization(self):
        identifiers = [f"001{i:03}" for i in range(9)]
        analyzer = DataAnalyzer(self.csv("tx.csv", {
            "article_id": identifiers + [identifiers[0], "999999"], "price": [1] * 11}))
        analyzer.load_data()
        analyzer.join_products(self.csv("products.csv", {
            "article_id": identifiers, "source_image_available": [True] * 7 + [False, True],
            "image_sampled": [True] * 8 + [False]}))
        images = self.root / "images"
        (images / "001").mkdir(parents=True)
        for identifier in identifiers[:6]:
            (images / "001" / f"{identifier}.jpg").touch()
        half = np.zeros((32, 32), dtype=np.uint8)
        half[16:] = 255
        rgb = np.repeat(half[..., None], 3, axis=2)
        rgba = np.concatenate([rgb, np.zeros((32, 32, 1), dtype=np.uint8)], axis=2)
        pixels = [half, rgb, rgba, half[..., None], np.zeros((8, 8)), ValueError("broken")]
        calls = []

        def read(path):
            """파일명에 대응하는 픽셀 또는 디코딩 실패를 반환한다."""
            calls.append(path.stem)
            result = pixels[int(path.stem[-3:])]
            if isinstance(result, Exception):
                raise result
            return result

        with patch("matplotlib.image.imread", side_effect=read):
            analyzer.extract_image_features(image_dir=images, batch_size=2)
        self.assertEqual(len(calls), 6)  # 반복 거래도 상품 이미지를 다시 읽지 않는다.
        expected = ["ok"] * 4 + ["too_small", "corrupt", "missing", "missing", "not_sampled"]
        self.assertEqual(analyzer.products.image_status.tolist(), expected)
        self.assertEqual(analyzer.df.image_status.iloc[-1], "unmatched_product")
        np.testing.assert_allclose(analyzer.products.image_mean.iloc[:4], .5)
        np.testing.assert_allclose(analyzer.products.image_std.iloc[:4], .5)
        self.assertTrue(analyzer.products.image_mean.iloc[4:].isna().all())
        self.assertEqual(analyzer.image_batch_info["shape"], (2, 32, 32, 3))
        first = analyzer.df[["image_mean", "image_std"]].copy()
        with patch("matplotlib.image.imread", side_effect=read):
            analyzer.extract_image_features(image_dir=images, batch_size=3, advanced=True)
        pd.testing.assert_frame_equal(first, analyzer.df[["image_mean", "image_std"]])
        histogram = analyzer.products.filter(regex=r"^image_hist_")
        np.testing.assert_allclose(histogram.iloc[:4].sum(axis=1), 1)
        self.assertTrue(histogram.iloc[4:].isna().all().all())
        self.assertEqual(analyzer.df.image_hist_0.iloc[0], analyzer.df.image_hist_0.iloc[-2])
        self.assertTrue(analyzer.df.columns.is_unique)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            analyzer.extract_image_features(image_dir=images, batch_size=0)
        with self.assertRaisesRegex(ValueError, "directory not found"):
            analyzer.extract_image_features(image_dir=images / "absent")


if __name__ == "__main__":
    unittest.main()
