"""저장소 제출 검사. 입력: 추적 파일·문서·노트북·집계. 출력: 성공 로그 또는 예외. 부작용: 파일과 Git 목록을 읽고 검사 결과를 출력한다."""

import ast
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def check_local_links(path, root):
    """입력: Markdown path와 저장소 root. 출력: 없음. 부작용: 파일을 읽고 저장소 밖 경로·누락 파일에 예외를 발생시킨다. 코드 예제는 제외한다."""
    prose = []
    fence = None
    for line in path.read_text(encoding="utf-8").splitlines():
        marker = re.fullmatch(r" {0,3}(`{3,}|~{3,})(.*)", line)	# 최대 세 칸 들여쓴 백틱·물결표 코드 블록 경계를 찾는다.
        if fence is None:	# 코드 블록 밖의 본문만 링크 검사 대상으로 모은다.
            if marker and (marker[1][0] == "~" or "`" not in marker[2]):	# 백틱 코드 블록의 정보 문자열에는 백틱을 허용하지 않는다.
                fence = marker[1]
                prose.append("")
            else:
                prose.append(line)
        elif marker and marker[1].startswith(fence) and not marker[2].strip():	# 같은 기호의 충분히 긴 닫는 경계만 코드 블록을 끝낸다.
            fence = None
    for paragraph in re.split(r"\n[ \t]*\n", "\n".join(prose)):

        visible = re.sub(r"(?<!`)(`+)(?!`).*?(?<!`)\1(?!`)", "", paragraph, flags=re.DOTALL)	# 같은 길이의 백틱으로 닫힌 인라인 코드 안 링크는 검사하지 않는다.
        for link in re.findall(r"\]\(([^)]+)\)", visible):
            if link.startswith(("http:", "https:", "#", "mailto:")):	# 외부 주소·문서 내 앵커·메일은 로컬 파일 존재 검사에서 제외한다.
                continue
            target = (path.parent / urlsplit(link).path).resolve()	# 쿼리·앵커를 제외하고 현재 문서 기준의 상대 파일 경로를 계산한다.
            target.relative_to(root)	# 저장소 바깥으로 나가는 상대 링크는 예외로 처리한다.
            if not target.exists():	# 실제 파일·폴더가 없으면 문서 위치와 링크를 함께 보고한다.
                raise ValueError(f"Broken local link in {path.relative_to(root).as_posix()}: {link}")


def check_repository():
    """제출 파일·문서 링크·실행 출력·분석 의존성의 기본 조건을 검사한다.

    입력: 저장소 파일과 Git 추적 목록. 출력: 없음, 성공 시 확인 로그를 출력한다.
    부작용: 파일·Git 상태를 읽으며 누락·잘못된 출력·금지 의존성은 예외로 알린다.
    """
    for name in ("src/pipeline.py", "notebooks/analysis_report.ipynb", "README.md"):
        if not (ROOT / name).is_file():	# 미션 제출에 필요한 최소 파일부터 확인한다.
            raise ValueError(f"Missing submission file: {name}")
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    if any(name.startswith(("data/", ".venv/")) for name in tracked):	# 로컬 표본·가상환경이 Git 추적 파일에 섞이면 실패한다.
        raise ValueError("Local data/environment is tracked by Git.")
    for name in ["README.md", "index.md", "reverse_index.md", *[str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "docs").rglob("*.md")]]:
        check_local_links(ROOT / name, ROOT)
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        for cell in notebook["cells"]:
            if path.name == "analysis_report.ipynb":	# 평가 노트북의 정상 실행 결과는 유지하고 오류 출력만 거부한다.
                if any(output.get("output_type") == "error" for output in cell.get("outputs", [])):	# 셀 실행 오류가 있는 결과를 제출 성공으로 취급하지 않는다.
                    raise ValueError("Analysis report contains an execution error.")
            elif cell.get("outputs") or cell.get("execution_count") is not None:	# 준비 노트북에는 출력과 실행 횟수가 남아 있지 않아야 한다.
                raise ValueError(f"Unexpected outputs in preparation notebook: {path.name}")
    public_path = ROOT / "docs/results/analysis_report.md"
    if public_path.exists():	# 보조 보고서가 생성된 경우 연결된 결과 묶음의 완전성도 확인한다.
        if len(list((ROOT / "docs/results/figures").glob("*.png"))) != 6:	# 미션에서 요구한 여섯 종류 차트의 누락·추가를 확인한다.
            raise ValueError("Expected six reviewed aggregate figures.")
        aggregate = json.loads((ROOT / "docs/results/analysis_aggregates.json").read_text(encoding="utf-8"))
        if "profile" not in aggregate or "monthly" not in aggregate:	# 고객 프로파일과 월별 금액 집계는 필수 결과다.
            raise ValueError("Missing analysis summary.")
        if "bonus" in aggregate:	# 보너스가 실행 기록에 있으면 해당 출력 파일도 모두 필요하다.
            for filename in ("cohort_retention.csv", "cohort_counts.csv", "cohort_sizes.csv",
                             "cohort_retention.png", "image_histogram.png", "rfm_interactive.html"):
                if not (ROOT / "docs/results/bonus" / filename).is_file():	# 표·그림·독립 HTML 중 하나라도 없으면 불완전한 결과다.
                    raise ValueError(f"Missing bonus output: {filename}")
            if aggregate["bonus"]["plotly"]["points"] != aggregate["customers"]:	# 인터랙티브 차트가 전체 고객 관측을 보존하는지 확인한다.
                raise ValueError("Interactive plot does not contain all customers.")
    forbidden = {"cv2", "PIL", "sklearn", "nltk", "ydata_profiling", "pandas_profiling", "sweetviz"}
    for name in ("src/pipeline.py", "utils/analytics.py", "utils/image_features.py", "utils/reporting.py", "utils/bonus.py"):
        tree = ast.parse((ROOT / name).read_text(encoding="utf-8"))	# 실행 도구를 제외한 계산 모듈의 정적 가져오기 문장을 조사한다.
        for node in ast.walk(tree):
            modules = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
            if any(module.split(".")[0] in forbidden for module in modules):	# 하위 모듈 가져오기도 최상위 패키지 이름으로 판정한다.
                raise ValueError(f"Forbidden analysis import in {name}")
    print("Repository checks passed: submission files, documentation links, executed analysis report, data exclusion, analysis imports.")


if __name__ == "__main__":
    check_repository()
