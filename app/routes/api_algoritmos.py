from flask import Blueprint, request, jsonify, current_app
from ..utils.calculos_comunes import get_datos_globales

algoritmos_bp = Blueprint("algoritmos", __name__)


@algoritmos_bp.route("/ejecutar_algoritmo", methods=["POST"])
def api_ejecutar_algoritmo():
    datos = get_datos_globales()
    BellmanFord = current_app.config["BELLMAN_FORD"]
    ProgramacionDinamica = current_app.config["PROGRAMACION_DINAMICA"]
    Backtracking = current_app.config["BACKTRACKING"]
    try:
        data = request.get_json()
        algoritmo = data["algoritmo"]
        if not datos["grafo"]:
            return jsonify({"error": "No hay datos cargados para optimizar"}), 400
        if not datos["vehiculos"]:
            return jsonify({"error": "No hay vehículos registrados"}), 400
        if algoritmo == "bellman_ford":
            bellman = BellmanFord(datos["grafo"])
            resultados = bellman.optimizar_rutas(datos["clientes"], datos["vehiculos"])
        elif algoritmo == "programacion_dinamica":
            pd = ProgramacionDinamica(datos["grafo"])
            resultados = pd.optimizar_rutas(datos["clientes"], datos["vehiculos"])
        elif algoritmo == "backtracking":
            bt = Backtracking(datos["grafo"])
            resultados = bt.optimizar_rutas(datos["clientes"], datos["vehiculos"])
        else:
            return jsonify({"error": "Algoritmo no válido"}), 400
        datos["resultados"] = resultados
        return jsonify(
            {
                "success": True,
                "message": f"Algoritmo {algoritmo} ejecutado exitosamente",
                "resultados": resultados,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error al ejecutar algoritmo: {str(e)}"}), 500
