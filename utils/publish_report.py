"""승인된 비식별 집계와 명시적으로 선택한 집계 Markdown 보고서를 로컬 공개 폴더에 만든다."""

import argparse
import base64
from copy import deepcopy
import json
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def aggregate_snapshot(source):
    """알려진 집계 필드만 선택하고 식별자·행·개인 경로를 내보내지 않는다."""
    keys = ("settings", "reference_date", "versions", "transaction_rows", "customers", "products",
            "joined_columns", "cleaning", "extraction", "join", "image_statuses", "largest_batch",
            "imputation", "outliers", "rfm", "profile", "correlations", "monthly")
    result = {key: deepcopy(source[key]) for key in keys if key in source}
    forbidden = {"customer_id", "article_id", "rows", "records", "drive_source", "token", "url", "path"}

    def validate(value):
        """예상하지 않은 행 필드·ID·주소가 집계 구조에 섞이면 중단한다."""
        if isinstance(value, dict):
            if forbidden.intersection(value):
                raise ValueError("Private row/connection fields in aggregate output.")
            for key in value: validate(key)
            for child in value.values(): validate(child)
        elif isinstance(value, list):
            for child in value: validate(child)
        elif isinstance(value, str) and re.search(r"\b[0-9a-f]{64}\b|https?://|[A-Z]:[\\/]", value, re.I):
            raise ValueError("Identifier or private location in aggregate output.")
    validate(result)
    result["publication_policy"] = {"original_rows": False, "customer_product_ids": False,
                                    "original_images": False, "individual_product_features": False,
                                    "user_approved_aggregates": True}
    return result


def redact_notebook(notebook, public_images):
    """원본 로드 출력을 제거한 로컬 검토용 사본을 반환한다. 원격 공개 파일이 아니다.

    원본 출력 전부를 막연히 익명화하지 않는다. 허용 구간을 명시하고 알 수 없는
    셀 출력은 비운다. 이미지 출력은 개인 실행본의 그림 대신 공개 집계 그림으로 교체한다.
    """
    result = deepcopy(notebook)
    allowed = {"NB_FEATURES", "NB_CLEAN", "NB_RFM", "NB_STATS", "NB_PLOTS", "NB_REPRO", "INSIGHTS"}
    section, image_index = None, 0
    for cell in result["cells"]:
        source = "".join(cell.get("source", []))
        cell["metadata"] = {}
        if cell["cell_type"] == "markdown":
            match = re.search(r"^## (NB_[A-Z]+)", source, re.M)
            if match: section = match.group(1)
            elif source.startswith("## 실제 결과의 비즈니스 해석"): section = "INSIGHTS"
            elif source.startswith("## "): section = None
            continue
        if section not in allowed:
            cell["outputs"] = []
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                raise ValueError("Cannot publish a failed notebook.")
            data = output.get("data", {})
            if "image/png" in data:
                if image_index >= len(public_images):
                    raise ValueError("Unexpected figure count.")
                data.clear()
                data["image/png"] = base64.b64encode(public_images[image_index]).decode("ascii")
                data["text/plain"] = ["Approved aggregate chart"]
                image_index += 1
            if "data" in output:
                output["metadata"] = {}
            else:
                output.pop("metadata", None)
    if image_index != len(public_images):
        raise ValueError("Public figure count differs from notebook outputs.")
    result["metadata"] = {key: notebook["metadata"][key] for key in ("kernelspec", "language_info") if key in notebook["metadata"]}
    # source 자체에도 개인 ID가 박혀 있으면 공개본 생성을 중단한다.
    text = json.dumps(result, ensure_ascii=False)
    if re.search(r"\b[0-9a-f]{64}\b", text, re.I):
        raise ValueError("Potential customer identifier in public notebook.")
    notice = {"cell_type": "markdown", "metadata": {}, "id": "publication-notice",
              "source": ["# 공개용 비식별 실행 보고서\n", "NB_LOAD의 원본 행 출력은 제거했다. 그림은 집계 전용 버전이며 이미지 산점도는 상품 3개 이상인 구간만 표시한다. 전체 비공개 실행본은 data/processed에 보관한다. 원본 CSV·고객/상품 ID·상품 이미지는 포함하지 않는다.\n"]}
    result["cells"].insert(0, notice)
    return result


