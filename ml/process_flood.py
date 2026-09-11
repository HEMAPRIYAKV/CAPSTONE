import pandas as pd
import json

# Load EM-DAT flood dataset
flood_path = r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\flood_events.csv"

df = pd.read_csv(flood_path, encoding="latin1")

print("Flood events loaded:", len(df))


def extract_states(admin_units):
    """Extract state names from EM-DAT Admin Units."""
    try:
        data = json.loads(admin_units)
        states = []

        for item in data:
            if "adm1_name" in item:
                states.append(item["adm1_name"])

        return states

    except:
        return []


# Extract states
df["states"] = df["Admin Units"].apply(extract_states)

# Create date using available year/month/day
df["date"] = pd.to_datetime(
    dict(
        year=df["Start Year"],
        month=df["Start Month"],
        day=df["Start Day"].fillna(1)
    ),
    errors="coerce"
)

# Keep only useful columns
result = df[
    ["date", "states", "Disaster Subtype"]
].copy()

# One row per state involved in a flood
result = result.explode("states")

# Rename state column
result = result.rename(
    columns={
        "states": "state_name",
        "Disaster Subtype": "flood_type"
    }
)

# Remove rows where state wasn't found
result = result.dropna(subset=["state_name"])

# Add flood label
result["flood_occurred"] = 1

# Save
output_path = r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\flood_events_clean.csv"

result.to_csv(output_path, index=False)

print("\n===== CLEAN FLOOD DATA =====")
print("Rows:", len(result))

print("\nColumns:")
print(result.columns.tolist())

print("\nFirst 20 rows:")
print(result.head(20).to_string(index=False))

print("\nStates found:")
print(result["state_name"].unique())

print("\nSaved to:")
print(output_path)