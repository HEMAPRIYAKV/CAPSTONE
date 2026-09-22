from backend.road_network import load_road_network


if __name__ == "__main__":

    # Chennai test location
    latitude = 13.0827
    longitude = 80.2707

    print("==============================")
    print("REAL ROAD NETWORK TEST")
    print("==============================")

    graph = load_road_network(
        latitude,
        longitude,
        distance_m=2000
    )

    print()
    print("TEST SUCCESSFUL")
    print(
        "Road nodes:",
        len(graph.nodes)
    )

    print(
        "Road segments:",
        len(graph.edges)
    )