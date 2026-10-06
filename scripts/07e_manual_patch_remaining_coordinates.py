from pathlib import Path
import pandas as pd


INPUT_FILE = Path(
    "data/processed/district_coordinates_final_v2.csv"
)

OUTPUT_FILE = Path(
    "data/processed/district_coordinates_complete.csv"
)


df = pd.read_csv(INPUT_FILE)


# Representative district points.
# These are manually sourced only for locations
# that automated administrative geocoding failed on.

MANUAL_COORDS = {

    ("Dadra and Nagar Haveli", "DADRA AND NAGAR HAVELI"):
        (20.203750, 73.065833),

    ("Odisha", "NABARANGPUR"):
        (19.616667, 82.375000),

    ("Puducherry", "MAHE"):
        (11.708333, 75.533333),

    ("Rajasthan", "DHOLPUR"):
        (26.702519, 77.893392),

    ("Sikkim", "EAST DISTRICT"):
        (27.333333, 88.666667),

    ("Sikkim", "WEST DISTRICT"):
        (27.333333, 88.250000),

    ("Uttar Pradesh", "SHRAVASTI"):
        (27.507500, 82.004700),
}


print("\n===== MANUAL PATCH =====")

patched = 0


for (state, district), (lat, lon) in MANUAL_COORDS.items():

    mask = (
        (df["State_Name"] == state)
        &
        (df["District_Name"] == district)
    )

    if mask.sum() == 0:

        print(
            "NOT FOUND IN FILE:",
            state,
            district
        )

        continue

    df.loc[mask, "latitude"] = lat
    df.loc[mask, "longitude"] = lon

    df.loc[
        mask,
        "display_name"
    ] = f"{district}, {state}, India"

    df.loc[
        mask,
        "query_used"
    ] = "manual_verified_source"

    # Keep provenance clear:
    # this was manually patched,
    # not returned by Nominatim.
    df.loc[
        mask,
        "status"
    ] = "manual_verified"

    print(
        f"FIXED: {district}, {state}"
    )

    print(
        f"       {lat}, {lon}"
    )

    patched += 1


# ----------------------------------
# VALIDATE
# ----------------------------------

missing_coords = df[
    df["latitude"].isna()
    |
    df["longitude"].isna()
]


print("\n===== FINAL RESULT =====")

print("Total records:", len(df))

print(
    "Administrative verified:",
    (
        df["status"]
        == "verified_admin"
    ).sum()
)

print(
    "Manual verified:",
    (
        df["status"]
        == "manual_verified"
    ).sum()
)

print(
    "Missing coordinates:",
    len(missing_coords)
)


if len(missing_coords) > 0:

    print(
        missing_coords[
            [
                "State_Name",
                "District_Name",
                "status"
            ]
        ].to_string(index=False)
    )


df.to_csv(
    OUTPUT_FILE,
    index=False
)


print(
    "\nSaved:",
    OUTPUT_FILE
)