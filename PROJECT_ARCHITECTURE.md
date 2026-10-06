# SmartFarm AI - Project Architecture

SmartFarm AI is a full-stack agricultural decision-support system focused on Kharif rice in India.

The application combines:

- Machine learning based yield prediction
- Historical agricultural analytics
- Live weather information
- Weather-based irrigation advisory
- Web dashboard
- REST API

---

## System Architecture

```text
User
  |
  v
Web Dashboard
HTML + CSS + JavaScript
  |
  v
FastAPI Backend
  |
  +--------------------+
  |                    |
  v                    v
Yield Prediction    Weather Service
  |                    |
  v                    v
Scikit-learn        Open-Meteo API
Model
  |
  +--------------------+
  |
  v
Historical Field Insights
  |
  v
Processed Crop Dataset
```

---

## Backend

The backend is built using FastAPI.

Main application files:

```text
app/
├── api.py
├── weather_service.py
└── insights_service.py
```

### api.py

Acts as the main application entry point.

It:

- Loads the trained yield model
- Loads historical agricultural data
- Validates states and districts
- Provides prediction endpoints
- Connects weather and insights services
- Serves the frontend

### weather_service.py

Responsible for:

- District coordinate lookup
- Open-Meteo API requests
- Current weather
- Seven-day forecast
- Weather-based irrigation advisory

### insights_service.py

Responsible for:

- District-level historical aggregation
- State-level historical aggregation
- Yield statistics
- Best and worst years
- District vs state comparison
- Historical trend data

---

## Machine Learning Layer

The deployed model is:

```text
models/kharif_rice_yield_model.joblib
```

Model inputs:

```text
State
District
Crop Year
Cultivated Area
```

Model output:

```text
Predicted Kharif Rice Yield (tonnes/hectare)
```

Estimated production is calculated as:

```text
Predicted Production = Predicted Yield × Area
```

The model was selected using a chronological train/test evaluation.

---

## Data Layer

Runtime data files:

```text
data/processed/rice_with_weather.csv
data/processed/district_coordinates_complete.csv
```

`rice_with_weather.csv` provides historical agricultural records used by the API and Field Insights module.

`district_coordinates_complete.csv` provides district coordinates required for live weather lookup.

Historical NASA POWER weather data was used during model experimentation but is not required for every production API request.

---

## Frontend

The frontend is located in:

```text
frontend/
├── index.html
├── style.css
└── app.js
```

It contains three main modules:

```text
Yield Console
Weather Advisory
Field Insights
```

The frontend communicates with the FastAPI backend through REST endpoints.

---

## API Layer

Main endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web dashboard |
| GET | `/health` | Backend health |
| GET | `/states` | Available states |
| GET | `/districts/{state}` | District lookup |
| POST | `/predict-yield` | Yield prediction |
| GET | `/weather/{state}/{district}` | Weather and irrigation advisory |
| GET | `/insights/{state}/{district}` | Historical field insights |

Swagger documentation is available at:

```text
/docs
```

---

## Weather Flow

```text
State + District
      |
      v
District Coordinates
      |
      v
Open-Meteo API
      |
      +--> Current Weather
      |
      +--> 7-Day Forecast
      |
      v
Weather-Based Irrigation Advisory
```

The irrigation advisory is rule-based and is not currently an ML model.

---

## Research Pipeline

Research and training scripts are separated from the production application:

```text
scripts/
```

The pipeline covers:

```text
Crop data collection
        |
        v
Data validation
        |
        v
Rice data preparation
        |
        v
District coordinate collection
        |
        v
NASA POWER weather collection
        |
        v
Weather feature engineering
        |
        v
Model comparison
        |
        v
Kharif model selection
        |
        v
Saved production model
```

The production API loads the saved model instead of retraining it at startup.

---

## Current Scope

```text
Crop    : Rice
Season  : Kharif
Country : India
Level   : State / District
```

The architecture can later be extended with additional crops, newer historical data, soil information and field sensors.