import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score


# Load dataset
data = pd.read_csv("datasets/traffic_data.csv")


# Input features
X = data[
    [
        "vehicle_count",
        "average_speed",
        "road_capacity"
    ]
]


# Target
y = data["traffic_density"]


# Convert Low/Medium/High into numbers
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)


# Create ML model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# Train model
model.fit(X_train, y_train)


# Test model
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("Model trained successfully!")
print(f"Model Accuracy: {accuracy * 100:.2f}%")


# Save model and label encoder
joblib.dump(model, "traffic_model.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

print("traffic_model.pkl saved successfully!")
print("label_encoder.pkl saved successfully!")
