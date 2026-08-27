import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report


# --------------------------------
# Project paths
# --------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "datasets" / "traffic_data.csv"
MODEL_PATH = BASE_DIR / "ai-model" / "traffic_model.pkl"
ENCODER_PATH = BASE_DIR / "ai-model" / "label_encoder.pkl"


# --------------------------------
# Load dataset
# --------------------------------

data = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")
print(f"Total rows: {len(data)}")


# --------------------------------
# Input features
# --------------------------------

X = data[
    [
        "vehicle_count",
        "average_speed",
        "road_capacity"
    ]
]


# --------------------------------
# Target
# --------------------------------

y = data["traffic_density"]


# --------------------------------
# Convert labels to numbers
# --------------------------------

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)


print("\nTraffic classes:")
print(label_encoder.classes_)


# --------------------------------
# Split dataset
# --------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)


print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# --------------------------------
# Create Random Forest model
# --------------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# --------------------------------
# Train model
# --------------------------------

model.fit(X_train, y_train)


# --------------------------------
# Test model
# --------------------------------

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n--------------------------------")
print("MODEL TRAINING COMPLETED")
print("--------------------------------")

print(f"Model Accuracy: {accuracy * 100:.2f}%")


# --------------------------------
# Classification report
# --------------------------------

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_
    )
)


# --------------------------------
# Save model
# --------------------------------

joblib.dump(model, MODEL_PATH)
joblib.dump(label_encoder, ENCODER_PATH)


print("\n--------------------------------")
print("FILES SAVED")
print("--------------------------------")

print(f"Model: {MODEL_PATH}")
print(f"Encoder: {ENCODER_PATH}")