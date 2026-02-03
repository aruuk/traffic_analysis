
import json
import math

class RoadNetworkGenerator:
    def __init__(self, bounds):
        self.bounds = bounds  # [[lon_min, lat_min], [lon_max, lat_max]] (approx based on geojson)
        self.nodes = []
        self.edges = []
        
    def generate_grid(self, rows=5, cols=5):
        lon_min, lat_min = self.bounds[0]
        lon_max, lat_max = self.bounds[1]
        
        lat_step = (lat_max - lat_min) / (rows - 1)
        lon_step = (lon_max - lon_min) / (cols - 1)
        
        # larger avenues
        main_roads_rows = {1, 3} 
        main_roads_cols = {1, 3}

        # Generate Nodes
        node_grid = {}
        for r in range(rows):
            for c in range(cols):
                lat = lat_min + r * lat_step
                lon = lon_min + c * lon_step
                node_id = f"n_{r}_{c}"
                self.nodes.append({
                    "id": node_id,
                    "lat": lat,
                    "lon": lon
                })
                node_grid[(r, c)] = node_id

        # Generate Edges
        edge_id_counter = 1
        for r in range(rows):
            for c in range(cols):
                u = node_grid[(r, c)]
                
                # Horizontal edges
                if c < cols - 1:
                    v = node_grid[(r, c + 1)]
                    is_main = r in main_roads_rows
                    self.create_edge(edge_id_counter, u, v, is_main)
                    edge_id_counter += 1
                    
                # Vertical edges
                if r < rows - 1:
                    v = node_grid[(r + 1, c)]
                    is_main = c in main_roads_cols
                    self.create_edge(edge_id_counter, u, v, is_main)
                    edge_id_counter += 1

    def create_edge(self, eid, u, v, is_main):
        base_speed = 60 if is_main else 40
        lanes = 3 if is_main else 1
        road_type = "avenue" if is_main else "street"
        
        self.edges.append({
            "id": str(eid),
            "source": u,
            "target": v,
            "type": road_type,
            "lanes": lanes,
            "base_speed": base_speed,
            "length": 0.5 + (0.5 if is_main else 0) # dummy length km
        })
        # Undirected graph logic: create reverse edge? 
        # For simplicity, traffic usually flows both ways. 
        # Let's create a separate edge for reverse direction to be realistic.
        self.edges.append({
            "id": str(eid) + "_rev",
            "source": v,
            "target": u,
            "type": road_type,
            "lanes": lanes,
            "base_speed": base_speed,
            "length": 0.5 + (0.5 if is_main else 0)
        })

    def save(self, filepath):
        data = {
            "nodes": self.nodes,
            "edges": self.edges,
            "bounds": self.bounds
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Generated {len(self.nodes)} nodes and {len(self.edges)} edges.")

if __name__ == "__main__":
    # Bounds: lon_min, lat_min  to  lon_max, lat_max
    # 74.5750, 42.8580 to 74.6250, 42.8860
    bounds = [[74.5750, 42.8580], [74.6250, 42.8860]]
    generator = RoadNetworkGenerator(bounds)
    generator.generate_grid(rows=6, cols=6) # 36 intersections
    generator.save("data/road_network.json")
