import pandas as pd

df = pd.read_csv(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\weather\historical_weather.csv"
)

city_to_state = {
    "Delhi": "Delhi",
    "Mumbai": "Maharashtra",
    "Kolkāta": "West Bengal",
    "Bangalore": "Karnataka",
    "Chennai": "Tamil Nadu",
    "Ghāziābād": "Uttar Pradesh",
    "Supaul": "Bihar",
    "Vadodara": "Gujarat",
    "Rājkot": "Gujarat",
    "Vishākhapatnam": "Andhra Pradesh",
    "Bhopāl": "Madhya Pradesh",
    "Pimpri-Chinchwad": "Maharashtra",
    "Patna": "Bihar",
    "Bilāspur": "Chhattisgarh",
    "Ludhiāna": "Punjab",
    "Aurangābād": "Maharashtra",
    "Srīnagar": "Jammu and Kashmir",
    "Vasai-Virar": "Maharashtra",
    "Vijayavāda": "Andhra Pradesh",
    "Vārānasi": "Uttar Pradesh",
    "Haldwāni": "Uttarakhand",
    "Najafgarh": "Delhi"
}

df["state_name"] = df["city"].map(city_to_state)

print("===== CITY → STATE MAPPING =====")
print(df[["city", "state_name"]].drop_duplicates().sort_values("state_name"))

print("\n===== STATES COVERED =====")
print(df["state_name"].nunique())
print(df["state_name"].drop_duplicates().sort_values().tolist())

print("\n===== UNMAPPED CITIES =====")
print(df[df["state_name"].isna()]["city"].unique())