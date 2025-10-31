# backend/simulate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_data(wards=8, days=365, start_date=None, seed=42):
    np.random.seed(seed)
    if start_date is None:
        start_date = datetime(2025,4,1)
    rows = []
    for w in range(1, wards+1):
        vuln = 1.0 + 0.2*np.random.rand()  # ward vulnerability
        lat = 18.52 + np.random.randn()*0.01
        lon = 73.85 + np.random.randn()*0.01
        for d in range(days):
            date = (start_date + timedelta(days=d)).date()
            temp = 28 + 4*np.sin(2*np.pi*(d/365)) + np.random.randn()*1.8
            rainfall = max(0, 8 + 6*np.sin(2*np.pi*(d/180)) + np.random.randn()*4)
            humidity = np.clip(65 + 10*np.random.randn(), 30, 100)
            wqi = np.clip(80 - 0.4*rainfall + np.random.randn()*3, 10, 100)
            # disease incidence influenced by rainfall, wqi, vuln
            cases = int(np.random.poisson(lam=max(0.5, (0.03*rainfall + 0.02*(30-temp) + (40-wqi)/15) * vuln + 0.5)))
            rows.append([date, f"Ward-{w}", lat, lon, temp, rainfall, humidity, wqi, cases])
    df = pd.DataFrame(rows, columns=["date","ward","lat","lon","temp","rainfall","humidity","wqi","reported_cases"])
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/raw_dataset.csv", index=False)
    print("Saved data/raw_dataset.csv")
    return df

if __name__ == "__main__":
    generate_data()
