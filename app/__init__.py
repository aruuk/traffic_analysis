
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app) # Enable CORS for all routes
    
    # Register Blueprints
    from app.routes.traffic import bp as traffic_bp
    from app.routes.routing import bp as routing_bp
    from app.routes.system import bp as system_bp
    
    app.register_blueprint(traffic_bp)
    app.register_blueprint(routing_bp)
    app.register_blueprint(system_bp)
    
    return app
