"""
Real-Time Evacuation Service

Pipeline:

Live location
      ↓
OSM road network
      ↓
Chennai flood hazard polygons
      ↓
Road-level flood exposure
      ↓
XGBoost flood probability
      ↓
Effective road risk
      ↓
Risk-aware A*
      ↓
Evacuation route
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


def calculate_evacuation_route(
    start_latitude,
    start_longitude,
    shelter_latitude,
    shelter_longitude,
    flood_probability,
    network_distance=5000
):

    # --------------------------------------------------
    # 1. Load real OSM road network
    # --------------------------------------------------

    graph = load_road_network(
        start_latitude,
        start_longitude,
        network_distance
    )

    # --------------------------------------------------
    # 2. Load actual Chennai flood polygons
    # --------------------------------------------------

    flood = load_flood_hazard()

    # --------------------------------------------------
    # 3. Assign spatial flood exposure to roads
    # --------------------------------------------------

    graph = calculate_road_exposure(
        graph,
        flood
    )

    # --------------------------------------------------
    # 4. Find nearest road nodes
    # --------------------------------------------------

    start_node = find_nearest_node(
        graph,
        start_latitude,
        start_longitude
    )

    shelter_node = find_nearest_node(
        graph,
        shelter_latitude,
        shelter_longitude
    )

    # --------------------------------------------------
    # 5. Calculate risk-aware route
    # --------------------------------------------------

    route = find_safe_route(
        graph=graph,
        start_node=start_node,
        target_node=shelter_node,
        flood_probability=flood_probability
    )

    return {
        "start": {
            "latitude": start_latitude,
            "longitude": start_longitude,
            "road_node": start_node
        },

        "destination": {
            "latitude": shelter_latitude,
            "longitude": shelter_longitude,
            "road_node": shelter_node
        },

        "flood_probability": flood_probability,

        "routing": route
    }