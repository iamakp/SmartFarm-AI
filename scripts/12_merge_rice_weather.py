from pathlib import Path
import pandas as pd


RICE_FILE = Path(
    "data/processed/rice_yield_clean.csv"
)

WEATHER_FILE = Path(
    "data/processed/district_year_weather_features.csv"
)

OUTPUT_FILE = Path(
    "data/processed/rice_with_weather.csv"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

rice = pd.read_csv(RICE_FILE)
weather = pd.read_csv(WEATHER_FILE)

print("\n===== INPUT DATA =====")

print("Rice rows:", len(rice))
print("Weather rows:", len(weather))


# --------------------------------------------------
# PREPARE MERGE KEY
# --------------------------------------------------

# Rice uses Crop_Year
# Weather uses Year

weather = weather.rename(
    columns={
        "Year": "Crop_Year"
    }
)


# --------------------------------------------------
# MERGE
# --------------------------------------------------

merged = rice.merge(
    weather,
    on=[
        "State_Name",
        "District_Name",
        "Crop_Year"
    ],
    how="left",
    validate="many_to_one"
)


print("\n===== MERGE RESULT =====")

print("Rows after merge:", len(merged))


# --------------------------------------------------
# CHECK MATCH RATE
# --------------------------------------------------

weather_marker = "Annual_Temp_Mean"

matched = merged[
    weather_marker
].notna().sum()

unmatched = merged[
    weather_marker
].isna().sum()

match_rate = (
    matched / len(merged)
) * 100


print("Matched rows:", matched)
print("Unmatched rows:", unmatched)

print(
    f"Weather match rate: {match_rate:.2f}%"
)


# --------------------------------------------------
# SHOW UNMATCHED IF ANY
# --------------------------------------------------

if unmatched > 0:

    missing = (
        merged[
            merged[
                weather_marker
            ].isna()
        ][
            [
                "State_Name",
                "District_Name",
                "Crop_Year"
            ]
        ]
        .drop_duplicates()
    )

    print(
        "\n===== UNMATCHED LOCATIONS ====="
    )

    print(
        missing.to_string(
            index=False
        )
    )


# --------------------------------------------------
# FINAL MISSING VALUES
# --------------------------------------------------

print(
    "\nTotal missing values after merge:",
    merged.isna().sum().sum()
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

merged.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    "\nSaved:",
    OUTPUT_FILE
)