import pandas as pd

weather_path = r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\weather\weather.csv"

# Load dataset
df = pd.read_csv(weather_path)

print("\n===== DATASET INFORMATION =====")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n===== COLUMN NAMES =====")
print(df.columns.tolist())

print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== DATA TYPES =====")
print(df.dtypes)

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())