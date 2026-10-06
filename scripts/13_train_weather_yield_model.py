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
# PATHS
# ==================================================

DATA_FILE = Path(
    "data/processed/rice_with_weather.csv"
)

OLD_MODEL_FILE = Path(
    "models/rice_yield_model.joblib"
)

NEW_MODEL_FILE = Path(
    "models/rice_yield_weather_model.joblib"
)

PREDICTION_FILE = Path(
    "data/processed/weather_model_test_predictions.csv"
)


# ==================================================
# LOAD DATA
# ==================================================

df = pd.read_csv(DATA_FILE)

print("\n===== DATA LOADED =====")
print("Rows:", len(df))


# ==================================================
# FEATURES
# ==================================================

categorical_features = [
    "State_Name",
    "District_Name",
    "Season"
]


basic_numeric_features = [
    "Crop_Year",
    "Area"
]


weather_features = [

    # Annual
    "Annual_Temp_Mean",
    "Annual_Temp_Max_Mean",
    "Annual_Temp_Min_Mean",
    "Annual_Humidity_Mean",
    "Annual_Rainfall_mm",

    # Pre-monsoon
    "PreMonsoon_Temp_Mean",
    "PreMonsoon_Temp_Max_Mean",
    "PreMonsoon_Temp_Min_Mean",
    "PreMonsoon_Humidity_Mean",
    "PreMonsoon_Rainfall_mm",

    # Monsoon
    "Monsoon_Temp_Mean",
    "Monsoon_Temp_Max_Mean",
    "Monsoon_Temp_Min_Mean",
    "Monsoon_Humidity_Mean",
    "Monsoon_Rainfall_mm",

    # Post-monsoon
    "PostMonsoon_Temp_Mean",
    "PostMonsoon_Temp_Max_Mean",
    "PostMonsoon_Temp_Min_Mean",
    "PostMonsoon_Humidity_Mean",
    "PostMonsoon_Rainfall_mm",

    # Winter
    "Winter_Temp_Mean",
    "Winter_Temp_Max_Mean",
    "Winter_Temp_Min_Mean",
    "Winter_Humidity_Mean",
    "Winter_Rainfall_mm"
]


all_features = (
    categorical_features
    + basic_numeric_features
    + weather_features
)

target = "Yield"


X = df[all_features]
y = df[target]


# ==================================================
# SAME TIME-BASED SPLIT AS OLD MODEL
# ==================================================

train_mask = (
    df["Crop_Year"] <= 2011
)

test_mask = (
    df["Crop_Year"] >= 2012
)


X_train = X[train_mask]
y_train = y[train_mask]

X_test = X[test_mask]
y_test = y[test_mask]


print("\n===== TIME SPLIT =====")

print(
    "Training years:",
    df.loc[
        train_mask,
        "Crop_Year"
    ].min(),
    "to",
    df.loc[
        train_mask,
        "Crop_Year"
    ].max()
)

print(
    "Testing years:",
    df.loc[
        test_mask,
        "Crop_Year"
    ].min(),
    "to",
    df.loc[
        test_mask,
        "Crop_Year"
    ].max()
)

print(
    "Training rows:",
    len(X_train)
)

print(
    "Testing rows:",
    len(X_test)
)


# ==================================================
# PREPROCESSING
# ==================================================

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
            "numerical",
            "passthrough",
            basic_numeric_features
            + weather_features
        )
    ]
)


# ==================================================
# RANDOM FOREST
# ==================================================

rf = RandomForestRegressor(

    n_estimators=350,

    random_state=42,

    n_jobs=-1,

    min_samples_leaf=2
)


model = Pipeline(
    steps=[

        (
            "preprocessing",
            preprocessor
        ),

        (
            "random_forest",
            rf
        )
    ]
)


# ==================================================
# TRAIN
# ==================================================

print(
    "\nTraining weather-enhanced Random Forest..."
)

model.fit(
    X_train,
    y_train
)


# ==================================================
# PREDICTIONS
# ==================================================

predictions = model.predict(
    X_test
)


# ==================================================
# METRICS
# ==================================================

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
    "\n===== WEATHER MODEL RESULT ====="
)

print(
    f"MAE : {mae:.4f} tonnes/hectare"
)

print(
    f"RMSE: {rmse:.4f} tonnes/hectare"
)

print(
    f"R²  : {r2:.4f}"
)


# ==================================================
# COMPARE WITH OLD MODEL
# ==================================================

print(
    "\n===== OLD vs WEATHER MODEL ====="
)

if OLD_MODEL_FILE.exists():

    old_bundle = joblib.load(
        OLD_MODEL_FILE
    )

    old_mae = old_bundle.get(
        "mae"
    )

    old_rmse = old_bundle.get(
        "rmse"
    )

    old_r2 = old_bundle.get(
        "r2"
    )

    print(
        f"Old MAE     : {old_mae:.4f}"
    )

    print(
        f"Weather MAE : {mae:.4f}"
    )

    print()

    print(
        f"Old RMSE     : {old_rmse:.4f}"
    )

    print(
        f"Weather RMSE : {rmse:.4f}"
    )

    print()

    print(
        f"Old R²      : {old_r2:.4f}"
    )

    print(
        f"Weather R²  : {r2:.4f}"
    )


    mae_change = (
        (old_mae - mae)
        / old_mae
    ) * 100


    print(
        f"\nMAE improvement over old model: "
        f"{mae_change:.2f}%"
    )

else:

    print(
        "Old model file not found."
    )


# ==================================================
# FEATURE IMPORTANCE
# ==================================================

print(
    "\n===== TOP FEATURE IMPORTANCE ====="
)

trained_preprocessor = model.named_steps[
    "preprocessing"
]

trained_rf = model.named_steps[
    "random_forest"
]


feature_names = (
    trained_preprocessor
    .get_feature_names_out()
)


importance_df = pd.DataFrame({

    "Feature":
        feature_names,

    "Importance":
        trained_rf.feature_importances_
})


importance_df = (
    importance_df
    .sort_values(
        "Importance",
        ascending=False
    )
)


print(
    importance_df
    .head(20)
    .to_string(
        index=False
    )
)


# ==================================================
# SAVE TEST PREDICTIONS
# ==================================================

prediction_df = df.loc[
    test_mask,
    [
        "State_Name",
        "District_Name",
        "Crop_Year",
        "Season",
        "Area",
        "Yield"
    ]
].copy()


prediction_df[
    "Predicted_Yield"
] = predictions


prediction_df[
    "Absolute_Error"
] = abs(
    prediction_df["Yield"]
    - prediction_df["Predicted_Yield"]
)


prediction_df.to_csv(
    PREDICTION_FILE,
    index=False
)


# ==================================================
# SAVE MODEL
# ==================================================

NEW_MODEL_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


joblib.dump(
    {

        "model":
            model,

        "features":
            all_features,

        "weather_features":
            weather_features,

        "target":
            target,

        "mae":
            mae,

        "rmse":
            rmse,

        "r2":
            r2

    },
    NEW_MODEL_FILE
)


print(
    "\nModel saved:",
    NEW_MODEL_FILE
)

print(
    "Test predictions saved:",
    PREDICTION_FILE
)