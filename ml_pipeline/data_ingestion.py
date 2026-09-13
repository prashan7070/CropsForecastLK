"""
CropsForecastLK: Automated Data Ingestion & Raw Data Audit Module
Author: Sathindu (ML Foundational Pipeline Owner)

This module handles:
1. Automated loading of Sri Lanka agricultural census datasets (Excel/CSV).
2. Strict schema verification against expected 7 domain columns.
3. Raw data structural audit (identifying dirty strings, commas, aggregate rows, zero extent anomalies).
4. Fast caching to CSV for accelerated downstream notebook execution.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ml_pipeline.config import (
    ARTIFACTS_DIR,
    CATEGORICAL_COLUMNS,
    CROP_CATEGORIES,
    DATA_RAW_DIR,
    DIRTY_STRING_INDICATORS,
    EXPECTED_COLUMNS,
    HIGHLAND_CROPS,
    NUMERIC_COLUMNS,
    PRIMARY_TARGET,
    RAW_CSV_PATH,
    RAW_DATA_PATH,
    RAW_EXCEL_PATH,
    SEASONS,
    SECONDARY_TARGET,
    SRI_LANKA_DISTRICTS,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("DataIngestion")

# Cache CSV path for accelerating notebook reloads
CACHED_RAW_CSV = DATA_RAW_DIR / "researchData_cached.csv"


def load_raw_data(
    file_path: Optional[Path] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """
    Automated loader for raw agricultural census data from Department of Census & Statistics.

    Priority:
    1. Direct file_path if provided.
    2. Cached CSV (researchData_cached.csv) if use_cache is True and cache exists.
    3. Official Excel file (data/raw/researchData.xlsx).
    4. Raw CSV fallback (data/raw/researchData.csv).
    """
    target_excel = file_path or RAW_EXCEL_PATH

    # Check for fast cached CSV first if requested
    if use_cache and CACHED_RAW_CSV.exists():
        logger.info(f"Loading cached raw dataset from {CACHED_RAW_CSV}...")
        df = pd.read_csv(CACHED_RAW_CSV, low_memory=False)
        logger.info(f"Cached dataset loaded successfully: {df.shape[0]:,} rows, {df.shape[1]} columns.")
        return df

    # Check official Excel file
    if target_excel.exists():
        logger.info(f"Loading official raw Excel dataset from {target_excel} (this may take a few seconds)...")
        try:
            df = pd.read_excel(target_excel, engine="openpyxl")
            logger.info(f"Successfully loaded Excel sheet: {df.shape[0]:,} rows, {df.shape[1]} columns.")

            # Save cached CSV for rapid future loads
            try:
                df.to_csv(CACHED_RAW_CSV, index=False)
                logger.info(f"Created fast load cache at {CACHED_RAW_CSV}")
            except Exception as cache_err:
                logger.warning(f"Could not create cache CSV: {cache_err}")

            return df
        except Exception as e:
            logger.warning(f"Failed to read Excel file with openpyxl ({e}). Checking CSV fallback...")

    # Check alternative raw CSV
    if RAW_CSV_PATH.exists():
        logger.info(f"Loading raw dataset from {RAW_CSV_PATH}...")
        df = pd.read_csv(RAW_CSV_PATH, low_memory=False)
        logger.info(f"CSV dataset loaded: {df.shape[0]:,} rows, {df.shape[1]} columns.")
        return df

    raise FileNotFoundError(
        f"Raw agricultural dataset not found! Please place 'researchData.xlsx' in '{DATA_RAW_DIR}'."
    )


def validate_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates structural compliance of raw dataframe against EXPECTED_COLUMNS.
    """
    errors: List[str] = []

    if df.empty:
        errors.append("Dataset is completely empty (0 records).")
        return False, errors

    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing mandatory columns: {missing_cols}")

    return len(errors) == 0, errors


