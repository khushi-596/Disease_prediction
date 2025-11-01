import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

raw_path = DATA_DIR / "raw_dataset.csv"
proc_path = DATA_DIR / "processed_dataset.csv"

if not raw_path.exists():
    raise FileNotFoundError(f"{raw_path} not found. Run merge_datasets.py first.")

df = pd.read_csv(raw_path, parse_dates=["Date"])
df = df.sort_values(["Ward", "Date"])

# Normalize column names to expected casing if necessary
# Assuming your CSV uses columns like Temp, Humidity, etc. If different, adjust list below.
num_cols = ["Temp", "Humidity", "Rainfall", "WQI", "pH", "Turbidity", "Reported_Cases"]
available_num_cols = [c for c in num_cols if c in df.columns]

# Interpolate only numeric available columns
if available_num_cols:
    df[available_num_cols] = df[available_num_cols].interpolate(limit_direction="both")

# Create lag and rolling features safely (only if column exists)
if "Reported_Cases" in df.columns:
    df["Cases_Lag1"] = df.groupby("Ward")["Reported_Cases"].shift(1).fillna(0)
    df["Cases_7d_Avg"] = (
        df.groupby("Ward")["Reported_Cases"]
          .rolling(7, min_periods=1)
          .mean()
          .reset_index(0, drop=True)
    )
else:
    df["Cases_Lag1"] = 0
    df["Cases_7d_Avg"] = 0

if "Rainfall" in df.columns:
    df["Rain_3d_Avg"] = (
        df.groupby("Ward")["Rainfall"]
          .rolling(3, min_periods=1)
          .mean()
          .reset_index(0, drop=True)
    )
else:
    df["Rain_3d_Avg"] = 0

# Ward code
if "Ward" in df.columns:
    df["Ward_Code"] = df["Ward"].astype("category").cat.codes
else:
    df["Ward_Code"] = -1

df.to_csv(proc_path, index=False)
print("✅ Processed dataset saved:", df.shape)
