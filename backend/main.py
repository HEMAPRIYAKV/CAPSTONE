from fastapi import FastAPI
from pydantic import BaseModel

from backend.weather_api import (
    get_live_weather,
    get_normal_rainfall
)

from backend.prediction import predict_flood

from backend.shelter_service import calculate_shelter_routes

from backend.evacuation_service import (
    calculate_evacuation_route
)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="IDIECS Backend"
)


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "message": "IDIECS Backend is running!"
    }


# ============================================================
# LIVE FLOOD PREDICTION
# ============================================================

@app.get("/live-predict")
def live_prediction():

    # --------------------------------------------------------
    # Chennai, Tamil Nadu coordinates
    # --------------------------------------------------------

    latitude = 13.0827
    longitude = 80.2707

    state_name = "Tamil Nadu"


    # --------------------------------------------------------
    # Get live weather
    # --------------------------------------------------------

    weather = get_live_weather(
        latitude,
        longitude
    )

    if weather is None:

        return {
            "error": "Unable to retrieve live weather data"
        }


    # --------------------------------------------------------
    # Get historical normal rainfall
    # --------------------------------------------------------

    normal = get_normal_rainfall(
        state_name
    )

    if normal is None:

        return {
            "error": "Normal rainfall data not found"
        }


    # --------------------------------------------------------
    # Calculate rainfall deviation
    # --------------------------------------------------------

    if normal > 0:

        deviation = (
            (
                weather["rainfall_1day"]
                - normal
            )
            / normal
        ) * 100

    else:

        deviation = 0


    # --------------------------------------------------------
    # Prepare input for XGBoost
    # --------------------------------------------------------

    prediction_input = {

        "rainfall_1day":
            weather["rainfall_1day"],

        "rainfall_3day":
            weather["rainfall_3day"],

        "rainfall_7day":
            weather["rainfall_7day"],

        "normal":
            normal,

        "deviation":
            deviation,

        "temperature":
            weather["temperature"],

        "humidity":
            weather["humidity"],

        "pressure":
            weather["pressure"],

        "wind_speed":
            weather["wind_speed"]
    }


    # --------------------------------------------------------
    # Send data to XGBoost
    # --------------------------------------------------------

    result = predict_flood(
        prediction_input
    )


    # --------------------------------------------------------
    # Return complete prediction
    # --------------------------------------------------------

    return {

        "location":
            "Chennai, Tamil Nadu",

        "weather": {

            "temperature":
                weather["temperature"],

            "humidity":
                weather["humidity"],

            "rainfall_1day":
                weather["rainfall_1day"],

            "rainfall_3day":
                weather["rainfall_3day"],

            "rainfall_7day":
                weather["rainfall_7day"],

            "pressure":
                weather["pressure"],

            "wind_speed":
                weather["wind_speed"]
        },

        "historical_normal":
            round(normal, 2),

        "deviation":
            round(deviation, 2),

        "prediction":
            result
    }


# ============================================================
# MANUAL / SIMULATED FLOOD PREDICTION
# ============================================================

class FloodInput(BaseModel):

    rainfall_1day: float

    rainfall_3day: float

    rainfall_7day: float

    normal: float

    deviation: float

    temperature: float

    humidity: float

    pressure: float

    wind_speed: float


@app.post("/predict")
def predict(data: FloodInput):

    # Convert request data into dictionary

    prediction_input = data.model_dump()

    # Send data to XGBoost

    result = predict_flood(
        prediction_input
    )

    # Return prediction

    return result


# ============================================================
# REAL-TIME EVACUATION ROUTING
# ============================================================

class EvacuationInput(BaseModel):

    latitude: float

    longitude: float

    shelter_latitude: float

    shelter_longitude: float

    network_distance: int = 5000


@app.post("/evacuation")
def evacuation(data: EvacuationInput):

    # --------------------------------------------------------
    # 1. Get live weather
    # --------------------------------------------------------

    weather = get_live_weather(
        data.latitude,
        data.longitude
    )

    if weather is None:

        return {
            "error": "Unable to retrieve live weather data"
        }


    # --------------------------------------------------------
    # 2. Get historical normal rainfall
    # --------------------------------------------------------

    state_name = "Tamil Nadu"

    normal = get_normal_rainfall(
        state_name
    )

    if normal is None:

        return {
            "error": "Normal rainfall data not found"
        }


    # --------------------------------------------------------
    # 3. Calculate rainfall deviation
    # --------------------------------------------------------

    if normal > 0:

        deviation = (
            (
                weather["rainfall_1day"]
                - normal
            )
            / normal
        ) * 100

    else:

        deviation = 0


    # --------------------------------------------------------
    # 4. Prepare XGBoost input
    # --------------------------------------------------------

    prediction_input = {

        "rainfall_1day":
            weather["rainfall_1day"],

        "rainfall_3day":
            weather["rainfall_3day"],

        "rainfall_7day":
            weather["rainfall_7day"],

        "normal":
            normal,

        "deviation":
            deviation,

        "temperature":
            weather["temperature"],

        "humidity":
            weather["humidity"],

        "pressure":
            weather["pressure"],

        "wind_speed":
            weather["wind_speed"]
    }


    # --------------------------------------------------------
    # 5. Predict flood probability
    # --------------------------------------------------------

    prediction = predict_flood(
        prediction_input
    )


    # --------------------------------------------------------
    # 6. Extract flood probability
    # --------------------------------------------------------

    flood_probability = prediction[
        "probability_decimal"
    ]


    # --------------------------------------------------------
    # 7. Calculate risk-aware evacuation route
    # --------------------------------------------------------

    route = calculate_evacuation_route(

        start_latitude=data.latitude,

        start_longitude=data.longitude,

        shelter_latitude=data.shelter_latitude,

        shelter_longitude=data.shelter_longitude,

        flood_probability=flood_probability,

        network_distance=data.network_distance
    )


    # --------------------------------------------------------
    # 8. Return complete evacuation response
    # --------------------------------------------------------

    return {

        "location": {

            "latitude":
                data.latitude,

            "longitude":
                data.longitude
        },

        "weather":
            weather,

        "prediction":
            prediction,

        "evacuation":
            route
    }



