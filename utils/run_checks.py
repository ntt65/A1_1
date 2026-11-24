"""가상 입력 회귀 검증과 선택적인 실제 표본 노트북 실행을 묶는 실행 도구.

입력: 명령행의 --with-sample과 로컬 테스트·표본. 출력: 검증 로그와 실행 노트북.
부작용: 하위 프로세스를 실행하며 표본 선택 시 환경변수·data/의 실행 파일을 만든다.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]	# 호출 위치와 무관하게 저장소 루트를 기준으로 경로를 계산한다.


def run_notebook(notebook_path, output_path):
    """분석 노트북을 현재 파이썬의 새 커널에서 실행한다.

    입력: 원본 notebook_path와 data/ 내부의 output_path. 출력: 실행본의 절대 경로.
    부작용: 환경변수·런타임 폴더·실행본을 쓰고 커널을 실행한다. 셀 실패는 전파한다.
    """
    notebook_path, output_path = Path(notebook_path).resolve(), Path(output_path).resolve()
    output_path.relative_to((ROOT / "data").resolve())	# 출력이 Git 제외 영역을 벗어나면 실행 전에 예외로 중단한다.
    runtime = ROOT / "data" / ".jupyter"
    for name, directory in (("JUPYTER_CONFIG_DIR", runtime / "config"),
                            ("JUPYTER_RUNTIME_DIR", runtime / "runtime"),
                            ("IPYTHONDIR", runtime / "ipython"),
                            ("MPLCONFIGDIR", runtime / "matplotlib")):
        directory.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(directory)	# 커널·그래프 설정을 저장소의 로컬 실행 영역에 모은다.

    import nbformat
    from jupyter_client import KernelManager
    from nbclient import NotebookClient

    notebook = nbformat.read(notebook_path, as_version=4)
    manager = KernelManager(kernel_name="python3")

    manager.kernel_spec.argv[0] = sys.executable	# 등록된 기본 파이썬 대신 현재 검증 중인 가상환경을 사용한다.
    def report_progress(cell, cell_index, **kwargs):
        """입력: 실행한 cell·cell_index·추가 콜백 인수. 출력: 없음. 부작용: 완료 셀 번호를 표준 출력에 기록한다."""
        print(f"Notebook code cell {cell_index + 1}: execution finished", flush=True)
    client = NotebookClient(notebook, km=manager, timeout=180, startup_timeout=30,
                            resources={"metadata": {"path": str(ROOT)}},
                            on_cell_executed=report_progress)
    print("Starting a fresh notebook kernel in the current Python environment...", flush=True)
    client.execute(cleanup_kc=True)	# 셀 오류를 호출자에게 전파하고 실행 후 커널 자원을 정리한다.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_bytes(nbformat.writes(notebook).encode("utf-8"))	# 운영체제별 줄바꿈 변환 없이 직렬화한 바이트를 보존한다.
    return output_path


def main():
    """입력: 명령행 옵션. 출력: 없음. 부작용: 회귀 테스트와 선택한 표본 노트북을 실행하며 실패를 예외로 전파한다."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-sample", action="store_true", help="Execute the local H&M notebook too")
    args = parser.parse_args()
    subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                   cwd=ROOT, check=True)	# 회귀 테스트가 실패하면 실제 표본 실행으로 진행하지 않는다.
    if args.with_sample:	# 명시적으로 요청한 경우에만 로컬 표본과 새 커널을 사용한다.
        output = run_notebook(ROOT / "notebooks" / "analysis_report.ipynb",
                              ROOT / "data" / "processed" / "analysis_report.executed.ipynb")
        print(f"Notebook passed; private outputs saved to {output}")


if __name__ == "__main__":
    main()
