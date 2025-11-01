from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import joblib
import numpy as np
import tensorflow as tf

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
FRONTEND_DIR = BASE_DIR.parent / "frontend"

DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

app = FastAPI(title="🌈 Indradhanu Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files at /frontend
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# Load models (safe-file checks)
rf_path = MODEL_DIR / "rf_model.pkl"
lstm_path = MODEL_DIR / "lstm_model.h5"

rf_model = None
lstm_model = None

if rf_path.exists():
    rf_model = joblib.load(rf_path)
    print(f"✅ Loaded RF model from {rf_path}")
else:
    print(f"⚠️ RF model not found at {rf_path}. /predict_rf will fail until model is trained/saved.")

if lstm_path.exists():
    lstm_model = tf.keras.models.load_model(lstm_path, compile=False)
    print(f"✅ Loaded LSTM model from {lstm_path}")
else:
    print(f"⚠️ LSTM model not found at {lstm_path}. /predict_lstm will fail until model is trained/saved.")

@app.get("/")
def root():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return JSONResponse({"message": "Frontend not found. Visit /frontend if mounted."})

class RFInput(BaseModel):
    Temp: float
    Humidity: float
    Rainfall: float
    Wqi: float
    Ph: float
    Turbidity: float
    Cases_Lag1: float
    Cases_7d_Avg: float
    Rain_3d_Avg: float

@app.post("/predict_rf/")
def predict_rf(data: RFInput):
    if rf_model is None:
        return JSONResponse({"error": "RF model not available"}, status_code=503)

    X = np.array([[
        data.Temp, data.Humidity, data.Rainfall, data.Wqi,
        data.Ph, data.Turbidity, data.Cases_Lag1, data.Cases_7d_Avg, data.Rain_3d_Avg
    ]], dtype=float)

    try:
        pred = rf_model.predict(X)[0]
        risk = "HIGH" if int(pred) == 1 else "LOW"
        return {"risk_level": risk}
    except Exception as e:
        return JSONResponse({"error": "Prediction failed", "detail": str(e)}, status_code=500)

@app.post("/predict_lstm/")
def predict_lstm(seq: list[list[float]]):
    if lstm_model is None:
        return JSONResponse({"error": "LSTM model not available"}, status_code=503)

    try:
        arr = np.array(seq, dtype=float)
        # If user sends a single sequence (timesteps x features), we ensure proper shape
        if arr.ndim == 2:
            arr = arr.reshape(1, arr.shape[0], arr.shape[1])
        pred = lstm_model.predict(arr)
        # Assume model outputs one value per sample
        return {"predicted_cases": float(pred[0][0])}
    except Exception as e:
        return JSONResponse({"error": "LSTM prediction failed", "detail": str(e)}, status_code=500)

from fastapi.responses import JSONResponse
import json

@app.get("/admin_summary")
def get_admin_summary():
    summary_path = DATA_DIR / "admin_summary.json"
    if not summary_path.exists():
        return JSONResponse({"error": "admin_summary.json not found. Run admin_summary.py first."}, status_code=404)
    with open(summary_path) as f:
        data = json.load(f)
    return data
