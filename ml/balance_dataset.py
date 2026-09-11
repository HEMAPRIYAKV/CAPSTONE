import pandas as pd


# ============================================================
# LOAD DATASET
# ============================================================

input_file = "data/prototype_training_data.csv"

df = pd.read_csv(input_file)

print("Original dataset:")
print(df["flood_occurred"].value_counts())


# ============================================================
# SEPARATE FLOOD AND NO-FLOOD DATA
# ============================================================

flood = df[df["flood_occurred"] == 1]

no_flood = df[df["flood_occurred"] == 0]


# ============================================================
# BALANCE THE DATASET
# ============================================================

# Use all available flood samples
# Randomly select the same number of no-flood samples

no_flood_sample = no_flood.sample(
    n=len(flood),
    random_state=42
)


# Combine both classes

balanced_df = pd.concat(
    [flood, no_flood_sample],
    ignore_index=True
)


# Shuffle the dataset

balanced_df = balanced_df.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ============================================================
# SAVE BALANCED DATASET
# ============================================================

output_file = "data/balanced_training_data.csv"

balanced_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\nBalanced dataset:")
print(balanced_df["flood_occurred"].value_counts())

print("\nTotal rows:", len(balanced_df))

print("\nSaved to:")
print(output_file)