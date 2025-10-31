import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Force CPU mode

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

# Paths
DATA_PATH = "data/processed_dataset.csv"
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# ========== LSTM Training ==========
def train_lstm_sequences(df, seq_len=5, epochs=3):
    print("\n🔄 Preparing sequences for LSTM...")
    sequences, targets = [], []
    for ward, g in df.groupby("ward"):
        vals = g["reported_cases"].values
        for i in range(len(vals) - seq_len):
            sequences.append(vals[i:i + seq_len])
            targets.append(vals[i + seq_len])
    X = np.array(sequences).reshape(-1, seq_len, 1).astype(float)
    y = np.array(targets).astype(float)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = Sequential([
        LSTM(16, input_shape=(seq_len, 1)),
        Dense(8, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    es = EarlyStopping(patience=2, restore_best_weights=True)
    print(f"🚀 Training LSTM for {epochs} epochs...")
    model.fit(X_train, y_train, validation_data=(X_test, y_test),
              epochs=epochs, batch_size=16, verbose=1, callbacks=[es])

    preds = model.predict(X_test, verbose=0)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"✅ LSTM training done. RMSE={rmse:.3f}")

    model.save(os.path.join(MODELS_DIR, "lstm_model.h5"))
    return model


# ========== Random Forest Training ==========
def train_random_forest(df, lstm_model=None, seq_len=5):
    print("\n🌳 Preparing data for Random Forest...")
    df = df.sort_values(["ward", "date"])

    # Efficient LSTM batch predictions
    lstm_preds = []
    for ward, g in df.groupby("ward"):
        vals = g["reported_cases"].values
        if len(vals) <= seq_len or lstm_model is None:
            lstm_preds.extend([0] * len(vals))
            continue
        X_seq = np.array([vals[i - seq_len:i] for i in range(seq_len, len(vals))]).reshape(-1, seq_len, 1)
        preds = lstm_model.predict(X_seq, verbose=0).ravel()
        lstm_preds.extend([0] * seq_len + list(preds))

    df["lstm_pred"] = lstm_preds

    features = ["temp", "rainfall", "wqi", "cases_lag1", "cases_7d_avg", "lstm_pred"]
    df = df.dropna()
    X = df[features]
    y = df["reported_cases"]

    print("🚀 Training Random Forest...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestRegressor(n_estimators=50, random_state=42)
    rf.fit(X_train, y_train)

    preds = rf.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    print(f"✅ RF training done. RMSE={rmse:.3f}, R2={r2:.3f}")

    joblib.dump(rf, os.path.join(MODELS_DIR, "rf_model.pkl"))
    print("💾 Saved models/rf_model.pkl")


# ========== Main Pipeline ==========
def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("❌ processed_dataset.csv not found. Run etl.py first!")

    df = pd.read_csv(DATA_PATH)
    print(f"📊 Loaded {len(df)} rows from {DATA_PATH}")

    # Train LSTM
    lstm_model = train_lstm_sequences(df, seq_len=5, epochs=3)

    # Train Random Forest using LSTM predictions
    train_random_forest(df, lstm_model)

    print("\n🎉 All models trained successfully and saved in /models")


if __name__ == "__main__":
    main()
