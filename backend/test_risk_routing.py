"""
Risk-Aware Routing Test

Compares:

1. Normal shortest-distance route
2. Flood-risk-aware route

using the actual Chennai flood hazard map.
"""

import networkx as nx

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


START_LAT = 13.0827
START_LON = 80.2707

# Temporary destination for routing experiment.
DEST_LAT = 13.0475
DEST_LON = 80.0442

FLOOD_PROBABILITY = 0.8679


def calculate_route_statistics(
    graph,
    route
):

    distance = 0.0
    exposure_total = 0.0
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

        # MultiDiGraph can have multiple edges.
        edge = min(
            edge_data.values(),
            key=lambda x: x.get(
                "length",
                float("inf")
            )
        )

        distance += (
            edge.get(
                "length",
                0.0
            ) / 1000
        )

        exposure_total += edge.get(
            "flood_exposure",
            0.0
        )

        segments += 1

    average_exposure = (
        exposure_total / segments
        if segments > 0
        else 0.0
    )

    return {
        "distance_km": round(
            distance,
            3
        ),
        "average_exposure": round(
            average_exposure,
            4
        ),
        "segments": segments
    }


if __name__ == "__main__":

    print("==============================")
    print("RISK-AWARE ROUTING TEST")
    print("==============================")

    print(
        f"Flood probability: "
        f"{FLOOD_PROBABILITY}"
    )

    # --------------------------------------------------
    # Load road network
    # --------------------------------------------------

    graph = load_road_network(
        START_LAT,
        START_LON,
        distance_m=10000
    )

    # --------------------------------------------------
    # Load flood polygons
    # --------------------------------------------------

    flood = load_flood_hazard()

    # --------------------------------------------------
    # Apply spatial exposure
    # --------------------------------------------------

    graph = calculate_road_exposure(
        graph,
        flood
    )

    # --------------------------------------------------
    # Find road nodes
    # --------------------------------------------------

    start_node = find_nearest_node(
        graph,
        START_LAT,
        START_LON
    )

    destination_node = find_nearest_node(
        graph,
        DEST_LAT,
        DEST_LON
    )

    print()
    print(
        "Start node:",
        start_node
    )

    print(
        "Destination node:",
        destination_node
    )

    # ==================================================
    # ROUTE 1 — SHORTEST DISTANCE
    # ==================================================

    print()
    print("==============================")
    print("SHORTEST DISTANCE ROUTE")
    print("==============================")

    shortest_route = nx.shortest_path(
        graph,
        start_node,
        destination_node,
        weight="length"
    )

    shortest_stats = calculate_route_statistics(
        graph,
        shortest_route
    )

    print(
        "Distance:",
        shortest_stats[
            "distance_km"
        ],
        "km"
    )

    print(
        "Average flood exposure:",
        shortest_stats[
            "average_exposure"
        ]
    )

    print(
        "Road segments:",
        shortest_stats[
            "segments"
        ]
    )

    # ==================================================
    # ROUTE 2 — RISK-AWARE A*
    # ==================================================

    print()
    print("==============================")
    print("RISK-AWARE ROUTE")
    print("==============================")

    safe_route = find_safe_route(
        graph=graph,
        start_node=start_node,
        target_node=destination_node,
        flood_probability=FLOOD_PROBABILITY
    )

    if not safe_route.get(
        "route_found",
        False
    ):

        print(
            "No risk-aware route found."
        )

        raise SystemExit

    risk_route = safe_route[
        "route"
    ]

    risk_stats = calculate_route_statistics(
        graph,
        risk_route
    )

    print(
        "Distance:",
        risk_stats[
            "distance_km"
        ],
        "km"
    )

    print(
        "Average flood exposure:",
        risk_stats[
            "average_exposure"
        ]
    )

    print(
        "Road segments:",
        risk_stats[
            "segments"
        ]
    )

    print(
        "Risk-aware cost:",
        safe_route.get(
            "total_cost"
        )
    )

    # ==================================================
    # COMPARISON
    # ==================================================

    print()
    print("==============================")
    print("ROUTE COMPARISON")
    print("==============================")

    print(
        f"Shortest route distance : "
        f"{shortest_stats['distance_km']} km"
    )

    print(
        f"Risk-aware route distance: "
        f"{risk_stats['distance_km']} km"
    )

    print(
        f"Shortest route exposure : "
        f"{shortest_stats['average_exposure']}"
    )

    print(
        f"Risk-aware exposure     : "
        f"{risk_stats['average_exposure']}"
    )

    distance_difference = (
        risk_stats["distance_km"]
        -
        shortest_stats["distance_km"]
    )

    exposure_difference = (
        shortest_stats["average_exposure"]
        -
        risk_stats["average_exposure"]
    )

    print()
    print(
        f"Additional distance: "
        f"{round(distance_difference, 3)} km"
    )

    print(
        f"Exposure reduction: "
        f"{round(exposure_difference, 4)}"
    )

    print()
    print("==============================")
    print("TEST COMPLETE")
    print("==============================")