def publish_report():
    """새로 읽은 상품 피처로 집계 차트·표·검토된 실행 보고서를 생성한다."""
    import matplotlib.pyplot as plt
    from src.pipeline import DataAnalyzer
    from utils.reporting import make_figures, monthly_amount
    from scripts.restore_hm_sample import sha256
    import nbformat

    source = json.loads((ROOT / "data/processed/analysis_verification.json").read_text(encoding="utf-8"))
    for name, expected in source["input_sha256"].items():
        if sha256(ROOT / "data/raw/hm" / name) != expected:
            raise ValueError("Input changed. Run the full notebook before publishing.")
    public = aggregate_snapshot(source)
    output = ROOT / "docs/results"
    figures_dir = output / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    analyzer = DataAnalyzer(ROOT / "data/raw/hm/transactions_sample.csv")
    analyzer.load_data(date_columns=["t_dat"])
    analyzer.validate_transactions(start=source["settings"]["start_inclusive"], end=source["settings"]["end_exclusive"])
    analyzer.join_products(ROOT / "data/raw/hm/articles_sample.csv")
    analyzer.extract_text_features("prod_name")
    analyzer.extract_image_features(image_dir=ROOT / "data/raw/hm/images",
        image_size=source["settings"]["image_size"], batch_size=source["settings"]["batch_size"])
    rfm = analyzer.calculate_rfm("customer_id", "t_dat", "price", reference_date=source["reference_date"])
    profile = analyzer.profile_segments(rfm)
    public["statistics"] = analyzer.summarize(["price", "prod_name_length", "prod_name_word_count"]).to_dict(orient="index")
    expected_profile = pd.DataFrame.from_dict(source["profile"], orient="index").rename_axis("Segment")
    pd.testing.assert_frame_equal(profile, expected_profile, check_dtype=False)
    monthly = monthly_amount(analyzer.df, "t_dat", "price", source["settings"]["start_inclusive"], source["settings"]["end_exclusive"])
    clipped = analyzer.clip_outliers("price", source["settings"]["iqr_threshold"])
    figures = make_figures(analyzer.df, clipped, analyzer.products, rfm, profile, monthly)
    # 공개 박스플롯은 개별 거래 가격 점 대신 사분위·수염 요약만 표시한다.
    ax = figures["02_boxplot"].axes[0]; ax.clear()
    ax.boxplot([analyzer.df.price.to_numpy(), clipped.to_numpy()], tick_labels=["Raw", "IQR clipped"],
               showfliers=False, whis=(0, 100))
    ax.set(title="Amount before/after clipping (min/max whiskers)", xlabel="EDA treatment", ylabel="Amount (source units)")
    # 원래 상품별 점을 내보내지 않고 고정 구간의 집계 점으로 대체한다.
    observed = analyzer.products.loc[analyzer.products.image_status == "ok"]
    counts, x_edges, y_edges = np.histogram2d(observed.image_mean, observed.image_std,
                                           bins=[np.linspace(0, 1, 21), np.linspace(0, .5, 21)])
    i, j = np.where(counts >= 3)
    ax = figures["05_scatter"].axes[0]; ax.clear()
    ax.scatter((x_edges[i] + x_edges[i+1])/2, (y_edges[j] + y_edges[j+1])/2, s=counts[i,j]*10, color="#306b9b", alpha=.7)
    ax.set(title="Image feature bins (at least 3 products per bin)", xlabel="Pixel mean bin center (0–1)", ylabel="Pixel std bin center (0–1)")
    image_bytes = []
    for name, figure in figures.items():
        figure.tight_layout()
        path = figures_dir / f"{name}.png"
        figure.savefig(path, dpi=110, bbox_inches="tight")
        plt.close(figure)
        image_bytes.append(path.read_bytes())
    (output / "analysis_aggregates.json").write_text(json.dumps(public, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    profile.to_csv(output / "segment_profile.csv")
    monthly.to_csv(output / "monthly_amount.csv")
    notebook = json.loads((ROOT / "data/processed/analysis_report.executed.ipynb").read_text(encoding="utf-8"))
    public_notebook = redact_notebook(notebook, image_bytes)
    nbformat.validate(public_notebook)
    (ROOT / "data/processed/analysis_report.redacted.ipynb").write_text(json.dumps(public_notebook, ensure_ascii=False, indent=1), encoding="utf-8")
    write_public_markdown(public, output / "analysis_report.md")
    print("Published locally: aggregate JSON, group/month tables, six aggregate charts, static Markdown report. Executed notebooks remain private.")


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
    sections = ["# 공개 집계 분석 보고서", "실제 분석에서 검증한 비식별 집계만 명시적으로 선택한 정적 보고서다. 원본 행·고객/상품 ID·상품 이미지·노트북 stdout은 포함하지 않는다. 실제 실행 노트북은 비공개 data/processed에 보존한다."]
    sections += ["## 자료 범위", table([{"기준일": aggregates["reference_date"], "유효 거래": aggregates["transaction_rows"], "고객": aggregates["customers"], "상품": aggregates["products"]}])]
    sections += ["## 기술통계", table([{"변수": name, **values} for name, values in aggregates["statistics"].items()])]
    sections += ["## 상관관계", table(aggregates["correlations"]), "유효 완전 관측 쌍의 Pearson 계수다. 이미지 관계는 관측 상품, 빈도–금액 관계는 고객 단위이며 인과로 해석하지 않는다."]
    sections += ["## 고객 프로파일", table([{"그룹": name, **values} for name, values in aggregates["profile"].items()])]
    sections += ["## 월별 합계", table([{"월": month, "원본 단위 금액": value} for month, value in aggregates["monthly"].items()])]
    sections += ["## 정제·대치·IQR", table([aggregates["cleaning"]]), table([{"피처": name, **values} for name, values in aggregates["imputation"].items()]), table([{"변수": name, **values} for name, values in aggregates["outliers"].items()])]
    sections += ["## 차트 6종", "공개 박스플롯은 개별 점 대신 최소/최대 수염을 사용한다. 이미지 산점도는 상품3개 이상인 구간의 중심·빈도만 표시한다."]
    for name in ["01_histogram", "02_boxplot", "03_bar", "04_heatmap", "05_scatter", "06_line"]:
        sections.append(f"![{name}](figures/{name}.png)")
    sections += ["## 해석과 재현", "금액은 원본 단위이고 전체 고객을 대표하지 않는다. 현재 원본 접근권한 없이도 집계 결과를 확인할 수 있다. 실행·SRC·인사이트는 [README](../../README.md)에 본문으로 정리했다. 같은 입력·설정의 전체 분석과 새 환경 재현은 README의 명령을 사용한다."]
    Path(path).write_text("\n\n".join(sections) + "\n", encoding="utf-8")


def main():
    """이용 조건과 집계 내용을 확인한 사용자가 명시적으로 호출하는 CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-aggregates", action="store_true", help="Confirm review of the source terms and aggregate contents")
    if not parser.parse_args().approved_aggregates:
        parser.error("Review the terms and public aggregates, then pass --approved-aggregates.")
    publish_report()


if __name__ == "__main__":
    main()
