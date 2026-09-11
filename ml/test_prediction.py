import pandas as pd
import joblib

# Load model
model = joblib.load(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\ml\flood_model.pkl"
)

# Load data
data = pd.read_csv(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\prototype_training_data.csv"
)

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

# Get probabilities
probabilities = model.predict_proba(data[features])[:, 1]

data["flood_probability"] = probabilities

# Show highest-risk records
result = data.sort_values(
    "flood_probability",
    ascending=False
)

print("\n===== TOP 10 FLOOD PREDICTIONS =====")
print(
    result[
        [
            "date",
            "state_name",
            "rainfall_3day",
            "rainfall_7day",
            "humidity",
            "flood_probability",
            "flood_occurred"
        ]
    ].head(10).to_string(index=False)
)