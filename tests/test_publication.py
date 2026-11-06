"""공개 보고서에서 원본 행·식별자 출력이 빠지는지 검증한다."""
import json
import unittest
from utils.publish_report import aggregate_snapshot, redact_notebook


class PublicationTests(unittest.TestCase):
    """집계 허용 목록과 원본 셀 제거를 작은 가상 출력으로 확인한다."""

    def test_snapshot_excludes_private_top_level_fields(self):
        public = aggregate_snapshot({"customers": 10, "customer_id": "a"*64, "records": [{"price": 1}]})
        self.assertEqual(public["customers"], 10)
        self.assertNotIn("customer_id", public)
        self.assertNotIn("records", public)
        with self.assertRaisesRegex(ValueError, "Private"):
            aggregate_snapshot({"profile": {"customer_id": "private"}})
        with self.assertRaisesRegex(ValueError, "Identifier"):
            aggregate_snapshot({"profile": {"a"*64: 10}})

    def test_raw_load_output_removed_and_safe_summary_kept(self):
        notebook = {"metadata": {}, "cells": [
            {"cell_type": "markdown", "source": ["## NB_LOAD"], "metadata": {}},
            {"cell_type": "code", "source": ["display(df.head())"], "outputs": [{"output_type": "stream", "text": "PRIVATE_ROW"}], "metadata": {}},
            {"cell_type": "markdown", "source": ["## NB_RFM"], "metadata": {}},
            {"cell_type": "code", "source": ["display(profile)"], "outputs": [{"output_type": "stream", "text": "GROUP_TOTAL"}], "metadata": {}}]}
        public = redact_notebook(notebook, [])
        text = json.dumps(public)
        self.assertNotIn("PRIVATE_ROW", text)
        self.assertIn("GROUP_TOTAL", text)
        self.assertIn("PRIVATE_ROW", json.dumps(notebook))  # 원본 실행본은 변경하지 않는다.


if __name__ == "__main__":
    unittest.main()
