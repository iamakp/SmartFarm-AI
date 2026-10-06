# SmartFarm AI - Data Sources

SmartFarm AI uses traceable real-world agricultural and weather data.

The project does not fabricate NPK, pH, soil-moisture or crop-production values.

---

## 1. Government of India Crop Production Data

Historical district-level crop-production records originate from Government of India Open Government Data resources.

Official resource:
https://www.data.gov.in/resource/district-wise-season-wise-crop-production-statistics-1997

Catalog:
https://www.data.gov.in/catalog/district-wise-season-wise-crop-production-statistics-0

The dataset contains:

- State
- District
- Crop Year
- Season
- Crop
- Area
- Production

The project uses the commonly available 1997-2015 version containing approximately 246,000 records.

A public script-downloadable mirror was used during development:
https://github.com/JitendraAmbekar/india-crop-production-analysis

Rice yield was calculated as:

Yield = Production / Area

---

## 2. NASA POWER Historical Weather

NASA POWER was used during historical weather experiments.

Documentation:
https://power.larc.nasa.gov/docs/services/api/temporal/daily/

District coordinates were used to retrieve historical meteorological information and create seasonal weather features.

NASA POWER provides gridded meteorological data and should not be interpreted as measurements from a weather station located directly inside a farm.

---

## 3. Open-Meteo Live Weather

The production application uses Open-Meteo for current weather and seven-day forecasts.

Weather information includes temperature, humidity, precipitation, wind speed, rainfall probability, maximum and minimum temperature, and reference evapotranspiration (ET0).

This data powers the Weather Advisory and weather-based irrigation advisory modules.

---

## Data Integrity Policy

SmartFarm AI does not generate fabricated soil or nutrient values.

Soil-related features should only be added when a legitimate and traceable dataset is available.

---

## Production Runtime Files

The deployed application currently uses:

data/processed/rice_with_weather.csv
data/processed/district_coordinates_complete.csv
models/kharif_rice_yield_model.joblib

Intermediate research datasets are not required by the production API.
