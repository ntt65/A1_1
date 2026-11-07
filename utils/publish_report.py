"""미션의 실제 실행 노트북·표·그림을 변경 없이 제출 위치에 보존한다."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def aggregate_snapshot(source):
    """검증 기록을 내용 삭제·치환 없이 사본으로 반환한다."""
    return deepcopy(source)


def preserve_execution(source_path, target_path):
    """성공한 실행 노트북을 바이트 그대로 복사한다. 표·ID·이미지를 숨기지 않는다."""
    source_path, target_path = Path(source_path), Path(target_path)
    payload = source_path.read_bytes()
    notebook = json.loads(payload)
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code" and cell.get("execution_count") is None:
            raise ValueError("Notebook has unexecuted code cells.")
        if any(output.get("output_type") == "error" for output in cell.get("outputs", [])):
            raise ValueError("Notebook execution failed.")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(payload)
    return target_path


def publish_report():
    """원본 실행본과 차트·집계를 제출 경로에 복사하고 집계 Markdown을 만든다."""
    import pandas as pd
    source = json.loads((ROOT / "data/processed/analysis_verification.json").read_text(encoding="utf-8"))
    output = ROOT / "docs/results"
    (output / "figures").mkdir(parents=True, exist_ok=True)
    snapshot = aggregate_snapshot(source)
    from src.pipeline import DataAnalyzer
    analyzer = DataAnalyzer(ROOT / "data/raw/hm/transactions_sample.csv")
    analyzer.load_data(date_columns=["t_dat"])
    analyzer.validate_transactions(start=source["settings"]["start_inclusive"], end=source["settings"]["end_exclusive"])
    analyzer.join_products(ROOT / "data/raw/hm/articles_sample.csv")
    analyzer.extract_text_features("prod_name")
    snapshot["statistics"] = analyzer.summarize(["price", "prod_name_length", "prod_name_word_count"]).to_dict(orient="index")
    (output / "analysis_aggregates.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    pd.DataFrame.from_dict(source["profile"], orient="index").rename_axis("Segment").to_csv(output / "segment_profile.csv")
    pd.Series(source["monthly"], name="Amount").to_csv(output / "monthly_amount.csv")
    for path in (ROOT / "data/processed/figures").glob("*.png"):
        shutil.copyfile(path, output / "figures" / path.name)
    bonus_source = ROOT / "data/processed/bonus"
    if "bonus" in source:
        (output / "bonus").mkdir(exist_ok=True)
        for path in bonus_source.iterdir():
            if path.is_file() and path.suffix in {".csv", ".png", ".html"}:
                shutil.copyfile(path, output / "bonus" / path.name)
    preserve_execution(ROOT / "data/processed/analysis_report.executed.ipynb", ROOT / "notebooks/analysis_report.ipynb")
    write_public_markdown(snapshot, output / "analysis_report.md")
    print("Submission prepared: original executed notebook, unchanged charts and complete analysis records.")


def write_public_markdown(aggregates, path):
    """검증한 집계 구조에서만 공개 Markdown을 만든다. 노트북 stdout은 사용하지 않는다."""
    def table(records):
        """집계 표를 추가 패키지 없이 Markdown으로 표현한다."""
        if not records: return ""
        columns = list(records[0])
        lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
        for record in records:
            lines.append("| " + " | ".join(str(record.get(column, "")) for column in columns) + " |")
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
        sections.append(f"![{name}](figures/{name}.png)")
    sections += ["## 해석과 재현", "금액은 원본 단위이고 전체 고객을 대표하지 않는다. 현재 원본 접근권한 없이도 집계 결과를 확인할 수 있다. 실행·SRC·인사이트는 [README](../../README.md)에 본문으로 정리했다. 같은 입력·설정의 전체 분석과 새 환경 재현은 README의 명령을 사용한다."]
    if "bonus" in aggregates:
        sections += ["## 보너스 실행 결과", "8구간 정규화 이미지 히스토그램·인접 절대차 엣지, 첫 관찰 구매월 코호트, Plotly RFM을 실제 실행했다. 가입일이 없어 코호트는 가입 기준이 아니다.",
                     "![관측 이미지 밝기 히스토그램](bonus/image_histogram.png)",
                     "![첫 관찰 구매월 코호트](bonus/cohort_retention.png)",
                     "[인터랙티브 RFM HTML](bonus/rfm_interactive.html): 내려받아 브라우저로 연다. 원본 고객 ID와 전체 관측을 포함하며 Plotly JS를 내장한다."]
    Path(path).write_text("\n\n".join(sections) + "\n", encoding="utf-8")


def main():
    """원본 실행 결과를 저장하는 CLI. 이전 옵션은 호환성을 위해 받는다."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-aggregates", action="store_true", help="Compatibility option")
    parser.parse_args()
    publish_report()


if __name__ == "__main__":
    main()
