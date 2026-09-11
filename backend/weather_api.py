import requests
import pandas as pd
from datetime import datetime


# ============================================================
# GET LIVE WEATHER + 7-DAY RAINFALL HISTORY
# ============================================================

def get_live_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "pressure_msl,"
            "wind_speed_10m"
        ),

        "daily": "precipitation_sum",

        "past_days": 7,
        "forecast_days": 1,

        "timezone": "auto"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Weather API Error:", response.status_code)
        return None

    data = response.json()

    # --------------------------------------------------------
    # CURRENT WEATHER
    # --------------------------------------------------------

    current = data["current"]

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    rainfall = current["precipitation"]
    rain = current["rain"]
    pressure = current["pressure_msl"]
    wind_speed = current["wind_speed_10m"]

    # --------------------------------------------------------
    # DAILY RAINFALL
    # --------------------------------------------------------

    daily_rainfall = data["daily"]["precipitation_sum"]

    # The API returns the previous 7 days + current day.
    # We exclude today's incomplete rainfall from the
    # accumulated historical rainfall calculations.

    rainfall_1day = daily_rainfall[-2]

    rainfall_3day = sum(
        daily_rainfall[-4:-1]
    )

    rainfall_7day = sum(
        daily_rainfall[-8:-1]
    )

    return {
        "temperature": temperature,
        "humidity": humidity,
        "rainfall": rainfall,
        "rain": rain,
        "pressure": pressure,
        "wind_speed": wind_speed,

        "rainfall_1day": rainfall_1day,
        "rainfall_3day": rainfall_3day,
        "rainfall_7day": rainfall_7day
    }


# ============================================================
# GET HISTORICAL NORMAL RAINFALL
# ============================================================

def get_normal_rainfall(state_name):

    file_path = "data/weather/clean_weather.csv"

    df = pd.read_csv(file_path)

    df["date"] = pd.to_datetime(df["date"])

    today = datetime.now()

    # Select the same state and same month/day
    state_data = df[
        (df["state_name"].str.lower() == state_name.lower()) &
        (df["date"].dt.month == today.month) &
        (df["date"].dt.day == today.day)
    ]

    if state_data.empty:
        return None

    # Average historical normal rainfall
    normal = state_data["normal"].dropna().mean()

    return normal


# ============================================================
# TEST THE WEATHER API
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Example Location: Chennai, Tamil Nadu
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

    print("\n===== LIVE WEATHER DATA =====")

    if weather:

        print(
            "Temperature       :",
            weather["temperature"],
            "°C"
        )

        print(
            "Humidity          :",
            weather["humidity"],
            "%"
        )

        print(
            "Current Rainfall  :",
            weather["rainfall"],
            "mm"
        )

        print(
            "Pressure          :",
            weather["pressure"],
            "hPa"
        )

        print(
            "Wind Speed        :",
            weather["wind_speed"],
            "km/h"
        )

        # ----------------------------------------------------
        # Rainfall history
        # ----------------------------------------------------

        print("\n===== RAINFALL HISTORY =====")

        print(
            "1-Day Rainfall    :",
            weather["rainfall_1day"],
            "mm"
        )

        print(
            "3-Day Rainfall    :",
            weather["rainfall_3day"],
            "mm"
        )

        print(
            "7-Day Rainfall    :",
            weather["rainfall_7day"],
            "mm"
        )

        # ----------------------------------------------------
        # Historical normal
        # ----------------------------------------------------

        normal = get_normal_rainfall(state_name)

        print("\n===== HISTORICAL NORMAL =====")

        if normal is not None:

            print(
                "Normal Rainfall   :",
                round(normal, 2),
                "mm"
            )

            # ------------------------------------------------
            # Calculate live rainfall deviation
            # ------------------------------------------------

            if normal > 0:

                deviation = (
                    (
                        weather["rainfall_1day"]
                        - normal
                    )
                    / normal
                ) * 100

                print(
                    "Deviation         :",
                    round(deviation, 2),
                    "%"
                )

            else:

                print(
                    "Deviation         : Cannot calculate"
                )

        else:

            print(
                "Normal rainfall data not found."
            )

    else:

        print(
            "Unable to retrieve weather data."
        )