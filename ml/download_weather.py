import pandas as pd
import requests
import time

# ==========================================
# 1. Load 50-city list
# ==========================================

city_file = r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\weather\cities.csv"

cities = pd.read_csv(city_file)

print("Cities found:", len(cities))
print(cities.head())


# ==========================================
# 2. Download weather
# ==========================================

all_weather = []

for index, city in cities.iterrows():

    city_name = city["city_name"]
    latitude = city["latitude"]
    longitude = city["longitude"]

    print(f"\nDownloading {index + 1}/{len(cities)}: {city_name}")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2009-01-01",
        "end_date": "2020-12-31",
        "daily": [
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "surface_pressure_mean",
            "wind_speed_10m_mean"
        ],
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("ERROR:", response.status_code)
        continue

    data = response.json()

    daily = data["daily"]

    weather = pd.DataFrame({
        "date": daily["time"],
        "city": city_name,
        "latitude": latitude,
        "longitude": longitude,
        "temperature": daily["temperature_2m_mean"],
        "humidity": daily["relative_humidity_2m_mean"],
        "pressure": daily["surface_pressure_mean"],
        "wind_speed": daily["wind_speed_10m_mean"]
    })

    all_weather.append(weather)

    time.sleep(1)


# ==========================================
# 3. Combine all cities
# ==========================================

weather_df = pd.concat(
    all_weather,
    ignore_index=True
)

# ==========================================
# 4. Save
# ==========================================

output_path = r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\weather\historical_weather.csv"

weather_df.to_csv(
    output_path,
    index=False
)

print("\n================================")
print("DOWNLOAD COMPLETE")
print("================================")

print("Rows:", len(weather_df))
print("Columns:", weather_df.columns.tolist())

print("\nFirst 10 rows:")
print(weather_df.head(10))

print("\nSaved to:")
print(output_path)