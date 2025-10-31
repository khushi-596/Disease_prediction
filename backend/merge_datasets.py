import pandas as pd

# Load CSVs (filenames and columns start with capital letters)
Weather = pd.read_csv("/content/Disease_prediction/backend/data/Weather.csv", parse_dates=["Date"])
Water   = pd.read_csv("/content/Disease_prediction/backend/data/Water.csv", parse_dates=["Date"])
Health  = pd.read_csv("/content/Disease_prediction/backend/data/Health.csv", parse_dates=["Date"])

# Merge step by step using exact column names
merged = pd.merge(Weather, Water, on=["Date", "Ward"], how="outer")
merged = pd.merge(merged, Health, on=["Date", "Ward"], how="outer")

# Fill numeric columns forward/backward
num_cols = merged.select_dtypes(include="number").columns
merged[num_cols] = merged[num_cols].fillna(method="ffill").fillna(method="bfill")

# Sort and save
merged = merged.sort_values(["Ward", "Date"])
merged.to_csv("/content/Disease_prediction/backend/data/raw_dataset.csv", index=False)
print("✅ Merged dataset saved:", merged.shape)
