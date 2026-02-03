
from flask import Blueprint, request, jsonify
from app.ml.predictor import predictor
from datetime import datetime, timedelta

bp = Blueprint('traffic', __name__, url_prefix='/api/traffic')

@bp.route('/predict', methods=['GET'])
def predict_traffic():
    # Params: minutes (15, 30, 60), bbox (west,south,east,north)
    minutes = int(request.args.get('minutes', 15))
    bbox_str = request.args.get('bbox')
    
    target_time = datetime.now() + timedelta(minutes=minutes)
    
    # We need to get edges within this bbox ???
    # Or just return ALL prediction for the district since it's small?
    # For MVP of one district, returning all is simpler and cleaner.
    
    # Get all edges from predictor's known edges?
    # Predictor stores encoders but not edge list.
    # We should load edges from road_network.json again or cache them in a service.
    
    # Let's import road network data (quick hack: load json)
    import json
    with open('data/road_network.json', 'r') as f:
        network = json.load(f)
        
    edges = network['edges']
    # Filter by bbox if needed? With such a small district, not needed.
    
    predictions = predictor.predict(edges, target_time)
    
    if predictions is None:
        return jsonify({"error": "Model not loaded"}), 503
        
    # Convert to GeoJSON FeatureCollection
    features = []
    
    # Helper to find coords for edge
    # This is inefficient, O(N^2) if not optimized. 
    # Better: dict of node_id -> [lat, lon]
    nodes_map = {n['id']: [n['lon'], n['lat']] for n in network['nodes']}
    
    for edge in edges:
        eid = edge['id']
        congestion = predictions.get(eid, 0.0)
        
        u = edge['source']
        v = edge['target']
        
        coords = [nodes_map[u], nodes_map[v]] # [[lon, lat], [lon, lat]]
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "edge_id": eid,
                "congestion": congestion,
                "speed_kmh": round(edge['base_speed'] * (1 - congestion**2), 1),
                "road_name": f"{edge['type'].title()} {eid}", 
                "timestamp": target_time.isoformat()
            }
        })
        
    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })
