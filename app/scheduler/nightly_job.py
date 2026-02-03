
import threading
import time
import pandas as pd
from app.ml.predictor import predictor
from app.ml.train_model import train_baseline # We might need a separate retrain function
# Actually, train_baseline hardcodes paths. We should refactor or adapt.
# For MVP simplicity, let's duplicate/adapt the retraining logic here or import a shared trainer.

# Ideally, we have a trainer class. Let's create a simple retrain function here.
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder

DAILY_DATA_PATH = "data/daily_collected.csv"
HISTORICAL_DATA_PATH = "data/historical_traffic_2y.csv"
MODEL_DIR = "models"

def retrain_model_v2():
    print("Nightly Job: Starting Model Retraining...")
    
    # 1. Load all data (Historical + Daily)
    # in real life, we might window this. Here, just load recent daily data.
    if not os.path.exists(DAILY_DATA_PATH):
        print("Nightly Job: No daily data found.")
        return False
        
    daily_df = pd.read_csv(DAILY_DATA_PATH)
    if len(daily_df) < 10:
        print("Nightly Job: Not enough daily data to retrain.")
        return False
        
    print(f"Nightly Job: Found {len(daily_df)} new data points.")
    
    # For MVP, let's just train on Historical + Daily
    # Or just Daily to show it changes? 
    # Better to mix for stability, but emphasizing "new data".
    
    hist_df = pd.read_csv(HISTORICAL_DATA_PATH)
    
    # Normalize formats
    # Daily: timestamp,edge_id,source_type,traffic_level,speed
    # Hist: timestamp,edge_id,traffic_level,avg_speed, ... features
    
    # We need to enrich daily data with features (hour, day, etc.)
    daily_df['timestamp'] = pd.to_datetime(daily_df['timestamp'])
    daily_df['hour'] = daily_df['timestamp'].dt.hour
    daily_df['day_of_week'] = daily_df['timestamp'].dt.dayofweek
    daily_df['is_weekend'] = daily_df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    # Defaults for other features
    daily_df['is_holiday'] = 0
    daily_df['is_event'] = 0
    daily_df['is_accident'] = 0
    daily_df['is_roadwork'] = 0
    
    # Combined
    # Rename speed -> avg_speed for consistency
    daily_df = daily_df.rename(columns={'speed': 'avg_speed'})
    
    # Select columns
    cols = ['edge_id', 'traffic_level', 'avg_speed', 'hour', 'day_of_week', 'is_weekend', 'is_holiday', 'is_event', 'is_accident', 'is_roadwork']
    
    combined_df = pd.concat([hist_df[cols], daily_df[cols]])
    
    # Retrain
    le_edge = LabelEncoder()
    combined_df['edge_id_encoded'] = le_edge.fit_transform(combined_df['edge_id'])
    
    features = [
        'edge_id_encoded', 'hour', 'day_of_week', 'is_weekend', 
        'is_holiday', 'is_event', 'is_accident', 'is_roadwork'
    ]
    target = 'traffic_level'
    
    X = combined_df[features]
    y = combined_df[target]
    
    rf = RandomForestRegressor(n_estimators=50, max_depth=15, n_jobs=-1, random_state=42)
    rf.fit(X, y)
    
    # Save as V2
    new_model_path = os.path.join(MODEL_DIR, "model_v2.pkl")
    model_data = {
        'model': rf,
        'label_encoders': {'edge_id': le_edge},
        'features': features,
        'version': f'v2_{int(time.time())}' # Timestamp version
    }
    joblib.dump(model_data, new_model_path)
    print(f"Nightly Job: New model saved to {new_model_path}")
    
    # Hot Swap
    print("Nightly Job: Hot-swapping model...")
    predictor.reload(new_model_path)
    print(f"Nightly Job: Model swapped to {predictor.version}. Zero downtime achieved.")
    return True

def start_scheduler():
    # In a real app, use APScheduler. Here, just a simple loop or exposable function.
    # The requirement says "At night... logic".
    # We can expose this via an API endpoint to trigger it manually for demo.
    pass

if __name__ == "__main__":
    retrain_model_v2()
