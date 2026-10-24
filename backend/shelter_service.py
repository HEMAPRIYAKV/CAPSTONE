"""
Shelter Routing Service

For every GCC relief centre:

    1. Find the nearest road node
    2. Calculate a risk-aware route
    3. Measure route distance
    4. Measure average flood exposure
    5. Calculate shelter suitability

The system then identifies the most suitable
GCC relief centre.

Important:
GCC occupancy is not available for every centre.
Unknown occupancy is preserved as unknown.
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
    load_gcc_shelters,
    select_shelter,
    calculate_shelter_score
)


# Cached static evacuation infrastructure
_CACHED_GRAPH = None
_CACHED_SHELTERS = None
_CACHED_NETWORK_DISTANCE = None


def calculate_geographic_distance_km(
    latitude1,
    longitude1,
    latitude2,
    longitude2
):
    """
    Calculate straight-line geographic distance
    between two latitude/longitude points.
    """

    from math import radians, sin, cos, sqrt, atan2

    earth_radius_km = 6371.0

    lat1 = radians(latitude1)
    lat2 = radians(latitude2)

    delta_lat = radians(latitude2 - latitude1)
    delta_lon = radians(longitude2 - longitude1)

    a = (
        sin(delta_lat / 2) ** 2
        +
        cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius_km * c


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
    Calculate risk-aware routes to GCC
    relief centres.
    """

    global _CACHED_GRAPH
    global _CACHED_SHELTERS
    global _CACHED_NETWORK_DISTANCE

    # --------------------------------------------------
    # Load or reuse real OSM road network
    # --------------------------------------------------

    if (
        _CACHED_GRAPH is None
        or _CACHED_NETWORK_DISTANCE != network_distance
    ):
        print("Building road network cache...")

        graph = load_road_network(
            start_latitude,
            start_longitude,
            network_distance
        )

        flood = load_flood_hazard()

        graph = calculate_road_exposure(
            graph,
            flood
        )

        _CACHED_GRAPH = graph
        _CACHED_NETWORK_DISTANCE = network_distance

    else:
        print("Using cached road network...")
        graph = _CACHED_GRAPH

    # --------------------------------------------------
    # Find user's nearest road node
    # --------------------------------------------------

    start_node = find_nearest_node(
        graph,
        start_latitude,
        start_longitude
    )

    # --------------------------------------------------
    # Load or reuse GCC relief centres
    # --------------------------------------------------

    if _CACHED_SHELTERS is None:
        print("Loading GCC shelter cache...")
        _CACHED_SHELTERS = load_gcc_shelters()
    else:
        print("Using cached GCC shelters...")

    shelters = _CACHED_SHELTERS

    candidates = []

    skipped_status = 0
    skipped_route = 0

    # --------------------------------------------------
    # Pre-filter geographically nearby shelters
    # --------------------------------------------------

    eligible_shelters = []

    for shelter in shelters:

        # Respect an explicit GCC "No" status.
        status = shelter.get("status")

        if (
            status is not None
            and str(status).strip().lower() == "no"
        ):
            skipped_status += 1
            continue

        geographic_distance = (
            calculate_geographic_distance_km(
                start_latitude,
                start_longitude,
                shelter["latitude"],
                shelter["longitude"]
            )
        )

        eligible_shelters.append(
            (
                geographic_distance,
                shelter
            )
        )

    eligible_shelters.sort(
        key=lambda item: item[0]
    )

    # Run expensive risk-aware A* only for
    # the geographically nearest candidates.
    route_candidates = [
        shelter
        for _, shelter in eligible_shelters[:15]
    ]

    # --------------------------------------------------
    # Evaluate shortlisted GCC relief centres
    # --------------------------------------------------

    for shelter in route_candidates:

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
            skipped_route += 1
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
            available_capacity=shelter.get(
                "available_capacity"
            ),
            accessibility=shelter.get(
                "accessibility"
            )
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

        "shelters_evaluated":
            len(candidates),

        "shelters_skipped_status":
            skipped_status,

        "shelters_skipped_route":
            skipped_route,

        "candidate_shelters":
            candidates,

        "recommended_shelter":
            recommended
    }

