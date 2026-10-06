\
from pathlib import Path
import pandas as pd

PATH = Path("data/raw/crop_production.csv")

if not PATH.exists():
    raise FileNotFoundError(
        "Real dataset not found. Run: python 00_download_real_crop_data.py"
    )

df = pd.read_csv(PATH)

print("\n===== REAL DATA VALIDATION =====")
print("Rows:", len(df))
print("Columns:", list(df.columns))

print("\nMissing values:")
print(df.isna().sum())

print("\nYears:")
print(df["Crop_Year"].min(), "to", df["Crop_Year"].max())

print("\nStates:", df["State_Name"].nunique())
print("Districts:", df["District_Name"].nunique())
print("Crops:", df["Crop"].nunique())

print("\nMost common crops:")
print(df["Crop"].astype(str).str.strip().value_counts().head(20))

print("\nSample:")
print(df.head())
