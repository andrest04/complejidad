from flask import Blueprint, request, jsonify, current_app
from ..utils.calculos_comunes import get_datos_globales

clientes_bp = Blueprint("clientes", __name__)


@clientes_bp.route("/obtener_clientes")
def api_obtener_clientes():
    datos = get_datos_globales()
    try:
        return jsonify({"clientes": datos["clientes"]})
    except Exception as e:
        return jsonify({"error": f"Error al obtener clientes: {str(e)}"}), 500


@clientes_bp.route("/agregar_cliente", methods=["POST"])
def api_agregar_cliente():
    datos = get_datos_globales()
    grafo_builder = current_app.config["GRAFO_BUILDER"]
    try:
        data = request.get_json()
        cliente = {
            "id": len(datos["clientes"]) + 1,
            "nombre": data["nombre"],
            "latitud": float(data["latitud"]),
            "longitud": float(data["longitud"]),
            "prioridad": int(data["prioridad"]),
            "ventana_inicio": data["ventana_inicio"],
            "ventana_fin": data["ventana_fin"],
            "pedido": float(data["pedido"]),
        }
        datos["clientes"].append(cliente)
        if datos["clientes"]:
            datos["grafo"] = grafo_builder.construir_grafo(datos["clientes"])
        return jsonify(
            {
                "success": True,
                "message": "Cliente agregado exitosamente",
                "cliente": cliente,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error al agregar cliente: {str(e)}"}), 500
