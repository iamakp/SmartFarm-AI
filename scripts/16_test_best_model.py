import joblib
import pandas as pd


MODEL_PATH = "models/kharif_rice_yield_model.joblib"
DATA_PATH = "data/processed/rice_with_weather.csv"


# ==================================================
# LOAD MODEL
# ==================================================

bundle = joblib.load(MODEL_PATH)

model = bundle["model"]
features = bundle["features"]


# ==================================================
# LOAD REFERENCE DATA
# ==================================================

df = pd.read_csv(DATA_PATH)

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


# Only Kharif
df = df[
    df["Season"] == "Kharif"
].copy()


# ==================================================
# HELPER
# ==================================================

def find_case_insensitive(value, valid_values):

    value = value.strip().lower()

    mapping = {
        str(item).strip().lower(): item
        for item in valid_values
    }

    return mapping.get(value)


# ==================================================
# START
# ==================================================

print("\n===== SMART FARM AI =====")
print("Kharif Rice Yield Prediction")


# ==================================================
# STATE INPUT
# ==================================================

state_input = input(
    "\nState: "
)

states = sorted(
    df["State_Name"].unique()
)

state = find_case_insensitive(
    state_input,
    states
)


if state is None:

    print(
        "\n❌ State not found in training data."
    )

    print(
        "\nAvailable states:"
    )

    for s in states:
        print("-", s)

    exit()


print(
    "Matched State:",
    state
)


# ==================================================
# DISTRICT INPUT
# ==================================================

state_df = df[
    df["State_Name"] == state
]

districts = sorted(
    state_df[
        "District_Name"
    ].unique()
)


district_input = input(
    "District: "
)


district = find_case_insensitive(
    district_input,
    districts
)


if district is None:

    print(
        "\n❌ District not found for",
        state
    )

    print(
        "\nAvailable districts:"
    )

    for d in districts:
        print("-", d)

    exit()


print(
    "Matched District:",
    district
)


# ==================================================
# YEAR
# ==================================================

year = int(
    input(
        "Crop Year: "
    )
)


if year < 1997 or year > 2015:

    print(
        "\n⚠ Warning:"
    )

    print(
        "Current historical model was built "
        "using 1997-2015 data."
    )

    print(
        "Prediction outside this range "
        "should not be considered reliable."
    )


# ==================================================
# AREA
# ==================================================

area = float(
    input(
        "Area in hectares: "
    )
)


if area <= 0:

    print(
        "\n❌ Area must be greater than 0."
    )

    exit()


# ==================================================
# CREATE MODEL INPUT
# ==================================================

input_data = pd.DataFrame(
    [
        {
            "State_Name":
                state,

            "District_Name":
                district,

            "Crop_Year":
                year,

            "Area":
                area
        }
    ]
)


input_data = input_data[
    features
]


# ==================================================
# PREDICTION
# ==================================================

predicted_yield = float(
    model.predict(
        input_data
    )[0]
)


estimated_production = (
    predicted_yield
    * area
)


# ==================================================
# RESULT
# ==================================================

print(
    "\n=============================="
)

print(
    "       PREDICTION RESULT"
)

print(
    "=============================="
)


print(
    f"State              : {state}"
)

print(
    f"District           : {district}"
)

print(
    "Crop               : Rice"
)

print(
    "Season             : Kharif"
)

print(
    f"Area               : {area:.2f} hectares"
)

print(
    f"Predicted Yield    : "
    f"{predicted_yield:.2f} tonnes/hectare"
)

print(
    f"Estimated Production: "
    f"{estimated_production:.2f} tonnes"
)


print(
    "\n===== MODEL INFORMATION ====="
)

print(
    f"MAE : {bundle['mae']:.4f}"
)

print(
    f"RMSE: {bundle['rmse']:.4f}"
)

print(
    f"R²  : {bundle['r2']:.4f}"
)