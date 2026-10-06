\
import requests
import pandas as pd
from io import StringIO
from pathlib import Path

print("\nNASA POWER - REAL WEATHER DOWNLOAD")
print("----------------------------------")
latitude = float(input("Latitude: "))
longitude = float(input("Longitude: "))
start = input("Start date YYYYMMDD: ").strip()
end = input("End date YYYYMMDD: ").strip()

parameters = "T2M,T2M_MAX,T2M_MIN,RH2M,PRECTOTCORR"

url = "https://power.larc.nasa.gov/api/temporal/daily/point"

params = {
    "parameters": parameters,
    "community": "AG",
    "longitude": longitude,
    "latitude": latitude,
    "start": start,
    "end": end,
    "format": "CSV",
}

print("\nFetching real NASA POWER weather data...")
r = requests.get(url, params=params, timeout=120)
r.raise_for_status()

# NASA CSV response starts with metadata lines.
lines = r.text.splitlines()
header_index = next(
    i for i, line in enumerate(lines)
    if line.startswith("YEAR,")
)

csv_text = "\n".join(lines[header_index:])
df = pd.read_csv(StringIO(csv_text))

out = Path(
    f"data/raw/nasa_weather_{latitude}_{longitude}_{start}_{end}.csv"
)
out.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out, index=False)

print("\nRows:", len(df))
print("Columns:", list(df.columns))
print(df.head())
print("\nSaved:", out)
