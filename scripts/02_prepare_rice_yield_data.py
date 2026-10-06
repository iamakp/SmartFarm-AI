\
from pathlib import Path
import pandas as pd

RAW = Path("data/raw/crop_production.csv")
OUT = Path("data/processed/rice_yield.csv")

if not RAW.exists():
    raise FileNotFoundError(
        "Run python 00_download_real_crop_data.py first."
    )

df = pd.read_csv(RAW)

# Clean column text
for col in ["State_Name", "District_Name", "Season", "Crop"]:
    df[col] = df[col].astype(str).str.strip()

# First real model focuses on one crop: Rice.
# Reason: production units and agronomic behaviour can differ strongly by crop.
df = df[df["Crop"].str.lower() == "rice"].copy()

# Keep valid observations
df = df.dropna(
    subset=[
        "State_Name", "District_Name", "Crop_Year",
        "Season", "Area", "Production"
    ]
)

df = df[(df["Area"] > 0) & (df["Production"] >= 0)].copy()

# Target: tonnes per hectare
df["Yield"] = df["Production"] / df["Area"]

# Remove only clearly unusable/infinite values
df = df[df["Yield"].notna()]
df = df[df["Yield"] >= 0]

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)

print("\n===== RICE DATASET PREPARED =====")
print("Rows:", len(df))
print("Years:", int(df["Crop_Year"].min()), "to", int(df["Crop_Year"].max()))
print("States:", df["State_Name"].nunique())
print("Districts:", df["District_Name"].nunique())
print("\nYield summary (tonnes/hectare):")
print(df["Yield"].describe())
print("\nSaved:", OUT)
