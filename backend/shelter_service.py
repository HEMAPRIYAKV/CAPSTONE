"""
Shelter Routing Service

For every available shelter:

    1. Find the nearest road node
    2. Calculate a risk-aware route
    3. Measure route distance
    4. Measure average flood exposure
    5. Calculate shelter suitability

The system then selects the most suitable shelter.
"""


from backend.road_network import (
    load_road_network,
    find_nearest_node
)

from backend.flood_exposure import (
    load_flood_hazard,
    calculate_road_exposure
)

from backend.routing import (
    find_safe_route
)

from backend.shelter import (
    load_shelters,
    select_shelter,
    calculate_shelter_score
)


def calculate_route_exposure(
    graph,
    route
):
    """
    Calculate average flood exposure
    along a route.
    """

    if not route:
        return 0.0

    total_exposure = 0.0
    segments = 0

    for index in range(
        len(route) - 1
    ):

        u = route[index]
        v = route[index + 1]

        edge_data = graph.get_edge_data(
            u,
            v
        )

        if edge_data is None:
            continue

        edge = min(
            edge_data.values(),
            key=lambda data:
            data.get(
                "length",
                float("inf")
            )
        )

        total_exposure += edge.get(
            "flood_exposure",
            0.0
        )

        segments += 1

    if segments == 0:
        return 0.0

    return (
        total_exposure
        /
        segments
    )


def calculate_shelter_routes(
    start_latitude,
    start_longitude,
    flood_probability,
    network_distance=10000
):
    """
    Calculate risk-aware routes to all
    available shelters.
    """

    # --------------------------------------------------
    # Load road network
    # --------------------------------------------------

    graph = load_road_network(
        start_latitude,
        start_longitude,
        network_distance
    )

    # --------------------------------------------------
    # Load flood hazard map
    # --------------------------------------------------

    flood = load_flood_hazard()

    # --------------------------------------------------
    # Apply spatial road exposure
    # --------------------------------------------------

    graph = calculate_road_exposure(
        graph,
        flood
    )

    # --------------------------------------------------
    # Find user's nearest road node
    # --------------------------------------------------

    start_node = find_nearest_node(
        graph,
        start_latitude,
        start_longitude
    )

    shelters = load_shelters()

    candidates = []

    # --------------------------------------------------
    # Evaluate every shelter
    # --------------------------------------------------

    for shelter in shelters:

        if shelter[
            "available_capacity"
        ] <= 0:

            continue

        shelter_node = find_nearest_node(
            graph,
            shelter["latitude"],
            shelter["longitude"]
        )

        route_result = find_safe_route(
            graph=graph,
            start_node=start_node,
            target_node=shelter_node,
            flood_probability=flood_probability
        )

        if not route_result.get(
            "route_found",
            False
        ):

            continue

        route = route_result.get(
            "route",
            []
        )

        distance_km = route_result.get(
            "distance_km",
            0.0
        )

        exposure = calculate_route_exposure(
            graph,
            route
        )

        score = calculate_shelter_score(
            distance_km=distance_km,
            route_exposure=exposure,
            available_capacity=shelter[
                "available_capacity"
            ],
            accessibility=shelter[
                "accessibility"
            ]
        )

        candidates.append({
            **shelter,

            "road_node": shelter_node,

            "distance_km": round(
                distance_km,
                3
            ),

            "average_flood_exposure":
                round(
                    exposure,
                    4
                ),

            "shelter_score": round(
                score,
                3
            ),

            "route": route,

            "route_cost":
                route_result.get(
                    "total_cost"
                )
        })

    # --------------------------------------------------
    # Select shelter
    # --------------------------------------------------

    recommended = select_shelter(
        candidates
    )

    return {
        "start": {
            "latitude":
                start_latitude,
            "longitude":
                start_longitude,
            "road_node":
                start_node
        },

        "flood_probability":
            flood_probability,

        "candidate_shelters":
            candidates,

        "recommended_shelter":
            recommended
    }