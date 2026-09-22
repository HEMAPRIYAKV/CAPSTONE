"""
Spatial Flood Exposure Engine

Uses the Chennai flood inundation-zone KML to assign
flood exposure values to real OpenStreetMap road segments.

Flood categories in the dataset:
    Very Low  -> 0.10
    Low       -> 0.30
    Moderate  -> 0.50
    High      -> 0.75
    Very High -> 0.95
"""

import os

import geopandas as gpd
import osmnx as ox


FLOOD_DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "flood",
    "chennai_flood_hazard.kml"
)


CATEGORY_EXPOSURE = {
    "VERY LOW": 0.10,
    "LOW": 0.30,
    "MODERATE": 0.50,
    "HIGH": 0.75,
    "VERY HIGH": 0.95
}


def load_flood_hazard():
    """
    Load the Chennai flood inundation polygons.
    """

    if not os.path.exists(FLOOD_DATA_PATH):
        raise FileNotFoundError(
            f"Flood hazard file not found:\n"
            f"{FLOOD_DATA_PATH}"
        )

    print("Loading Chennai flood hazard data...")

    flood = gpd.read_file(
        FLOOD_DATA_PATH,
        driver="KML"
    )

    print(
        f"Flood polygons loaded: {len(flood)}"
    )

    print(
        "Flood categories:"
    )

    print(
        flood["CATEGORY"].value_counts()
    )

    if flood.crs is None:
        flood = flood.set_crs("EPSG:4326")

    else:
        flood = flood.to_crs("EPSG:4326")

    return flood


def category_to_exposure(category):
    """
    Convert the dataset's CATEGORY value
    into a normalized exposure value.
    """

    if category is None:
        return 0.0

    category = str(
        category
    ).strip().upper()

    return CATEGORY_EXPOSURE.get(
        category,
        0.0
    )


def calculate_road_exposure(
    graph,
    flood
):
    """
    Assign flood exposure to every OSM road segment.

    A representative point from each road segment
    is spatially matched against the flood polygons.
    """

    print(
        "Calculating spatial flood exposure..."
    )

    # Convert OSM graph into GeoDataFrames.
    nodes, edges = ox.graph_to_gdfs(
        graph
    )

    edges = edges.copy()

    # Make sure both datasets use the same CRS.
    edges = edges.to_crs(
        flood.crs
    )

    # Representative point of each road segment.
    edges[
        "representative_point"
    ] = edges.geometry.representative_point()

    road_points = gpd.GeoDataFrame(
        edges[
            ["representative_point"]
        ],
        geometry="representative_point",
        crs=edges.crs
    )

    # Keep only the information needed
    # from the flood polygons.
    flood_polygons = flood[
        [
            "CATEGORY",
            "geometry"
        ]
    ].copy()

    # Spatial join.
    joined = gpd.sjoin(
        road_points,
        flood_polygons,
        how="left",
        predicate="within"
    )

    # Default exposure outside flood zones.
    exposure_by_edge = {}

    for index, row in joined.iterrows():

        category = row.get(
            "CATEGORY"
        )

        exposure = category_to_exposure(
            category
        )

        edge_key = index

        # If a road intersects multiple
        # polygons, retain the highest
        # exposure encountered.
        if edge_key in exposure_by_edge:

            exposure_by_edge[
                edge_key
            ] = max(
                exposure_by_edge[edge_key],
                exposure
            )

        else:

            exposure_by_edge[
                edge_key
            ] = exposure

    # Write exposure back into NetworkX graph.
    for u, v, key, data in graph.edges(
        keys=True,
        data=True
    ):

        edge_index = (
            u,
            v,
            key
        )

        exposure = exposure_by_edge.get(
            edge_index,
            0.0
        )

        data[
            "flood_exposure"
        ] = float(
            exposure
        )

    print(
        "Flood exposure assigned to road network."
    )

    return graph


def summarize_road_exposure(graph):
    """
    Print a simple summary of road exposure.
    """

    exposure_counts = {
        "VERY LOW": 0,
        "LOW": 0,
        "MODERATE": 0,
        "HIGH": 0,
        "VERY HIGH": 0,
        "NO FLOOD ZONE": 0
    }

    for _, _, _, data in graph.edges(
        keys=True,
        data=True
    ):

        exposure = data.get(
            "flood_exposure",
            0.0
        )

        if exposure >= 0.95:
            exposure_counts[
                "VERY HIGH"
            ] += 1

        elif exposure >= 0.75:
            exposure_counts[
                "HIGH"
            ] += 1

        elif exposure >= 0.50:
            exposure_counts[
                "MODERATE"
            ] += 1

        elif exposure >= 0.30:
            exposure_counts[
                "LOW"
            ] += 1

        elif exposure >= 0.10:
            exposure_counts[
                "VERY LOW"
            ] += 1

        else:
            exposure_counts[
                "NO FLOOD ZONE"
            ] += 1

    print()
    print("==============================")
    print("ROAD FLOOD EXPOSURE SUMMARY")
    print("==============================")

    for category, count in exposure_counts.items():

        print(
            f"{category:<15} : {count}"
        )