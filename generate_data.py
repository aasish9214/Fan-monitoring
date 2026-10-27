"""Generate a reproducible synthetic temperature time-series for project demos.

This is simulated data, not measured sensor data. Replace it with real readings
before making claims about real-world model performance.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "temperature_readings.csv"


def generate(n: int = 3000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2026-01-01", periods=n, freq="min")
    t = np.arange(n)
    ambient = 27 + 2.5 * np.sin(2 * np.pi * t / 1440) + 0.7 * np.sin(2 * np.pi * t / 180)
    heat_load = np.clip(0.5 + 0.35 * np.sin(2 * np.pi * t / 420) + rng.normal(0, 0.12, n), 0, 1.2)
    temp = np.empty(n)
    fan = np.zeros(n)
    temp[0] = ambient[0] + 1.5
    for i in range(1, n):
        # Synthetic thermal dynamics: heat load raises temperature; fan cools it.
        fan[i - 1] = np.clip((temp[i - 1] - 29) * 12, 0, 100)
        temp[i] = temp[i - 1] + 0.045 * (ambient[i] - temp[i - 1]) + 0.11 * heat_load[i] - 0.006 * fan[i - 1] + rng.normal(0, 0.08)
        temp[i] = np.clip(temp[i], 20, 45)
    temp += rng.normal(0, 0.12, n)  # sensor noise
    df = pd.DataFrame({"timestamp": timestamps, "temperature_c": temp.round(3), "ambient_c": ambient.round(3), "heat_load": heat_load.round(3), "fan_speed_pct": fan.round(1)})
    df.to_csv(OUT, index=False)
    return df

if __name__ == "__main__":
    frame = generate()
    print(f"Wrote {len(frame)} simulated rows to {OUT}")
