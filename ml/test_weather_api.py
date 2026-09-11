import requests

latitude = 28.6139
longitude = 77.2090

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": "2009-01-01",
    "end_date": "2009-01-10",
    "daily": [
        "temperature_2m_mean",
        "relative_humidity_2m_mean",
        "surface_pressure_mean",
        "wind_speed_10m_mean"
    ],
    "timezone": "Asia/Kolkata"
}

response = requests.get(url, params=params)

print("Status code:", response.status_code)

data = response.json()

print("\n===== WEATHER DATA =====")
print(data)