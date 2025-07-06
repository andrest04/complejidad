from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from ..utils.calculos_comunes import get_datos_globales

vehiculos_bp = Blueprint("vehiculos", __name__)


@vehiculos_bp.route("/obtener_vehiculos")
def api_obtener_vehiculos():
    """Obtener lista de vehículos registrados"""
    datos = get_datos_globales()
    try:
        return jsonify({"vehiculos": datos["vehiculos"]})
    except Exception as e:
        return jsonify({"error": f"Error al obtener vehículos: {str(e)}"}), 500