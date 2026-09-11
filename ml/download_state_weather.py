import pandas as pd
import requests
import time

# State representative coordinates
states = {
    "Andhra Pradesh": (16.5062, 80.6480),
    "Arunachal Pradesh": (27.0844, 93.6053),
    "Assam": (26.1445, 91.7362),
    "Bihar": (25.5941, 85.1376),
    "Chhattisgarh": (21.2514, 81.6296),
    "Delhi": (28.6139, 77.2090),
    "Gujarat": (23.0225, 72.5714),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jammu and Kashmir": (34.0837, 74.7973),
    "Jharkhand": (23.3441, 85.3096),
    "Karnataka": (12.9716, 77.5946),
    "Kerala": (8.5241, 76.9366),
    "Madhya Pradesh": (23.2599, 77.4126),
    "Maharashtra": (19.0760, 72.8777),
    "Manipur": (24.8170, 93.9368),
    "Nagaland": (25.6751, 94.1086),
    "Odisha": (20.2961, 85.8245),
    "Puducherry": (11.9416, 79.8083),
    "Punjab": (30.7333, 76.7794),
    "Rajasthan": (26.9124, 75.7873),
    "Sikkim": (27.3389, 88.6065),
    "Tamil Nadu": (13.0827, 80.2707),
    "Tripura": (23.8315, 91.2868),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.5726, 88.3639)
}

start_date = "2009-01-01"
end_date = "2020-12-31"

all_data = []

for i, (state, coords) in enumerate(states.items(), 1):

    latitude, longitude = coords

    print(f"Downloading {i}/{len(states)}: {state}")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_mean",
            "relative_humidity_2m_mean",
            "surface_pressure_mean",
            "wind_speed_10m_mean"
        ],
        "timezone": "Asia/Kolkata"
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:

            data = response.json()

            daily = data["daily"]

            df = pd.DataFrame({
                "date": daily["time"],
                "state_name": state,
                "temperature": daily["temperature_2m_mean"],
                "humidity": daily["relative_humidity_2m_mean"],
                "pressure": daily["surface_pressure_mean"],
                "wind_speed": daily["wind_speed_10m_mean"]
            })

            all_data.append(df)

        else:
            print("ERROR:", response.status_code)

    except Exception as e:
        print("ERROR:", e)

    # Prevent API rate limiting
    time.sleep(2)


# Combine everything
if all_data:

    final_df = pd.concat(all_data, ignore_index=True)

    output_path = (
        r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone"
        r"\data\weather\state_weather.csv"
    )

    final_df.to_csv(output_path, index=False)

    print("\n================================")
    print("DOWNLOAD COMPLETE")
    print("================================")

    print("Rows:", len(final_df))
    print("States:", final_df["state_name"].nunique())
    print("Columns:", list(final_df.columns))

    print("\nFirst 10 rows:")
    print(final_df.head(10))

    print("\nSaved to:")
    print(output_path)

else:
    print("No data downloaded.")