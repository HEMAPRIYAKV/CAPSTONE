"""
Road Risk Engine

Converts location-level flood probability into
road-level disaster risk.

The road risk combines:

    XGBoost flood probability
    +
    road flood exposure
    +
    road condition
"""

RISK_PENALTIES = {
    "LOW": 1.0,
    "MEDIUM": 5.0,
    "HIGH": 20.0,
    "BLOCKED": float("inf")
}


ROAD_CONDITION_PENALTIES = {
    "GOOD": 0.0,
    "FAIR": 1.0,
    "POOR": 3.0,
    "BLOCKED": float("inf")
}


def calculate_effective_risk(
    flood_probability: float,
    road_exposure: float
) -> float:
    """
    Calculate effective flood risk for a road.

    flood_probability:
        XGBoost prediction between 0 and 1.

    road_exposure:
        Road-specific flood exposure between 0 and 1.

    The two values are combined to create a
    road-level risk score.
    """

    flood_probability = max(
        0.0,
        min(1.0, float(flood_probability))
    )

    road_exposure = max(
        0.0,
        min(1.0, float(road_exposure))
    )

    # Weighted combination.
    #
    # Flood prediction has greater influence,
    # while road exposure provides local differentiation.

    effective_risk = (
        0.7 * flood_probability
        +
        0.3 * road_exposure
    )

    return effective_risk


def classify_road_risk(
    effective_risk: float
) -> str:
    """
    Convert effective road risk into LOW/MEDIUM/HIGH.
    """

    if effective_risk >= 0.70:

        return "HIGH"

    elif effective_risk >= 0.30:

        return "MEDIUM"

    return "LOW"


def calculate_road_cost(
    distance_km: float,
    flood_probability: float,
    road_exposure: float = 0.0,
    road_condition: str = "GOOD",
    blocked: bool = False
) -> dict:
    """
    Calculate the complete disaster-aware cost
    of a road segment.
    """

    # --------------------------------------------------------
    # BLOCKED ROAD
    # --------------------------------------------------------

    if blocked:

        return {
            "risk_level": "BLOCKED",
            "effective_risk": 1.0,
            "cost": float("inf"),
            "blocked": True
        }


    road_condition = road_condition.upper()


    if road_condition == "BLOCKED":

        return {
            "risk_level": "BLOCKED",
            "effective_risk": 1.0,
            "cost": float("inf"),
            "blocked": True
        }


    # --------------------------------------------------------
    # EFFECTIVE FLOOD RISK
    # --------------------------------------------------------

    effective_risk = calculate_effective_risk(
        flood_probability,
        road_exposure
    )


    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    risk_level = classify_road_risk(
        effective_risk
    )


    # --------------------------------------------------------
    # RISK PENALTY
    # --------------------------------------------------------

    risk_penalty = RISK_PENALTIES[
        risk_level
    ]


    # --------------------------------------------------------
    # ROAD CONDITION PENALTY
    # --------------------------------------------------------

    condition_penalty = ROAD_CONDITION_PENALTIES.get(
        road_condition,
        0.0
    )


    # --------------------------------------------------------
    # TOTAL COST
    # --------------------------------------------------------

    total_cost = (
        float(distance_km)
        +
        risk_penalty
        +
        condition_penalty
    )


    return {

        "risk_level":
            risk_level,

        "effective_risk":
            round(
                effective_risk,
                4
            ),

        "cost":
            round(
                total_cost,
                3
            ),

        "blocked":
            False
    }