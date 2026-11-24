"""
Silver Layer Data Loader
========================

Responsibilities:
    - Read cleaned Parquet files.
    - Load data into PostgreSQL Silver schema.
    - Reuse the existing SQLAlchemy database engine.
    - Exclude temporary files.
"""

import sys
from pathlib import Path

import pandas as pd


# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))


# =====================================================
# Database Connection
# =====================================================

from depi_project.dbconnection.connection import get_engine


# =====================================================
# Configuration
# =====================================================

PARQUET_DIR = PROJECT_ROOT / "cleaned_data"

SCHEMA = "silver"

EXCLUDED_FILES = {"temp.parquet"}

CHUNK_SIZE = 10_000


# =====================================================
# Load Parquet Files
# =====================================================


def load_parquet_to_silver():

    engine = get_engine()

    if not PARQUET_DIR.exists():
        raise FileNotFoundError(f"Parquet directory not found: {PARQUET_DIR}")

    parquet_files = sorted(PARQUET_DIR.glob("*.parquet"))

    if not parquet_files:
        print("No Parquet files found.")
        return

    print("=" * 60)
    print("Starting Silver Layer Loading")
    print("=" * 60)

    for file in parquet_files:
        if file.name in EXCLUDED_FILES:
            print(f"Skipping: {file.name}")
            continue

        table_name = file.stem

        print(f"\nLoading table: {SCHEMA}.{table_name}")

        try:
            df = pd.read_parquet(file)

            print(f"Rows found: {len(df):,}")

            df.to_sql(
                name=table_name,
                con=engine,
                schema=SCHEMA,
                if_exists="append",
                index=False,
                chunksize=CHUNK_SIZE,
                method="multi",
            )

            print(f"Successfully loaded {SCHEMA}.{table_name} | Rows: {len(df):,}")

        except Exception as e:
            print(f"Failed to load {table_name}")
            print(f"Error: {e}")

            raise

    print("\n" + "=" * 60)
    print("Silver Layer Loading Completed!")
    print("=" * 60)


# =====================================================
# Main
# =====================================================

if __name__ == "__main__":
    load_parquet_to_silver()
