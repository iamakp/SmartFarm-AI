from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.weather_service import get_weather_for_district
from app.insights_service import get_field_insights


# ============================================================
# PROJECT BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "kharif_rice_yield_model.joblib"
)

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "rice_with_weather.csv"
)

FRONTEND_DIR = (
    BASE_DIR
    / "frontend"
)


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

if not MODEL_PATH.exists():
    raise RuntimeError(
        f"Model file not found: {MODEL_PATH}"
    )


if not DATA_PATH.exists():
    raise RuntimeError(
        f"Dataset file not found: {DATA_PATH}"
    )


if not FRONTEND_DIR.exists():
    raise RuntimeError(
        f"Frontend folder not found: {FRONTEND_DIR}"
    )


# ============================================================
# LOAD MACHINE LEARNING MODEL
# ============================================================

bundle = joblib.load(
    MODEL_PATH
)

model = bundle["model"]

model_features = bundle["features"]


# ============================================================
# LOAD REFERENCE DATA
# ============================================================

df = pd.read_csv(
    DATA_PATH
)


# ============================================================
# CLEAN IMPORTANT TEXT COLUMNS
# ============================================================

df["State_Name"] = (
    df["State_Name"]
    .astype(str)
    .str.strip()
)

df["District_Name"] = (
    df["District_Name"]
    .astype(str)
    .str.strip()
)

df["Season"] = (
    df["Season"]
    .astype(str)
    .str.strip()
)


# ============================================================
# KEEP KHARIF DATA
# ============================================================

kharif_df = df[
    df["Season"].str.lower()
    == "kharif"
].copy()


# ============================================================
# CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="SmartFarm AI API",
    version="1.2.0",
    description=(
        "SmartFarm AI backend for Kharif rice "
        "yield prediction, weather advisory "
        "and historical field insights."
    )
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# STATIC FRONTEND
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory=FRONTEND_DIR
    ),
    name="static"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class YieldRequest(BaseModel):
    state: str
    district: str
    year: int
    area: float


# ============================================================
# HELPER FUNCTION
# ============================================================

def match_value(
    user_value,
    valid_values
):

    if user_value is None:
        return None

    normalized_value = (
        str(user_value)
        .strip()
        .lower()
    )

    mapping = {
        str(value)
        .strip()
        .lower(): value
        for value in valid_values
    }

    return mapping.get(
        normalized_value
    )


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
def home():

    index_file = (
        FRONTEND_DIR
        / "index.html"
    )

    if not index_file.exists():

        raise HTTPException(
            status_code=500,
            detail=(
                "Frontend index.html "
                "not found."
            )
        )

    return FileResponse(
        index_file
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "project": "SmartFarm AI",
        "version": "1.2.0",
        "yield_model": "enabled",
        "weather_service": "enabled",
        "field_insights": "enabled"
    }


# ============================================================
# GET STATES
# ============================================================

@app.get("/states")
def get_states():

    states = sorted(
        kharif_df[
            "State_Name"
        ]
        .dropna()
        .unique()
    )

    return {
        "count": len(states),
        "states": states
    }


# ============================================================
# GET DISTRICTS
# ============================================================

@app.get("/districts/{state}")
def get_districts(
    state: str
):

    states = sorted(
        kharif_df[
            "State_Name"
        ]
        .dropna()
        .unique()
    )

    matched_state = match_value(
        state,
        states
    )

    if matched_state is None:

        raise HTTPException(
            status_code=404,
            detail="State not found."
        )

    district_rows = kharif_df[
        kharif_df[
            "State_Name"
        ]
        == matched_state
    ]

    districts = sorted(
        district_rows[
            "District_Name"
        ]
        .dropna()
        .unique()
    )

    return {
        "state": matched_state,
        "count": len(districts),
        "districts": districts
    }


# ============================================================
# YIELD PREDICTION
# ============================================================

