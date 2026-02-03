
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime

class TrafficPredictor:
    def __init__(self, model_path="models/model_v1.pkl"):
        self.model_data = None
        self.model_path = model_path
        self.load_model()
        
    def load_model(self):
        if os.path.exists(self.model_path):
            print(f"Loading model from {self.model_path}...")
            self.model_data = joblib.load(self.model_path)
            self.model = self.model_data['model']
            self.le_edge = self.model_data['label_encoders']['edge_id']
            self.features = self.model_data['features']
            self.version = self.model_data.get('version', 'unknown')
            print(f"Model {self.version} loaded.")
        else:
            print(f"Model file {self.model_path} not found.")
            self.model = None

    def reload(self, new_path=None):
        if new_path:
            self.model_path = new_path
        self.load_model()

    def predict(self, edges, target_time):
        """
        Predict traffic for a list of edges at target_time
        edges: list of edge dicts (must contain 'id')
        target_time: datetime object
        """
        if not self.model:
            return None
            
        # Prepare DataFrame
        hour = target_time.hour
        day_of_week = target_time.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        
        # Holidays/Events would need an external service or calendar
        # For MVP, assume false or simple logic
        is_holiday = 0 
        is_event = 0
        is_accident = 0
        is_roadwork = 0 
        
        input_data = []
        valid_indices = []
        
        for i, edge in enumerate(edges):
            eid = edge['id']
            # Check if edge is known
            if eid in self.le_edge.classes_:
                eid_encoded = self.le_edge.transform([eid])[0]
                input_data.append({
                    'edge_id_encoded': eid_encoded,
                    'hour': hour,
                    'day_of_week': day_of_week,
                    'is_weekend': is_weekend,
                    'is_holiday': is_holiday,
                    'is_event': is_event,
                    'is_accident': is_accident,
                    'is_roadwork': is_roadwork
                })
                valid_indices.append(i)
        
        if not input_data:
            return []
            
        df = pd.DataFrame(input_data)
        # Ensure column order matches training
        X = df[self.features]
        
        predictions = self.model.predict(X)
        
        # Map back to edges
        results = {}
        for idx, pred in zip(valid_indices, predictions):
            edge_id = edges[idx]['id']
            results[edge_id] = max(0.0, min(1.0, pred))
            
        return results

# Singleton instance
predictor = TrafficPredictor()
