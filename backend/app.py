from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import joblib, numpy as np, tensorflow as tf

app = FastAPI(title="🌈 Indradhanu Backend")

# Allow JS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount frontend for hosting
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Load models
rf_model = joblib.load("backend/models/rf_model.pkl")
lstm_model = tf.keras.models.load_model("backend/models/lstm_model.h5", compile=False)

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.post("/predict_rf/")
def predict_rf(data: dict):
    X = np.array([[data["Temp"], data["Humidity"], data["Rainfall"], data["Wqi"], data["Ph"],
                   data["Turbidity"], data["Cases_Lag1"], data["Cases_7d_Avg"], data["Rain_3d_Avg"]]])
    pred = rf_model.predict(X)[0]
    return {"risk_level": "HIGH" if pred == 1 else "LOW"}

@app.post("/predict_lstm/")
def predict_lstm(seq: list[list[float]]):
    arr = np.array(seq).reshape(1, len(seq), len(seq[0]))
    pred = lstm_model.predict(arr)
    return {"predicted_cases": float(pred[0][0])}