@app.post("/predict-yield")
def predict_yield(
    request: YieldRequest
):

    # --------------------------------------------------------
    # STATE VALIDATION
    # --------------------------------------------------------

    states = sorted(
        kharif_df[
            "State_Name"
        ]
        .dropna()
        .unique()
    )

    matched_state = match_value(
        request.state,
        states
    )

    if matched_state is None:

        raise HTTPException(
            status_code=400,
            detail="Invalid state."
        )


    # --------------------------------------------------------
    # DISTRICT VALIDATION
    # --------------------------------------------------------

    district_rows = kharif_df[
        kharif_df[
            "State_Name"
        ]
        == matched_state
    ]

    districts = sorted(
        district_rows[
            "District_Name"
        ]
        .dropna()
        .unique()
    )

    matched_district = match_value(
        request.district,
        districts
    )

    if matched_district is None:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid district "
                f"for {matched_state}."
            )
        )


    # --------------------------------------------------------
    # YEAR VALIDATION
    # --------------------------------------------------------

    if (
        request.year < 1997
        or request.year > 2015
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Current yield model uses "
                "historical data from "
                "1997 to 2015."
            )
        )


    # --------------------------------------------------------
    # AREA VALIDATION
    # --------------------------------------------------------

    if request.area <= 0:

        raise HTTPException(
            status_code=400,
            detail=(
                "Area must be greater "
                "than zero."
            )
        )


    # --------------------------------------------------------
    # CREATE MODEL INPUT
    # --------------------------------------------------------

    input_data = pd.DataFrame(
        [
            {
                "State_Name":
                    matched_state,

                "District_Name":
                    matched_district,

                "Crop_Year":
                    request.year,

                "Area":
                    request.area
            }
        ]
    )

    input_data = input_data[
        model_features
    ]


    # --------------------------------------------------------
    # RUN MODEL
    # --------------------------------------------------------

    try:

        prediction = model.predict(
            input_data
        )

        predicted_yield = float(
            prediction[0]
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Model prediction "
                f"failed: {error}"
            )
        )


    # --------------------------------------------------------
    # ESTIMATED PRODUCTION
    # --------------------------------------------------------

    estimated_production = (
        predicted_yield
        *
        request.area
    )


    # --------------------------------------------------------
    # MODEL METRICS
    # --------------------------------------------------------

    mae = bundle.get("mae")
    rmse = bundle.get("rmse")
    r2 = bundle.get("r2")


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "state":
            matched_state,

        "district":
            matched_district,

        "crop":
            "Rice",

        "season":
            "Kharif",

        "year":
            request.year,

        "area_hectares":
            request.area,

        "predicted_yield_tonnes_per_hectare":
            round(
                predicted_yield,
                3
            ),

        "estimated_production_tonnes":
            round(
                estimated_production,
                2
            ),

        "model_metrics": {

            "mae": (
                round(mae, 4)
                if mae is not None
                else None
            ),

            "rmse": (
                round(rmse, 4)
                if rmse is not None
                else None
            ),

            "r2": (
                round(r2, 4)
                if r2 is not None
                else None
            )
        },

        "model_scope": {
            "crop":
                "Rice",

            "season":
                "Kharif",

            "historical_period":
                "1997-2015"
        }
    }


# ============================================================
# WEATHER + IRRIGATION ADVISORY
# ============================================================

@app.get(
    "/weather/{state}/{district}"
)
def weather(
    state: str,
    district: str
):

    # --------------------------------------------------------
    # STATE VALIDATION
    # --------------------------------------------------------

    states = sorted(
        kharif_df[
            "State_Name"
        ]
        .dropna()
        .unique()
    )

    matched_state = match_value(
        state,
        states
    )

    if matched_state is None:

        raise HTTPException(
            status_code=404,
            detail="State not found."
        )


    # --------------------------------------------------------
    # DISTRICT VALIDATION
    # --------------------------------------------------------

    district_rows = kharif_df[
        kharif_df[
            "State_Name"
        ]
        == matched_state
    ]

    districts = sorted(
        district_rows[
            "District_Name"
        ]
        .dropna()
        .unique()
    )

    matched_district = match_value(
        district,
        districts
    )

    if matched_district is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"District not found "
                f"for {matched_state}."
            )
        )


    # --------------------------------------------------------
    # FETCH WEATHER
    # --------------------------------------------------------

    try:

        return get_weather_for_district(
            matched_state,
            matched_district
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail=(
                f"Weather service unavailable: "
                f"{error}"
            )
        )


# ============================================================
# FIELD INSIGHTS
# ============================================================

@app.get(
    "/insights/{state}/{district}"
)
def field_insights(
    state: str,
    district: str
):

    # --------------------------------------------------------
    # STATE VALIDATION
    # --------------------------------------------------------

    states = sorted(
        kharif_df[
            "State_Name"
        ]
        .dropna()
        .unique()
    )

    matched_state = match_value(
        state,
        states
    )

    if matched_state is None:

        raise HTTPException(
            status_code=404,
            detail="State not found."
        )


    # --------------------------------------------------------
    # DISTRICT VALIDATION
    # --------------------------------------------------------

    district_rows = kharif_df[
        kharif_df[
            "State_Name"
        ]
        == matched_state
    ]

    districts = sorted(
        district_rows[
            "District_Name"
        ]
        .dropna()
        .unique()
    )

    matched_district = match_value(
        district,
        districts
    )

    if matched_district is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"District not found "
                f"for {matched_state}."
            )
        )


    # --------------------------------------------------------
    # GENERATE INSIGHTS
    # --------------------------------------------------------

    try:

        return get_field_insights(
            kharif_df,
            matched_state,
            matched_district
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to generate "
                f"field insights: {error}"
            )
        )