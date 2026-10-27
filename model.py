"""Feature engineering and model helpers for next-step temperature prediction."""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FEATURES = ["temperature_c", "lag_1", "lag_2", "rolling_mean_5", "rolling_mean_15", "ambient_c", "heat_load", "fan_speed_pct"]
ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "temperature_model.joblib"


def make_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["lag_1"] = out["temperature_c"].shift(1)
    out["lag_2"] = out["temperature_c"].shift(2)
    out["rolling_mean_5"] = out["temperature_c"].rolling(5).mean()
    out["rolling_mean_15"] = out["temperature_c"].rolling(15).mean()
    out["target_next_c"] = out["temperature_c"].shift(-1)
    return out.dropna().reset_index(drop=True)


def train_model(csv_path: Path | str | None = None):
    path = Path(csv_path) if csv_path else ROOT / "data" / "temperature_readings.csv"
    df = pd.read_csv(path)
    required = {"temperature_c", "ambient_c", "heat_load", "fan_speed_pct"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Dataset missing required columns: {sorted(missing)}")
    data = make_features(df)
    if len(data) < 50:
        raise ValueError("Need at least 50 valid rows to train the model.")
    split = int(len(data) * 0.8)  # chronological split avoids future-to-past leakage
    train, test = data.iloc[:split], data.iloc[split:]
    model = RandomForestRegressor(n_estimators=250, max_depth=12, min_samples_leaf=2, random_state=42, n_jobs=-1)
    model.fit(train[FEATURES], train["target_next_c"])
    pred = model.predict(test[FEATURES])
    metrics = {
        "mae_c": float(mean_absolute_error(test["target_next_c"], pred)),
        "rmse_c": float(np.sqrt(mean_squared_error(test["target_next_c"], pred))),
        "r2": float(r2_score(test["target_next_c"], pred)),
        "test_samples": int(len(test)),
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "metrics": metrics}, MODEL_PATH)
    result = test[["temperature_c", "target_next_c"]].copy()
    result["predicted_next_c"] = pred
    result.to_csv(ROOT / "data" / "predictions.csv", index=False)
    return metrics


def load_bundle(path: Path | str = MODEL_PATH):
    return joblib.load(path)


def predict_next(model, history: pd.DataFrame, ambient_c: float, heat_load: float, fan_speed_pct: float) -> float:
    """Predict next minute from up to 15 recent rows, newest row last."""
    if len(history) < 15:
        raise ValueError("Provide at least 15 recent temperature rows.")
    temps = history["temperature_c"].astype(float)
    row = pd.DataFrame([{
        "temperature_c": float(temps.iloc[-1]),
        "lag_1": float(temps.iloc[-2]),
        "lag_2": float(temps.iloc[-3]),
        "rolling_mean_5": float(temps.iloc[-5:].mean()),
        "rolling_mean_15": float(temps.iloc[-15:].mean()),
        "ambient_c": float(ambient_c),
        "heat_load": float(heat_load),
        "fan_speed_pct": float(fan_speed_pct),
    }])
    return float(model.predict(row[FEATURES])[0])
