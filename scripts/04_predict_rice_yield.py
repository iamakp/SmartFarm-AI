\
from pathlib import Path
import joblib
import pandas as pd

MODEL = Path("models/rice_yield_model.joblib")

if not MODEL.exists():
    raise FileNotFoundError(
        "Run python 03_train_real_yield_model.py first."
    )

bundle = joblib.load(MODEL)
model = bundle["pipeline"]

print("\nSmartFarm AI - Rice Yield Prediction")
print("------------------------------------")

state = input("State name: ").strip()
district = input("District name: ").strip()
year = int(input("Crop year: "))
season = input("Season (e.g. Kharif): ").strip()
area = float(input("Cultivated area in hectares: "))

row = pd.DataFrame(
    [{
        "State_Name": state,
        "District_Name": district,
        "Crop_Year": year,
        "Season": season,
        "Area": area,
    }]
)

predicted_yield = float(model.predict(row)[0])
predicted_production = predicted_yield * area

print("\n===== PREDICTION =====")
print(f"Predicted rice yield: {predicted_yield:.3f} tonnes/hectare")
print(f"Estimated production: {predicted_production:.2f} tonnes")
