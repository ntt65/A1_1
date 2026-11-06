"""새 복제본·새 가상환경·새 커널의 전체 분석 결과를 원본 실행과 대조한다."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]


def verify_reproduction():
    """추적 파일만 복제하고 표본을 안전하게 복원한 뒤 전체 결과를 비교한다.

    새 환경은 requirements 두 파일로 설치한다. 개인정보 연결 설정은 복사하지
    않는다. 결과와 환경은 Git 제외 data/reproduction 아래에 보관하며 삭제하지 않는다.
    """
    def run(arguments, directory=ROOT):
        """명시한 작업 폴더에서 명령을 실행하고 실패를 즉시 전달한다."""
        subprocess.run([str(value) for value in arguments], cwd=directory, check=True)

    baseline_path = ROOT / "data/processed/analysis_verification.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    base = (ROOT / "data/reproduction").resolve()
    base.mkdir(parents=True, exist_ok=True)
    destination = base / (datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6])
    destination.resolve().relative_to(base)
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source_branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    print("Cloning tracked files for isolated reproduction...", flush=True)
    run(["git", "clone", "--quiet", "--no-local", "--single-branch", "--branch", source_branch, ROOT, destination])
    run([sys.executable, "-m", "venv", destination / ".venv"])
    python = destination / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    print("Installing the pinned analysis and notebook dependencies...", flush=True)
    run([python, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--no-input",
         "--cache-dir", base / "pip-cache", "-r", "requirements.txt", "-r", "requirements-notebook.txt"], destination)
    run([python, "scripts/restore_hm_sample.py", "--archive", ROOT / "data/raw/hm/hm_sample.zip"], destination)
    run([python, "-B", "-m", "utils.run_checks", "--with-sample"], destination)
    repeated = json.loads((destination / "data/processed/analysis_verification.json").read_text(encoding="utf-8"))
    # 입력 동일성·설정·버전과 모든 주요 집계를 함께 대조한다.
    if baseline != repeated:
        differing = [key for key in set(baseline) | set(repeated) if baseline.get(key) != repeated.get(key)]
        raise ValueError(f"Reproduction differs in: {differing}")
    result = {"passed": True, "source_commit": source_commit, "source_branch": source_branch,
              "checkout": str(destination), "python": str(python), "compared_keys": sorted(baseline),
              "method": "fresh clone + fresh venv + restored sample + new kernel"}
    (ROOT / "data/processed/reproduction_verification.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Fresh-checkout reproduction matched every recorded field.", flush=True)
    return result


def main():
    """기준 노트북 실행 후 명시적으로 호출하는 재현 검증 CLI."""
    argparse.ArgumentParser(description=__doc__).parse_args()
    verify_reproduction()


if __name__ == "__main__":
    main()