# ============================================================
# AUTOMATIC GCC SHELTER EVACUATION
# ============================================================

class AutoEvacuationInput(BaseModel):

    latitude: float

    longitude: float

    network_distance: int = 5000


@app.post("/evacuation-auto")
def automatic_evacuation(data: AutoEvacuationInput):

    # --------------------------------------------------------
    # 1. Get live weather
    # --------------------------------------------------------

    weather = get_live_weather(
        data.latitude,
        data.longitude
    )

    if weather is None:

        return {
            "error": "Unable to retrieve live weather data"
        }


    # --------------------------------------------------------
    # 2. Get historical normal rainfall
    # --------------------------------------------------------

    state_name = "Tamil Nadu"

    normal = get_normal_rainfall(
        state_name
    )

    if normal is None:

        return {
            "error": "Normal rainfall data not found"
        }


    # --------------------------------------------------------
    # 3. Calculate rainfall deviation
    # --------------------------------------------------------

    if normal > 0:

        deviation = (
            (
                weather["rainfall_1day"]
                - normal
            )
            / normal
        ) * 100

    else:

        deviation = 0


    # --------------------------------------------------------
    # 4. Prepare XGBoost input
    # --------------------------------------------------------

    prediction_input = {

        "rainfall_1day":
            weather["rainfall_1day"],

        "rainfall_3day":
            weather["rainfall_3day"],

        "rainfall_7day":
            weather["rainfall_7day"],

        "normal":
            normal,

        "deviation":
            deviation,

        "temperature":
            weather["temperature"],

        "humidity":
            weather["humidity"],

        "pressure":
            weather["pressure"],

        "wind_speed":
            weather["wind_speed"]
    }


    # --------------------------------------------------------
    # 5. Predict flood probability
    # --------------------------------------------------------

    prediction = predict_flood(
        prediction_input
    )


    # --------------------------------------------------------
    # 6. Extract flood probability
    # --------------------------------------------------------

    flood_probability = prediction[
        "probability_decimal"
    ]


    # --------------------------------------------------------
    # 7. Evaluate GCC relief centres
    # --------------------------------------------------------

    shelter_result = calculate_shelter_routes(

        start_latitude=data.latitude,

        start_longitude=data.longitude,

        flood_probability=flood_probability,

        network_distance=data.network_distance
    )


    # --------------------------------------------------------
    # 8. Extract recommended shelter
    # --------------------------------------------------------

    recommended = shelter_result[
        "recommended_shelter"
    ]


    if recommended is None:

        return {

            "location": {

                "latitude":
                    data.latitude,

                "longitude":
                    data.longitude
            },

            "weather":
                weather,

            "prediction":
                prediction,

            "shelter_routing":
                shelter_result,

            "error":
                "No suitable GCC relief centre found"
        }


    # --------------------------------------------------------
    # 9. Return complete evacuation response
    # --------------------------------------------------------

    return {

        "location": {

            "latitude":
                data.latitude,

            "longitude":
                data.longitude
        },

        "weather":
            weather,

        "prediction":
            prediction,

        "shelter": {

            "id":
                recommended["id"],

            "name":
                recommended["name"],

            "latitude":
                recommended["latitude"],

            "longitude":
                recommended["longitude"],

            "capacity":
                recommended["capacity"],

            "available_capacity":
                recommended["available_capacity"],

            "occupancy_data_available":
                recommended[
                    "occupancy_data_available"
                ],

            "status":
                recommended["status"],

            "distance_km":
                recommended["distance_km"],

            "average_flood_exposure":
                recommended[
                    "average_flood_exposure"
                ],

            "shelter_score":
                recommended["shelter_score"]
        },

        "routing": {

            "route_found":
                True,

            "route_nodes":
                len(
                    recommended["route"]
                ),

            "route_cost":
                recommended["route_cost"],

            "route":
                recommended["route"]
        },

        "shelter_statistics": {

            "evaluated":
                shelter_result[
                    "shelters_evaluated"
                ],

            "skipped_status":
                shelter_result[
                    "shelters_skipped_status"
                ],

            "skipped_route":
                shelter_result[
                    "shelters_skipped_route"
                ]
        }
    }
