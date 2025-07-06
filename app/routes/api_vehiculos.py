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


@vehiculos_bp.route("/registrar_vehiculo", methods=["POST"])
def api_registrar_vehiculo():
    """Registrar un nuevo vehículo"""
    datos = get_datos_globales()
    try:
        data = request.get_json()

        # Validar datos requeridos
        campos_requeridos = ["placa", "capacidad", "tipo"]
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({"error": f"Campo requerido faltante: {campo}"}), 400

        # Verificar que la placa no esté duplicada
        for vehiculo_existente in datos["vehiculos"]:
            if vehiculo_existente["placa"].upper() == data["placa"].upper():
                return jsonify({"error": "Ya existe un vehículo con esa placa"}), 400

        vehiculo = {
            "id": len(datos["vehiculos"]) + 1,
            "placa": data["placa"].upper(),
            "capacidad": float(data["capacidad"]),
            "tipo": data["tipo"],
            "modelo": data.get("modelo", "No especificado"),
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
    except ValueError as e:
        return jsonify({"error": "Datos inválidos: " + str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al registrar vehículo: {str(e)}"}), 500


@vehiculos_bp.route("/eliminar_vehiculo/<int:vehiculo_id>", methods=["DELETE"])
def api_eliminar_vehiculo(vehiculo_id):
    """Eliminar un vehículo"""
    datos = get_datos_globales()
    try:
        vehiculos = datos["vehiculos"]
        vehiculo_encontrado = None
        indice = -1

        for i, vehiculo in enumerate(vehiculos):
            if vehiculo["id"] == vehiculo_id:
                vehiculo_encontrado = vehiculo
                indice = i
                break

        if vehiculo_encontrado is None:
            return jsonify({"error": "Vehículo no encontrado"}), 404

        # Verificar si el vehículo está siendo usado en alguna ruta activa
        if "resultados" in datos and datos["resultados"]:
            rutas = datos["resultados"].get("rutas", [])
            for ruta in rutas:
                if ruta.get("vehiculo_id") == vehiculo_id:
                    return (
                        jsonify(
                            {
                                "error": "No se puede eliminar un vehículo que está asignado a una ruta"
                            }
                        ),
                        400,
                    )

        datos["vehiculos"].pop(indice)

        return jsonify(
            {
                "success": True,
                "message": f"Vehículo {vehiculo_encontrado['placa']} eliminado exitosamente",
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error al eliminar vehículo: {str(e)}"}), 500


@vehiculos_bp.route("/actualizar_vehiculo/<int:vehiculo_id>", methods=["PUT"])
def api_actualizar_vehiculo(vehiculo_id):
    """Actualizar información de un vehículo"""
    datos = get_datos_globales()
    try:
        data = request.get_json()
        vehiculos = datos["vehiculos"]
        vehiculo_encontrado = None

        for vehiculo in vehiculos:
            if vehiculo["id"] == vehiculo_id:
                vehiculo_encontrado = vehiculo
                break

        if vehiculo_encontrado is None:
            return jsonify({"error": "Vehículo no encontrado"}), 404

        # Actualizar campos permitidos
        campos_actualizables = ["capacidad", "tipo", "modelo", "disponible"]
        for campo in campos_actualizables:
            if campo in data:
                if campo == "capacidad":
                    vehiculo_encontrado[campo] = float(data[campo])
                elif campo == "disponible":
                    vehiculo_encontrado[campo] = bool(data[campo])
                else:
                    vehiculo_encontrado[campo] = data[campo]

        return jsonify(
            {
                "success": True,
                "message": "Vehículo actualizado exitosamente",
                "vehiculo": vehiculo_encontrado,
            }
        )
    except ValueError as e:
        return jsonify({"error": "Datos inválidos: " + str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al actualizar vehículo: {str(e)}"}), 500


@vehiculos_bp.route("/cargar_flota", methods=["POST"])
def api_cargar_flota():
    """Cargar vehículos desde archivo JSON"""
    datos = get_datos_globales()
    try:
        if "archivo" not in request.files:
            return jsonify({"error": "No se encontró archivo"}), 400

        archivo = request.files["archivo"]
        if archivo.filename == "":
            return jsonify({"error": "No se seleccionó archivo"}), 400

        if not archivo.filename.endswith(".json"):
            return jsonify({"error": "El archivo debe ser JSON"}), 400

        # Leer y parsear JSON
        import json

        contenido = archivo.read().decode("utf-8")
        vehiculos_json = json.loads(contenido)

        if not isinstance(vehiculos_json, list):
            return (
                jsonify(
                    {"error": "El archivo JSON debe contener una lista de vehículos"}
                ),
                400,
            )

        vehiculos_agregados = 0
        vehiculos_omitidos = 0

        for vehiculo_data in vehiculos_json:
            try:
                # Verificar campos requeridos
                if not all(
                    campo in vehiculo_data for campo in ["placa", "capacidad", "tipo"]
                ):
                    vehiculos_omitidos += 1
                    continue

                # Verificar duplicados
                placa_existe = any(
                    v["placa"].upper() == vehiculo_data["placa"].upper()
                    for v in datos["vehiculos"]
                )

                if placa_existe:
                    vehiculos_omitidos += 1
                    continue

                vehiculo = {
                    "id": len(datos["vehiculos"]) + 1,
                    "placa": vehiculo_data["placa"].upper(),
                    "capacidad": float(vehiculo_data["capacidad"]),
                    "tipo": vehiculo_data["tipo"],
                    "modelo": vehiculo_data.get("modelo", "No especificado"),
                    "disponible": True,
                    "fecha_registro": datetime.now().isoformat(),
                }

                datos["vehiculos"].append(vehiculo)
                vehiculos_agregados += 1

            except (ValueError, KeyError):
                vehiculos_omitidos += 1
                continue

        return jsonify(
            {
                "success": True,
                "message": f"Se cargaron {vehiculos_agregados} vehículos exitosamente",
                "vehiculos_agregados": vehiculos_agregados,
                "vehiculos_omitidos": vehiculos_omitidos,
                "total_vehiculos": len(datos["vehiculos"]),
            }
        )

    except json.JSONDecodeError:
        return jsonify({"error": "Archivo JSON inválido"}), 400
    except Exception as e:
        return jsonify({"error": f"Error al cargar flota: {str(e)}"}), 500
