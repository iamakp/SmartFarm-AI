from pathlib import Path
import time
import requests
import pandas as pd


# -----------------------------------------
# FILE PATHS
# -----------------------------------------

RICE_DATA = Path("data/processed/rice_yield_clean.csv")
OUTPUT_FILE = Path("data/processed/district_coordinates.csv")


# -----------------------------------------
# LOAD RICE DATA
# -----------------------------------------

df = pd.read_csv(RICE_DATA)

districts = (
    df[["State_Name", "District_Name"]]
    .drop_duplicates()
    .sort_values(["State_Name", "District_Name"])
    .reset_index(drop=True)
)

print("Unique state-district combinations:", len(districts))


# -----------------------------------------
# LOAD PREVIOUS PROGRESS
# -----------------------------------------

if OUTPUT_FILE.exists():

    old = pd.read_csv(OUTPUT_FILE)

    completed = set(
        zip(
            old["State_Name"],
            old["District_Name"]
        )
    )

    results = old.to_dict("records")

    print(
        "Previous records found:",
        len(results)
    )

else:

    completed = set()
    results = []


# -----------------------------------------
# GEOCODING FUNCTION
# -----------------------------------------

def geocode_location(state, district):

    base_url = "https://nominatim.openstreetmap.org/search"

    headers = {
        "User-Agent": "SmartFarmAI-Academic-Project/1.0"
    }

    # First query
    queries = [
        f"{district}, {state}, India",

        # Fallback:
        # remove word DISTRICT if present
        f"{district.replace('DISTRICT', '').strip()}, {state}, India"
    ]

    for query in queries:

        params = {
            "q": query,
            "format": "json",
            "limit": 1,
            "countrycodes": "in"
        }

        try:

            response = requests.get(
                base_url,
                params=params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            if data:

                return {
                    "latitude": float(data[0]["lat"]),
                    "longitude": float(data[0]["lon"]),
                    "display_name": data[0]["display_name"],
                    "query_used": query,
                    "status": "success"
                }

        except Exception as e:

            print(
                "Request error:",
                district,
                "-",
                str(e)
            )

            time.sleep(5)

    return {
        "latitude": None,
        "longitude": None,
        "display_name": None,
        "query_used": None,
        "status": "not_found"
    }


# -----------------------------------------
# PROCESS DISTRICTS
# -----------------------------------------

total = len(districts)

for index, row in districts.iterrows():

    state = row["State_Name"]
    district = row["District_Name"]

    key = (state, district)

    # Already processed
    if key in completed:
        continue

    print(
        f"\n[{index + 1}/{total}] "
        f"{district}, {state}"
    )

    geo = geocode_location(
        state,
        district
    )

    record = {
        "State_Name": state,
        "District_Name": district,
        **geo
    }

    results.append(record)

    print(
        "Status:",
        geo["status"]
    )

    if geo["status"] == "success":

        print(
            "Coordinates:",
            geo["latitude"],
            geo["longitude"]
        )

    # Save progress immediately
    output_df = pd.DataFrame(results)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # Be respectful to public geocoding service
    time.sleep(1.2)


# -----------------------------------------
# FINAL SUMMARY
# -----------------------------------------

final_df = pd.DataFrame(results)

print("\n===== GEOCODING COMPLETE =====")

print(
    "Total:",
    len(final_df)
)

print(
    "Success:",
    (
        final_df["status"]
        == "success"
    ).sum()
)

print(
    "Not found:",
    (
        final_df["status"]
        == "not_found"
    ).sum()
)

print(
    "\nSaved:",
    OUTPUT_FILE
)