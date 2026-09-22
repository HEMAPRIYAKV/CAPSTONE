import joblib
import pandas as pd
import os

from backend.risk_engine import assess_risk


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

    # --------------------------------------------------------
    # FEATURES USED BY THE TRAINED XGBOOST MODEL
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # PREPARE MODEL INPUT
    # --------------------------------------------------------

    input_data = pd.DataFrame([{

        # The existing trained model expects "actual".
        # We preserve the same mapping used previously.
        "actual":
            data["rainfall_1day"],

        "rainfall_1day":
            data["rainfall_1day"],

        "rainfall_3day":
            data["rainfall_3day"],

        "rainfall_7day":
            data["rainfall_7day"],

        "normal":
            data["normal"],

        "deviation":
            data["deviation"],

        "temperature":
            data["temperature"],

        "humidity":
            data["humidity"],

        "pressure":
            data["pressure"],

        "wind_speed":
            data["wind_speed"]
    }])


    # ========================================================
    # XGBOOST FLOOD PROBABILITY
    # ========================================================

    probability = model.predict_proba(
        input_data[features]
    )[0][1]

    probability = float(probability)


    # ========================================================
    # RISK ASSESSMENT
    # ========================================================

    risk_result = assess_risk(
        probability
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "probability":
            risk_result["probability_percent"],

        "probability_decimal":
            risk_result["flood_probability"],

        "risk":
            risk_result["risk_level"],

        "action":
            risk_result["action"]
    }