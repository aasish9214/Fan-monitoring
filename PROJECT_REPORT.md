# Capstone Project Report

## Title
**AI-Based Adaptive Fan Speed Control Using Temperature Prediction**

## Abstract
This project develops a prototype for predicting near-future temperature and using the prediction to recommend fan speed. A Random Forest regression model uses recent temperature history, rolling averages, ambient temperature, estimated heat load, and the previous fan command. The predicted temperature is mapped to a bounded fan-speed command and compared with a threshold-based controller. Python and scikit-learn implement the data pipeline and model, while Streamlit presents temperature history, model metrics, and fan commands. An ESP32 PWM example is provided for a low-voltage hardware prototype. The included dataset is simulated and is intended for software demonstration; real sensor collection and controlled experiments are required before drawing conclusions about physical performance.

## 1. Problem statement
Conventional threshold-based fan control reacts after temperature crosses a chosen level. The project investigates whether forecasting the next temperature sample can provide a more anticipatory cooling command while limiting abrupt changes in fan speed.

## 2. Objectives
1. Generate or collect timestamped temperature readings.
2. Engineer time-series features from recent measurements.
3. Train a regression model for next-sample temperature prediction.
4. Convert the prediction to a 0–100% fan command.
5. Compare predictive control with a threshold baseline.
6. Visualize readings, commands, and prediction metrics.
7. Demonstrate a safe path to an ESP32-controlled low-voltage fan.

## 3. System architecture

```text
Temperature sensor / CSV data
            |
            v
   Data validation and ordering
            |
            v
 Lag features + rolling averages
            |
            v
 Random Forest temperature predictor
            |
            v
 Predicted next temperature
            |
            v
 Bounded fan-speed policy ---> Fan driver ---> DC fan
            |
            +----> Dashboard / CSV log

Baseline path: Current temperature ---> Threshold controller ---> Comparison
```

## 4. Tools and components
- Software: Python, Pandas, NumPy, scikit-learn, Matplotlib, Streamlit, joblib.
- Controller: ESP32 (suggested) or compatible Arduino board.
- Sensor: DS18B20 or another appropriately interfaced temperature sensor.
- Actuator: low-voltage DC fan and compatible MOSFET/driver.

## 5. Dataset and preprocessing
The repository generates a deterministic synthetic series with temperature, ambient temperature, heat-load estimate, and fan-speed command. The synthetic process imitates gradual ambient changes, heating, cooling, and sensor noise; it is not a substitute for physical measurements. Samples are ordered chronologically. Features are formed from the current value, two lags, and 5- and 15-sample moving averages. The target is the following sample's temperature. Rows without complete lag/rolling features or target values are removed.

For a physical experiment, log sensor readings at a consistent interval and record sensor type, placement, ambient conditions, fan specification, supply voltage, and heat-load changes. Check for missing values and impossible readings before training.

## 6. Model methodology
A Random Forest regressor is trained on the first 80% of the feature rows and evaluated on the final 20%. This chronological split is preferable to a shuffled split for forecasting. The random seed and model parameters are fixed for reproducibility. The model is serialized to `models/temperature_model.joblib` with the evaluation metrics.

### Evaluation metrics
- **MAE:** mean absolute difference between predicted and actual temperature, in °C.
- **RMSE:** square root of mean squared prediction error, in °C; it penalizes larger errors more heavily.
- **R²:** goodness-of-fit score relative to predicting the test-set mean.

Metrics produced from the included generated dataset must be labeled *synthetic-data results*. Recalculate them using held-out measured sensor data for a real-world claim.

## 7. Control strategy
The baseline controller maps current temperature linearly from 0% fan speed at the configured lower threshold to 100% at the upper threshold. The predictive controller applies the same mapping to the predicted next temperature, then limits each update to a maximum change of 20 percentage points. Commands are clipped to 0–100%. The dashboard permits changing the thresholds. A practical deployment should add sensor validation, minimum fan speed where required by the fan, hysteresis, manual override, watchdog behavior, and a safe fallback.

## 8. Software implementation
- `src/generate_data.py`: reproducible synthetic dataset generation.
- `src/model.py`: feature engineering, model training, evaluation, serialization, and prediction.
- `src/controller.py`: baseline and predictive control policies and PWM conversion.
- `app.py`: dashboard for current inputs, next-step prediction, speed comparison, trend plot, metrics, and CSV export.
- `firmware/esp32_fan_pwm.ino`: Serial-command PWM output example for an ESP32.

## 9. Hardware implementation and safety
Use a compatible sensor interface and a driver circuit rated for the fan's current. Do not connect a fan directly to a microcontroller GPIO. The firmware example accepts a speed percentage over USB Serial; the Python dashboard does not automatically communicate with the ESP32. A full integrated prototype must implement and test a serial or network link, sensor acquisition, error handling, and fallback behavior. Validate at low voltage before longer operation.

## 10. Results and discussion
Run `python src/train_model.py` to create the synthetic dataset, train the model, and print MAE, RMSE, R², and test sample count. Run `streamlit run app.py` to view the plots and compare fan commands. Insert the actual printed metrics into the final submission and state explicitly that they are synthetic. After hardware testing, add a table comparing both controllers over identical test scenarios.

Suggested results table for measured experiments:

| Test condition | Controller | MAE (°C) | Peak temperature (°C) | Settling time (s) | Average PWM (%) |
|---|---|---:|---:|---:|---:|
| Constant load | Threshold | To measure | To measure | To measure | To measure |
| Constant load | Predictive | To measure | To measure | To measure | To measure |
| Heat-load step | Threshold | To measure | To measure | To measure | To measure |
| Heat-load step | Predictive | To measure | To measure | To measure | To measure |

## 11. Limitations
- The included dataset is simulated, not collected from a physical system.
- Heat load is a simplified estimated input.
- The demo predicts one time step and assumes regular sampling.
- The dashboard recommends commands but does not connect to hardware.
- Fan PWM behavior depends on the specific fan and driver.
- No energy savings or superior performance should be claimed without measurements.

## 12. Future enhancements
1. Collect sensor data continuously and retrain with measured operating conditions.
2. Add a serial/Wi-Fi interface and ESP32 sensor acquisition.
3. Add anomaly detection and a sensor-disconnection fallback.
4. Compare Random Forest with linear regression, gradient boosting, and simple persistence forecasting.
5. Evaluate power using an actual current/voltage measurement rather than PWM duty alone.
6. Tune the controller using controlled tests and add hysteresis or a more advanced control method.

## Conclusion
This project provides an end-to-end software prototype for next-step temperature prediction and adaptive fan-speed recommendation. It includes reproducible data generation, time-series feature engineering, a trained regression model, evaluation metrics, a baseline controller, visualization, and an ESP32 PWM example. The software can be demonstrated without hardware and extended with real sensor measurements. The next essential step for a credible physical capstone is to collect measured data, integrate a properly rated fan driver, and compare both controllers under identical test conditions.
