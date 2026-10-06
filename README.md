# SmartFarm AI

## Live Demo

🚀 **Live Application:** https://smartfarm-ai-j8sx.onrender.com

📘 **API Documentation:** https://smartfarm-ai-j8sx.onrender.com/docs

**AI-Based Kharif Rice Yield Prediction, Live Weather Advisory and Historical Field Intelligence System**

SmartFarm AI is a full-stack agricultural decision-support system built using **real historical agricultural data**, machine learning and live weather information.

The project currently focuses on **Kharif rice in India** and intentionally avoids fabricated agricultural values such as synthetic NPK, pH or soil-moisture data.

---

## Features

- Kharif rice Yield Prediction
- Estimated crop production
- Live district-level weather
- Seven-day weather forecast
- Weather-based irrigation advisory
- Historical district yield analysis
- District vs state performance comparison
- Interactive web dashboard
- FastAPI REST API

---

## Application Modules

### Yield Console

Predicts historical Kharif rice yield using:

```text
State
District
Crop Year
Cultivated Area
```

The system returns:

```text
Predicted Yield (t/ha)
Estimated Production (tonnes)
```

Estimated production is calculated as:

```text
Production = Predicted Yield × Area
```

### Weather Advisory

Uses the **Open-Meteo API** to provide:

- Current temperature
- Humidity
- Precipitation
- Wind speed
- Seven-day forecast
- Rainfall probability
- Reference evapotranspiration (ET0)

A rule-based irrigation advisory is generated from forecast weather conditions.

> The irrigation advisory is weather-based and is not an ML irrigation model. Actual irrigation also depends on soil moisture, crop stage, soil type and field conditions.

### Field Insights

Provides historical Kharif rice analytics including:

- Average and median yield
- Best and worst performing years
- Latest available yield
- Area and production
- District vs state comparison
- Historical yield trends

---

## Machine Learning Model

The deployed model predicts **Kharif rice yield** using:

```text
State
District
Crop Year
Area
```

A chronological train/test split was used:

```text
Training: 1997-2011
Testing : 2012-2015
```

### Model Performance

| Metric | Result |
|---|---:|
| MAE | 0.3927 t/ha |
| RMSE | 0.6192 t/ha |
| R² | 0.6439 |

Multiple historical weather feature combinations were also evaluated. The basic model achieved the best MAE in the final Kharif experiment and was selected for deployment.

---

## Data Sources

### Agricultural Data

Historical district-level crop production records originate from **Government of India Open Government Data resources**.

Yield was calculated as:

```text
Yield = Production / Area
```

### Historical Weather

**NASA POWER** data was used during weather-feature experiments.

NASA POWER provides gridded meteorological information and should not be treated as measurements from a weather station located directly inside a farm.

### Live Weather

Current weather and forecast information are obtained from **Open-Meteo**.

---

## Technology Stack

| Component | Technology |
|---|---|
| Backend | FastAPI |
| Server | Uvicorn |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas |
| Model Storage | Joblib |
| Frontend | HTML, CSS, JavaScript |
| Live Weather | Open-Meteo |
| Historical Weather | NASA POWER |
| Language | Python 3.12 |

---

## Project Structure

```text
SmartFarm_AI_REAL/
│
├── app/
│   ├── api.py
│   ├── weather_service.py
│   └── insights_service.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── data/
│   └── processed/
│       ├── district_coordinates_complete.csv
│       └── rice_with_weather.csv
│
├── models/
│   └── kharif_rice_yield_model.joblib
│
├── scripts/
│   └── data processing, training and experiments
│
├── .gitignore
├── .python-version
├── DATA_SOURCES.md
├── PROJECT_ARCHITECTURE.md
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd SmartFarm_AI_REAL
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run the Application

```bash
uvicorn app.api:app --reload
```

Open:

```text
Web Application:
http://127.0.0.1:8000/

Swagger API Documentation:
http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web dashboard |
| GET | `/health` | Backend health check |
| GET | `/states` | Available states |
| GET | `/districts/{state}` | Districts for selected state |
| POST | `/predict-yield` | Kharif rice Yield Prediction |
| GET | `/weather/{state}/{district}` | Weather and irrigation advisory |
| GET | `/insights/{state}/{district}` | Historical field insights |

---

## Important Limitations

The deployed yield model is based on historical agricultural records from **1997-2015**.

It should therefore **not be described as a validated 2026 yield forecasting model** without retraining using newer agricultural data.

The model uses cultivated area as an input, which may capture historical and regional structural patterns.

The irrigation advisory currently uses weather information only and does not use field-level soil sensors.

SmartFarm AI is designed as a **decision-support and research system**, not as a replacement for professional agronomic assessment.

---

## Current Scope

```text
Crop    : Rice
Season  : Kharif
Country : India
Level   : State / District
```

Future work can extend the system with newer agricultural data, additional crops, soil information, field sensors and more advanced irrigation models.

---

## Project Goal

SmartFarm AI demonstrates how **real agricultural datasets, machine learning, live weather services, backend APIs and frontend development** can be combined into a practical agricultural decision-support platform.

The project emphasizes:

> **Real data, transparent modelling, reproducible experimentation and clearly stated limitations.**
