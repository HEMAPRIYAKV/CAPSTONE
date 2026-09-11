import joblib
import pandas as pd

# Load trained model
model = joblib.load(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\ml\flood_model.pkl"
)

print("\n===== IDIECS FLOOD PREDICTION =====")

rainfall_1day = float(input("1-day rainfall (mm): "))
rainfall_3day = float(input("3-day rainfall (mm): "))
rainfall_7day = float(input("7-day rainfall (mm): "))
normal = float(input("Normal rainfall (mm): "))
deviation = float(input("Rainfall deviation (%): "))
temperature = float(input("Temperature (°C): "))
humidity = float(input("Humidity (%): "))
pressure = float(input("Pressure (hPa): "))
wind_speed = float(input("Wind speed (km/h): "))

# Input for XGBoost
input_data = pd.DataFrame([{
    "actual": rainfall_1day,
    "rainfall_1day": rainfall_1day,
    "rainfall_3day": rainfall_3day,
    "rainfall_7day": rainfall_7day,
    "normal": normal,
    "deviation": deviation,
    "temperature": temperature,
    "humidity": humidity,
    "pressure": pressure,
    "wind_speed": wind_speed
}])

# XGBoost probability
ml_probability = model.predict_proba(input_data)[0][1] * 100


# Prototype risk rules
if rainfall_7day >= 150 or rainfall_3day >= 80:
    risk = "HIGH"

elif rainfall_7day >= 75 or rainfall_3day >= 40:
    risk = "MEDIUM"

else:
    risk = "LOW"


print("\n================================")
print("        IDIECS RESULT")
print("================================")

print(f"XGBoost Probability : {ml_probability:.2f}%")
print(f"7-Day Rainfall      : {rainfall_7day:.2f} mm")
print(f"3-Day Rainfall      : {rainfall_3day:.2f} mm")

print("--------------------------------")

print(f"Prototype Risk Level : {risk}")

if risk == "HIGH":
    print("⚠️ FLOOD ALERT")
    print("Recommended Action  : Evacuate to a safe shelter")

elif risk == "MEDIUM":
    print("⚠️ FLOOD WATCH")
    print("Recommended Action  : Monitor conditions")

else:
    print("✓ NORMAL")
    print("Recommended Action  : No immediate evacuation required")

print("================================")