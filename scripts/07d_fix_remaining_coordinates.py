from pathlib import Path
import time
import requests
import pandas as pd


INPUT_FILE = Path(
    "data/processed/district_coordinates_final.csv"
)

OUTPUT_FILE = Path(
    "data/processed/district_coordinates_final_v2.csv"
)


# --------------------------------------------------
# ALTERNATIVE / CURRENT DISTRICT NAMES
# Original dataset names are NOT changed.
# These names are used only for geocoding.
# --------------------------------------------------

ALIASES = {

    ("Assam", "KAMRUP METRO"):
        ["Kamrup Metropolitan", "Kamrup Metro"],

    ("Bihar", "KAIMUR (BHABUA)"):
        ["Kaimur", "Kaimur Bhabua"],

    ("Bihar", "PURBI CHAMPARAN"):
        ["East Champaran", "Purbi Champaran"],

    ("Chhattisgarh", "KOREA"):
        ["Koriya", "Korea"],

    (
        "Dadra and Nagar Haveli",
        "DADRA AND NAGAR HAVELI"
    ):
        ["Dadra and Nagar Haveli"],

    ("Karnataka", "BAGALKOT"):
        ["Bagalkote", "Bagalkot"],

    ("Karnataka", "BELGAUM"):
        ["Belagavi", "Belgaum"],

    ("Karnataka", "BELLARY"):
        ["Ballari", "Bellary"],

    ("Karnataka", "CHIKBALLAPUR"):
        [
            "Chikkaballapur",
            "Chikkaballapura",
            "Chikballapur"
        ],

    ("Karnataka", "CHIKMAGALUR"):
        [
            "Chikkamagaluru",
            "Chikmagalur"
        ],

    ("Karnataka", "MYSORE"):
        ["Mysuru", "Mysore"],

    ("Maharashtra", "AURANGABAD"):
        [
            "Chhatrapati Sambhajinagar",
            "Aurangabad"
        ],

    ("Odisha", "DEOGARH"):
        ["Deogarh", "Debagarh"],

    ("Odisha", "NABARANGPUR"):
        ["Nabarangpur"],

    ("Odisha", "SONEPUR"):
        ["Subarnapur", "Sonepur"],

    ("Puducherry", "MAHE"):
        ["Mahe", "Mahé"],

    ("Puducherry", "PONDICHERRY"):
        ["Puducherry", "Pondicherry"],

    ("Punjab", "FIROZEPUR"):
        ["Ferozepur", "Firozpur"],

    ("Rajasthan", "DHOLPUR"):
        ["Dholpur"],

    # Historical Sikkim districts.
    # Dataset is 1997-2015, so we retain
    # historical district identity.
    ("Sikkim", "EAST DISTRICT"):
        [
            "East Sikkim",
            "East District Sikkim"
        ],

    ("Sikkim", "WEST DISTRICT"):
        [
            "West Sikkim",
            "West District Sikkim"
        ],

    ("Tamil Nadu", "TUTICORIN"):
        [
            "Thoothukudi",
            "Tuticorin"
        ],

    ("Tamil Nadu", "VILLUPURAM"):
        [
            "Viluppuram",
            "Villupuram"
        ],

    ("Tripura", "SEPAHIJALA"):
        [
            "Sepahijala",
            "Sipahijala"
        ],

    ("Uttar Pradesh", "SHRAVASTI"):
        [
            "Shravasti",
            "Shrawasti"
        ],

    ("Uttar Pradesh", "SIDDHARTH NAGAR"):
        [
            "Siddharthnagar",
            "Siddharth Nagar"
        ],

    ("West Bengal", "COOCHBEHAR"):
        [
            "Cooch Behar",
            "Coochbehar"
        ],

    ("West Bengal", "MEDINIPUR EAST"):
        [
            "Purba Medinipur",
            "East Medinipur"
        ],

    ("West Bengal", "MEDINIPUR WEST"):
        [
            "Paschim Medinipur",
            "West Medinipur"
        ],
}


# --------------------------------------------------
# LOAD EXISTING RESULTS
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

print("Total records:", len(df))

unresolved_mask = (
    df["status"] != "verified_admin"
)

print(
    "Currently unresolved:",
    unresolved_mask.sum()
)


# --------------------------------------------------
# GEOCODING
# --------------------------------------------------

def geocode_alias(state, names):

    url = (
        "https://nominatim.openstreetmap.org/search"
    )

    headers = {
        "User-Agent":
        "SmartFarmAI-Academic-Project/1.0"
    }

    for name in names:

        queries = [

            f"{name} district, {state}, India",

            f"{name}, {state}, India"
        ]

        for query in queries:

            print("Trying:", query)

            params = {
                "q": query,
                "format": "json",
                "limit": 10,
                "countrycodes": "in",
                "addressdetails": 1
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

                for candidate in candidates:

                    category = str(
                        candidate.get(
                            "category",
                            candidate.get(
                                "class",
                                ""
                            )
                        )
                    ).lower()

                    place_type = str(
                        candidate.get(
                            "type",
                            ""
                        )
                    ).lower()

                    address_type = str(
                        candidate.get(
                            "addresstype",
                            ""
                        )
                    ).lower()

                    admin_result = (

                        category == "boundary"

                        or place_type
                        == "administrative"

                        or address_type in [
                            "state_district",
                            "county",
                            "district"
                        ]
                    )

                    if admin_result:

                        return {

                            "latitude":
                                float(
                                    candidate["lat"]
                                ),

                            "longitude":
                                float(
                                    candidate["lon"]
                                ),

                            "display_name":
                                candidate[
                                    "display_name"
                                ],

                            "query_used":
                                query,

                            "geo_type":
                                place_type,

                            "address_type":
                                address_type,

                            "status":
                                "verified_admin"
                        }

            except Exception as e:

                print(
                    "Request error:",
                    str(e)
                )

                time.sleep(3)

            time.sleep(1.1)

    return None


# --------------------------------------------------
# RETRY ONLY UNRESOLVED ROWS
# --------------------------------------------------

for index, row in df[
    unresolved_mask
].iterrows():

    state = row["State_Name"]
    district = row["District_Name"]

    print(
        "\n================================"
    )

    print(
        district,
        ",",
        state
    )

    names = ALIASES.get(
        (state, district),
        [district.title()]
    )

    result = geocode_alias(
        state,
        names
    )

    if result is not None:

        print(
            "FIXED:",
            result["display_name"]
        )

        print(
            "Coordinates:",
            result["latitude"],
            result["longitude"]
        )

        for key, value in result.items():

            df.at[
                index,
                key
            ] = value

    else:

        print(
            "STILL UNRESOLVED"
        )

    # Save continuously
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

resolved = (
    df["status"]
    == "verified_admin"
).sum()

unresolved = (
    df["status"]
    != "verified_admin"
).sum()


print(
    "\n===== REPAIR SUMMARY ====="
)

print(
    "Total:",
    len(df)
)

print(
    "Verified:",
    resolved
)

print(
    "Still unresolved:",
    unresolved
)


print(
    "\n===== REMAINING ====="
)

remaining = df[
    df["status"]
    != "verified_admin"
]

if len(remaining) == 0:

    print(
        "NONE - all coordinates resolved."
    )

else:

    print(
        remaining[
            [
                "State_Name",
                "District_Name"
            ]
        ].to_string(index=False)
    )


print(
    "\nSaved:",
    OUTPUT_FILE
)