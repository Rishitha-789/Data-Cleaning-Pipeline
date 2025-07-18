import pandas as pd
import numpy as np
import os

# 1. Load Data
def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    df = pd.read_csv(filepath)
    print("Data loaded successfully.")
    return df

# 2. Summary Printer
def summarize_data(df, title=""):
    print(f"\n{title} Summary:")
    print(df.info())
    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDescriptive stats (numeric only):")
    numeric_cols = df.select_dtypes(include=[np.number])
    if not numeric_cols.empty:
        print(numeric_cols.describe())
    else:
        print("No numeric columns found.")

# 3. Handle Missing Values
def handle_missing(df, strategy='mean'):
    df_cleaned = df.copy()
    for col in df_cleaned.columns:
        if pd.api.types.is_numeric_dtype(df_cleaned[col]):
            if strategy == 'mean':
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].mean())
            elif strategy == 'median':
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())
            elif strategy == 'drop':
                df_cleaned = df_cleaned.dropna(subset=[col])
        else:
            df_cleaned[col] = df_cleaned[col].fillna("unknown")
    return df_cleaned

# 4. Remove Outliers (IQR Method)
def remove_outliers(df, z_thresh=1.5):
    df_cleaned = df.copy()
    numeric_cols = df_cleaned.select_dtypes(include=np.number).columns
    original_len = len(df_cleaned)

    for col in numeric_cols:
        Q1 = df_cleaned[col].quantile(0.25)
        Q3 = df_cleaned[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - z_thresh * IQR
        upper = Q3 + z_thresh * IQR
        df_cleaned = df_cleaned[(df_cleaned[col] >= lower) & (df_cleaned[col] <= upper)]

    removed = original_len - len(df_cleaned)
    print(f"Outlier rows removed: {removed}")
    return df_cleaned

# 5. Normalize Data Formats
def normalize_format(df):
    df_cleaned = df.copy()
    for col in df_cleaned.columns:
        if df_cleaned[col].dtype == "object":
            # Standardize text
            df_cleaned[col] = df_cleaned[col].astype(str).str.strip().str.lower()

            # Try convert to numeric, set errors='coerce' so bad values become NaN
            converted = pd.to_numeric(df_cleaned[col], errors='coerce')

            # Only assign if at least some values were converted to numbers
            if converted.notna().sum() > 0:
                df_cleaned[col] = converted
                print(f"Converted column to numeric: {col}")
    return df_cleaned


# 6. Cleaning Pipeline
def clean_data(filepath):
    df = load_data(filepath)
    if df is None:
        return

    summarize_data(df, "Original Data")

    df = normalize_format(df)
    df = handle_missing(df, strategy='mean')
    df = remove_outliers(df)

    summarize_data(df, "Cleaned Data")

    cleaned_file = filepath.replace(".csv", "_cleaned.csv")
    df.to_csv(cleaned_file, index=False)
    print(f"\nCleaned data saved to: {cleaned_file}")

# 7. Run Script
if __name__ == "__main__":
    clean_data("data.csv")
