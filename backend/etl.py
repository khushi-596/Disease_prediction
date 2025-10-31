import pandas as pd

# read merged file using correct column names
df = pd.read_csv("/content/Disease_prediction/backend/data/raw_dataset.csv", parse_dates=["Date"])
df = df.sort_values(["Ward", "Date"])

# interpolate numeric columns
num_cols = ["Temp","Humidity","Rainfall","WQI","pH","Turbidity","Reported_Cases"]
df[num_cols] = df[num_cols].interpolate(limit_direction="both")

# create lag and rolling features (note: use your actual column names)
df["Cases_Lag1"] = df.groupby("Ward")["Reported_Cases"].shift(1).fillna(0)
df["Cases_7d_Avg"] = (
    df.groupby("Ward")["Reported_Cases"]
      .rolling(7, min_periods=1)
      .mean()
      .reset_index(0, drop=True)
)
df["Rain_3d_Avg"] = (
    df.groupby("Ward")["Rainfall"]
      .rolling(3, min_periods=1)
      .mean()
      .reset_index(0, drop=True)
)
df["Ward_Code"] = df["Ward"].astype("category").cat.codes

df.to_csv("/content/Disease_prediction/backend/data/processed_dataset.csv", index=False)
print("✅ Processed dataset saved:", df.shape)
