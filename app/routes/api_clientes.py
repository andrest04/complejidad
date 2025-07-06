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


@api_clientes_bp.route("/api/clientes/<int:cliente_id>", methods=["PUT"])
def actualizar_cliente(cliente_id):
    """Actualiza un cliente específico"""
    datos = current_app.config["DATOS_GLOBALES"]
    clientes = datos.get("clientes", [])

    cliente_index = next(
        (i for i, c in enumerate(clientes) if c.get("id") == cliente_id), None
    )

    if cliente_index is None:
        return jsonify({"error": "Cliente no encontrado"}), 404

    data = request.get_json()

    # Validaciones básicas
    campos_requeridos = ["nombre", "latitud", "longitud", "distrito"]
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({"error": f"Campo requerido: {campo}"}), 400

    # Actualizar cliente
    cliente_actualizado = clientes[cliente_index].copy()
    cliente_actualizado.update(
        {
            "nombre": data["nombre"],
            "latitud": float(data["latitud"]),
            "longitud": float(data["longitud"]),
            "distrito": data["distrito"],
            "prioridad": int(data.get("prioridad", 1)),
            "ventana_inicio": data.get("ventana_inicio", "08:00"),
            "ventana_fin": data.get("ventana_fin", "18:00"),
            "pedido": float(data.get("pedido", 0)),
        }
    )

    clientes[cliente_index] = cliente_actualizado
    current_app.config["DATOS_GLOBALES"]["clientes"] = clientes

    return jsonify(
        {"mensaje": "Cliente actualizado correctamente", "cliente": cliente_actualizado}
    )


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


@api_clientes_bp.route("/api/clientes/recargar", methods=["POST"])
def recargar_clientes():
    """Recarga los clientes desde el CSV"""
    try:
        clientes = cargar_clientes_csv()
        current_app.config["DATOS_GLOBALES"]["clientes"] = clientes
        return jsonify(
            {"mensaje": "Clientes recargados correctamente", "total": len(clientes)}
        )
    except Exception as e:
        return jsonify({"error": f"Error al recargar clientes: {str(e)}"}), 500
