import math
import time
from typing import Dict, List, Tuple, Optional
from ..utils.calculos_comunes import calcular_distancia, construir_matriz_distancias


class BellmanFord:
    """Implementación del algoritmo Bellman-Ford para optimización de rutas"""

    def __init__(self, grafo: Dict):
        self.grafo = grafo
        self.nodos = list(grafo.keys())
        self.distancias = {}
        self.predecesores = {}

    def bellman_ford_caminos_minimos(
        self, matriz_distancias: Dict, origen: str
    ) -> Tuple[Dict, Dict]:
        """Ejecuta el algoritmo Bellman-Ford para encontrar caminos mínimos"""
        # Inicialización
        distancias = {nodo: float("inf") for nodo in matriz_distancias.keys()}
        predecesores = {nodo: None for nodo in matriz_distancias.keys()}

        distancias[origen] = 0

        # Relajación de aristas
        for _ in range(len(matriz_distancias) - 1):
            for u in matriz_distancias.keys():
                for v in matriz_distancias[u].keys():
                    peso = matriz_distancias[u][v]
                    if (
                        distancias[u] != float("inf")
                        and distancias[u] + peso < distancias[v]
                    ):
                        distancias[v] = distancias[u] + peso
                        predecesores[v] = u

        # Detección de ciclos negativos
        for u in matriz_distancias.keys():
            for v in matriz_distancias[u].keys():
                peso = matriz_distancias[u][v]
                if (
                    distancias[u] != float("inf")
                    and distancias[u] + peso < distancias[v]
                ):
                    raise ValueError("Se detectó un ciclo negativo en el grafo")

        return distancias, predecesores

    def reconstruir_camino(self, predecesores: Dict, destino: str) -> List[str]:
        """Reconstruye el camino desde el origen hasta el destino"""
        camino = []
        actual = destino

        while actual is not None:
            camino.append(actual)
            actual = predecesores.get(actual)

        return list(reversed(camino))

    def asignar_clientes_a_vehiculos(
        self,
        clientes: List[Dict],
        vehiculos: List[Dict],
        distancias: Dict,
        predecesores: Dict,
    ) -> List[Dict]:
        """Asigna clientes a vehículos basándose en capacidad y distancia"""
        
        rutas = []
        clientes_asignados = set()

        # Ordenar clientes por prioridad (menor número = mayor prioridad)
        clientes_ordenados = sorted(clientes, key=lambda x: x["prioridad"])

        # Ordenar vehículos por capacidad (mayor a menor)
        vehiculos_ordenados = sorted(
            vehiculos, key=lambda x: x["capacidad"], reverse=True
        )

        for vehiculo in vehiculos_ordenados:
            if not vehiculo["disponible"]:
                continue

            ruta_vehiculo = {
                "vehiculo_id": vehiculo["id"],
                "placa": vehiculo["placa"],
                "capacidad": vehiculo["capacidad"],
                "clientes": [],
                "distancia_total": 0,
                "carga_total": 0,
                "tiempo_estimado": 0,
            }

            capacidad_restante = vehiculo["capacidad"]

            for cliente in clientes_ordenados:
                if cliente["id"] in clientes_asignados:
                    continue

                # Verificar capacidad
                if cliente["pedido"] > capacidad_restante:
                    continue

                # Calcular distancia desde el último punto de la ruta
                if not ruta_vehiculo["clientes"]:
                    # Primer cliente desde depósito
                    distancia = distancias.get(cliente["id"], float("inf"))
                    camino = self.reconstruir_camino(predecesores, cliente["id"])
                else:
                    # Desde el último cliente
                    ultimo_cliente = ruta_vehiculo["clientes"][-1]
                    distancia = calcular_distancia(
                        ultimo_cliente["latitud"],
                        ultimo_cliente["longitud"],
                        cliente["latitud"],
                        cliente["longitud"],
                    )
                    camino = [ultimo_cliente["id"], cliente["id"]]

                # Verificar restricciones de tiempo (8 horas máximo)
                tiempo_estimado = distancia * 2  # 2 minutos por km (estimación)
                if ruta_vehiculo["tiempo_estimado"] + tiempo_estimado > 480:  # 8 horas
                    continue

                ruta_vehiculo["clientes"].append(cliente)
                ruta_vehiculo["distancia_total"] += distancia
                ruta_vehiculo["carga_total"] += cliente["pedido"]
                ruta_vehiculo["tiempo_estimado"] += tiempo_estimado
                capacidad_restante -= cliente["pedido"]
                clientes_asignados.add(cliente["id"])

            if ruta_vehiculo["clientes"]:
                # Agregar retorno al depósito
                if ruta_vehiculo["clientes"]:
                    ultimo_cliente = ruta_vehiculo["clientes"][-1]
                    distancia_deposito = calcular_distancia(
                        ultimo_cliente["latitud"],
                        ultimo_cliente["longitud"],
                        -12.0464,
                        -77.0428,  # Coordenadas del depósito
                    )
                    ruta_vehiculo["distancia_total"] += distancia_deposito
                    ruta_vehiculo["tiempo_estimado"] += distancia_deposito * 2

                rutas.append(ruta_vehiculo)

        return rutas

    def optimizar_rutas(self, clientes: List[Dict], vehiculos: List[Dict]) -> Dict:
        """Método principal para optimizar rutas usando Bellman-Ford"""
        tiempo_inicio = time.time()

        try:
            # Construir matriz de distancias
            matriz_distancias = construir_matriz_distancias(clientes)

            # Ejecutar Bellman-Ford desde el depósito
            distancias, predecesores = self.bellman_ford_caminos_minimos(
                matriz_distancias, "deposito"
            )

            # Asignar clientes a vehículos
            rutas = self.asignar_clientes_a_vehiculos(
                clientes, vehiculos, distancias, predecesores
            )

            # Calcular métricas
            distancia_total = sum(ruta["distancia_total"] for ruta in rutas)
            tiempo_total = sum(ruta["tiempo_estimado"] for ruta in rutas)
            clientes_atendidos = sum(len(ruta["clientes"]) for ruta in rutas)
            vehiculos_utilizados = len(rutas)

            tiempo_ejecucion = time.time() - tiempo_inicio

            resultados = {
                "algoritmo": "Bellman-Ford",
                "tiempo_ejecucion": tiempo_ejecucion,
                "rutas": rutas,
                "metricas": {
                    "distancia_total": distancia_total,
                    "tiempo_total": tiempo_total,
                    "clientes_atendidos": clientes_atendidos,
                    "vehiculos_utilizados": vehiculos_utilizados,
                    "eficiencia": clientes_atendidos / max(vehiculos_utilizados, 1),
                },
                "distancias_minimas": distancias,
                "predecesores": predecesores,
            }

            return resultados

        except Exception as e:
            return {
                "algoritmo": "Bellman-Ford",
                "error": str(e),
                "tiempo_ejecucion": time.time() - tiempo_inicio,
            }


def optimizar_rutas_bellman_ford(clientes: List[Dict], vehiculos: List[Dict], **kwargs) -> Dict:
    """
    Función principal para optimizar rutas usando el algoritmo Bellman-Ford
    
    Args:
        clientes: Lista de clientes con sus coordenadas y pedidos
        vehiculos: Lista de vehículos con sus capacidades
        **kwargs: Parámetros adicionales (ignorados para simplificar)
    
    Returns:
        Dict con los resultados de la optimización
    """
    try:
        # Crear instancia del algoritmo
        bellman_ford = BellmanFord({})
        
        # Ejecutar optimización directamente
        resultados = bellman_ford.optimizar_rutas(clientes, vehiculos)
        
        # Agregar información básica
        resultados["fecha_ejecucion"] = time.time()
        
        return resultados
        
    except Exception as e:
        return {
            "algoritmo": "Bellman-Ford",
            "error": f"Error en optimización: {str(e)}",
            "tiempo_ejecucion": 0,
            "fecha_ejecucion": time.time()
        }
