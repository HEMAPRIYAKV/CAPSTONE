"""
Flood Risk Assessment Engine

Converts the probability produced by the XGBoost
flood prediction model into a meaningful risk level.
"""

# ------------------------------------------------------------
# RISK THRESHOLDS
# ------------------------------------------------------------
# These are currently aligned with the thresholds that were
# already being used in the existing prediction system.
#
# We can tune them later using model evaluation/calibration.
# ------------------------------------------------------------

LOW_THRESHOLD = 0.30
HIGH_THRESHOLD = 0.70


def assess_risk(flood_probability: float) -> dict:
    """
    Convert flood probability into a flood-risk level.

    Parameters
    ----------
    flood_probability : float
        XGBoost probability in the range 0.0 - 1.0.

    Returns
    -------
    dict
        Flood probability, percentage, risk level and action.
    """

    # Keep probability inside valid range
    flood_probability = max(
        0.0,
        min(1.0, float(flood_probability))
    )

    # --------------------------------------------------------
    # CLASSIFY RISK
    # --------------------------------------------------------

    if flood_probability >= HIGH_THRESHOLD:

        risk_level = "HIGH"

        action = (
            "Evacuate to a safe shelter "
            "using the recommended route"
        )

    elif flood_probability >= LOW_THRESHOLD:

        risk_level = "MEDIUM"

        action = (
            "Monitor the situation and "
            "prepare for possible evacuation"
        )

    else:

        risk_level = "LOW"

        action = (
            "No immediate evacuation required; "
            "continue monitoring conditions"
        )

    return {

        "flood_probability": round(
            flood_probability,
            4
        ),

        "probability_percent": round(
            flood_probability * 100,
            2
        ),

        "risk_level": risk_level,

        "action": action
    }