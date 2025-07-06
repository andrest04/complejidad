from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import io
import csv
from ..utils.calculos_comunes import get_datos_globales

general_bp = Blueprint("general", __name__)


@general_bp.route("/obtener_datos_mapa")
def api_obtener_datos_mapa():
    """Obtener datos para mostrar en el mapa"""
    try:
        datos = get_datos_globales()

        if not datos:
            return jsonify({"error": "Datos globales no inicializados"}), 500

        if "clientes" not in datos:
            datos["clientes"] = []

        clientes_con_color = []
        for cliente in datos["clientes"]:
            try:
                cliente_copia = cliente.copy()
                # Agregar color basado en prioridad
                colores_prioridad = {
                    1: "#FF0000",  # Rojo - Prioridad más alta
                    2: "#FF6600",  # Naranja
                    3: "#FFCC00",  # Amarillo
                    4: "#00CC00",  # Verde
                    5: "#0066CC",  # Azul - Prioridad más baja
                }
                cliente_copia["color"] = colores_prioridad.get(
                    cliente.get("prioridad", 3), "#999999"
                )
                # Asegurar que tenemos coordenadas válidas
                lat = cliente.get("latitud", cliente.get("lat", 0))
                lng = cliente.get("longitud", cliente.get("lng", 0))

                if lat == 0 and lng == 0:
                    continue  # Saltar clientes con coordenadas inválidas

                cliente_copia["lat"] = float(lat)
                cliente_copia["lng"] = float(lng)
                cliente_copia["latitud"] = float(lat)
                cliente_copia["longitud"] = float(lng)

                clientes_con_color.append(cliente_copia)
            except (ValueError, TypeError, KeyError) as e:
                print(f"Error procesando cliente {cliente.get('id', 'unknown')}: {e}")
                continue  # Saltar este cliente y continuar

        rutas = []
        if datos.get("resultados") and isinstance(datos["resultados"], dict):
            rutas = datos["resultados"].get("rutas", [])

        return jsonify(
            {
                "clientes": clientes_con_color,
                "rutas": rutas,
                "total_clientes": len(clientes_con_color),
                "clientes_omitidos": len(datos["clientes"]) - len(clientes_con_color),
            }
        )
    except Exception as e:
        print(f"Error completo en obtener_datos_mapa: {e}")
        return jsonify({"error": f"Error al obtener datos del mapa: {str(e)}"}), 500


@general_bp.route("/estadisticas")
def api_estadisticas():
    """Obtener estadísticas generales"""
    datos = get_datos_globales()
    try:
        # Calcular estadísticas de clientes
        clientes = datos["clientes"]
        vehiculos = datos["vehiculos"]

        pedidos_total = sum(float(cliente.get("pedido", 0)) for cliente in clientes)
        capacidad_total = sum(
            float(vehiculo.get("capacidad", 0)) for vehiculo in vehiculos
        )

        # Estadísticas por prioridad
        prioridades = {}
        for cliente in clientes:
            prioridad = cliente.get("prioridad", 3)
            if prioridad not in prioridades:
                prioridades[prioridad] = 0
            prioridades[prioridad] += 1

        # Ventanas críticas (horarios de apertura temprana o cierre tardío)
        ventanas_criticas = 0
        for cliente in clientes:
            inicio = cliente.get("ventana_inicio", "09:00")
            fin = cliente.get("ventana_fin", "17:00")
            if inicio <= "08:00" or fin >= "18:00":
                ventanas_criticas += 1

        return jsonify(
            {
                "pedidos_total": pedidos_total,
                "capacidad_total": capacidad_total,
                "clientes_total": len(clientes),
                "vehiculos_total": len(vehiculos),
                "prioridades": prioridades,
                "ventanas_criticas": ventanas_criticas,
                "prioridad_alta": prioridades.get(1, 0) + prioridades.get(2, 0),
                "total_clientes": len(clientes),
                "total_vehiculos": len(vehiculos),
                "vehiculos_disponibles": len(
                    [v for v in vehiculos if v.get("disponible", True)]
                ),
                "tiene_resultados": "resultados" in datos
                and datos["resultados"] is not None,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error al obtener estadísticas: {str(e)}"}), 500


@general_bp.route("/cargar_csv", methods=["POST"])
def api_cargar_csv():
    """Cargar clientes desde archivo CSV"""
    datos = get_datos_globales()
    grafo_builder = current_app.config["GRAFO_BUILDER"]
    parser_csv = current_app.config.get("PARSER_CSV")

    try:
        if "archivo" not in request.files:
            return jsonify({"error": "No se encontró archivo"}), 400

        archivo = request.files["archivo"]
        if archivo.filename == "":
            return jsonify({"error": "No se seleccionó archivo"}), 400

        if not archivo.filename.endswith(".csv"):
            return jsonify({"error": "El archivo debe ser CSV"}), 400

        # Leer contenido del archivo
        contenido = archivo.read().decode("utf-8")
        archivo_io = io.StringIO(contenido)

        # Parsear CSV
        nuevos_clientes = []
        reader = csv.DictReader(archivo_io)

        for i, row in enumerate(reader, 1):
            try:
                cliente = {
                    "id": len(datos["clientes"]) + len(nuevos_clientes) + 1,
                    "nombre": row.get("nombre", f"Cliente {i}"),
                    "latitud": float(row.get("latitud", row.get("lat", 0))),
                    "longitud": float(row.get("longitud", row.get("lng", 0))),
                    "lat": float(row.get("latitud", row.get("lat", 0))),
                    "lng": float(row.get("longitud", row.get("lng", 0))),
                    "prioridad": int(row.get("prioridad", 3)),
                    "ventana_inicio": row.get("ventana_inicio", "09:00"),
                    "ventana_fin": row.get("ventana_fin", "17:00"),
                    "pedido": float(row.get("pedido", 100)),
                }
                nuevos_clientes.append(cliente)
            except (ValueError, KeyError) as e:
                return jsonify({"error": f"Error en fila {i}: {str(e)}"}), 400

        # Agregar clientes a los datos globales
        datos["clientes"].extend(nuevos_clientes)

        # Reconstruir grafo
        if datos["clientes"]:
            datos["grafo"] = grafo_builder.construir_grafo(datos["clientes"])

        return jsonify(
            {
                "success": True,
                "message": f"{len(nuevos_clientes)} clientes cargados exitosamente",
                "clientes_nuevos": len(nuevos_clientes),
                "clientes_total": len(datos["clientes"]),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Error al cargar CSV: {str(e)}"}), 500
