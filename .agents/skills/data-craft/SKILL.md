---
name: data-craft
description: >-
  Use this skill when inspecting, profiling, exploring, cleaning, transforming,
  or building pipelines for data files (CSV, Excel, Parquet, JSON, SQLite, etc.).
  Enforces non-destructive operations, external compute profiling, audit logging
  for dropped rows, and schema contracts.
---

# Data Craft: Professional Data Engineering & Analysis

Standard operating procedures for exploring, cleaning, and transforming data reliably without polluting prompt context.

---

## 1. Zero-Dump Profiling & EDA (Think in Code)

Never dump large datasets into chat context. Always compute summaries externally.

1. **External Inspection:**
   - Run a short Python one-liner via `run_command` to inspect shape, column types, and missing values.
   ```powershell
   python -c "import pandas as pd; df=pd.read_csv('data.csv'); print(f'Shape: {df.shape}\nNulls:\n{df.isnull().sum()}\nDtypes:\n{df.dtypes}')"
   ```
2. **Produce a Compact Data Health Card:**
   - **Dimensions:** Total rows and columns.
   - **Missing Data:** Columns with nulls and their percentage.
   - **Data Types:** Flags for mismatched types (e.g., dates or numbers stored as strings).
   - **Duplicates:** Count of duplicate records or non-unique keys.
   - **Outliers/Range:** Min, max, and distinct counts for key categorical fields.

---

## 2. Immutable Raw Data Rule

- **Raw Data is Read-Only:** Never modify, overwrite, or delete original source files.
- Always write cleaned or transformed datasets to a separate file or directory (e.g., `data/processed/`, `cleaned_<filename>`).
- If interim temporary files are needed, clean them up or store them in a dedicated scratch directory.

---

## 3. Transformation & Audit Logging

Every data transformation must be observable and reproducible:

1. **Row Count Tracking:**
   - Track row counts before and after every major step (filter, join, deduplication).
   - *Rule:* Any unexpected row explosion after a `merge`/`join` is treated as a Cartesian bug until proven otherwise.
2. **Explicit Drop Reasons (Audit Log):**
   - Whenever rows are filtered or dropped, document the exact reason and count:
     - e.g., *"Dropped 42 rows where `email` is null."*
     - e.g., *"Dropped 15 rows with `transaction_date` outside target range 2026-01-01 to 2026-12-31."*
3. **Reproducibility & Determinism:**
   - Set random seeds explicitly for any stochastic operations (e.g., train/test split, sampling: `random_state=42`).
   - The entire transformation must run cleanly from start to finish via a single script.

---

## 4. Schema & Data Integrity Contracts

Before saving the final output:
1. **Schema Validation:** Ensure output column names, data types, and nullability constraints match expected specifications.
2. **Key Uniqueness:** If a column is intended as a primary/foreign key, assert uniqueness (`assert df['id'].is_unique`).
3. **Spot-Check:** Manually verify 3 to 5 sample rows end-to-end to ensure transformation logic matches business expectations.
4. **Summary Report:** Report final row count delta (`Input: X rows -> Output: Y rows (Z dropped)`).
