import pandas as pd
import joblib

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# LOAD BALANCED DATASET
# ============================================================

data = pd.read_csv(
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone\data\balanced_training_data.csv"
)

print("Dataset shape:", data.shape)

print("\nClass distribution:")
print(data["flood_occurred"].value_counts())


# ============================================================
# FEATURES
# ============================================================

features = [
    "actual",
    "rainfall_1day",
    "rainfall_3day",
    "rainfall_7day",
    "normal",
    "deviation",
    "temperature",
    "humidity",
    "pressure",
    "wind_speed"
]

X = data[features]
y = data["flood_occurred"]


# ============================================================
# TRAIN-TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))


# ============================================================
# XGBOOST MODEL
# ============================================================

model = XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    random_state=42,
    eval_metric="logloss"
)


# ============================================================
# TRAIN
# ============================================================

model.fit(
    X_train,
    y_train
)


# ============================================================
# PREDICTION
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n================================")
print("MODEL RESULTS")
print("================================")

print(
    "Accuracy:",
    accuracy
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

model_path = (
    r"C:\Users\hemap\OneDrive\Desktop\Documents\capstone"
    r"\ml\flood_model.pkl"
)

joblib.dump(
    model,
    model_path
)

print("\nModel saved to:")

print(model_path)