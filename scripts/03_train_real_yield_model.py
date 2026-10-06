from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

DATA_PATH = Path("data/processed/rice_yield_clean.csv")
MODEL_PATH = Path("models/rice_yield_model.joblib")


# --------------------------------------------------
# LOAD CLEANED REAL DATA
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

print("\n===== DATA LOADED =====")
print("Rows:", len(df))


# --------------------------------------------------
# FEATURES AND TARGET
# --------------------------------------------------

features = [
    "State_Name",
    "District_Name",
    "Crop_Year",
    "Season",
    "Area"
]

target = "Yield"

X = df[features]
y = df[target]


# --------------------------------------------------
# TIME-BASED TRAIN TEST SPLIT
# --------------------------------------------------

years = sorted(df["Crop_Year"].unique())

split_index = int(len(years) * 0.80)

train_years = years[:split_index]
test_years = years[split_index:]

train_mask = df["Crop_Year"].isin(train_years)
test_mask = df["Crop_Year"].isin(test_years)

X_train = X[train_mask]
y_train = y[train_mask]

X_test = X[test_mask]
y_test = y[test_mask]


print("\n===== TIME SPLIT =====")

print(
    "Training years:",
    min(train_years),
    "to",
    max(train_years)
)

print(
    "Testing years:",
    min(test_years),
    "to",
    max(test_years)
)

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# --------------------------------------------------
# BASELINE MODEL
# --------------------------------------------------

baseline = DummyRegressor(strategy="mean")

baseline.fit(
    np.zeros((len(y_train), 1)),
    y_train
)

baseline_predictions = baseline.predict(
    np.zeros((len(y_test), 1))
)

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_predictions
    )
)


print("\n===== BASELINE MODEL =====")

print(
    f"Baseline MAE : {baseline_mae:.4f}"
)

print(
    f"Baseline RMSE: {baseline_rmse:.4f}"
)


# --------------------------------------------------
# PREPROCESSING
# --------------------------------------------------

categorical_features = [
    "State_Name",
    "District_Name",
    "Season"
]

numerical_features = [
    "Crop_Year",
    "Area"
]


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
            numerical_features
        )
    ]
)


# --------------------------------------------------
# RANDOM FOREST
# --------------------------------------------------

random_forest = RandomForestRegressor(
    n_estimators=300,
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
            random_forest
        )
    ]
)


# --------------------------------------------------
# TRAIN MODEL
# --------------------------------------------------

print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

predictions = model.predict(
    X_test
)


# --------------------------------------------------
# EVALUATION
# --------------------------------------------------

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


print("\n===== RANDOM FOREST RESULT =====")

print(
    f"MAE : {mae:.4f} tonnes/hectare"
)

print(
    f"RMSE: {rmse:.4f} tonnes/hectare"
)

print(
    f"R²  : {r2:.4f}"
)


# --------------------------------------------------
# COMPARE WITH BASELINE
# --------------------------------------------------

improvement = (
    (baseline_mae - mae)
    / baseline_mae
) * 100


print("\n===== COMPARISON =====")

print(
    f"Baseline MAE     : {baseline_mae:.4f}"
)

print(
    f"Random Forest MAE: {mae:.4f}"
)

print(
    f"MAE improvement : {improvement:.2f}%"
)


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    {
        "model": model,
        "features": features,
        "target": target,
        "train_years": train_years,
        "test_years": test_years,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    },
    MODEL_PATH
)


print(
    "\nModel saved:",
    MODEL_PATH
)