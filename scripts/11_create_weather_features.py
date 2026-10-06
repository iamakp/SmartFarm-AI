import calendar
from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "data/processed/nasa_monthly_weather.csv"
)

OUTPUT_FILE = Path(
    "data/processed/district_year_weather_features.csv"
)


# --------------------------------------------------
# LOAD MONTHLY WEATHER
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("\n===== MONTHLY WEATHER LOADED =====")
print("Rows:", len(df))


# --------------------------------------------------
# CONVERT PRECIPITATION RATE TO MONTHLY AMOUNT
# --------------------------------------------------

# PRECTOTCORR monthly value is treated as the
# monthly mean daily precipitation rate.
#
# Estimated rainfall amount for that month:
#
# rainfall_month = PRECTOTCORR * days_in_month

df["Days_In_Month"] = df.apply(
    lambda row: calendar.monthrange(
        int(row["Year"]),
        int(row["Month"])
    )[1],
    axis=1
)

df["Rainfall_mm"] = (
    df["PRECTOTCORR"]
    * df["Days_In_Month"]
)


# --------------------------------------------------
# DEFINE CLIMATE PERIODS
# --------------------------------------------------

# These are climate windows, NOT claimed to be
# exact crop growing seasons for every state.

df["Period"] = "Other"

df.loc[
    df["Month"].isin([3, 4, 5]),
    "Period"
] = "PreMonsoon"

df.loc[
    df["Month"].isin([6, 7, 8, 9]),
    "Period"
] = "Monsoon"

df.loc[
    df["Month"].isin([10, 11]),
    "Period"
] = "PostMonsoon"

df.loc[
    df["Month"].isin([12, 1, 2]),
    "Period"
] = "Winter"


# --------------------------------------------------
# ANNUAL FEATURES
# --------------------------------------------------

annual = (
    df.groupby(
        [
            "State_Name",
            "District_Name",
            "Year"
        ]
    )
    .agg(

        Annual_Temp_Mean=(
            "T2M",
            "mean"
        ),

        Annual_Temp_Max_Mean=(
            "T2M_MAX",
            "mean"
        ),

        Annual_Temp_Min_Mean=(
            "T2M_MIN",
            "mean"
        ),

        Annual_Humidity_Mean=(
            "RH2M",
            "mean"
        ),

        Annual_Rainfall_mm=(
            "Rainfall_mm",
            "sum"
        )

    )
    .reset_index()
)


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def aggregate_period(
    dataframe,
    period_name,
    prefix
):

    temp = dataframe[
        dataframe["Period"]
        == period_name
    ]

    result = (
        temp.groupby(
            [
                "State_Name",
                "District_Name",
                "Year"
            ]
        )
        .agg(

            Temp_Mean=(
                "T2M",
                "mean"
            ),

            Temp_Max_Mean=(
                "T2M_MAX",
                "mean"
            ),

            Temp_Min_Mean=(
                "T2M_MIN",
                "mean"
            ),

            Humidity_Mean=(
                "RH2M",
                "mean"
            ),

            Rainfall_mm=(
                "Rainfall_mm",
                "sum"
            )

        )
        .reset_index()
    )

    result = result.rename(
        columns={

            "Temp_Mean":
                f"{prefix}_Temp_Mean",

            "Temp_Max_Mean":
                f"{prefix}_Temp_Max_Mean",

            "Temp_Min_Mean":
                f"{prefix}_Temp_Min_Mean",

            "Humidity_Mean":
                f"{prefix}_Humidity_Mean",

            "Rainfall_mm":
                f"{prefix}_Rainfall_mm"
        }
    )

    return result


# --------------------------------------------------
# PERIOD FEATURES
# --------------------------------------------------

premonsoon = aggregate_period(
    df,
    "PreMonsoon",
    "PreMonsoon"
)

monsoon = aggregate_period(
    df,
    "Monsoon",
    "Monsoon"
)

postmonsoon = aggregate_period(
    df,
    "PostMonsoon",
    "PostMonsoon"
)

winter = aggregate_period(
    df,
    "Winter",
    "Winter"
)


# --------------------------------------------------
# MERGE ALL FEATURES
# --------------------------------------------------

weather = annual.copy()

for feature_df in [
    premonsoon,
    monsoon,
    postmonsoon,
    winter
]:

    weather = weather.merge(
        feature_df,
        on=[
            "State_Name",
            "District_Name",
            "Year"
        ],
        how="left"
    )


# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

print("\n===== WEATHER FEATURES CREATED =====")

print(
    "Rows:",
    len(weather)
)

print(
    "Districts:",
    weather[
        [
            "State_Name",
            "District_Name"
        ]
    ]
    .drop_duplicates()
    .shape[0]
)

print(
    "Years:",
    weather["Year"].min(),
    "to",
    weather["Year"].max()
)

print(
    "\nMissing values:",
    weather.isna().sum().sum()
)


print("\n===== SAMPLE =====")

print(
    weather.head().to_string(
        index=False
    )
)


print("\n===== RAINFALL SUMMARY =====")

print(
    weather[
        [
            "Annual_Rainfall_mm",
            "Monsoon_Rainfall_mm",
            "PreMonsoon_Rainfall_mm"
        ]
    ].describe()
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

weather.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    "\nSaved:",
    OUTPUT_FILE
)