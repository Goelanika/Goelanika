"""Air Quality Index prediction with an interpretable ML workflow."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

rng = np.random.default_rng(42)
ROOT = Path(__file__).parent
DATA, OUT = ROOT / "data", ROOT / "outputs"
DATA.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

n = 5000
df = pd.DataFrame({
    "city_zone": rng.choice(["Residential", "Commercial", "Industrial"], n, p=[.5, .3, .2]),
    "pm25": np.clip(rng.normal(72, 34, n), 5, 250),
    "pm10": np.clip(rng.normal(125, 48, n), 15, 350),
    "no2": np.clip(rng.normal(38, 16, n), 3, 120),
    "so2": np.clip(rng.normal(18, 8, n), 1, 70),
    "temperature": rng.normal(27, 7, n),
    "humidity": np.clip(rng.normal(58, 18, n), 10, 100),
    "wind_speed": np.clip(rng.normal(8, 3, n), 0.5, 25),
})
zone_effect = df.city_zone.map({"Residential": 0, "Commercial": 9, "Industrial": 22})
df["aqi"] = (
    .62 * df.pm25 + .28 * df.pm10 + .35 * df.no2 + .16 * df.so2
    + .08 * df.humidity - .75 * df.wind_speed + zone_effect
    + rng.normal(0, 8, n)
).clip(0, 500).round(1)

# Add realistic missing values; the pipeline handles them without leakage.
for col in ["pm25", "no2", "humidity"]:
    df.loc[rng.choice(n, 35, replace=False), col] = np.nan
df.to_csv(DATA / "air_quality.csv", index=False)

X = df.drop(columns="aqi")
y = df["aqi"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=.2, random_state=42
)
numeric = X.select_dtypes(include="number").columns.tolist()
categorical = ["city_zone"]
preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]), numeric),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
])
model = Pipeline([
    ("preprocess", preprocess),
    ("regressor", RandomForestRegressor(
        n_estimators=180, max_depth=12, min_samples_leaf=3,
        random_state=42, n_jobs=-1
    )),
])
model.fit(X_train, y_train)
pred = model.predict(X_test)
metrics = pd.DataFrame({
    "metric": ["MAE", "RMSE", "R2"],
    "value": [
        mean_absolute_error(y_test, pred),
        mean_squared_error(y_test, pred) ** .5,
        r2_score(y_test, pred),
    ],
})
metrics.to_csv(OUT / "model_metrics.csv", index=False)

feature_names = model.named_steps["preprocess"].get_feature_names_out()
importance = pd.DataFrame({
    "feature": feature_names,
    "importance": model.named_steps["regressor"].feature_importances_,
}).sort_values("importance", ascending=False)
importance.to_csv(OUT / "feature_importance.csv", index=False)

predictions = pd.DataFrame({
    "actual_aqi": y_test.reset_index(drop=True),
    "predicted_aqi": pred.round(2),
})
predictions.head(250).to_csv(OUT / "sample_predictions.csv", index=False)
print(metrics.to_string(index=False))
print("\nTop features:")
print(importance.head(6).to_string(index=False))
