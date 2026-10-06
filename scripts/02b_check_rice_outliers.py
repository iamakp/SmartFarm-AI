import pandas as pd

df = pd.read_csv("data/processed/rice_yield.csv")

print("\n===== YIELD QUANTILES =====")
print(df["Yield"].quantile([
    0.90,
    0.95,
    0.99,
    0.995,
    0.999
]))

print("\n===== TOP 20 HIGHEST YIELDS =====")
cols = [
    "State_Name",
    "District_Name",
    "Crop_Year",
    "Season",
    "Area",
    "Production",
    "Yield"
]

print(
    df.sort_values("Yield", ascending=False)[cols]
      .head(20)
      .to_string(index=False)
)

print("\n===== ZERO YIELD RECORDS =====")
zero = df[df["Yield"] == 0]

print("Zero yield rows:", len(zero))
print(zero[cols].head(20).to_string(index=False))

print("\n===== YIELD > 10 TONNES/HECTARE =====")
high = df[df["Yield"] > 10]

print("Rows:", len(high))

print(
    high.sort_values("Yield", ascending=False)[cols]
        .to_string(index=False)
)
