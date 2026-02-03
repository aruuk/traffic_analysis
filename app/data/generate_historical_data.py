
import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta
import os

def load_road_network(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def is_peak_hour(hour, is_weekend):
    if is_weekend:
        return 12 <= hour <= 18  # Weekend peak
    else:
        return (7 <= hour <= 9) or (17 <= hour <= 19) # Weekday peaks

def generate_historical_data(network_file, output_file, years=2):
    network = load_road_network(network_file)
    edges = network['edges']
    
    end_date = datetime.now().replace(minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=years*365)
    
    records = []
    
    current = start_date
    print(f"Generating data from {start_date} to {end_date}...")
    
    # Pre-calculate holidays (simplified)
    holidays = set()
    # Add some dummy holidays (Jan 1st, May 1st, Aug 31st for KG)
    for y in range(start_date.year, end_date.year + 1):
        holidays.add(f"{y}-01-01")
        holidays.add(f"{y}-05-01")
        holidays.add(f"{y}-08-31")

    total_days = (end_date - start_date).days
    day_count = 0

    while current < end_date:
        if 5 <= current.hour <= 22:
            is_weekend = current.weekday() >= 5
            date_str = current.strftime("%Y-%m-%d")
            is_holiday = date_str in holidays
            
            # Global event factors (rain, snow, big accident elsewhere)
            # 5% chance of bad weather impacting whole district
            weather_factor = 1.0
            if random.random() < 0.05:
                weather_factor = 0.7 # limit speed
            
            for edge in edges:
                # Base factors
                base_speed = edge['base_speed']
                capacity = edge['lanes'] * 1000 # dummy capacity
                
                # Time patterns
                hour_factor = 0.0
                if is_peak_hour(current.hour, is_weekend):
                    hour_factor = 0.8 # High base congestion
                elif 10 <= current.hour <= 16:
                    hour_factor = 0.4
                else:
                    hour_factor = 0.1
                
                # Variability
                noise = random.uniform(-0.1, 0.1)
                
                # Special events
                is_accident = 0
                is_roadwork = 0
                is_event = 0 # e.g. football game
                
                # Random rare events
                if random.random() < 0.001: is_accident = 1
                if random.random() < 0.001: is_roadwork = 1
                if random.random() < 0.005 and is_weekend: is_event = 1
                
                # Calculate Congestion (0 to 1)
                # Congestion = volume / capacity (proxy)
                # We simulate congestion directly
                
                congestion = hour_factor + noise
                
                if is_accident: congestion += 0.4
                if is_roadwork: congestion += 0.2
                if is_event: congestion += 0.3
                if is_holiday and not is_weekend: congestion *= 0.6 # Less traffic on holidays
                
                # Cap congestion
                congestion = max(0.0, min(1.0, congestion))
                
                # Calculate Speed
                # Speed drops as congestion rises
                # v = v_free * (1 - congestion)^beta
                speed = base_speed * weather_factor * (1 - congestion**2)
                speed = max(5.0, speed) # Minimum speed
                
                records.append({
                    "timestamp": current.isoformat(),
                    "edge_id": edge['id'],
                    "traffic_level": round(congestion, 3), # Target variable
                    "avg_speed": round(speed, 1),
                    "is_holiday": 1 if is_holiday else 0,
                    "is_weekend": 1 if is_weekend else 0,
                    "hour": current.hour,
                    "day_of_week": current.weekday(),
                    "is_accident": is_accident,
                    "is_roadwork": is_roadwork, 
                    "is_event": is_event
                })
        
        current += timedelta(hours=1)
        
        # Progress tracking
        if current.hour == 0:
            day_count += 1
            if day_count % 100 == 0:
                print(f"Generated {day_count}/{total_days} days")

    df = pd.DataFrame(records)
    print(f"Saving {len(df)} records to {output_file}...")
    df.to_csv(output_file, index=False)
    print("Done!")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    generate_historical_data("data/road_network.json", "data/historical_traffic_2y.csv")
