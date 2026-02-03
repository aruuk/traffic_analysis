
import json
import networkx as nx
import math
from app.ml.predictor import predictor
from datetime import datetime

ROAD_NETWORK_FILE = "data/road_network.json"

class RoutingService:
    def __init__(self):
        self.graph = None
        self.nodes_spatial = [] # List of (id, lat, lon) for nearest search
        self.load_graph()
        
    def load_graph(self):
        with open(ROAD_NETWORK_FILE, 'r') as f:
            data = json.load(f)
            
        self.graph = nx.DiGraph()
        
        # Add nodes
        for n in data['nodes']:
            self.graph.add_node(n['id'], pos=(n['lat'], n['lon']))
            self.nodes_spatial.append((n['id'], n['lat'], n['lon']))
            
        # Add edges (static properties)
        for e in data['edges']:
            self.graph.add_edge(e['source'], e['target'], 
                                id=e['id'], 
                                length=e['length'],
                                base_speed=e['base_speed'])
                                
    def find_nearest_node(self, lat, lon):
        # Naive linear search for MVP (valid for small graph)
        best_node = None
        min_dist = float('inf')
        
        for nid, nlat, nlon in self.nodes_spatial:
            dist = (nlat - lat)**2 + (nlon - lon)**2
            if dist < min_dist:
                min_dist = dist
                best_node = nid
        return best_node

    def get_route(self, start_coords, end_coords, transport_type='car', departure_time=None):
        """
        start_coords: (lat, lon)
        end_coords: (lat, lon)
        departure_time: datetime (default now)
        """
        if not departure_time:
            departure_time = datetime.now()
            
        start_node = self.find_nearest_node(*start_coords)
        end_node = self.find_nearest_node(*end_coords)
        
        if not start_node or not end_node:
            print("Start or end node not found")
            return None
            
        # 1. Get predicted traffic for all edges at this time
        edges_list = [{'id': data['id']} for u, v, data in self.graph.edges(data=True)]
        
        # Predict congestion
        predictions = predictor.predict(edges_list, departure_time)
        
        if not predictions:
            predictions = {e['id']: 0.0 for e in edges_list} # Fallback
            
        # 2. Update graph weights based on traffic
        for u, v, data in self.graph.edges(data=True):
            eid = data['id']
            base_speed = data['base_speed']
            length_km = data['length']
            
            congestion = predictions.get(eid, 0.0)
            
            # Transport type modifiers
            if transport_type == 'walking':
                speed = 5.0 # 5 km/h constant
            elif transport_type == 'bus':
                speed = base_speed * 0.7 * (1 - congestion**1.5) # Bus slower and affected by traffic
            else: # car
                speed = base_speed * (1 - congestion**2)
            
            speed = max(1.0, speed) # Min speed 1 km/h
            
            # Weight = time in hours (or minutes)
            travel_time_hours = length_km / speed
            travel_time_minutes = travel_time_hours * 60
            
            self.graph[u][v]['weight'] = travel_time_minutes
            self.graph[u][v]['speed'] = speed
            self.graph[u][v]['congestion'] = congestion

        # 3. Dijkstra
        try:
            path = nx.shortest_path(self.graph, start_node, end_node, weight='weight')
            
            # Construct result
            total_time = 0
            route_coords = []
            
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i+1]
                edge_data = self.graph[u][v]
                total_time += edge_data['weight']
                
                # Add coordinates
                u_pos = self.graph.nodes[u]['pos']
                # v_pos = self.graph.nodes[v]['pos']
                route_coords.append([u_pos[0], u_pos[1]])
            
            # Add last point
            last_pos = self.graph.nodes[path[-1]]['pos']
            route_coords.append([last_pos[0], last_pos[1]])
            
            return {
                "poly": route_coords, # [[lat, lon], ...]
                "duration_min": round(total_time, 1),
                "distance_km": 0 # TODO calculate total distance
            }
            
        except nx.NetworkXNoPath:
            return None

routing_service = RoutingService()
