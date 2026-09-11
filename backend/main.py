from fastapi import FastAPI
from pydantic import BaseModel

from backend.weather_api import (
    get_live_weather,
    get_normal_rainfall
)

from backend.prediction import predict_flood


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