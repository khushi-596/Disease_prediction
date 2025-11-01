import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

proc_path = DATA_DIR / "processed_dataset.csv"
if not proc_path.exists():
    raise FileNotFoundError(f"{proc_path} not found. Run ETL first.")

df = pd.read_csv(proc_path, parse_dates=["Date"])
df = df.sort_values(["Ward", "Date"])

# Select a ward to train on (example: first unique ward)
if "Ward" not in df.columns:
    raise ValueError("Column 'Ward' missing in processed dataset.")
ward_name = df["Ward"].unique()[0]
ward_df = df[df["Ward"] == ward_name]

features = ["Temp", "Humidity", "Rainfall", "WQI", "pH", "Turbidity", "Cases_Lag1", "Cases_7d_Avg", "Rain_3d_Avg"]
features = [f for f in features if f in ward_df.columns]
target = "Reported_Cases"
if target not in ward_df.columns:
    raise ValueError(f"Target column '{target}' missing in processed dataset.")

X = ward_df[features].values
y = ward_df[target].values.reshape(-1, 1)

# Scaling
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y)

def make_seq(X, y, win=7):
    Xs, ys = [], []
    for i in range(win, len(X)):
        Xs.append(X[i - win:i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)

X_seq, y_seq = make_seq(X_scaled, y_scaled, win=7)
if X_seq.size == 0:
    raise ValueError("Not enough data to create sequences. Need more rows per ward.")

model = Sequential([
    LSTM(64, input_shape=(X_seq.shape[1], X_seq.shape[2]), return_sequences=True),
    Dropout(0.2),
    LSTM(32),
    Dense(1)
])
model.compile(optimizer="adam", loss="mse")
model.fit(X_seq, y_seq, epochs=30, batch_size=16, verbose=1)

model.save(MODEL_DIR / "lstm_model.h5")
joblib.dump(scaler_X, MODEL_DIR / "scaler_X.pkl")
joblib.dump(scaler_y, MODEL_DIR / "scaler_y.pkl")
print("✅ LSTM & scalers saved to", MODEL_DIR)
