import pandas as pd

FILE = "data/processed/district_coordinates.csv"

df = pd.read_csv(FILE)

print("\n===== COORDINATE VALIDATION =====")

print("Total records:", len(df))

success = df[df["status"] == "success"].copy()
failed = df[df["status"] != "success"].copy()

print("Successful:", len(success))
print("Failed:", len(failed))


# -------------------------------------
# FAILED DISTRICTS
# -------------------------------------

print("\n===== NOT FOUND DISTRICTS =====")

if len(failed) == 0:
    print("None")
else:
    print(
        failed[
            [
                "State_Name",
                "District_Name"
            ]
        ].to_string(index=False)
    )

    failed[
        [
            "State_Name",
            "District_Name"
        ]
    ].to_csv(
        "data/processed/district_coordinates_failed.csv",
        index=False
    )


# -------------------------------------
# CHECK INDIA COORDINATE RANGE
# Approximate bounding box
# -------------------------------------

outside_india = success[
    (success["latitude"] < 6)
    | (success["latitude"] > 38)
    | (success["longitude"] < 68)
    | (success["longitude"] > 98)
]

print("\n===== COORDINATES OUTSIDE INDIA RANGE =====")

print("Count:", len(outside_india))

if len(outside_india) > 0:

    print(
        outside_india[
            [
                "State_Name",
                "District_Name",
                "latitude",
                "longitude",
                "display_name"
            ]
        ].to_string(index=False)
    )


# -------------------------------------
# DUPLICATE COORDINATES
# -------------------------------------

duplicates = success[
    success.duplicated(
        subset=[
            "latitude",
            "longitude"
        ],
        keep=False
    )
].sort_values(
    [
        "latitude",
        "longitude"
    ]
)

print("\n===== DUPLICATE COORDINATES =====")

print("Rows:", len(duplicates))

if len(duplicates) > 0:

    print(
        duplicates[
            [
                "State_Name",
                "District_Name",
                "latitude",
                "longitude",
                "display_name"
            ]
        ].to_string(index=False)
    )


# -------------------------------------
# SAMPLE SUCCESSFUL LOCATIONS
# -------------------------------------

print("\n===== SAMPLE SUCCESSFUL LOCATIONS =====")

print(
    success[
        [
            "State_Name",
            "District_Name",
            "latitude",
            "longitude",
            "display_name"
        ]
    ]
    .sample(
        min(20, len(success)),
        random_state=42
    )
    .to_string(index=False)
)


print("\nValidation complete.")