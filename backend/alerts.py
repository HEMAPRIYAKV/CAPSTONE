"""
Emergency Alert Module
"""


def generate_alert(
    risk_level: str,
    flood_probability: float,
    shelter: dict | None = None
) -> dict:
    """
    Generate an emergency response message based on flood risk.
    """

    risk_level = risk_level.upper()

    if risk_level == "HIGH":

        message = (
            "High flood risk detected. "
            "Follow the recommended evacuation route "
            "and proceed toward the designated safe shelter."
        )

        severity = "HIGH"

    elif risk_level == "MEDIUM":

        message = (
            "Moderate flood risk detected. "
            "Monitor the situation and prepare for possible evacuation."
        )

        severity = "MEDIUM"

    else:

        message = (
            "Low flood risk detected. "
            "Continue monitoring weather and flood conditions."
        )

        severity = "LOW"

    alert = {
        "severity": severity,
        "flood_probability": round(
            flood_probability,
            4
        ),
        "message": message
    }

    if shelter:
        alert["recommended_shelter"] = shelter.get(
            "name"
        )

    return alert