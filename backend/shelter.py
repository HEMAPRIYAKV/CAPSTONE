"""
Shelter Management Module

Loads candidate shelters and provides the
information required by the evacuation system.

Shelter suitability considers:

    - route distance
    - route flood exposure
    - available capacity
    - accessibility
"""


import csv
import os


SHELTER_DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "shelters.csv"
)


def load_shelters():
    """
    Load shelters from the local CSV dataset.
    """

    if not os.path.exists(SHELTER_DATA_PATH):
        raise FileNotFoundError(
            f"Shelter dataset not found:\n"
            f"{SHELTER_DATA_PATH}"
        )

    shelters = []

    with open(
        SHELTER_DATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            shelters.append({
                "id": row["id"],
                "name": row["name"],
                "latitude": float(
                    row["latitude"]
                ),
                "longitude": float(
                    row["longitude"]
                ),
                "capacity": int(
                    row["capacity"]
                ),
                "available_capacity": int(
                    row["available_capacity"]
                ),
                "accessibility":
                    row[
                        "accessibility"
                    ].strip().lower() == "true"
            })

    return shelters


def calculate_shelter_score(
    distance_km,
    route_exposure,
    available_capacity,
    accessibility
):
    """
    Calculate a suitability score.

    Lower score = more suitable.

    This is a prototype engineering score and
    can later be calibrated experimentally.
    """

    capacity_penalty = 0.0

    if available_capacity <= 0:

        return float("inf")

    elif available_capacity < 50:

        capacity_penalty = 10.0

    elif available_capacity < 100:

        capacity_penalty = 5.0

    accessibility_penalty = (
        0.0
        if accessibility
        else 10.0
    )

    return (
        distance_km
        +
        (route_exposure * 20.0)
        +
        capacity_penalty
        +
        accessibility_penalty
    )


def select_shelter(
    candidates
):
    """
    Select the candidate with the
    lowest suitability score.
    """

    valid_candidates = [
        candidate
        for candidate in candidates
        if candidate.get(
            "available_capacity",
            0
        ) > 0
    ]

    if not valid_candidates:
        return None

    valid_candidates.sort(
        key=lambda candidate:
        candidate.get(
            "shelter_score",
            float("inf")
        )
    )

    return valid_candidates[0]