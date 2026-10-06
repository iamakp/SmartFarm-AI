import pandas as pd

FILE = "data/processed/rice_yield_clean.csv"

df = pd.read_csv(FILE)

# Remove accidental spaces
df["Season"] = df["Season"].astype(str).str.strip()

print("\n===== UNIQUE RICE SEASONS =====")

print(df["Season"].value_counts())

print("\nNumber of unique seasons:")
print(df["Season"].nunique())

print("\nExact season names:")
for season in sorted(df["Season"].unique()):
    print(repr(season))