from pathlib import Path
import time
import requests
import pandas as pd


COORD_FILE = Path(
    "data/processed/district_coordinates_complete.csv"
)

OUTPUT_FILE = Path(
    "data/processed/nasa_monthly_weather.csv"
)

START_YEAR = 1997
END_YEAR = 2015

PARAMETERS = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "PRECTOTCORR"
]


# --------------------------------------------------
# LOAD DISTRICT COORDINATES
# --------------------------------------------------

coords = pd.read_csv(COORD_FILE)

print("District-state locations:", len(coords))


# --------------------------------------------------
# LOAD PREVIOUS PROGRESS
# --------------------------------------------------

if OUTPUT_FILE.exists():

    existing = pd.read_csv(OUTPUT_FILE)

    completed = set(
        zip(
            existing["State_Name"],
            existing["District_Name"]
        )
    )

    results = existing.to_dict("records")

    print(
        "Previously downloaded districts:",
        len(completed)
    )

else:

    completed = set()
    results = []


# --------------------------------------------------
# NASA POWER REQUEST
# --------------------------------------------------

def fetch_weather(lat, lon):

    url = (
        "https://power.larc.nasa.gov/"
        "api/temporal/monthly/point"
    )

    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": START_YEAR,
        "end": END_YEAR,
        "format": "JSON"
    }

    response = requests.get(
        url,
        params=params,
        timeout=90
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# PROCESS NASA JSON
# --------------------------------------------------

def parse_weather(
    data,
    state,
    district,
    latitude,
    longitude
):

    parameter_data = data[
        "properties"
    ][
        "parameter"
    ]

    rows = []

    # NASA keys look like:
    # 199701, 199702, ... 201512
    first_parameter = PARAMETERS[0]

    time_keys = parameter_data[
        first_parameter
    ].keys()

    for time_key in time_keys:

        # Annual value sometimes appears as YYYY13.
        # We only want months 01-12.
        if len(time_key) != 6:
            continue

        year = int(time_key[:4])
        month = int(time_key[4:])

        if month < 1 or month > 12:
            continue

        row = {
            "State_Name": state,
            "District_Name": district,
            "latitude": latitude,
            "longitude": longitude,
            "Year": year,
            "Month": month
        }

        for parameter in PARAMETERS:

            value = parameter_data[
                parameter
            ].get(
                time_key,
                None
            )

            row[parameter] = value

        rows.append(row)

    return rows


# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

total = len(coords)

for index, row in coords.iterrows():

    state = row["State_Name"]
    district = row["District_Name"]

    key = (state, district)

    if key in completed:
        continue

    latitude = row["latitude"]
    longitude = row["longitude"]

    print(
        f"\n[{index + 1}/{total}] "
        f"{district}, {state}"
    )

    try:

        data = fetch_weather(
            latitude,
            longitude
        )

        weather_rows = parse_weather(
            data,
            state,
            district,
            latitude,
            longitude
        )

        results.extend(weather_rows)

        print(
            "Monthly rows received:",
            len(weather_rows)
        )

        if len(weather_rows) > 0:

            sample = weather_rows[0]

            print(
                "Sample:",
                sample["Year"],
                sample["Month"],
                "T2M =",
                sample["T2M"],
                "Rain =",
                sample["PRECTOTCORR"]
            )

    except Exception as e:

        print(
            "ERROR:",
            district,
            "-",
            str(e)
        )

        # Do not mark failed district as completed.
        time.sleep(5)
        continue

    # Save progress after each district
    output_df = pd.DataFrame(results)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    completed.add(key)

    time.sleep(1)


# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

final_df = pd.DataFrame(results)

print("\n===== NASA WEATHER DOWNLOAD COMPLETE =====")

print(
    "Rows:",
    len(final_df)
)

print(
    "District-state combinations:",
    final_df[
        [
            "State_Name",
            "District_Name"
        ]
    ].drop_duplicates().shape[0]
)

print(
    "Years:",
    final_df["Year"].min(),
    "to",
    final_df["Year"].max()
)

print(
    "\nSaved:",
    OUTPUT_FILE
)