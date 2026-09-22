"""
Risk-Aware Real Road Routing

Uses:
    OpenStreetMap road network
    +
    XGBoost flood probability
    +
    road exposure
    +
    A* routing

The same road network can be re-evaluated whenever
the flood probability changes, enabling dynamic rerouting.
"""

import math
import heapq

from backend.road_risk import calculate_road_cost


# ---------------------------------------------------------
# DISTANCE
# ---------------------------------------------------------

def haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate geographical distance between two coordinates.
    Returns kilometres.
    """

    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ---------------------------------------------------------
# A* HEURISTIC
# ---------------------------------------------------------

def heuristic(graph, node, target):
    """
    Straight-line geographical distance.
    """

    node_data = graph.nodes[node]
    target_data = graph.nodes[target]

    return haversine_distance(
        node_data["y"],
        node_data["x"],
        target_data["y"],
        target_data["x"]
    )


# ---------------------------------------------------------
# ROAD EXPOSURE
# ---------------------------------------------------------

def get_road_exposure(edge_data):
    """
    Returns road exposure between 0 and 1.

    If exposure is not available, use a conservative
    default value of 0.5.
    """

    exposure = edge_data.get(
        "flood_exposure",
        0.5
    )

    try:
        exposure = float(exposure)
    except (TypeError, ValueError):
        exposure = 0.5

    return max(
        0.0,
        min(1.0, exposure)
    )


# ---------------------------------------------------------
# EDGE COST
# ---------------------------------------------------------

def calculate_edge_cost(
    edge_data,
    flood_probability
):
    """
    Calculate risk-aware cost for a road segment.
    """

    distance_km = float(
        edge_data.get(
            "length",
            0
        )
    ) / 1000.0

    road_exposure = get_road_exposure(
        edge_data
    )

    road_condition = edge_data.get(
        "road_condition",
        "GOOD"
    )

    blocked = edge_data.get(
        "blocked",
        False
    )

    result = calculate_road_cost(
        distance_km=distance_km,
        flood_probability=flood_probability,
        road_exposure=road_exposure,
        road_condition=road_condition,
        blocked=blocked
    )

    return result


# ---------------------------------------------------------
# A* ROUTING
# ---------------------------------------------------------

def find_safe_route(
    graph,
    start_node,
    target_node,
    flood_probability
):
    """
    Find a route that considers both distance
    and predicted flood risk.
    """

    priority_queue = []

    heapq.heappush(
        priority_queue,
        (
            0,
            start_node
        )
    )

    came_from = {
        start_node: None
    }

    cost_so_far = {
        start_node: 0
    }

    edge_information = {}

    while priority_queue:

        current_priority, current = (
            heapq.heappop(
                priority_queue
            )
        )

        if current == target_node:
            break

        for neighbor in graph.successors(
            current
        ):

            edge_options = graph[
                current
            ][neighbor]

            # MultiDiGraph can contain
            # multiple edges between nodes.
            for edge_key, edge_data in edge_options.items():

                road_cost = calculate_edge_cost(
                    edge_data,
                    flood_probability
                )

                if math.isinf(
                    road_cost["cost"]
                ):
                    continue

                new_cost = (
                    cost_so_far[current]
                    +
                    road_cost["cost"]
                )

                if (
                    neighbor not in cost_so_far
                    or new_cost
                    < cost_so_far[neighbor]
                ):

                    cost_so_far[
                        neighbor
                    ] = new_cost

                    priority = (
                        new_cost
                        +
                        heuristic(
                            graph,
                            neighbor,
                            target_node
                        )
                    )

                    heapq.heappush(
                        priority_queue,
                        (
                            priority,
                            neighbor
                        )
                    )

                    came_from[
                        neighbor
                    ] = current

                    edge_information[
                        (current, neighbor)
                    ] = {
                        "edge_key": edge_key,
                        **road_cost,
                        "distance_km":
                            round(
                                float(
                                    edge_data.get(
                                        "length",
                                        0
                                    )
                                ) / 1000,
                                3
                            ),
                        "road_name":
                            edge_data.get(
                                "name",
                                "Unnamed road"
                            )
                    }

    if target_node not in came_from:

        return {
            "route_found": False,
            "message":
                "No safe route available"
        }

    # -----------------------------------------------------
    # RECONSTRUCT ROUTE
    # -----------------------------------------------------

    route = []

    current = target_node

    while current is not None:

        route.append(
            current
        )

        current = came_from[
            current
        ]

    route.reverse()

    roads = []

    total_distance = 0.0
    total_cost = 0.0

    for i in range(
        len(route) - 1
    ):

        from_node = route[i]
        to_node = route[i + 1]

        info = edge_information[
            (from_node, to_node)
        ]

        roads.append(
            {
                "from":
                    from_node,

                "to":
                    to_node,

                "road_name":
                    info["road_name"],

                "distance_km":
                    info["distance_km"],

                "flood_risk":
                    info["risk_level"],

                "effective_risk":
                    info["effective_risk"],

                "blocked":
                    info["blocked"]
            }
        )

        total_distance += (
            info["distance_km"]
        )

        total_cost += (
            info["cost"]
        )

    return {
        "route_found": True,

        "route":
            route,

        "distance_km":
            round(
                total_distance,
                3
            ),

        "total_cost":
            round(
                total_cost,
                3
            ),

        "roads":
            roads,

        "flood_probability":
            round(
                float(
                    flood_probability
                ),
                4
            )
    }