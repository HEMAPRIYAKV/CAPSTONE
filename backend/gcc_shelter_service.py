"""
GCC Real Relief Centre Service

Fetches official relief-centre data from the
Greater Chennai Corporation GIS service.

Important:
- Capacity comes from GCC.
- Occupancy is used only when reported.
- Missing occupancy is NOT treated as zero.
- Records are fetched page by page.
"""

import requests


GCC_RELIEF_CENTER_URL = (
    "https://gisgcc.chennaicorporation.gov.in/"
    "server/rest/services/GCCPublic/"
    "ICCC_Relief_CookingCenter/MapServer/0/query"
)

PAGE_SIZE = 500


def _to_number(value):
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _occupancy_value(value):
    """
    Convert a reported occupancy value to an integer.

    Returns None when GCC has not reported the value.
    """
    number = _to_number(value)

    if number is None:
        return None

    return max(0, int(number))


def _fetch_page(offset):
    params = {
        "where": "1=1",
        "outFields": (
            "objectid,"
            "s_no,"
            "zone,"
            "ward,"
            "name_of_the_relief_centre,"
            "capacity,"
            "latitude,"
            "longitud,"
            "status,"
            "no_of_male_stayed,"
            "no_of_female_stayed,"
            "no_of_childrens_stayed,"
            "updatedon,"
            "road_name"
        ),
        "returnGeometry": "false",
        "resultOffset": offset,
        "resultRecordCount": PAGE_SIZE,
        "f": "json"
    }

    response = requests.get(
        GCC_RELIEF_CENTER_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(
            f"GCC API error: {data['error']}"
        )

    return data


def fetch_gcc_relief_centres():
    """
    Fetch all available GCC relief-centre records.
    """

    centres = []
    offset = 0

    while True:
        data = _fetch_page(offset)

        features = data.get("features", [])

        if not features:
            break

        for feature in features:

            attributes = feature.get(
                "attributes",
                {}
            )

            capacity = _to_number(
                attributes.get("capacity")
            )

            latitude = _to_number(
                attributes.get("latitude")
            )

            longitude = _to_number(
                attributes.get("longitud")
            )

            # Skip records without essential
            # geographic/capacity information.
            if (
                latitude is None
                or longitude is None
                or capacity is None
            ):
                continue

            male = _occupancy_value(
                attributes.get(
                    "no_of_male_stayed"
                )
            )

            female = _occupancy_value(
                attributes.get(
                    "no_of_female_stayed"
                )
            )

            children = _occupancy_value(
                attributes.get(
                    "no_of_childrens_stayed"
                )
            )

            occupancy_values = [
                male,
                female,
                children
            ]

            occupancy_data_available = any(
                value is not None
                for value in occupancy_values
            )

            if occupancy_data_available:
                occupied = sum(
                    value or 0
                    for value in occupancy_values
                )

                available_capacity = max(
                    0,
                    int(capacity) - occupied
                )
            else:
                occupied = None
                available_capacity = None

            status = attributes.get("status")

            if status is not None:
                status = str(status).strip()

            centres.append({
                "id": (
                    f"GCC-{attributes.get('objectid')}"
                ),

                "name": attributes.get(
                    "name_of_the_relief_centre"
                ),

                "latitude": latitude,
                "longitude": longitude,

                "capacity": int(capacity),

                "occupied": occupied,

                "available_capacity":
                    available_capacity,

                "occupancy_data_available":
                    occupancy_data_available,

                "status": status,

                "zone": attributes.get("zone"),
                "ward": attributes.get("ward"),

                "road_name": attributes.get(
                    "road_name"
                ),

                "updatedon": attributes.get(
                    "updatedon"
                ),

                "accessibility": None,

                "accessibility_data_available":
                    False
            })

        exceeded = data.get(
            "exceededTransferLimit",
            False
        )

        if not exceeded:
            break

        offset += len(features)

    return centres