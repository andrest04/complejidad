import math
from typing import Dict, List
from flask import current_app


def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia entre dos puntos usando la fórmula de Haversine"""
    R = 6371  # Radio de la Tierra en km

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def construir_matriz_distancias(clientes: List[Dict]) -> Dict:
    """Construye la matriz de distancias entre todos los nodos"""
    matriz = {}

    # Agregar depósito
    deposito = {
        "id": "deposito",
        "nombre": "Depósito Central",
        "latitud": -12.0464,
        "longitud": -77.0428,
    }

    todos_nodos = [deposito] + clientes

    for i, nodo1 in enumerate(todos_nodos):
        matriz[nodo1["id"]] = {}
        for j, nodo2 in enumerate(todos_nodos):
            if i == j:
                matriz[nodo1["id"]][nodo2["id"]] = 0
            else:
                distancia = calcular_distancia(
                    nodo1["latitud"],
                    nodo1["longitud"],
                    nodo2["latitud"],
                    nodo2["longitud"],
                )
                matriz[nodo1["id"]][nodo2["id"]] = distancia

    return matriz


def get_datos_globales():
    """Función común para obtener datos globales de la configuración"""
    return current_app.config["DATOS_GLOBALES"]
