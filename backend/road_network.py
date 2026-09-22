"""
Real Road Network Loader

Uses OpenStreetMap through OSMnx.

The graph contains actual road nodes and road segments
instead of the temporary A-B-C-D test graph.
"""

import osmnx as ox


def load_road_network(
    latitude,
    longitude,
    distance_m=5000
):
    """
    Download the drivable road network around
    the requested location.
    """

    print(
        "Loading real road network..."
    )

    graph = ox.graph_from_point(
        (
            latitude,
            longitude
        ),
        dist=distance_m,
        network_type="drive",
        simplify=True
    )

    print(
        f"Loaded {len(graph.nodes)} road nodes"
    )

    print(
        f"Loaded {len(graph.edges)} road segments"
    )

    return graph


def find_nearest_node(
    graph,
    latitude,
    longitude
):
    """
    Find the road node closest to
    the user's coordinates.
    """

    node = ox.distance.nearest_nodes(
        graph,
        X=longitude,
        Y=latitude
    )

    return node
def add_flood_exposure(
    graph,
    default_exposure=0.5
):
    """
    Add flood exposure to every road.

    Prototype version:
    exposure is initialized using a default value.

    Later this can be replaced by:
        - historical flood locations
        - flood maps
        - DEM/elevation
        - drainage information
        - satellite flood observations
    """

    for u, v, key, data in graph.edges(
        keys=True,
        data=True
    ):

        data[
            "flood_exposure"
        ] = default_exposure

        data[
            "road_condition"
        ] = "GOOD"

        data[
            "blocked"
        ] = False

    return graph