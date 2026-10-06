from pathlib import Path
import time
import requests
import pandas as pd


INPUT_FILE = Path("data/processed/district_coordinates.csv")
OUTPUT_FILE = Path("data/processed/district_coordinates_final.csv")


# ------------------------------------------------
# OLD / DIFFERENT DISTRICT NAMES
# ------------------------------------------------

ALIASES = {

    "NICOBARS": "Nicobar",
    "SOUTH ANDAMANS": "South Andaman",

    "VISAKHAPATANAM": "Visakhapatnam",

    "DOHAD": "Dahod",

    "EAST SINGHBUM": "East Singhbhum",

    "DAKSHIN KANNAD": "Dakshina Kannada",
    "DAVANGERE": "Davanagere",
    "UTTAR KANNAD": "Uttara Kannada",

    "FIROZEPUR": "Ferozepur",

    "RANGAREDDI": "Ranga Reddy",

    "KUSHI NAGAR": "Kushinagar",
    "SANT KABEER NAGAR": "Sant Kabir Nagar",

    "RUDRA PRAYAG": "Rudraprayag",
    "UDAM SINGH NAGAR": "Udham Singh Nagar",
    "UTTAR KASHI": "Uttarkashi",

    "24 PARAGANAS NORTH": "North 24 Parganas",
    "24 PARAGANAS SOUTH": "South 24 Parganas",
}


# ------------------------------------------------
# LOAD CURRENT DATA
# ------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Total districts:", len(df))


# ------------------------------------------------
# GEOCODE ONLY ADMINISTRATIVE LOCATION
# ------------------------------------------------

def get_admin_coordinate(state, district):

    search_name = ALIASES.get(
        district,
        district.title()
    )

    url = "https://nominatim.openstreetmap.org/search"

    headers = {
        "User-Agent":
        "SmartFarmAI-Academic-Research/1.0"
    }

    # We explicitly use the word district
    queries = [

        f"{search_name} district, {state}, India",

        f"{search_name}, {state}, India"
    ]

    for query in queries:

        params = {
            "q": query,
            "format": "json",
            "limit": 5,
            "addressdetails": 1,
            "countrycodes": "in"
        }

        try:

            r = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=30
            )

            r.raise_for_status()

            candidates = r.json()

            # ----------------------------------
            # Prefer administrative boundaries
            # ----------------------------------

            for candidate in candidates:

                category = str(
                    candidate.get("class", "")
                ).lower()

                candidate_type = str(
                    candidate.get("type", "")
                ).lower()

                addresstype = str(
                    candidate.get(
                        "addresstype",
                        ""
                    )
                ).lower()

                valid_admin = (

                    category == "boundary"

                    or candidate_type
                    == "administrative"

                    or addresstype in [
                        "county",
                        "state_district"
                    ]
                )

                if valid_admin:

                    return {
                        "latitude":
                            float(candidate["lat"]),

                        "longitude":
                            float(candidate["lon"]),

                        "display_name":
                            candidate[
                                "display_name"
                            ],

                        "query_used":
                            query,

                        "geo_type":
                            candidate_type,

                        "address_type":
                            addresstype,

                        "status":
                            "verified_admin"
                    }

        except Exception as e:

            print(
                "Error:",
                district,
                str(e)
            )

            time.sleep(3)

    return {
        "latitude": None,
        "longitude": None,
        "display_name": None,
        "query_used": None,
        "geo_type": None,
        "address_type": None,
        "status": "not_found"
    }


# ------------------------------------------------
# PROCESS ALL DISTRICTS AGAIN
# ------------------------------------------------

results = []

total = len(df)

for i, row in df.iterrows():

    state = row["State_Name"]
    district = row["District_Name"]

    print(
        f"\n[{i + 1}/{total}] "
        f"{district}, {state}"
    )

    geo = get_admin_coordinate(
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

    if geo["status"] == "verified_admin":

        print(
            "Coordinates:",
            geo["latitude"],
            geo["longitude"]
        )

        print(
            "Matched:",
            geo["display_name"]
        )

    # Save after every request
    pd.DataFrame(
        results
    ).to_csv(
        OUTPUT_FILE,
        index=False
    )

    time.sleep(1.2)


# ------------------------------------------------
# SUMMARY
# ------------------------------------------------

final_df = pd.DataFrame(results)

verified = (
    final_df["status"]
    == "verified_admin"
).sum()

failed = (
    final_df["status"]
    != "verified_admin"
).sum()


print(
    "\n===== FINAL GEOCODING SUMMARY ====="
)

print(
    "Total:",
    len(final_df)
)

print(
    "Verified administrative locations:",
    verified
)

print(
    "Still unresolved:",
    failed
)

print(
    "\nSaved:",
    OUTPUT_FILE
)


print(
    "\n===== UNRESOLVED ====="
)

print(
    final_df[
        final_df["status"]
        != "verified_admin"
    ][
        [
            "State_Name",
            "District_Name"
        ]
    ].to_string(index=False)
)