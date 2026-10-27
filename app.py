"""Streamlit dashboard. Run with: streamlit run app.py"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from controller import adaptive_controller, threshold_controller
from model import MODEL_PATH, load_bundle, predict_next
from generate_data import generate

st.set_page_config(page_title="AI Adaptive Fan Control", page_icon="🌡️", layout="wide")
st.title("🌡️ AI-Based Adaptive Fan Speed Control")
st.caption("Predict the next temperature and adapt fan speed. Demo uses simulated data unless you load your own sensor CSV.")

with st.sidebar:
    st.header("Demo settings")
    current_temp = st.slider("Current temperature (°C)", 20.0, 45.0, 31.0, 0.1)
    ambient = st.slider("Ambient temperature (°C)", 15.0, 40.0, 28.0, 0.5)
    heat_load = st.slider("Estimated heat load", 0.0, 1.2, 0.6, 0.05)
    current_speed = st.slider("Current fan speed (%)", 0, 100, 30, 5)
    low_temp = st.slider("Cooling starts at (°C)", 20.0, 35.0, 28.0, 0.5)
    high_temp = st.slider("Maximum cooling at (°C)", low_temp + 1.0, 45.0, max(low_temp + 1.0, 36.0), 0.5)

csv_path = ROOT / "data" / "temperature_readings.csv"
if not csv_path.exists():
    generate()
df = pd.read_csv(csv_path)

if not MODEL_PATH.exists():
    st.warning("Model not found. In the project folder run `python src/train_model.py`, then refresh this page.")
    st.stop()
bundle = load_bundle()
model = bundle["model"]
history = df.tail(20).copy()
history.loc[history.index[-1], "temperature_c"] = current_temp
try:
    predicted = predict_next(model, history, ambient, heat_load, current_speed)
except Exception as exc:
    st.error(f"Prediction unavailable: {exc}")
    st.stop()
adaptive_speed = adaptive_controller(predicted, current_speed, low_temp, high_temp)
baseline_speed = threshold_controller(current_temp, low_temp, high_temp)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current temperature", f"{current_temp:.1f} °C")
c2.metric("Predicted next-minute temp", f"{predicted:.1f} °C", f"{predicted-current_temp:+.2f} °C")
c3.metric("AI fan command", f"{adaptive_speed}%")
c4.metric("Threshold baseline", f"{baseline_speed}%")
st.info("This dashboard calculates a recommended fan command; it does not control hardware unless you implement a suitable serial/Wi-Fi interface.")

st.subheader("Recent temperature readings")
plot_df = df.tail(180).copy()
fig, ax = plt.subplots(figsize=(10, 3.5))
ax.plot(np.arange(len(plot_df)), plot_df["temperature_c"], label="Temperature (°C)")
ax.set_xlabel("Recent samples (1 sample = 1 minute in demo data)")
ax.set_ylabel("Temperature (°C)")
ax.grid(True, alpha=0.3)
ax.legend()
st.pyplot(fig)
plt.close(fig)

st.subheader("Fan speed comparison")
fig2, ax2 = plt.subplots(figsize=(7, 3))
ax2.bar(["AI predictive", "Threshold baseline"], [adaptive_speed, baseline_speed])
ax2.set_ylim(0, 100)
ax2.set_ylabel("Fan speed command (%)")
ax2.grid(axis="y", alpha=0.3)
st.pyplot(fig2)
plt.close(fig2)

with st.expander("Model evaluation (held-out synthetic data)"):
    st.write("These metrics are calculated by a chronological hold-out test on generated synthetic data; they are not evidence of real-world performance.")
    st.json(bundle.get("metrics", {}))
    st.write("MAE and RMSE are in °C; lower is better. R² is a goodness-of-fit score and should be interpreted with the dataset context.")

st.subheader("Export a sample command")
st.download_button("Download current recommendation CSV", pd.DataFrame([{"current_temp_c": current_temp, "predicted_next_c": predicted, "ai_fan_speed_pct": adaptive_speed, "threshold_fan_speed_pct": baseline_speed}]).to_csv(index=False), file_name="fan_recommendation.csv", mime="text/csv")
