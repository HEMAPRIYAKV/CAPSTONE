"""
Dynamic Evacuation Routing

Recalculates the evacuation route whenever
the predicted flood probability changes.
"""

from backend.evacuation_service import (
    calculate_evacuation_route
)


class DynamicRouteManager:

    def __init__(
        self,
        start_latitude,
        start_longitude,
        shelter_latitude,
        shelter_longitude
    ):

        self.start_latitude = (
            start_latitude
        )

        self.start_longitude = (
            start_longitude
        )

        self.shelter_latitude = (
            shelter_latitude
        )

        self.shelter_longitude = (
            shelter_longitude
        )

        self.current_probability = None
        self.current_route = None

    def calculate_route(
        self,
        flood_probability
    ):

        self.current_probability = (
            float(
                flood_probability
            )
        )

        self.current_route = (
            calculate_evacuation_route(
                start_latitude=
                    self.start_latitude,

                start_longitude=
                    self.start_longitude,

                shelter_latitude=
                    self.shelter_latitude,

                shelter_longitude=
                    self.shelter_longitude,

                flood_probability=
                    self.current_probability
            )
        )

        return self.current_route

    def update_flood_probability(
        self,
        new_probability
    ):
        """
        Called when new weather/prediction
        information becomes available.
        """

        new_probability = float(
            new_probability
        )

        old_probability = (
            self.current_probability
        )

        self.current_probability = (
            new_probability
        )

        # First prediction
        if old_probability is None:

            route = self.calculate_route(
                new_probability
            )

            return {
                "rerouted": True,
                "reason":
                    "Initial route calculated",
                "old_probability":
                    None,
                "new_probability":
                    new_probability,
                "route":
                    route
            }

        # Check whether risk changed
        probability_change = abs(
            new_probability
            -
            old_probability
        )

        # Recalculate if probability
        # changes significantly.
        if probability_change >= 0.05:

            route = self.calculate_route(
                new_probability
            )

            return {
                "rerouted": True,
                "reason":
                    "Flood probability changed",
                "old_probability":
                    old_probability,
                "new_probability":
                    new_probability,
                "route":
                    route
            }

        return {
            "rerouted": False,
            "reason":
                "Flood probability change "
                "was below rerouting threshold",
            "old_probability":
                old_probability,
            "new_probability":
                new_probability,
            "route":
                self.current_route
        }