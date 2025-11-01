import pandas as pd
import json
from pathlib import Path

# --- Define consistent base paths ---
BASE_DIR = Path(__file__).resolve().parent  # backend/
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# --- Input file ---
data_path = DATA_DIR / "processed_dataset.csv"
if not data_path.exists():
    raise FileNotFoundError(f"{data_path} not found! Run ETL first.")

df = pd.read_csv(data_path)

# --- Normalize columns ---
df.columns = df.columns.str.lower()

expected_cols = {"ward", "reported_cases", "rainfall", "temp", "humidity", "wqi"}
missing = expected_cols - set(df.columns)
if missing:
    raise ValueError(f"Missing columns in processed dataset: {missing}")

# --- Summarize by ward ---
ward_summary = (
    df.groupby("ward")
      .agg({
          "reported_cases": "mean",
          "rainfall": "mean",
          "temp": "mean",
          "humidity": "mean",
          "wqi": "mean"
      })
      .round(2)
      .reset_index()
)

# --- Risk labeling ---
overall_avg = df["reported_cases"].mean()
ward_summary["risk_level"] = ward_summary["reported_cases"].apply(
    lambda x: "HIGH" if x > overall_avg else "LOW"
)

# --- Prepare summary dictionary ---
summary = {
    "wards": ward_summary.to_dict(orient="records"),
    "metadata": {
        "total_wards": int(ward_summary.shape[0]),
        "avg_cases": round(float(overall_avg), 2)
    }
}

# --- Save summary ---
output_path = DATA_DIR / "admin_summary.json"
with open(output_path, "w") as f:
    json.dump(summary, f, indent=2)

print(f"✅ Admin summary saved to {output_path.resolve()}")
