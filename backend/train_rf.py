import pandas as pd, joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

df = pd.read_csv("/content/Disease_prediction/backend/data/processed_dataset.csv")

# match exact names from your dataset
X = df[["Temp","Humidity","Rainfall","WQI","pH","Turbidity",
        "Cases_Lag1","Cases_7d_Avg","Rain_3d_Avg"]]
y = (df["Reported_Cases"] > df["Reported_Cases"].mean()).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf = RandomForestClassifier(n_estimators=150, random_state=42)
rf.fit(X_train, y_train)

pred = rf.predict(X_test)
acc = accuracy_score(y_test, pred)
print(f"✅ RF trained. Accuracy: {acc:.3f}")

joblib.dump(rf, "/content/Disease_prediction/backend/models/rf_model.pkl")
print("💾 Saved rf_model.pkl")
