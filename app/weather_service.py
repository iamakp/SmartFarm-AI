from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

import json
import pandas as pd


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

COORDINATES_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "district_coordinates_complete.csv"
)


# ==================================================
# LOAD DISTRICT COORDINATES
# ==================================================

if not COORDINATES_PATH.exists():
    raise RuntimeError(
        "district_coordinates_complete.csv not found."
    )


coordinates_df = pd.read_csv(
    COORDINATES_PATH
)


# ==================================================
# DETECT COLUMN NAMES
# ==================================================

def find_column(possible_names):

    columns_lower = {
        col.lower(): col
        for col in coordinates_df.columns
    }

    for name in possible_names:

        if name.lower() in columns_lower:

            return columns_lower[
                name.lower()
            ]

    raise RuntimeError(
        f"Could not find column from: {possible_names}"
    )


STATE_COL = find_column(
    [
        "State_Name",
        "State",
        "state"
    ]
)

DISTRICT_COL = find_column(
    [
        "District_Name",
        "District",
        "district"
    ]
)

LAT_COL = find_column(
    [
        "Latitude",
        "latitude",
        "lat"
    ]
)

LON_COL = find_column(
    [
        "Longitude",
        "longitude",
        "lon",
        "lng"
    ]
)


coordinates_df[STATE_COL] = (
    coordinates_df[STATE_COL]
    .astype(str)
    .str.strip()
)

coordinates_df[DISTRICT_COL] = (
    coordinates_df[DISTRICT_COL]
    .astype(str)
    .str.strip()
)


# ==================================================
# GET COORDINATES
# ==================================================

def get_coordinates(
    state,
    district
):

    state_normalized = (
        state
        .strip()
        .lower()
    )

    district_normalized = (
        district
        .strip()
        .lower()
    )


    matches = coordinates_df[

        (
            coordinates_df[STATE_COL]
            .str.lower()
            == state_normalized
        )

        &

        (
            coordinates_df[DISTRICT_COL]
            .str.lower()
            == district_normalized
        )

    ]


    if matches.empty:

        raise ValueError(
            "Coordinates not found for this district."
        )


    row = matches.iloc[0]


    return {
        "state":
            row[STATE_COL],

        "district":
            row[DISTRICT_COL],

        "latitude":
            float(row[LAT_COL]),

        "longitude":
            float(row[LON_COL])
    }


# ==================================================
# WEATHER API
# ==================================================

def fetch_weather(
    latitude,
    longitude
):

    base_url = (
        "https://api.open-meteo.com/v1/forecast"
    )


    params = {

        "latitude":
            latitude,

        "longitude":
            longitude,

        "current":
            ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m"
                ]
            ),

        "daily":
            ",".join(
                [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "et0_fao_evapotranspiration"
                ]
            ),

        "timezone":
            "auto",

        "forecast_days":
            7
    }


    url = (
        base_url
        + "?"
        + urlencode(params)
    )


    try:

        with urlopen(
            url,
            timeout=15
        ) as response:

            data = json.loads(
                response
                .read()
                .decode("utf-8")
            )


    except (
        HTTPError,
        URLError,
        TimeoutError
    ) as error:

        raise RuntimeError(
            f"Weather service unavailable: {error}"
        )


    return data


# ==================================================
# IRRIGATION WEATHER SIGNAL
# ==================================================

def create_irrigation_signal(
    weather
):

    current = weather.get(
        "current",
        {}
    )

    daily = weather.get(
        "daily",
        {}
    )


    precipitation = daily.get(
        "precipitation_sum",
        []
    )

    rain_probability = daily.get(
        "precipitation_probability_max",
        []
    )

    et0 = daily.get(
        "et0_fao_evapotranspiration",
        []
    )


    rain_next_48h = sum(
        value or 0
        for value in precipitation[:2]
    )


    today_rain_probability = (
        rain_probability[0]
        if rain_probability
        else 0
    )


    today_et0 = (
        et0[0]
        if et0
        else 0
    )


    temperature = current.get(
        "temperature_2m",
        0
    )

    humidity = current.get(
        "relative_humidity_2m",
        0
    )


    # ----------------------------------------------
    # RULE-BASED WEATHER ADVISORY
    # ----------------------------------------------

    if (
        rain_next_48h >= 15
        or
        (
            today_rain_probability >= 80
            and
            rain_next_48h >= 5
        )
    ):

        level = "LOW"

        message = (
            "Significant rainfall is expected. "
            "Avoid unnecessary irrigation and "
            "reassess field conditions after rain."
        )


    elif (
        rain_next_48h >= 5
        or
        today_rain_probability >= 60
    ):

        level = "LOW_TO_MODERATE"

        message = (
            "Some rainfall is expected. "
            "Avoid heavy irrigation and check "
            "field water level before irrigating."
        )


    elif (
        temperature >= 34
        or
        humidity <= 45
        or
        today_et0 >= 5
    ):

        level = "HIGHER_WEATHER_DEMAND"

        message = (
            "Little rainfall is expected and "
            "weather conditions may increase "
            "water demand. Check field moisture "
            "or standing water level before irrigation."
        )


    else:

        level = "MODERATE"

        message = (
            "No strong weather trigger detected. "
            "Monitor field moisture and crop stage "
            "before deciding irrigation."
        )


    return {

        "level":
            level,

        "message":
            message,

        "rain_next_48h_mm":
            round(
                rain_next_48h,
                2
            ),

        "today_rain_probability_percent":
            today_rain_probability,

        "today_reference_et0_mm":
            today_et0
    }


# ==================================================
# COMPLETE WEATHER RESPONSE
# ==================================================

def get_weather_for_district(
    state,
    district
):

    location = get_coordinates(
        state,
        district
    )


    weather = fetch_weather(
        location["latitude"],
        location["longitude"]
    )


    irrigation_signal = (
        create_irrigation_signal(
            weather
        )
    )


    daily = weather.get(
        "daily",
        {}
    )


    forecast = []


    dates = daily.get(
        "time",
        []
    )


    for i in range(
        len(dates)
    ):

        forecast.append(
            {

                "date":
                    dates[i],

                "temperature_max_c":
                    daily[
                        "temperature_2m_max"
                    ][i],

                "temperature_min_c":
                    daily[
                        "temperature_2m_min"
                    ][i],

                "precipitation_mm":
                    daily[
                        "precipitation_sum"
                    ][i],

                "rain_probability_percent":
                    daily[
                        "precipitation_probability_max"
                    ][i],

                "reference_et0_mm":
                    daily[
                        "et0_fao_evapotranspiration"
                    ][i],

                "weather_code":
                    daily[
                        "weather_code"
                    ][i]
            }
        )


    return {

        "location":
            location,

        "current":
            weather.get(
                "current",
                {}
            ),

        "irrigation_advisory":
            irrigation_signal,

        "forecast":
            forecast,

        "source":
            "Open-Meteo"
    }