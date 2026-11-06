"""제출 과정에서 원본 값과 실행 출력을 보존하는지 검증한다."""
import json
from pathlib import Path
import tempfile
import unittest
from utils.publish_report import aggregate_snapshot, preserve_execution


class PublicationTests(unittest.TestCase):
    """원본 기록 사본과 바이트 단위 실행본 보존을 확인한다."""

    def test_snapshot_preserves_original_fields(self):
        source = {"customers": 10, "customer_id": "original-id", "records": [{"price": 1}]}
        result = aggregate_snapshot(source)
        self.assertEqual(result, source)
        result["records"][0]["price"] = 2
        self.assertEqual(source["records"][0]["price"], 1)

    def test_execution_is_copied_without_masking(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.ipynb"
            target = Path(directory) / "target.ipynb"
            notebook = {"cells": [{"cell_type": "code", "execution_count": 1,
                "outputs": [{"output_type": "stream", "name": "stdout", "text": "original customer and row"}]}]}
            source.write_text(json.dumps(notebook), encoding="utf8")
            preserve_execution(source, target)
            self.assertEqual(source.read_bytes(), target.read_bytes())
            notebook["cells"][0]["outputs"] = [{"output_type": "error"}]
            source.write_text(json.dumps(notebook), encoding="utf8")
            with self.assertRaisesRegex(ValueError, "failed"):
                preserve_execution(source, target)


if __name__ == "__main__":
    unittest.main()
