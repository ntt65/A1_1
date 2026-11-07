"""제출 파일·문서 링크·노트북 출력·공개 데이터 제외를 점검한다."""

import ast
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def check_local_links(path, root):
    """Markdown의 실제 상대 링크를 검증하고 코드 예제 안의 경로는 건너뛴다."""
    prose = []
    fence = None
    for line in path.read_text(encoding="utf-8").splitlines():
        marker = re.fullmatch(r" {0,3}(`{3,}|~{3,})(.*)", line)
        if fence is None:
            if marker and (marker[1][0] == "~" or "`" not in marker[2]):
                fence = marker[1]
                prose.append("")
            else:
                prose.append(line)
        elif marker and marker[1].startswith(fence) and not marker[2].strip():
            fence = None
    for paragraph in re.split(r"\n[ \t]*\n", "\n".join(prose)):
        # A code span closes only with a backtick run of the same length.
        visible = re.sub(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", "", paragraph, flags=re.DOTALL)
        for link in re.findall(r"\]\(([^)]+)\)", visible):
            if link.startswith(("http:", "https:", "#", "mailto:")):
                continue
            target = (path.parent / link.split("#")[0]).resolve()
            target.relative_to(root)
            if not target.exists():
                raise ValueError(f"Broken local link in {path.relative_to(root).as_posix()}: {link}")


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
        check_local_links(ROOT / name, ROOT)
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for cell in notebook["cells"]:
            if path.name == "analysis_report.ipynb":
                if any(output.get("output_type") == "error" for output in cell.get("outputs", [])):
                    raise ValueError("Analysis report contains an execution error.")
            elif cell.get("outputs") or cell.get("execution_count") is not None:
                raise ValueError(f"Unexpected outputs in preparation notebook: {path.name}")
    public_path = ROOT / "docs/results/analysis_report.md"
    if public_path.exists():
        if len(list((ROOT / "docs/results/figures").glob("*.png"))) != 6:
            raise ValueError("Expected six reviewed aggregate figures.")
        aggregate = json.loads((ROOT / "docs/results/analysis_aggregates.json").read_text(encoding="utf-8"))
        if "profile" not in aggregate or "monthly" not in aggregate:
            raise ValueError("Missing analysis summary.")
        if "bonus" in aggregate:
            for filename in ("cohort_retention.csv", "cohort_counts.csv", "cohort_sizes.csv",
                             "cohort_retention.png", "image_histogram.png", "rfm_interactive.html"):
                if not (ROOT / "docs/results/bonus" / filename).is_file():
                    raise ValueError(f"Missing bonus output: {filename}")
            if aggregate["bonus"]["plotly"]["points"] != aggregate["customers"]:
                raise ValueError("Interactive plot does not contain all customers.")
    forbidden = {"cv2", "PIL", "sklearn", "nltk", "ydata_profiling", "pandas_profiling", "sweetviz"}
    for name in ("src/pipeline.py", "utils/analytics.py", "utils/image_features.py", "utils/reporting.py", "utils/bonus.py"):
        tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
            if any(module.split(".")[0] in forbidden for module in modules):
                raise ValueError(f"Forbidden analysis import in {name}")
    print("Repository checks passed: submission files, documentation links, executed analysis report, data exclusion, analysis imports.")


if __name__ == "__main__":
    check_repository()
