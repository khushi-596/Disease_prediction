import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

weather_path = DATA_DIR / "Weather.csv"
water_path = DATA_DIR / "Water.csv"
health_path = DATA_DIR / "Health.csv"
out_path = DATA_DIR / "raw_dataset.csv"

# Basic existence checks
for p in (weather_path, water_path, health_path):
    if not p.exists():
        raise FileNotFoundError(f"Required file not found: {p}")

Weather = pd.read_csv(weather_path, parse_dates=["Date"])
Water   = pd.read_csv(water_path, parse_dates=["Date"])
Health  = pd.read_csv(health_path, parse_dates=["Date"])

# Merge step by step using exact column names ("Date" and "Ward" expected)
merged = pd.merge(Weather, Water, on=["Date", "Ward"], how="outer")
merged = pd.merge(merged, Health, on=["Date", "Ward"], how="outer")

# Fill numeric columns forward/backward and fallback to 0
num_cols = merged.select_dtypes(include="number").columns
if len(num_cols) > 0:
    merged[num_cols] = merged[num_cols].fillna(method="ffill").fillna(method="bfill").fillna(0)

merged = merged.sort_values(["Ward", "Date"])
merged.to_csv(out_path, index=False)
print("✅ Merged dataset saved:", merged.shape)
