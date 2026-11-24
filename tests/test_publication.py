"""제출 과정에서 원본 값과 실행 출력을 보존하는지 검증한다."""
import json
from pathlib import Path
import tempfile
import unittest
from utils.publish_report import aggregate_snapshot, preserve_execution


class PublicationTests(unittest.TestCase):
    """원본 기록 사본과 바이트 단위 실행본 보존을 확인한다."""

    def test_snapshot_preserves_original_fields(self):
        """가상 중첩 집계로 모든 원본 필드와 깊은 사본의 독립성을 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        source = {"customers": 10, "customer_id": "original-id", "records": [{"price": 1}]}
        result = aggregate_snapshot(source)
        self.assertEqual(result, source)
        result["records"][0]["price"] = 2
        self.assertEqual(source["records"][0]["price"], 1)	# 중첩된 사본을 수정해도 원본 가격은 바뀌지 않아야 한다.

    def test_execution_is_copied_without_masking(self):
        """임시 노트북으로 실행본의 바이트 보존과 오류 출력 거부를 검증한다. 반환값은 없고 임시 입력·검사 객체만 변경한다."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.ipynb"
            target = Path(directory) / "target.ipynb"
            notebook = {"cells": [{"cell_type": "code", "execution_count": 1,
                "outputs": [{"output_type": "stream", "name": "stdout", "text": "original customer and row"}]}]}
            source.write_text(json.dumps(notebook), encoding="utf8")
            preserve_execution(source, target)
            self.assertEqual(source.read_bytes(), target.read_bytes())	# 표·고객 ID·실행 결과를 포함한 원본 바이트를 그대로 보존한다.
            notebook["cells"][0]["outputs"] = [{"output_type": "error"}]	# 오류 실행본은 제출본으로 복사할 수 없는 실패 입력으로 만든다.
            source.write_text(json.dumps(notebook), encoding="utf8")
            with self.assertRaisesRegex(ValueError, "failed"):
                preserve_execution(source, target)


if __name__ == "__main__":
    unittest.main()	# 파일을 직접 실행했을 때 이 모듈의 회귀 검사를 수행한다.
