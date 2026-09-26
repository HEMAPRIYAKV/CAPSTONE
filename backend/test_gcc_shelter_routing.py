from backend.road_network import (
    load_road_network,
    find_nearest_node
)

from backend.flood_exposure import (
    load_flood_hazard,
    calculate_road_exposure
)

from backend.routing import find_safe_route

from backend.shelter import (
    load_gcc_shelters,
    calculate_shelter_score
)


START_LAT = 13.0827
START_LON = 80.2707
FLOOD_PROBABILITY = 0.6976


def calculate_route_exposure(graph, route):

    if not route:
        return 0.0

    total_exposure = 0.0
    segments = 0

    for i in range(len(route) - 1):

        u = route[i]
        v = route[i + 1]

        edge_data = graph.get_edge_data(u, v)

        if edge_data is None:
            continue

        edge = min(
            edge_data.values(),
            key=lambda data:
            data.get("length", float("inf"))
        )

        total_exposure += edge.get(
            "flood_exposure",
            0.0
        )

        segments += 1

    if segments == 0:
        return 0.0

    return total_exposure / segments


print()
print("Loading real road network...")

graph = load_road_network(
    START_LAT,
    START_LON,
    5000
)

print()
print("Loading flood hazard...")

flood = load_flood_hazard()

graph = calculate_road_exposure(
    graph,
    flood
)

start_node = find_nearest_node(
    graph,
    START_LAT,
    START_LON
)

shelters = [
    shelter
    for shelter in load_gcc_shelters()
    if str(
        shelter.get("status", "")
    ).strip().lower() != "no"
][:10]


print()
print("GCC SHELTER ROUTING TEST")
print("=========================")
print(
    "Flood probability:",
    FLOOD_PROBABILITY
)
print(
    "Shelters being tested:",
    len(shelters)
)
print()


candidates = []


for shelter in shelters:

    print(
        "Testing",
        shelter["id"],
        "-",
        shelter["name"]
    )

    shelter_node = find_nearest_node(
        graph,
        shelter["latitude"],
        shelter["longitude"]
    )

    route_result = find_safe_route(
        graph=graph,
        start_node=start_node,
        target_node=shelter_node,
        flood_probability=FLOOD_PROBABILITY
    )

    if not route_result.get(
        "route_found",
        False
    ):

        print("  Route: NOT FOUND")
        print()
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

    candidate = {
        **shelter,

        "distance_km": round(
            distance_km,
            3
        ),

        "average_flood_exposure": round(
            exposure,
            4
        ),

        "route_cost": route_result.get(
            "total_cost"
        ),

        "shelter_score": round(
            score,
            3
        ),

        "route_nodes": len(route)
    }

    candidates.append(candidate)

    print(
        "  Distance:",
        candidate["distance_km"],
        "km"
    )

    print(
        "  Flood exposure:",
        candidate[
            "average_flood_exposure"
        ]
    )

    print(
        "  Route cost:",
        candidate["route_cost"]
    )

    print(
        "  Shelter score:",
        candidate["shelter_score"]
    )

    print()


print()
print("TEST SUMMARY")
print("============")
print(
    "Routes found:",
    len(candidates),
    "/",
    len(shelters)
)

print()

for candidate in candidates:

    print(
        candidate["id"],
        "|",
        candidate["distance_km"],
        "km | exposure:",
        candidate[
            "average_flood_exposure"
        ],
        "| score:",
        candidate["shelter_score"]
    )

print()
print("Test complete.")
