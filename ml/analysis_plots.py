import pandas as pd
import matplotlib.pyplot as plt

# Load balanced dataset
df = pd.read_csv("../data/balanced_training_data.csv")

# Separate flood and non-flood samples
non_flood = df[df["flood_occurred"] == 0]
flood = df[df["flood_occurred"] == 1]

# Calculate average rainfall values
rainfall_values = [
    non_flood["rainfall_7day"].mean(),
    flood["rainfall_7day"].mean()
]

labels = [
    "Non-Flood",
    "Flood"
]

# Create plot
plt.figure(figsize=(7, 5))

bars = plt.bar(
    labels,
    rainfall_values
)

plt.title("Average 7-Day Rainfall: Flood vs Non-Flood")
plt.xlabel("Class")
plt.ylabel("Average 7-Day Rainfall (mm)")

# Display values above bars
for bar, value in zip(bars, rainfall_values):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{value:.2f}",
        ha="center"
    )

plt.tight_layout()

# Save plot
plt.savefig(
    "../results/rainfall_flood_analysis.png",
    dpi=300
)

plt.show()

print("Average 7-Day Rainfall:")
print("Non-Flood:", round(non_flood["rainfall_7day"].mean(), 2), "mm")
print("Flood:", round(flood["rainfall_7day"].mean(), 2), "mm")

print("\nPlot saved successfully!")