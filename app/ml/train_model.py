
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# Paths
DATA_PATH = "data/historical_traffic_2y.csv"
MODEL_DIR = "models"
MODEL_PATH = f"{MODEL_DIR}/model_v1.pkl"
METADATA_PATH = f"{MODEL_DIR}/model_metadata.pkl"

def train_baseline():
    print("Loading historical data...")
    if not os.path.exists(DATA_PATH):
        print("Data file not found. Please generate it first.")
        return

    df = pd.read_csv(DATA_PATH)
    
    # Feature Engineering
    # Encode edge_id
    le_edge = LabelEncoder()
    df['edge_id_encoded'] = le_edge.fit_transform(df['edge_id'])
    
    features = [
        'edge_id_encoded', 'hour', 'day_of_week', 'is_weekend', 
        'is_holiday', 'is_event', 'is_accident', 'is_roadwork'
    ]
    target = 'traffic_level'
    
    X = df[features]
    y = df[target]
    
    print(f"Training on {len(df)} records with features: {features}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train
    # RandomForest is interpretable (feature importance) and robust
    rf = RandomForestRegressor(n_estimators=50, max_depth=15, n_jobs=-1, random_state=42)
    rf.fit(X_train, y_train)
    
    # Evaluate
    preds = rf.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    
    print(f"Model Trained. MSE: {mse:.4f}, R2: {r2:.4f}")
    
    # Feature Importance
    importances = dict(zip(features, rf.feature_importances_))
    print("Feature Importances:", importances)
    
    # Save Model components
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    model_data = {
        'model': rf,
        'label_encoders': {
            'edge_id': le_edge
        },
        'features': features,
        'metrics': {'mse': mse, 'r2': r2},
        'version': 'v1'
    }
    
    joblib.dump(model_data, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_baseline()
