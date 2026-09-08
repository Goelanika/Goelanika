# Air Quality Prediction using Machine Learning

## Objective

Build a reproducible regression workflow that predicts Air Quality Index (AQI) from pollutant, weather and location features.

## What this project demonstrates

- Python/Pandas data preparation and missing-value handling
- Scikit-learn preprocessing pipeline without train/test leakage
- Random Forest regression for non-linear patterns
- MAE, RMSE and R² model evaluation
- Feature importance and prediction review

## Run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python model.py
```

The script generates 5,000 reproducible synthetic observations using a fixed seed. This is a self-developed learning project and does not use confidential or real patient/customer information.
