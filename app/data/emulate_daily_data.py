
import json
import random
import time
import os
import pandas as pd
from datetime import datetime

# File paths
DAILY_DATA_FILE = "data/daily_collected.csv"
ROAD_NETWORK_FILE = "data/road_network.json"

def load_edges():
    with open(ROAD_NETWORK_FILE, 'r') as f:
        data = json.load(f)
    return data['edges']

def emulate_bot_data(edges):
    """Simulates 2GIS bot collecting data every 5 mins"""
    records = []
    timestamp = datetime.now().isoformat()
    
    # Bot covers 100% of major roads and 50% of minor roads each run
    for edge in edges:
        is_major = edge['lanes'] > 1
        coverage_prob = 1.0 if is_major else 0.5
        
        if random.random() < coverage_prob:
            # Simulate real-time congestion
            # In real system, this comes from an API
            # Here we random gen based on time or just random for emulator
            congestion = random.uniform(0, 0.8) 
            if random.random() < 0.01: congestion = 0.95 # Random jam
            
            records.append({
                "timestamp": timestamp,
                "edge_id": edge['id'],
                "source_type": "bot",
                "traffic_level": round(congestion, 3),
                "speed": round(edge['base_speed'] * (1 - congestion), 1)
            })
    return records

def emulate_volunteer_data(edges):
    """Simulates 150 volunteers driving around"""
    records = []
    timestamp = datetime.now().isoformat()
    
    # 150 volunteers, maybe 10% are driving right now
    active_users = 15
    
    for _ in range(active_users):
        edge = random.choice(edges)
        # Volunteer reports travel time/speed
        # Slightly noisy data
        congestion = random.uniform(0, 0.7)
        speed = edge['base_speed'] * (1 - congestion) * random.uniform(0.9, 1.1)
        
        records.append({
            "timestamp": timestamp,
            "edge_id": edge['id'],
            "source_type": "user",
            "traffic_level": round(congestion, 3), # Inferred from speed
            "speed": round(speed, 1)
        })
    return records

def run_emulator():
    os.makedirs("data", exist_ok=True)
    edges = load_edges()
    
    # Initialize file if not exists
    if not os.path.exists(DAILY_DATA_FILE):
        pd.DataFrame(columns=["timestamp", "edge_id", "source_type", "traffic_level", "speed"]).to_csv(DAILY_DATA_FILE, index=False)
    
    print("Starting Daily Emulator (Bot + Volunteers)... Press Ctrl+C to stop.")
    try:
        while True:
            # 1. Bot Cycle
            bot_data = emulate_bot_data(edges)
            
            # 2. Volunteer Cycle
            user_data = emulate_volunteer_data(edges)
            
            all_records = bot_data + user_data
            
            # Append to CSV
            df = pd.DataFrame(all_records)
            df.to_csv(DAILY_DATA_FILE, mode='a', header=False, index=False)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Collected {len(all_records)} (Bot: {len(bot_data)}, User: {len(user_data)}) data points.")
            
            # Sleep 5 seconds (simulating 5 minutes in demo speedup) for demo purposes?
            # User requirement: "updates every 5 minutes". 
            # For checking verify, we might want it faster, but let's stick to a reasonable demo loop.
            # Let's say 10 seconds for demo.
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("Emulator stopped.")

if __name__ == "__main__":
    run_emulator()
