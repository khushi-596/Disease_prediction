import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
DATA_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

proc_path = DATA_DIR / "processed_dataset.csv"
if not proc_path.exists():
    raise FileNotFoundError(f"{proc_path} not found. Run ETL first.")

df = pd.read_csv(proc_path)

feature_cols = ["Temp", "Humidity", "Rainfall", "WQI", "pH", "Turbidity", "Cases_Lag1", "Cases_7d_Avg", "Rain_3d_Avg"]
feature_cols = [c for c in feature_cols if c in df.columns]
if not feature_cols:
    raise ValueError("No feature columns found in processed dataset.")

if "Reported_Cases" not in df.columns:
    raise ValueError("Target column 'Reported_Cases' missing in processed dataset.")

X = df[feature_cols]
y = (df["Reported_Cases"] > df["Reported_Cases"].mean()).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf = RandomForestClassifier(n_estimators=150, random_state=42)
rf.fit(X_train, y_train)

pred = rf.predict(X_test)
acc = accuracy_score(y_test, pred)
print(f"✅ RF trained. Accuracy: {acc:.3f}")

joblib.dump(rf, MODEL_DIR / "rf_model.pkl")
print("💾 Saved rf_model.pkl to", MODEL_DIR)