def audit_raw_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs comprehensive structural, anomaly, and statistical data quality audit:
    - Total shape, column types, deep memory usage.
    - Missing value counts and percentages.
    - Detection of formatted string commas (e.g. '4,986.0').
    - Detection of missing indicator tokens ('n.a.', '-', 'nil').
    - Detection of summary/aggregate rows ('National Total', 'Island Total', 'Total').
    - Zero extent anomalies (Extent == 0 while Production > 0).
    """
    is_valid, validation_errors = validate_schema(df)

    audit_result: Dict[str, Any] = {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "columns": list(df.columns),
        "is_schema_valid": is_valid,
        "schema_errors": validation_errors,
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        "column_profiles": {},
        "dirty_formatting_detected": {},
        "aggregate_rows_detected": 0,
        "zero_extent_anomalies": 0,
    }

    # Detect summary aggregate rows (e.g. 'National Total', 'Total' season)
    agg_district_mask = df["District"].astype(str).str.contains(
        r"Total|National|Island|All", case=False, na=False, regex=True
    )
    agg_season_mask = df["Season"].astype(str).str.contains(
        r"Total|Annual|All", case=False, na=False, regex=True
    )
    total_agg_mask = agg_district_mask | agg_season_mask
    audit_result["aggregate_rows_detected"] = int(total_agg_mask.sum())

    # Profile each column
    for col in df.columns:
        col_series = df[col]
        null_count = int(col_series.isnull().sum())
        null_pct = round((null_count / len(df)) * 100, 2)
        unique_count = int(col_series.nunique(dropna=True))

        audit_result["column_profiles"][col] = {
            "dtype": str(col_series.dtype),
            "null_count": null_count,
            "null_percentage": null_pct,
            "unique_values": unique_count,
        }

    # Inspect numerical candidates for string formatting quirks (commas, tokens)
    for num_col in ["Extent", "Production"]:
        if num_col in df.columns:
            str_vals = df[num_col].astype(str).str.strip()

            # Comma formatted entries (e.g. '3,663.0')
            comma_count = int(str_vals.str.contains(",", regex=False).sum())

            # Text tokens representing nulls ('n.a.', '-', etc.)
            token_counts = {
                token: int((str_vals.str.lower() == token).sum())
                for token in DIRTY_STRING_INDICATORS
                if (str_vals.str.lower() == token).sum() > 0
            }

            audit_result["dirty_formatting_detected"][num_col] = {
                "comma_formatted_rows": comma_count,
                "missing_indicator_tokens": token_counts,
                "total_token_rows": sum(token_counts.values()),
            }

    # Check zero extent anomalies
    if "Extent" in df.columns and "Production" in df.columns:
        try:
            ext_cleaned = pd.to_numeric(
                df["Extent"].astype(str).str.replace(",", "", regex=False),
                errors="coerce",
            )
            prod_cleaned = pd.to_numeric(
                df["Production"].astype(str).str.replace(",", "", regex=False),
                errors="coerce",
            )
            anomaly_mask = (ext_cleaned == 0) & (prod_cleaned > 0)
            audit_result["zero_extent_anomalies"] = int(anomaly_mask.sum())
        except Exception:
            pass

    return audit_result


def save_audit_report(audit_result: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
    """Persists data audit results to JSON artifact."""
    save_path = output_path or (ARTIFACTS_DIR / "raw_data_audit.json")
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(audit_result, f, indent=2)
    logger.info(f"Audit report saved to {save_path}")
    return save_path


def print_audit_summary(audit_result: Dict[str, Any]) -> None:
    """Prints a clean CLI executive summary of the dataset audit."""
    print("\n" + "=" * 70)
    print(" CROPSFORECASTLK: RAW DATASET STRUCTURAL AUDIT REPORT")
    print("=" * 70)
    print(f" Total Records Ingested:      {audit_result['total_rows']:,}")
    print(f" Total Features:              {audit_result['total_columns']}")
    print(f" Memory Footprint:            {audit_result['memory_mb']} MB")
    print(f" Schema Validity:             {'PASS' if audit_result['is_schema_valid'] else 'FAIL'}")
    print(f" Summary/Aggregate Rows:      {audit_result['aggregate_rows_detected']:,}")
    print(f" Zero-Extent Anomalies:       {audit_result['zero_extent_anomalies']:,}")
    print("-" * 70)
    print(" Column Profiles:")
    for col, profile in audit_result["column_profiles"].items():
        print(
            f"   - {col:<15} | Type: {profile['dtype']:<10} | "
            f"Nulls: {profile['null_count']:>5} ({profile['null_percentage']}%) | "
            f"Uniques: {profile['unique_values']:>5}"
        )
    print("-" * 70)
    print(" String Formatting & Formatting Quirks:")
    for col, dirty in audit_result.get("dirty_formatting_detected", {}).items():
        print(f"   - {col}:")
        print(f"       * Comma-formatted strings: {dirty['comma_formatted_rows']:,}")
        print(f"       * Missing token representations: {dirty['total_token_rows']:,}")
    print("=" * 70 + "\n")


def run_ingestion_audit() -> Dict[str, Any]:
    """Complete orchestration for raw data ingestion and structural audit."""
    logger.info("Initiating CropsForecastLK raw data ingestion pipeline...")
    df = load_raw_data()
    audit_results = audit_raw_dataset(df)
    print_audit_summary(audit_results)
    save_audit_report(audit_results)
    return audit_results


if __name__ == "__main__":
    run_ingestion_audit()
