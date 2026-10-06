\
from pathlib import Path
import requests
import pandas as pd

OUT = Path("data/raw/crop_production.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

# This is a public mirror of the Government of India OGD crop production dataset.
# Official source page:
# https://www.data.gov.in/resource/district-wise-season-wise-crop-production-statistics-1997
#
# Mirror is used only so this script can download a plain CSV directly.
URL = (
    "https://raw.githubusercontent.com/"
    "JitendraAmbekar/india-crop-production-analysis/"
    "main/crop_production.csv"
)

print("Downloading real crop-production records...")
print("Official source: data.gov.in")
print("Destination:", OUT)

r = requests.get(URL, timeout=120)
r.raise_for_status()
OUT.write_bytes(r.content)

df = pd.read_csv(OUT)

print("\nDownload complete.")
print("Rows:", len(df))
print("Columns:", list(df.columns))
print("\nFirst 5 rows:")
print(df.head())
