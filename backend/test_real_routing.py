from backend.road_network import (
    load_road_network,
    find_nearest_node,
    add_flood_exposure
)

from backend.routing import find_safe_route


if __name__ == "__main__":

    print("==============================")
    print("REAL ROAD EVACUATION TEST")
    print("==============================")

    # -------------------------------------------------
    # START LOCATION
    # -------------------------------------------------

    start_latitude = 13.0827
    start_longitude = 80.2707

    # -------------------------------------------------
    # DESTINATION
    # Temporary destination for testing
    # -------------------------------------------------

    destination_latitude = 13.0475
    destination_longitude = 80.0442

    # -------------------------------------------------
    # CURRENT XGBOOST FLOOD PROBABILITY
    # From your /live-predict result
    # -------------------------------------------------

    flood_probability = 0.8679

    print()
    print(
        "Flood probability:",
        flood_probability
    )

    print()
    print("Loading road network...")

    graph = load_road_network(
        start_latitude,
        start_longitude,
        distance_m=10000
    )

    # -------------------------------------------------
    # ADD ROAD FLOOD EXPOSURE
    # -------------------------------------------------

    graph = add_flood_exposure(
        graph,
        default_exposure=0.5
    )

    # -------------------------------------------------
    # FIND NEAREST ROAD NODES
    # -------------------------------------------------

    start_node = find_nearest_node(
        graph,
        start_latitude,
        start_longitude
    )

    destination_node = find_nearest_node(
        graph,
        destination_latitude,
        destination_longitude
    )

    print()
    print(
        "Start road node:",
        start_node
    )

    print(
        "Destination road node:",
        destination_node
    )

    # -------------------------------------------------
    # RUN RISK-AWARE A*
    # -------------------------------------------------

    print()
    print("Calculating evacuation route...")

    result = find_safe_route(
        graph=graph,
        start_node=start_node,
        target_node=destination_node,
        flood_probability=flood_probability
    )

    # -------------------------------------------------
    # DISPLAY RESULT
    # -------------------------------------------------

    print()
    print("==============================")
    print("ROUTE RESULT")
    print("==============================")

    print(
        "Route found:",
        result["route_found"]
    )

    if result["route_found"]:

        print(
            "Distance:",
            result["distance_km"],
            "km"
        )

        print(
            "Total risk-aware cost:",
            result["total_cost"]
        )

        print(
            "Number of road segments:",
            len(result["roads"])
        )

        print()
        print("First 10 road segments:")

        for road in result["roads"][:10]:

            print(
                road
            )

    else:

        print(
            result["message"]
        )