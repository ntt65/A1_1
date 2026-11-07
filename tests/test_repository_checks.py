"""인용된 Markdown과 실제 제출 링크를 구분하는지 검증한다."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from utils.repository_checks import check_local_links


class RepositoryLinkTests(unittest.TestCase):
    """문서 링크 검사에 필요한 최소 파일을 임시로 만든다."""

    def test_quoted_markdown_is_ignored_but_real_links_are_checked(self):
        """인라인과 코드 블록 속 예제를 건너뛰고 실제 깨진 링크를 보고한다."""
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            report = root / "report.md"
            (root / "figure.png").touch()
            content = (
                "README: `![figure](docs/figure.png)`\n"
                "`` `[example](absent.md)` ``\n"
                "~~~~markdown\n![example](missing.png)\n~~~\n"
                "[still fenced](missing.md)\n~~~~\n"
                "```md\n[another example](missing.md)\n```\n"
                "![actual figure](figure.png)\n"
                "[figure source](figure.png?plain=1#L1)\n"
            )
            report.write_text(content, encoding="utf-8")
            check_local_links(report, root)
            report.write_text(content + "[broken](unavailable.md?plain=1#L1)\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"report\.md: unavailable\.md"):
                check_local_links(report, root)
