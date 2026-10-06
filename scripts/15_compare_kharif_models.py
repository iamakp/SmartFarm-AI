from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==================================================
# FILES
# ==================================================

DATA_FILE = Path(
    "data/processed/rice_with_weather.csv"
)

RESULT_FILE = Path(
    "data/processed/kharif_model_comparison.csv"
)

BEST_MODEL_FILE = Path(
    "models/kharif_rice_yield_model.joblib"
)


# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_csv(DATA_FILE)

# Remove accidental spaces
df["Season"] = (
    df["Season"]
    .astype(str)
    .str.strip()
)


# ==================================================
# KEEP ONLY KHARIF RICE
# ==================================================

df = df[
    df["Season"] == "Kharif"
].copy()


print("\n===== KHARIF RICE DATA =====")

print(
    "Rows:",
    len(df)
)

print(
    "Years:",
    df["Crop_Year"].min(),
    "to",
    df["Crop_Year"].max()
)

print(
    "States:",
    df["State_Name"].nunique()
)

print(
    "Districts:",
    df["District_Name"].nunique()
)


# ==================================================
# BASIC FEATURES
# ==================================================

categorical_features = [
    "State_Name",
    "District_Name"
]

basic_numeric = [
    "Crop_Year",
    "Area"
]


# ==================================================
# PRE-MONSOON WEATHER
# ==================================================

pre_monsoon = [

    "PreMonsoon_Temp_Mean",
    "PreMonsoon_Temp_Max_Mean",
    "PreMonsoon_Temp_Min_Mean",
    "PreMonsoon_Humidity_Mean",
    "PreMonsoon_Rainfall_mm"

]


# ==================================================
# MONSOON WEATHER
# ==================================================

monsoon = [

    "Monsoon_Temp_Mean",
    "Monsoon_Temp_Max_Mean",
    "Monsoon_Temp_Min_Mean",
    "Monsoon_Humidity_Mean",
    "Monsoon_Rainfall_mm"

]


# ==================================================
# EXPERIMENTS
# ==================================================

experiments = {

    "Basic":
        [],

    "PreMonsoon":
        pre_monsoon,

    "Monsoon":
        monsoon,

    "PreMonsoon + Monsoon":
        pre_monsoon + monsoon

}


# ==================================================
# TIME BASED TRAIN / TEST SPLIT
# ==================================================

train_mask = (
    df["Crop_Year"] <= 2011
)

test_mask = (
    df["Crop_Year"] >= 2012
)


print("\n===== TIME SPLIT =====")

print(
    "Training rows:",
    train_mask.sum()
)

print(
    "Testing rows:",
    test_mask.sum()
)


results = []

best_model = None
best_features = None
best_mae = float("inf")
best_name = None


# ==================================================
# TRAIN EACH MODEL
# ==================================================

for experiment_name, weather_features in experiments.items():

    print(
        "\n===================================="
    )

    print(
        "Experiment:",
        experiment_name
    )

    numeric_features = (
        basic_numeric
        + weather_features
    )

    all_features = (
        categorical_features
        + numeric_features
    )


    X = df[
        all_features
    ]

    y = df[
        "Yield"
    ]


    X_train = X[
        train_mask
    ]

    X_test = X[
        test_mask
    ]

    y_train = y[
        train_mask
    ]

    y_test = y[
        test_mask
    ]


    # ==============================================
    # PREPROCESSOR
    # ==============================================

    preprocessor = ColumnTransformer(

        transformers=[

            (
                "categorical",

                OneHotEncoder(
                    handle_unknown="ignore"
                ),

                categorical_features
            ),

            (
                "numeric",
                "passthrough",
                numeric_features
            )
        ]
    )


    # ==============================================
    # RANDOM FOREST
    # ==============================================

    rf = RandomForestRegressor(

        n_estimators=350,

        min_samples_leaf=2,

        random_state=42,

        n_jobs=-1
    )


    model = Pipeline(

        steps=[

            (
                "preprocessor",
                preprocessor
            ),

            (
                "random_forest",
                rf
            )
        ]
    )


    # ==============================================
    # TRAIN
    # ==============================================

    model.fit(
        X_train,
        y_train
    )


    # ==============================================
    # PREDICT
    # ==============================================

    predictions = model.predict(
        X_test
    )


    # ==============================================
    # METRICS
    # ==============================================

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )


    print(
        f"MAE  = {mae:.4f}"
    )

    print(
        f"RMSE = {rmse:.4f}"
    )

    print(
        f"R²   = {r2:.4f}"
    )


    results.append({

        "Experiment":
            experiment_name,

        "MAE":
            mae,

        "RMSE":
            rmse,

        "R2":
            r2

    })


    # ==============================================
    # STORE BEST MODEL
    # ==============================================

    if mae < best_mae:

        best_mae = mae

        best_model = model

        best_features = all_features

        best_name = experiment_name


# ==================================================
# FINAL COMPARISON
# ==================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    "MAE"
)


print(
    "\n\n===================================="
)

print(
    "KHARIF FINAL COMPARISON"
)

print(
    "===================================="
)


print(
    results_df.to_string(
        index=False
    )
)


# ==================================================
# BEST MODEL
# ==================================================

best_result = results_df.iloc[0]


print(
    "\n===== BEST KHARIF MODEL ====="
)

print(
    "Feature set:",
    best_result["Experiment"]
)

print(
    f"MAE : {best_result['MAE']:.4f}"
)

print(
    f"RMSE: {best_result['RMSE']:.4f}"
)

print(
    f"R²  : {best_result['R2']:.4f}"
)


# ==================================================
# SAVE COMPARISON
# ==================================================

results_df.to_csv(
    RESULT_FILE,
    index=False
)


# ==================================================
# SAVE BEST MODEL
# ==================================================

BEST_MODEL_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


joblib.dump(

    {

        "model":
            best_model,

        "model_name":
            best_name,

        "features":
            best_features,

        "season":
            "Kharif",

        "mae":
            float(best_result["MAE"]),

        "rmse":
            float(best_result["RMSE"]),

        "r2":
            float(best_result["R2"])

    },

    BEST_MODEL_FILE
)


print(
    "\nComparison saved:",
    RESULT_FILE
)

print(
    "Best model saved:",
    BEST_MODEL_FILE
)