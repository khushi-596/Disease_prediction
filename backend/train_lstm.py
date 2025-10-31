import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # hide TF warnings

import pandas as pd, numpy as np, joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# ... rest of your code


df = pd.read_csv("/content/Disease_prediction/backend/data/processed_dataset.csv")
df = df.sort_values(["Ward","Date"])
ward_df = df[df["Ward"] == df["Ward"].unique()[0]]

features = ["Temp","Humidity","Rainfall","WQI","pH","Turbidity","Cases_Lag1","Cases_7d_Avg","Rain_3d_Avg"]
target = "Reported_Cases"

X = ward_df[features].values
y = ward_df[target].values.reshape(-1,1)

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y)

def make_seq(X,y,win=7):
    Xs,ys=[],[]
    for i in range(win,len(X)):
        Xs.append(X[i-win:i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)

X_seq,y_seq = make_seq(X_scaled,y_scaled)

model = Sequential([
    LSTM(64, input_shape=(X_seq.shape[1],X_seq.shape[2]), return_sequences=True),
    Dropout(0.2),
    LSTM(32),
    Dense(1)
])
model.compile(optimizer="adam", loss="mse")
model.fit(X_seq, y_seq, epochs=30, batch_size=16, verbose=1)

model.save("/content/Disease_prediction/backend/models/lstm_model.h5")
joblib.dump(scaler_X, "/content/Disease_prediction/backend/models/scaler_X.pkl")
joblib.dump(scaler_y, "/content/Disease_prediction/backend/models/scaler_y.pkl")
print("✅ LSTM & scalers saved")
