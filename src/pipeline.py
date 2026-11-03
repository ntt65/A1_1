"""E-commerce multimodal data analysis pipeline."""

from __future__ import annotations

import argparse
from typing import Optional

import numpy as np
import pandas as pd


class DataAnalyzer:
    """Object-oriented data analysis pipeline for e-commerce data."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.df: Optional[pd.DataFrame] = None

    def load_data(self) -> pd.DataFrame:
        """Load input data from CSV path provided at initialization."""
        self.df = pd.read_csv(self.data_path)
        return self.df

    def handle_missing_values(self, strategy: str = "group_mean", group_col: Optional[str] = None) -> pd.DataFrame:
        """Handle missing values using supported strategies."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")

        if strategy == "group_mean":
            if group_col is None:
                raise ValueError("group_col must be provided when strategy='group_mean'.")

            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.difference([group_col])
            self.df[numeric_cols] = self.df.groupby(group_col)[numeric_cols].transform(
                lambda col: col.fillna(col.mean())
            )
            remaining_numeric = self.df.select_dtypes(include=[np.number]).columns
            self.df[remaining_numeric] = self.df[remaining_numeric].fillna(self.df[remaining_numeric].mean())
        elif strategy == "mean":
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
        elif strategy == "median":
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].median())
        elif strategy == "drop":
            self.df = self.df.dropna()
        else:
            raise ValueError("Unsupported strategy. Use one of: group_mean, mean, median, drop.")

        return self.df

    def detect_outliers(self, column: str, threshold: float = 1.5) -> pd.Series:
        """Detect outliers using the IQR method."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in data.")

        q1 = self.df[column].quantile(0.25)
        q3 = self.df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        return (self.df[column] < lower_bound) | (self.df[column] > upper_bound)

    def calculate_rfm(self, customer_col: str, date_col: str, amount_col: str) -> pd.DataFrame:
        """Calculate RFM metrics, scores, and customer segments."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")

        working = self.df.copy()
        working[date_col] = pd.to_datetime(working[date_col], errors="coerce")
        if working[date_col].isna().all():
            raise ValueError("All date values are invalid. Check date_col input.")

        reference_date = working[date_col].max() + pd.Timedelta(days=1)

        rfm = (
            working.groupby(customer_col)
            .agg(
                Recency=(date_col, lambda d: (reference_date - d.max()).days),
                Frequency=(customer_col, "count"),
                Monetary=(amount_col, "sum"),
            )
            .reset_index()
        )

        rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first", ascending=False), 4, labels=[1, 2, 3, 4]).astype(int)
        rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
        rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)

        conditions = [
            (rfm["R_Score"] >= 3) & (rfm["F_Score"] >= 3) & (rfm["M_Score"] >= 3),
            (rfm["F_Score"] >= 3) & (rfm["M_Score"] >= 2),
            (rfm["R_Score"] >= 3) & (rfm["F_Score"] <= 2),
            (rfm["R_Score"] <= 2) & (rfm["F_Score"] <= 2),
        ]
        labels = ["VIP", "Loyal", "New", "Churned"]
        rfm["Segment"] = np.select(conditions, labels, default="Potential")

        return rfm

    def extract_image_features(self, image_column: str) -> pd.DataFrame:
        """Extract vectorized mean/std image features from a NumPy-array column."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if image_column not in self.df.columns:
            raise ValueError(f"Column '{image_column}' not found in data.")

        image_data = np.asarray(self.df[image_column].tolist(), dtype=float)
        if image_data.ndim < 2:
            raise ValueError("image_column must contain same-shaped array-like values.")

        reduce_axes = tuple(range(1, image_data.ndim))
        self.df[f"{image_column}_mean"] = image_data.mean(axis=reduce_axes)
        self.df[f"{image_column}_std"] = image_data.std(axis=reduce_axes)

        return self.df

    def extract_text_features(self, text_column: str) -> pd.DataFrame:
        """Extract text length and word count features from a text column."""
        if self.df is None:
            raise ValueError("Data is not loaded. Call load_data() first.")
        if text_column not in self.df.columns:
            raise ValueError(f"Column '{text_column}' not found in data.")

        text_series = self.df[text_column].fillna("").astype(str)
        self.df[f"{text_column}_length"] = text_series.str.len()
        self.df[f"{text_column}_word_count"] = text_series.str.split().str.len()

        return self.df


def main() -> None:
    parser = argparse.ArgumentParser(description="Run e-commerce data analysis pipeline.")
    parser.add_argument("--data", required=True, help="Path to CSV data file")
    args = parser.parse_args()

    analyzer = DataAnalyzer(args.data)
    df = analyzer.load_data()
    print(f"Loaded dataset shape: {df.shape}")


if __name__ == "__main__":
    main()
