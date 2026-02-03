
from flask import Blueprint, jsonify
from app.ml.predictor import predictor

bp = Blueprint('system', __name__, url_prefix='/api/system')

@bp.route('/status', methods=['GET'])
def system_status():
    return jsonify({
        "status": "online",
        "model_version": getattr(predictor, 'version', 'unknown')
    })
