"""제출 결과 보존 도구. 입력: 로컬 실행본·검증 기록·차트. 출력: 제출 노트북·표·그림·보고서. 부작용: 제출 경로의 파일을 생성·갱신한다."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def aggregate_snapshot(source):
    """입력: 검증 기록 source. 출력: 중첩 값까지 분리한 전체 사본. 부작용: 없음, 원본 내용과 값은 변경하지 않는다."""
    return deepcopy(source)	# 이후 통계 추가가 원본 검증 기록의 중첩 구조를 바꾸지 않게 한다.


def preserve_execution(source_path, target_path):
    """입력: 실행본 source_path와 제출 target_path. 출력: 제출 경로. 부작용: 대상 파일을 원본 바이트로 기록하며 미실행·오류 셀은 거부한다."""
    source_path, target_path = Path(source_path), Path(target_path)
    payload = source_path.read_bytes()
    notebook = json.loads(payload)
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code" and cell.get("execution_count") is None:	# 실행하지 않은 코드 셀이 있으면 제출 위치에 복사하지 않는다.
            raise ValueError("Notebook has unexecuted code cells.")
        if any(output.get("output_type") == "error" for output in cell.get("outputs", [])):	# 오류가 있는 실행 결과를 성공한 분석으로 게시하지 않는다.
            raise ValueError("Notebook execution failed.")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(payload)	# 재직렬화 없이 표·고객 ID·이미지·실행 출력을 바이트 그대로 보존한다.
    return target_path


def publish_report():
    """입력: data/의 검증 기록·거래·상품·실행본·차트. 출력: 없음. 부작용: 기술통계를 재계산하고 제출 노트북·JSON·CSV·그림·Markdown을 갱신한다."""
    import pandas as pd
    source = json.loads((ROOT / "data/processed/analysis_verification.json").read_text(encoding="utf-8"))
    output = ROOT / "docs/results"
    (output / "figures").mkdir(parents=True, exist_ok=True)
    snapshot = aggregate_snapshot(source)
    from src.pipeline import DataAnalyzer
    analyzer = DataAnalyzer(ROOT / "data/raw/hm/transactions_sample.csv")
    analyzer.load_data(date_columns=["t_dat"])
    analyzer.validate_transactions(start=source["settings"]["start_inclusive"], end=source["settings"]["end_exclusive"])	# 원래 실행 기록과 같은 관찰 구간으로 유효 거래를 선정한다.
    analyzer.join_products(ROOT / "data/raw/hm/articles_sample.csv")
    analyzer.extract_text_features("prod_name")
    snapshot["statistics"] = analyzer.summarize(["price", "prod_name_length", "prod_name_word_count"]).to_dict(orient="index")	# 원본 거래·상품명에서 보고서에 필요한 기술통계를 재계산한다.
    (output / "analysis_aggregates.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")	# 비표준 NaN 값이 있으면 저장을 실패시켜 JSON의 유효성을 지킨다.
    pd.DataFrame.from_dict(source["profile"], orient="index").rename_axis("Segment").to_csv(output / "segment_profile.csv")
    pd.Series(source["monthly"], name="Amount").to_csv(output / "monthly_amount.csv")
    for path in (ROOT / "data/processed/figures").glob("*.png"):
        shutil.copyfile(path, output / "figures" / path.name)	# 원본 차트 파일을 다시 그리거나 가공하지 않고 복사한다.
    bonus_source = ROOT / "data/processed/bonus"
    if "bonus" in source:	# 실행 기록에 보너스 결과가 있는 경우에만 관련 산출물을 보존한다.
        (output / "bonus").mkdir(exist_ok=True)
        for path in bonus_source.iterdir():
            if path.is_file() and path.suffix in {".csv", ".png", ".html"}:	# 보너스의 표·정적 그림·독립 인터랙티브 문서를 복사한다.
                shutil.copyfile(path, output / "bonus" / path.name)
    preserve_execution(ROOT / "data/processed/analysis_report.executed.ipynb", ROOT / "notebooks/analysis_report.ipynb")
    write_public_markdown(snapshot, output / "analysis_report.md")
    print("Submission prepared: original executed notebook, unchanged charts and complete analysis records.")


def write_public_markdown(aggregates, path):
    """입력: 검증된 aggregates 사전과 출력 path. 출력: 없음. 부작용: 집계 Markdown 파일을 기록한다. 노트북 표준 출력은 읽지 않는다."""
    def table(records):
        """입력: 행 사전의 records 목록. 출력: Markdown 표 문자열, 빈 입력은 빈 문자열. 부작용: 없음."""
        if not records: return ""	# 빈 표는 머리글과 구분선을 만들지 않는다.
        columns = list(records[0])	# 첫 행의 키 순서로 표 전체의 열 순서를 고정한다.
        lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
        for record in records:
            lines.append("| " + " | ".join(str(record.get(column, "")) for column in columns) + " |")	# 해당 열이 없는 행은 빈 셀로 표현하고 원본 값은 문자열로 보존한다.
        return "\n".join(lines)
    sections = ["# 공개 집계 분석 보고서", "실제 분석 집계를 정리한 보조 보고서다. 실제 행·고객 ID·상품 이미지와 실행 출력은 notebooks/analysis_report.ipynb에 원본 그대로 보존한다."]
    sections += ["## 자료 범위", table([{"기준일": aggregates["reference_date"], "유효 거래": aggregates["transaction_rows"], "고객": aggregates["customers"], "상품": aggregates["products"]}])]
    sections += ["## 기술통계", table([{"변수": name, **values} for name, values in aggregates["statistics"].items()])]
    sections += ["## 상관관계", table(aggregates["correlations"]), "유효 완전 관측 쌍의 Pearson 계수다. 이미지 관계는 관측 상품, 빈도–금액 관계는 고객 단위이며 인과로 해석하지 않는다."]
    sections += ["## 고객 프로파일", table([{"그룹": name, **values} for name, values in aggregates["profile"].items()])]
    sections += ["## 월별 합계", table([{"월": month, "원본 단위 금액": value} for month, value in aggregates["monthly"].items()])]
    sections += ["## 정제·대치·IQR", table([aggregates["cleaning"]]), table([{"피처": name, **values} for name, values in aggregates["imputation"].items()]), table([{"변수": name, **values} for name, values in aggregates["outliers"].items()])]
    sections += ["## 차트 6종", "실제 분석의 원본 박스플롯과 상품별 관측 산점도를 그대로 사용한다."]
    for name in ["01_histogram", "02_boxplot", "03_bar", "04_heatmap", "05_scatter", "06_line"]:
        sections.append(f"![{name}](figures/{name}.png)")	# 보고서 위치를 기준으로 기존 여섯 차트의 상대 링크를 연결한다.
    sections += ["## 해석과 재현", "금액은 원본 단위이고 전체 고객을 대표하지 않는다. 현재 원본 접근권한 없이도 집계 결과를 확인할 수 있다. 실행·SRC·인사이트는 [README](../../README.md)에 본문으로 정리했다. 같은 입력·설정의 전체 분석과 새 환경 재현은 README의 명령을 사용한다."]
    if "bonus" in aggregates:	# 보너스 기록이 없는 실행에는 해당 절과 링크를 추가하지 않는다.
        sections += ["## 보너스 실행 결과", "8구간 정규화 이미지 히스토그램·인접 절대차 엣지, 첫 관찰 구매월 코호트, Plotly RFM을 실제 실행했다. 가입일이 없어 코호트는 가입 기준이 아니다.",
                     "![관측 이미지 밝기 히스토그램](bonus/image_histogram.png)",
                     "![첫 관찰 구매월 코호트](bonus/cohort_retention.png)",
                     "[인터랙티브 RFM HTML](bonus/rfm_interactive.html): 내려받아 브라우저로 연다. 원본 고객 ID와 전체 관측을 포함하며 Plotly JS를 내장한다."]
    Path(path).write_text("\n\n".join(sections) + "\n", encoding="utf-8")	# 절 사이 빈 줄을 유지하여 Markdown 제목·표·이미지가 구분되게 한다.


def main():
    """입력: 명령행 옵션. 출력: 없음. 부작용: 원본 실행 결과와 보조 집계를 제출 위치에 기록한다. 이전 옵션은 호환용으로 받는다."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-aggregates", action="store_true", help="Compatibility option")	# 기존 호출과의 호환성을 유지하며 결과 보존 동작을 바꾸지는 않는다.
    parser.parse_args()
    publish_report()


if __name__ == "__main__":
    main()
