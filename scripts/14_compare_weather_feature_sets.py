import pandas as pd
import numpy as np

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
# LOAD DATA
# ==================================================

df = pd.read_csv(
    "data/processed/rice_with_weather.csv"
)


# ==================================================
# BASIC FEATURES
# ==================================================

categorical = [
    "State_Name",
    "District_Name",
    "Season"
]

basic_numeric = [
    "Crop_Year",
    "Area"
]


# ==================================================
# WEATHER GROUPS
# ==================================================

annual = [
    "Annual_Temp_Mean",
    "Annual_Temp_Max_Mean",
    "Annual_Temp_Min_Mean",
    "Annual_Humidity_Mean",
    "Annual_Rainfall_mm"
]


premonsoon = [
    "PreMonsoon_Temp_Mean",
    "PreMonsoon_Temp_Max_Mean",
    "PreMonsoon_Temp_Min_Mean",
    "PreMonsoon_Humidity_Mean",
    "PreMonsoon_Rainfall_mm"
]


monsoon = [
    "Monsoon_Temp_Mean",
    "Monsoon_Temp_Max_Mean",
    "Monsoon_Temp_Min_Mean",
    "Monsoon_Humidity_Mean",
    "Monsoon_Rainfall_mm"
]


postmonsoon = [
    "PostMonsoon_Temp_Mean",
    "PostMonsoon_Temp_Max_Mean",
    "PostMonsoon_Temp_Min_Mean",
    "PostMonsoon_Humidity_Mean",
    "PostMonsoon_Rainfall_mm"
]


winter = [
    "Winter_Temp_Mean",
    "Winter_Temp_Max_Mean",
    "Winter_Temp_Min_Mean",
    "Winter_Humidity_Mean",
    "Winter_Rainfall_mm"
]


# ==================================================
# EXPERIMENTS
# ==================================================

experiments = {

    "Basic":
        [],

    "Annual":
        annual,

    "Monsoon":
        monsoon,

    "PreMonsoon + Monsoon":
        premonsoon + monsoon,

    "Annual + Monsoon":
        annual + monsoon,

    "Monsoon + PostMonsoon":
        monsoon + postmonsoon,

    "All Weather":
        (
            annual
            + premonsoon
            + monsoon
            + postmonsoon
            + winter
        )
}


# ==================================================
# TIME SPLIT
# ==================================================

train_mask = df["Crop_Year"] <= 2011
test_mask = df["Crop_Year"] >= 2012

results = []


# ==================================================
# TRAIN EACH EXPERIMENT
# ==================================================

for name, weather_features in experiments.items():

    print(
        "\n================================="
    )

    print(
        "Experiment:",
        name
    )

    numeric = (
        basic_numeric
        + weather_features
    )

    features = (
        categorical
        + numeric
    )

    X = df[features]
    y = df["Yield"]

    X_train = X[train_mask]
    y_train = y[train_mask]

    X_test = X[test_mask]
    y_test = y[test_mask]


    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical
            ),

            (
                "numeric",
                "passthrough",
                numeric
            )
        ]
    )


    rf = RandomForestRegressor(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=2
    )


    model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),

            (
                "model",
                rf
            )
        ]
    )


    model.fit(
        X_train,
        y_train
    )


    predictions = model.predict(
        X_test
    )


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
            name,

        "MAE":
            mae,

        "RMSE":
            rmse,

        "R2":
            r2
    })


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
    "\n\n================================="
)

print(
    "FINAL COMPARISON"
)

print(
    "================================="
)


print(
    results_df.to_string(
        index=False
    )
)


best = results_df.iloc[0]


print(
    "\n===== BEST MODEL BY MAE ====="
)

print(
    "Feature set:",
    best["Experiment"]
)

print(
    f"MAE : {best['MAE']:.4f}"
)

print(
    f"RMSE: {best['RMSE']:.4f}"
)

print(
    f"R²  : {best['R2']:.4f}"
)


results_df.to_csv(
    "data/processed/weather_feature_comparison.csv",
    index=False
)

print(
    "\nSaved:"
    " data/processed/"
    "weather_feature_comparison.csv"
)