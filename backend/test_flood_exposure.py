from backend.road_network import (
    load_road_network
)

from backend.flood_exposure import (
    load_flood_hazard,
    calculate_road_exposure,
    summarize_road_exposure
)


if __name__ == "__main__":

    print("==============================")
    print("SPATIAL FLOOD EXPOSURE TEST")
    print("==============================")

    latitude = 13.0827
    longitude = 80.2707

    # Load actual Chennai flood data.
    flood = load_flood_hazard()

    print()

    # Load actual OSM road network.
    graph = load_road_network(
        latitude,
        longitude,
        distance_m=5000
    )

    print()

    # Assign spatial flood exposure.
    graph = calculate_road_exposure(
        graph,
        flood
    )

    # Print exposure statistics.
    summarize_road_exposure(
        graph
    )

    print()
    print("==============================")
    print("SAMPLE ROAD EXPOSURE")
    print("==============================")

    count = 0

    for u, v, key, data in graph.edges(
        keys=True,
        data=True
    ):

        print(
            {
                "from": u,
                "to": v,
                "road_name": data.get(
                    "name",
                    "Unnamed road"
                ),
                "distance_km": round(
                    data.get(
                        "length",
                        0
                    ) / 1000,
                    3
                ),
                "flood_exposure": data.get(
                    "flood_exposure",
                    0.0
                )
            }
        )

        count += 1

        if count >= 10:
            break