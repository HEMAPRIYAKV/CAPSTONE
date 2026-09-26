"""
Shelter Management Module

Supports both:

1. Local development shelters
2. Official GCC relief-centre data

Shelter suitability considers:

    - route distance
    - route flood exposure
    - available capacity when reported
    - accessibility when reported

Important:
GCC records may not contain current occupancy or
accessibility information. Unknown values are kept
as unknown rather than being treated as zero/false.
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
    Load development shelters from the local CSV dataset.
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
                    ].strip().lower() == "true",

                "occupancy_data_available": True,
                "accessibility_data_available": True,
                "source": "development_csv"
            })

    return shelters


def calculate_shelter_score(
    distance_km,
    route_exposure,
    available_capacity,
    accessibility
):
    """
    Calculate a prototype shelter suitability score.

    Lower score = more suitable.

    Unknown capacity/accessibility values do not
    automatically make a shelter invalid.
    """

    capacity_penalty = 0.0

    # Capacity is unknown.
    if available_capacity is None:

        capacity_penalty = 0.0

    # Capacity is known.
    elif available_capacity <= 0:

        return float("inf")

    elif available_capacity < 50:

        capacity_penalty = 10.0

    elif available_capacity < 100:

        capacity_penalty = 5.0

    # Accessibility is unknown.
    if accessibility is None:

        accessibility_penalty = 0.0

    # Accessibility is known.
    else:

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


def select_shelter(candidates):
    """
    Select the candidate with the lowest
    suitability score.

    Candidates with known zero capacity are
    excluded.

    Candidates with unknown capacity remain
    eligible, because unknown does not mean full
    or empty.
    """

    valid_candidates = [
        candidate
        for candidate in candidates
        if (
            candidate.get(
                "available_capacity"
            ) is None
            or
            candidate.get(
                "available_capacity"
            ) > 0
        )
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
def load_gcc_shelters():
    """
    Load official GCC relief-centre records.

    The data is fetched from the Greater Chennai
    Corporation GIS service.
    """

    from backend.gcc_shelter_service import (
        fetch_gcc_relief_centres
    )

    shelters = fetch_gcc_relief_centres()

    for shelter in shelters:
        shelter["source"] = "gcc_gis"

    return shelters