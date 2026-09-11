import pandas as pd
import joblib

from sklearn.model_selection import train_test_split


# ============================================================
# LOAD DATA
# ============================================================

data = pd.read_csv(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\balanced_training_data.csv"
)


# ============================================================
# FEATURES
# ============================================================

features = [
    "actual",
    "rainfall_1day",
    "rainfall_3day",
    "rainfall_7day",
    "normal",
    "deviation",
    "temperature",
    "humidity",
    "pressure",
    "wind_speed"
]

X = data[features]
y = data["flood_occurred"]


# ============================================================
# SAME TRAIN-TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

model = joblib.load(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\ml\flood_model.pkl"
)


# ============================================================
# GET FLOOD PROBABILITIES
# ============================================================

probabilities = model.predict_proba(X_test)[:, 1]


# ============================================================
# CREATE RESULT TABLE
# ============================================================

results = pd.DataFrame({

    "Actual": y_test.values,

    "Flood_Probability_%": (
        probabilities * 100
    ).round(2),

    "Rainfall_1day": X_test["rainfall_1day"].values,

    "Rainfall_3day": X_test["rainfall_3day"].values,

    "Rainfall_7day": X_test["rainfall_7day"].values

})


# Sort by probability

results = results.sort_values(
    "Flood_Probability_%",
    ascending=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n==========================================")
print("XGBOOST FLOOD PROBABILITY RESULTS")
print("==========================================")

print(
    results.to_string(index=False)
)


# ============================================================
# SUMMARY
# ============================================================

print("\n==========================================")
print("PROBABILITY SUMMARY")
print("==========================================")

print(
    "\nFlood cases:"
)

print(
    results[
        results["Actual"] == 1
    ]["Flood_Probability_%"].describe()
)


print(
    "\nNo-flood cases:"
)

print(
    results[
        results["Actual"] == 0
    ]["Flood_Probability_%"].describe()
)