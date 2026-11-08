"""새 환경 재현 도구. 입력: 추적 코드·표본 ZIP·기준 JSON. 출력: 비교 결과. 부작용: data/에 복제본·환경·기록을 만들고 패키지를 설치한다."""

import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]


def verify_reproduction():
    """추적 파일의 새 복제본에서 표본 분석을 재현하고 기준 실행과 비교한다.

    입력: 저장소의 기준 JSON·현재 브랜치·표본 ZIP. 출력: 일치 여부와 환경을 담은 사전.
    부작용: data/에 복제본·가상환경·검증 기록을 쓰고 의존성 설치와 하위 명령을 실행한다.
    """
    def run(arguments, directory=ROOT):
        """입력: 명령 인수 목록과 작업 directory. 출력: 없음. 부작용: 하위 프로세스를 실행하며 실패를 즉시 전파한다."""
        subprocess.run([str(value) for value in arguments], cwd=directory, check=True)	# 경로 인수를 문자열로 통일하고 비정상 종료를 예외로 전달한다.

    baseline_path = ROOT / "data/processed/analysis_verification.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    base = (ROOT / "data/reproduction").resolve()
    base.mkdir(parents=True, exist_ok=True)
    destination = base / (datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6])	# 반복 실행이 기존 재현 결과를 덮지 않도록 독립 폴더를 만든다.
    destination.resolve().relative_to(base)	# 재현 작업의 대상이 지정한 로컬 영역 내부인지 확인한다.
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source_branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    print("Cloning tracked files for isolated reproduction...", flush=True)
    run(["git", "clone", "--quiet", "--no-local", "--single-branch", "--branch", source_branch, ROOT, destination])	# 현재 브랜치의 추적 코드만 독립 복제하여 미추적 로컬 파일과 분리한다.
    run([sys.executable, "-m", "venv", destination / ".venv"])
    python = destination / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")	# 운영체제별 가상환경 실행 파일 위치를 선택한다.
    print("Installing the pinned analysis and notebook dependencies...", flush=True)
    run([python, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "--no-input",
         "--cache-dir", base / "pip-cache", "-r", "requirements.txt", "-r", "requirements-notebook.txt",
         "-r", "requirements-bonus.txt"], destination)	# 분석·노트북·보너스의 고정된 의존성을 모두 설치한다.
    run([python, "scripts/restore_hm_sample.py", "--archive", ROOT / "data/raw/hm/hm_sample.zip"], destination)	# 개인 Drive 연결 설정은 복사하지 않고 기존 표본 ZIP만 검증·복원한다.
    run([python, "-B", "-m", "utils.run_checks", "--with-sample"], destination)	# 새 환경의 테스트와 새 커널 분석을 모두 통과해야 결과를 대조한다.
    repeated = json.loads((destination / "data/processed/analysis_verification.json").read_text(encoding="utf-8"))

    if baseline != repeated:	# 입력 동일성·설정·버전·주요 집계의 모든 기록을 비교한다.
        differing = [key for key in set(baseline) | set(repeated) if baseline.get(key) != repeated.get(key)]
        raise ValueError(f"Reproduction differs in: {differing}")	# 차이가 있으면 성공 기록을 쓰지 않고 상위 키를 보고한다.
    result = {"passed": True, "source_commit": source_commit, "source_branch": source_branch,
              "checkout": str(destination), "python": str(python), "compared_keys": sorted(baseline),
              "method": "fresh clone + fresh venv + restored sample + new kernel"}
    (ROOT / "data/processed/reproduction_verification.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")	# 성공한 재현의 커밋·환경·비교 범위를 로컬 기록으로 남긴다.
    print("Fresh-checkout reproduction matched every recorded field.", flush=True)
    return result


def main():
    """입력: 명령행 인수. 출력: 없음. 부작용: 새 복제본·환경을 만들어 전체 재현을 검증하고 결과를 기록한다."""
    argparse.ArgumentParser(description=__doc__).parse_args()
    verify_reproduction()


if __name__ == "__main__":
    main()
