import pandas as pd
from pathlib import Path


FILE = Path(
    "data/processed/nasa_monthly_weather.csv"
)

BAD_FILE = Path(
    "data/processed/nasa_weather_problem_rows.csv"
)


df = pd.read_csv(FILE)


print("\n===== BASIC CHECK =====")

print("Rows:", len(df))

print(
    "District-state combinations:",
    df[
        ["State_Name", "District_Name"]
    ].drop_duplicates().shape[0]
)

print(
    "Years:",
    df["Year"].min(),
    "to",
    df["Year"].max()
)


# --------------------------------------------------
# DUPLICATES
# --------------------------------------------------

key_columns = [
    "State_Name",
    "District_Name",
    "Year",
    "Month"
]

duplicate_count = df.duplicated(
    subset=key_columns
).sum()


print("\n===== DUPLICATES =====")

print(
    "Duplicate district-year-month rows:",
    duplicate_count
)


# --------------------------------------------------
# MISSING VALUES
# --------------------------------------------------

weather_columns = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "PRECTOTCORR"
]


print("\n===== MISSING VALUES =====")

print(
    df[weather_columns].isna().sum()
)


# --------------------------------------------------
# NASA FILL VALUES
# --------------------------------------------------
# NASA datasets can use large negative values
# such as -999 for unavailable data.

print("\n===== POSSIBLE FILL VALUES =====")

for column in weather_columns:

    bad = (
        df[column] <= -900
    ).sum()

    print(
        column,
        ":",
        bad
    )


# --------------------------------------------------
# MONTH COMPLETENESS
# --------------------------------------------------

monthly_counts = (
    df.groupby(
        [
            "State_Name",
            "District_Name",
            "Year"
        ]
    )
    .size()
)

incomplete = monthly_counts[
    monthly_counts != 12
]


print("\n===== MONTH COMPLETENESS =====")

print(
    "District-years without exactly 12 months:",
    len(incomplete)
)


if len(incomplete) > 0:

    print(
        incomplete.head(30)
    )


# --------------------------------------------------
# WEATHER RANGE CHECKS
# --------------------------------------------------

problem_mask = (

    (df["RH2M"] < 0)
    |
    (df["RH2M"] > 100)

    |
    (df["PRECTOTCORR"] < 0)

    |
    (df["T2M"] < -60)
    |
    (df["T2M"] > 60)

    |
    (df["T2M_MIN"] < -70)
    |
    (df["T2M_MIN"] > 60)

    |
    (df["T2M_MAX"] < -60)
    |
    (df["T2M_MAX"] > 70)

    |
    (df["T2M_MIN"] > df["T2M"])

    |
    (df["T2M"] > df["T2M_MAX"])
)


problems = df[
    problem_mask
].copy()


print("\n===== RANGE / LOGIC PROBLEMS =====")

print(
    "Problem rows:",
    len(problems)
)


if len(problems) > 0:

    problems.to_csv(
        BAD_FILE,
        index=False
    )

    print(
        problems.head(30).to_string(
            index=False
        )
    )

    print(
        "\nProblem rows saved:",
        BAD_FILE
    )


# --------------------------------------------------
# SUMMARY STATISTICS
# --------------------------------------------------

print("\n===== WEATHER SUMMARY =====")

print(
    df[weather_columns].describe()
)


print(
    "\nValidation complete."
)