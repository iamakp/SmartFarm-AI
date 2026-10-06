import pandas as pd

INPUT_FILE = "data/processed/rice_yield.csv"
OUTPUT_FILE = "data/processed/rice_yield_clean.csv"

df = pd.read_csv(INPUT_FILE)

print("Original rows:", len(df))

# Keep a copy of extreme records for documentation
extreme = df[df["Yield"] > 20]

print("\n===== EXCLUDED EXTREME RECORDS =====")
print(
    extreme[
        [
            "State_Name",
            "District_Name",
            "Crop_Year",
            "Season",
            "Area",
            "Production",
            "Yield"
        ]
    ].to_string(index=False)
)

# Conservative cleaning:
# remove only obviously extreme yield records
clean_df = df[df["Yield"] <= 20].copy()

print("\nRows removed:", len(df) - len(clean_df))
print("Rows remaining:", len(clean_df))

print("\n===== CLEAN YIELD SUMMARY =====")
print(clean_df["Yield"].describe())

clean_df.to_csv(OUTPUT_FILE, index=False)

print("\nSaved:", OUTPUT_FILE)