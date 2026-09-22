"""
Shelter Routing Integration Test
"""


from backend.shelter_service import (
    calculate_shelter_routes
)


START_LAT = 13.0827
START_LON = 80.2707

FLOOD_PROBABILITY = 0.8679


if __name__ == "__main__":

    print("==============================")
    print("SHELTER ROUTING TEST")
    print("==============================")

    print(
        f"Flood probability: "
        f"{FLOOD_PROBABILITY}"
    )

    result = calculate_shelter_routes(
        start_latitude=START_LAT,
        start_longitude=START_LON,
        flood_probability=FLOOD_PROBABILITY,
        network_distance=10000
    )

    print()
    print("==============================")
    print("CANDIDATE SHELTERS")
    print("==============================")

    for shelter in result[
        "candidate_shelters"
    ]:

        print()

        print(
            "Shelter:",
            shelter["name"]
        )

        print(
            "Distance:",
            shelter["distance_km"],
            "km"
        )

        print(
            "Average flood exposure:",
            shelter[
                "average_flood_exposure"
            ]
        )

        print(
            "Available capacity:",
            shelter[
                "available_capacity"
            ]
        )

        print(
            "Shelter score:",
            shelter[
                "shelter_score"
            ]
        )

    print()
    print("==============================")
    print("RECOMMENDED SHELTER")
    print("==============================")

    recommended = result[
        "recommended_shelter"
    ]

    if recommended is None:

        print(
            "No suitable shelter found."
        )

    else:

        print(
            "Name:",
            recommended["name"]
        )

        print(
            "Distance:",
            recommended[
                "distance_km"
            ],
            "km"
        )

        print(
            "Average flood exposure:",
            recommended[
                "average_flood_exposure"
            ]
        )

        print(
            "Available capacity:",
            recommended[
                "available_capacity"
            ]
        )

        print(
            "Shelter score:",
            recommended[
                "shelter_score"
            ]
        )

        print(
            "Route cost:",
            recommended[
                "route_cost"
            ]
        )

    print()
    print("==============================")
    print("TEST COMPLETE")
    print("==============================")