import joblib
import pandas as pd
import os


# ============================================================
# LOAD XGBOOST MODEL
# ============================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "flood_model.pkl"
)

model = joblib.load(MODEL_PATH)


# ============================================================
# FLOOD PREDICTION
# ============================================================

def predict_flood(data):

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

    # Prepare input for XGBoost
    input_data = pd.DataFrame([{

        "actual": data["rainfall_1day"],

        "rainfall_1day": data["rainfall_1day"],
        "rainfall_3day": data["rainfall_3day"],
        "rainfall_7day": data["rainfall_7day"],

        "normal": data["normal"],
        "deviation": data["deviation"],

        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "pressure": data["pressure"],
        "wind_speed": data["wind_speed"]

    }])


    # ========================================================
    # XGBOOST FLOOD PROBABILITY
    # ========================================================

    probability = model.predict_proba(
        input_data[features]
    )[0][1]

    probability_percent = float(probability) * 100


    # ========================================================
    # RISK CLASSIFICATION
    # ========================================================

    if probability_percent < 30:

        risk = "LOW RISK"

        action = (
            "No immediate evacuation required"
        )

    elif probability_percent < 70:

        risk = "MEDIUM RISK"

        action = (
            "Monitor the situation and "
            "prepare for evacuation"
        )

    else:

        risk = "RISKY"

        action = (
            "Evacuate to a safe shelter"
        )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "probability": round(
            probability_percent,
            2
        ),

        "risk": risk,

        "action": action

    }