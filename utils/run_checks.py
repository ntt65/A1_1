"""작은 회귀 검증과 선택적인 실제 표본 실행을 한 명령으로 수행한다.

python -m utils.run_checks는 가상 입력만 사용한다. --with-sample을 주면
현재 Python의 새 커널에서 분석 노트북을 실행하고 결과를 data/에만 저장한다.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_notebook(notebook_path, output_path):
    """노트북을 새 커널로 실행하고 비공개 결과 경로를 반환한다.

    입력은 변경하지 않는다. 실제 표본이 출력될 수 있어 output_path는 Git에서
    제외된 data/ 내부만 허용한다. 셀 실패는 예외로 전달해 완료로 기록하지 않는다.
    """
    notebook_path, output_path = Path(notebook_path).resolve(), Path(output_path).resolve()
    output_path.relative_to((ROOT / "data").resolve())
    runtime = ROOT / "data" / ".jupyter"
    for name, directory in (("JUPYTER_CONFIG_DIR", runtime / "config"),
                            ("JUPYTER_RUNTIME_DIR", runtime / "runtime"),
                            ("IPYTHONDIR", runtime / "ipython"),
                            ("MPLCONFIGDIR", runtime / "matplotlib")):
        directory.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(directory)

    import nbformat
    from jupyter_client import KernelManager
    from nbclient import NotebookClient

    notebook = nbformat.read(notebook_path, as_version=4)
    manager = KernelManager(kernel_name="python3")
    # 등록된 커널의 'python' 대신 지금 검증 중인 가상환경을 정확히 사용한다.
    manager.kernel_spec.argv[0] = sys.executable
    def report_progress(cell, cell_index, **kwargs):
        """원본 출력 대신 성공한 셀 번호만 기록해 장시간 실행 상태를 알린다."""
        print(f"Notebook code cell {cell_index + 1}: execution finished", flush=True)
    client = NotebookClient(notebook, km=manager, timeout=180, startup_timeout=30,
                            resources={"metadata": {"path": str(ROOT)}},
                            on_cell_executed=report_progress)
    print("Starting a fresh notebook kernel in the current Python environment...", flush=True)
    client.execute(cleanup_kc=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # 플랫폼별 줄바꿈 변환 없이 같은 UTF-8 직렬화 바이트를 보존한다.
    output_path.write_bytes(nbformat.writes(notebook).encode("utf-8"))
    return output_path


def main():
    """회귀 검증을 먼저 통과한 경우에만 선택한 실데이터 검증을 수행한다."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-sample", action="store_true", help="Execute the local H&M notebook too")
    args = parser.parse_args()
    subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"],
                   cwd=ROOT, check=True)
    if args.with_sample:
        output = run_notebook(ROOT / "notebooks" / "analysis_report.ipynb",
                              ROOT / "data" / "processed" / "analysis_report.executed.ipynb")
        print(f"Notebook passed; private outputs saved to {output}")


if __name__ == "__main__":
    main()
