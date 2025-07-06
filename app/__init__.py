from flask import Flask
from .config import Config
from .utils.grafo_builder import GrafoBuilder
from .utils.mapa_utils import MapaUtils
from .utils.parser_csv import ParserCSV
from .algoritmos.bellman_ford import BellmanFord
from .algoritmos.programacion_dinamica import ProgramacionDinamica
from .algoritmos.backtracking import Backtracking
import os
import json
from datetime import datetime


def create_app():
    """Factory function to create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    config = Config()
    app.config.from_object(config)

    # Instancias y clases globales
    app.config["DATOS_GLOBALES"] = {
        "clientes": [],
        "vehiculos": [],
        "grafo": None,
        "resultados": None,
    }
    app.config["GRAFO_BUILDER"] = GrafoBuilder()
    app.config["MAPA_UTILS"] = MapaUtils()
    app.config["PARSER_CSV"] = ParserCSV()
    app.config["BELLMAN_FORD"] = BellmanFord
    app.config["PROGRAMACION_DINAMICA"] = ProgramacionDinamica
    app.config["BACKTRACKING"] = Backtracking

    # Cargar datos iniciales
    parser_csv = ParserCSV()
    grafo_builder = app.config["GRAFO_BUILDER"]
    datos_globales = app.config["DATOS_GLOBALES"]
    try:
        archivo_csv = "Dataset/clientes_lima_1500.csv"
        if os.path.exists(archivo_csv):
            with open(archivo_csv, "r", encoding="utf-8") as f:
                clientes = parser_csv.leer_clientes_csv(f)
                datos_globales["clientes"] = clientes
                datos_globales["grafo"] = grafo_builder.construir_grafo(clientes)
            print(f"✅ CSV cargado: {len(clientes)} clientes")
        else:
            print(f"❌ Archivo no encontrado: {archivo_csv}")
    except Exception as e:
        print(f"❌ Error al cargar CSV: {str(e)}")
    try:
        archivo_json = "Dataset/flota_lima_1500.json"
        if os.path.exists(archivo_json):
            with open(archivo_json, "r", encoding="utf-8") as f:
                vehiculos = json.load(f)
                for i, vehiculo in enumerate(vehiculos):
                    vehiculo["id"] = i + 1
                    vehiculo["disponible"] = True
                    vehiculo["fecha_registro"] = datetime.now().isoformat()
                datos_globales["vehiculos"] = vehiculos
            print(f"✅ JSON cargado: {len(vehiculos)} vehículos")
        else:
            print(f"❌ Archivo no encontrado: {archivo_json}")
    except Exception as e:
        print(f"❌ Error al cargar JSON: {str(e)}")
    print(
        f"✅ Carga de datos completada: {len(datos_globales['clientes'])} clientes, {len(datos_globales['vehiculos'])} vehículos"
    )
    if datos_globales["clientes"]:
        print(
            "Primeros pedidos:", [c["pedido"] for c in datos_globales["clientes"][:5]]
        )
    if datos_globales["vehiculos"]:
        print(
            "Primeras capacidades:",
            [v["capacidad"] for v in datos_globales["vehiculos"][:5]],
        )

    # Register blueprints
    from .routes import (
        main_bp,
        api_clientes_bp,
        api_vehiculos_bp,
        api_algoritmos_bp,
        api_general_bp,
    )

    app.register_blueprint(main_bp)
    app.register_blueprint(api_clientes_bp)
    app.register_blueprint(api_vehiculos_bp, url_prefix="/api")
    app.register_blueprint(api_algoritmos_bp, url_prefix="/api")
    app.register_blueprint(api_general_bp, url_prefix="/api")

    return app
