import pandas as pd

# Load datasets
rainfall = pd.read_csv(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\weather\clean_weather.csv"
)

weather = pd.read_csv(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\weather\state_weather.csv"
)

flood = pd.read_csv(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\flood_events_clean.csv"
)

# Convert dates
rainfall["date"] = pd.to_datetime(rainfall["date"])
weather["date"] = pd.to_datetime(weather["date"])
flood["date"] = pd.to_datetime(flood["date"])

# Clean state names
for df in [rainfall, weather, flood]:
    df["state_name"] = df["state_name"].replace({
        "Orissa": "Odisha"
    })

# Remove invalid flood state
flood = flood[
    flood["state_name"] != "Administrative unit not available"
]

# Keep only required flood columns
flood = flood[
    ["date", "state_name", "flood_occurred"]
]

# Merge rainfall + weather
merged = pd.merge(
    rainfall,
    weather,
    on=["date", "state_name"],
    how="inner"
)

# Merge flood labels
merged = pd.merge(
    merged,
    flood,
    on=["date", "state_name"],
    how="left"
)

# No flood event = 0
merged["flood_occurred"] = merged["flood_occurred"].fillna(0)

# Save
output_path = (
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone"
    r"\data\prototype_training_data.csv"
)

merged.to_csv(output_path, index=False)

print("\n================================")
print("PROTOTYPE DATASET CREATED")
print("================================")

print("Rows:", len(merged))
print("Columns:", len(merged.columns))

print("\nColumns:")
print(list(merged.columns))

print("\nFlood distribution:")
print(merged["flood_occurred"].value_counts())

print("\nStates:")
print(merged["state_name"].nunique())

print("\nFirst 5 rows:")
print(merged.head())

print("\nSaved to:")
print(output_path)