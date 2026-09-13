"""
CropsForecastLK: Global Configuration Module
Contains directory paths, target variables, schema definitions,
and Sri Lankan agricultural domain constants.
"""

from pathlib import Path

# Base Paths (Monorepo root resolution)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
DOCS_DIR = BASE_DIR / "docs"

# Specific File Paths
RAW_EXCEL_PATH = DATA_RAW_DIR / "researchData.xlsx"
RAW_CSV_PATH = DATA_RAW_DIR / "researchData.csv"
RAW_DATA_PATH = RAW_EXCEL_PATH if RAW_EXCEL_PATH.exists() else RAW_CSV_PATH

PROCESSED_DATA_PATH = DATA_PROCESSED_DIR / "cleaned_highland_crops.csv"
ENGINEERED_DATA_PATH = DATA_PROCESSED_DIR / "engineered_features.parquet"
PIPELINE_ARTIFACT_PATH = ARTIFACTS_DIR / "crop_forecaster_pipeline.joblib"
BEST_PARAMS_PATH = ARTIFACTS_DIR / "optuna_study_best_params.json"
MODEL_METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"

# Dataset Schema Specification (Department of Census & Statistics)
EXPECTED_COLUMNS = [
    "District",
    "Season",
    "CropCategory",
    "Crop",
    "Year",
    "Extent",
    "Production",
]

CATEGORICAL_COLUMNS = ["District", "Season", "CropCategory", "Crop"]
NUMERIC_COLUMNS = ["Year", "Extent", "Production"]
TARGET_COLUMN = "Production"
PRIMARY_TARGET = "Production"        # Harvest output in Metric Tons (MT)
SECONDARY_TARGET = "Crop_Yield"      # Productivity ratio: Production / Extent (MT/Hectare)

# Domain Entities: Sri Lankan Administrative Districts
SRI_LANKA_DISTRICTS = [
    "Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo",
    "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara",
    "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar",
    "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya",
    "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya",
]

# Domain Entities: Agricultural Seasons
SEASONS = ["Yala", "Maha"]

# Domain Entities: Highland Crop Categories & Representative Crops
CROP_CATEGORIES = [
    "Cereals",
    "Pulses",
    "Oil Seeds",
    "Roots and Tubers",
    "Condiments",
    "Other Field Crops",
]

HIGHLAND_CROPS = [
    "Kurakkan",
    "Maize",
    "Green Gram",
    "Black Gram",
    "Cowpea",
    "Chili",
    "Red Onion",
    "Big Onion",
    "Potato",
    "Sweet Potato",
    "Cassava",
    "Ginger",
    "Turmeric",
]

# Dirty String Anomalies Detected in Census Raw Tables
DIRTY_STRING_INDICATORS = ["n.a.", "na", "n/a", "-", "--", " - ", "nil", "null"]

# Pipeline Hyperparameters & Seed
RANDOM_SEED = 42
TEMPORAL_SPLIT_TRAIN_END_YEAR = 2017
TEMPORAL_SPLIT_VAL_END_YEAR = 2020
