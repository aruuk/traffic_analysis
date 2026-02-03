
from flask import Blueprint, request, jsonify
from app.services.routing import routing_service

bp = Blueprint('routing', __name__, url_prefix='/api/route')

@bp.route('/optimize', methods=['POST'])
def optimize_route():
    data = request.json
    start = data.get('start') # {lat, lng}
    end = data.get('end')     # {lat, lng}
    transport = data.get('type', 'car')
    
    if not start or not end:
        return jsonify({"error": "Missing start or end coordinates"}), 400
        
    route_data = routing_service.get_route(
        [start['lat'], start['lng']],
        [end['lat'], end['lng']],
        transport_type=transport
    )
    
    if not route_data:
        return jsonify({"error": "No route found"}), 404
        
    return jsonify({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": route_data['poly'] # [[lat, lon], ...] - Leaflet wants [lat, lon] or [lon, lat]?
            # Leaflet Polyline uses [lat, lng]. GeoJSON standard is [lon, lat].
            # Backend usually emits GeoJSON [lon, lat].
            # My routing service returns coords from `graph.nodes[u]['pos']`.
            # In generate_road_network.py: `self.nodes.append({"lat": lat, "lon": lon})`
            # `self.graph.add_node(..., pos=(n['lat'], n['lon']))`
            # So `pos` is (lat, lon).
            # `route_coords.append([u_pos[0], u_pos[1]])` -> [lat, lon].
            # GeoJSON expects [lon, lat].
            # Let's verify what MapView.jsx expects.
            # MapView uses GeoJSON component. GeoJSON assumes [lon, lat].
            # I must ensure coordinates are [lon, lat].
        },
        "properties": {
            "duration_min": route_data['duration_min'],
            "distance_km": route_data['distance_km']
        }
    })
