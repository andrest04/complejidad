from flask import Blueprint, request, jsonify, current_app, render_template
from app.utils.parser_csv import cargar_clientes_csv
import json

api_clientes_bp = Blueprint("api_clientes", __name__)


@api_clientes_bp.route("/api/clientes", methods=["GET"])
def obtener_clientes():
    """Obtiene todos los clientes"""
    datos = current_app.config["DATOS_GLOBALES"]
    clientes = datos.get("clientes", [])

    # Filtros opcionales
    distrito = request.args.get("distrito")
    prioridad = request.args.get("prioridad")

    clientes_filtrados = clientes

    if distrito:
        clientes_filtrados = [
            c
            for c in clientes_filtrados
            if c.get("distrito", "").lower() == distrito.lower()
        ]

    if prioridad:
        try:
            prioridad_int = int(prioridad)
            clientes_filtrados = [
                c for c in clientes_filtrados if c.get("prioridad") == prioridad_int
            ]
        except ValueError:
            pass

    return jsonify({"total": len(clientes_filtrados), "clientes": clientes_filtrados})


@api_clientes_bp.route("/api/clientes/<int:cliente_id>", methods=["GET"])
def obtener_cliente(cliente_id):
    """Obtiene un cliente específico"""
    datos = current_app.config["DATOS_GLOBALES"]
    clientes = datos.get("clientes", [])

    cliente = next((c for c in clientes if c.get("id") == cliente_id), None)

    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    return jsonify(cliente)

@api_clientes_bp.route("/api/clientes/estadisticas", methods=["GET"])
def estadisticas_clientes():
    """Obtiene estadísticas de los clientes"""
    datos = current_app.config["DATOS_GLOBALES"]
    clientes = datos.get("clientes", [])

    if not clientes:
        return jsonify({"error": "No hay clientes cargados"}), 404

    # Calcular estadísticas
    total_clientes = len(clientes)

    # Por distrito
    distritos = {}
    for cliente in clientes:
        distrito = cliente.get("distrito", "Sin distrito")
        distritos[distrito] = distritos.get(distrito, 0) + 1

    # Por prioridad
    prioridades = {}
    for cliente in clientes:
        prioridad = cliente.get("prioridad", 1)
        prioridades[f"Prioridad {prioridad}"] = (
            prioridades.get(f"Prioridad {prioridad}", 0) + 1
        )

    # Pedidos
    pedidos = [float(cliente.get("pedido", 0)) for cliente in clientes]
    pedido_total = sum(pedidos)
    pedido_promedio = pedido_total / len(pedidos) if pedidos else 0

    return jsonify(
        {
            "total_clientes": total_clientes,
            "por_distrito": distritos,
            "por_prioridad": prioridades,
            "pedidos": {
                "total": round(pedido_total, 2),
                "promedio": round(pedido_promedio, 2),
                "minimo": round(min(pedidos), 2) if pedidos else 0,
                "maximo": round(max(pedidos), 2) if pedidos else 0,
            },
        }
    )
