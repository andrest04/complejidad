from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from ..utils.calculos_comunes import get_datos_globales

vehiculos_bp = Blueprint("vehiculos", __name__)


@vehiculos_bp.route("/registrar_vehiculo", methods=["POST"])
def api_registrar_vehiculo():
    datos = get_datos_globales()
    try:
        data = request.get_json()
        vehiculo = {
            "id": len(datos["vehiculos"]) + 1,
            "placa": data["placa"],
            "capacidad": float(data["capacidad"]),
            "tipo": data["tipo"],
            "disponible": True,
            "fecha_registro": datetime.now().isoformat(),
        }
        datos["vehiculos"].append(vehiculo)
        return jsonify(
            {
                "success": True,
                "message": "Vehículo registrado exitosamente",
                "vehiculo": vehiculo,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error al registrar vehículo: {str(e)}"}), 500


@vehiculos_bp.route("/obtener_vehiculos")
def api_obtener_vehiculos():
    datos = get_datos_globales()
    try:
        return jsonify({"vehiculos": datos["vehiculos"]})
    except Exception as e:
        return jsonify({"error": f"Error al obtener vehículos: {str(e)}"}), 500
