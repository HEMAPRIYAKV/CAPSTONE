import pandas as pd

# ==========================================
# 1. Load dataset
# ==========================================

weather_path = r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\weather\weather.csv"

df = pd.read_csv(weather_path)

print("Original shape:", df.shape)

# ==========================================
# 2. Convert date
# ==========================================

df["date"] = pd.to_datetime(df["date"])

# ==========================================
# 3. Remove rows with missing actual rainfall
# ==========================================

df = df.dropna(subset=["actual"]).copy()

print("After removing missing rainfall:", df.shape)

# ==========================================
# 4. Sort by state and date
# ==========================================

df = df.sort_values(
    ["state_name", "date"]
).reset_index(drop=True)

# ==========================================
# 5. Create rainfall history features
# ==========================================

df["rainfall_1day"] = (
    df.groupby("state_name")["actual"]
    .transform(lambda x: x.rolling(window=1).sum())
)

df["rainfall_3day"] = (
    df.groupby("state_name")["actual"]
    .transform(lambda x: x.rolling(window=3).sum())
)

df["rainfall_7day"] = (
    df.groupby("state_name")["actual"]
    .transform(lambda x: x.rolling(window=7).sum())
)

# ==========================================
# 6. Remove rows without complete
#    rainfall history
# ==========================================

df = df.dropna(
    subset=[
        "rainfall_1day",
        "rainfall_3day",
        "rainfall_7day"
    ]
).copy()

# ==========================================
# 7. Select useful columns
# ==========================================

final_df = df[
    [
        "date",
        "state_code",
        "state_name",
        "actual",
        "normal",
        "deviation",
        "rainfall_1day",
        "rainfall_3day",
        "rainfall_7day"
    ]
]

# ==========================================
# 8. Save cleaned dataset
# ==========================================

output_path = r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\weather\clean_weather.csv"

final_df.to_csv(output_path, index=False)

# ==========================================
# 9. Display results
# ==========================================

print("\n===== CLEAN DATASET =====")
print("Rows:", final_df.shape[0])
print("Columns:", final_df.shape[1])

print("\nColumns:")
print(final_df.columns.tolist())

print("\nFirst 10 rows:")
print(final_df.head(10))

print("\nMissing values:")
print(final_df.isnull().sum())

print("\nSaved to:")
print(output_path)