"""제출 파일·문서 링크·노트북 출력·공개 데이터 제외를 점검한다."""

import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def check_repository():
    """공개 산출물의 기본 조건을 확인하고 실패하면 원인을 예외로 알린다.

    링크는 저장소 안의 상대 파일을 확인한다. 허용 분석 라이브러리 점검은
    실제 계산 모듈에 적용하고 노트북 실행 도구의 의존성과 구분한다.
    """
    for name in ("src/pipeline.py", "notebooks/analysis_report.ipynb", "README.md"):
        if not (ROOT / name).is_file():
            raise ValueError(f"Missing submission file: {name}")
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    if any(name.startswith(("data/", ".venv/")) for name in tracked):
        raise ValueError("Local data/environment is tracked by Git.")
    for name in ["README.md", "index.md", "reverse_index.md", *[str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "docs").rglob("*.md")]]:
        path = ROOT / name
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if link.startswith(("http:", "https:", "#", "mailto:")):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            target.relative_to(ROOT)
            if not target.exists():
                raise ValueError(f"Broken local link in {name}: {link}")
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for cell in notebook["cells"]:
            if cell.get("outputs") or cell.get("execution_count") is not None:
                raise ValueError(f"Public notebook contains outputs: {path.name}")
    public_path = ROOT / "docs/results/analysis_report.md"
    if public_path.exists():
        public_text = public_path.read_text(encoding="utf-8")
        if re.search(r"\b[0-9a-f]{64}\b", public_text, re.I):
            raise ValueError("Potential identifier in public aggregate report.")
        if len(list((ROOT / "docs/results/figures").glob("*.png"))) != 6:
            raise ValueError("Expected six reviewed aggregate figures.")
        aggregate = json.loads((ROOT / "docs/results/analysis_aggregates.json").read_text(encoding="utf-8"))
        if aggregate["publication_policy"]["original_rows"] or aggregate["publication_policy"]["customer_product_ids"]:
            raise ValueError("Public aggregate policy includes original data.")
    forbidden = {"cv2", "PIL", "sklearn", "nltk", "ydata_profiling", "pandas_profiling", "sweetviz"}
    for name in ("src/pipeline.py", "utils/analytics.py", "utils/image_features.py", "utils/reporting.py"):
        tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
            if any(module.split(".")[0] in forbidden for module in modules):
                raise ValueError(f"Forbidden analysis import in {name}")
    print("Repository checks passed: submission files, documentation links, output-free notebooks, data exclusion, analysis imports.")


if __name__ == "__main__":
    check_repository()
