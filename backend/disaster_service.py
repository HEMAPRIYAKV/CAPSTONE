"""
Integrated Disaster Intelligence Service

Connects:
    Weather
    Flood Prediction
    Risk Assessment
    Road Risk
    Routing
    Shelter Recommendation
    Alerts
"""


from .risk_engine import assess_risk
from .road_risk import assess_road_risk
from .shelter import select_shelter
from .alerts import generate_alert


def analyze_disaster(
    flood_probability: float,
    shelters: list | None = None
) -> dict:
    """
    Execute the integrated disaster-response pipeline.

    This function will later receive the prediction generated
    by the existing XGBoost backend.
    """

    # -----------------------------------------
    # 1. FLOOD RISK ASSESSMENT
    # -----------------------------------------

    risk_result = assess_risk(
        flood_probability
    )

    risk_level = risk_result["risk_level"]

    # -----------------------------------------
    # 2. SHELTER SELECTION
    # -----------------------------------------

    recommended_shelter = None

    if shelters:
        recommended_shelter = select_shelter(
            shelters
        )

    # -----------------------------------------
    # 3. ALERT GENERATION
    # -----------------------------------------

    alert = generate_alert(
        risk_level=risk_level,
        flood_probability=flood_probability,
        shelter=recommended_shelter
    )

    # -----------------------------------------
    # 4. FINAL RESPONSE
    # -----------------------------------------

    return {
        "flood": risk_result,
        "shelter": recommended_shelter,
        "alert": alert
    }