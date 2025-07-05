import math
import time
from typing import Dict, List, Tuple, Optional
import copy
from ..utils.calculos_comunes import calcular_distancia, construir_matriz_distancias


class Backtracking:
    """Implementación de Backtracking con poda para optimización de rutas"""

    def __init__(self, grafo: Dict):
        self.grafo = grafo
        self.mejor_solucion = None
        self.mejor_costo = float("inf")
        self.nodos_visitados = set()
        self.tiempo_inicio = None
        self.tiempo_limite = 300  # 5 minutos

    def calcular_cota_inferior(
        self,
        ruta_actual: List[str],
        clientes_restantes: List[Dict],
        matriz_distancias: Dict,
    ) -> float:
        """Calcula una cota inferior para la poda"""
        if not ruta_actual:
            return 0

        # Distancia actual
        distancia_actual = 0
        for i in range(len(ruta_actual) - 1):
            distancia_actual += matriz_distancias[ruta_actual[i]][ruta_actual[i + 1]]

        # Cota inferior usando el árbol de expansión mínima
        if clientes_restantes:
            # Calcular MST para los nodos restantes
            nodos_restantes = [cliente["id"] for cliente in clientes_restantes]
            mst_costo = self.calcular_mst(nodos_restantes, matriz_distancias)

            # Agregar distancia desde el último nodo al MST y desde MST al depósito
            if ruta_actual:
                ultimo_nodo = ruta_actual[-1]
                min_distancia_mst = min(
                    matriz_distancias[ultimo_nodo][nodo] for nodo in nodos_restantes
                )
                min_distancia_deposito = min(
                    matriz_distancias[nodo]["deposito"] for nodo in nodos_restantes
                )

                return (
                    distancia_actual
                    + mst_costo
                    + min_distancia_mst
                    + min_distancia_deposito
                )

        return distancia_actual

    def calcular_mst(self, nodos: List[str], matriz_distancias: Dict) -> float:
        """Calcula el costo del árbol de expansión mínima usando Prim"""
        if len(nodos) <= 1:
            return 0

        # Implementación simplificada de Prim
        visitados = set()
        costo_total = 0

        # Empezar con el primer nodo
        visitados.add(nodos[0])

        while len(visitados) < len(nodos):
            min_distancia = float("inf")
            nodo_agregar = None

            for nodo_visitado in visitados:
                for nodo_no_visitado in nodos:
                    if nodo_no_visitado not in visitados:
                        distancia = matriz_distancias[nodo_visitado][nodo_no_visitado]
                        if distancia < min_distancia:
                            min_distancia = distancia
                            nodo_agregar = nodo_no_visitado

            if nodo_agregar:
                visitados.add(nodo_agregar)
                costo_total += min_distancia

        return costo_total

    def verificar_restricciones(
        self,
        ruta_actual: List[str],
        cliente: Dict,
        vehiculo: Dict,
        matriz_distancias: Dict,
    ) -> bool:
        """Verifica si se cumplen todas las restricciones"""
        # Verificar capacidad
        carga_actual = sum(
            c["pedido"] for c in self.obtener_clientes_en_ruta(ruta_actual)
        )
        if carga_actual + cliente["pedido"] > vehiculo["capacidad"]:
            return False

        # Verificar tiempo (estimación: 2 minutos por km)
        if ruta_actual:
            distancia_adicional = matriz_distancias[ruta_actual[-1]][cliente["id"]]
            tiempo_adicional = distancia_adicional * 2
            tiempo_actual = sum(
                matriz_distancias[ruta_actual[i]][ruta_actual[i + 1]] * 2
                for i in range(len(ruta_actual) - 1)
            )

            if tiempo_actual + tiempo_adicional > 480:  # 8 horas
                return False

        # Verificar ventana horaria (simplificado)
        # En una implementación real, se verificaría la hora actual vs ventana

        return True

    def obtener_clientes_en_ruta(self, ruta: List[str]) -> List[Dict]:
        """Obtiene los clientes que están en la ruta actual"""
        # Esta función necesitaría acceso a la lista completa de clientes
        # Por simplicidad, retornamos una lista vacía
        return []

    def backtracking_rutas(
        self,
        ruta_actual: List[str],
        clientes_restantes: List[Dict],
        vehiculos_disponibles: List[Dict],
        matriz_distancias: Dict,
        nivel: int = 0,
    ):
        """Algoritmo de backtracking con poda"""
        # Verificar límite de tiempo
        if time.time() - self.tiempo_inicio > self.tiempo_limite:
            return

        # Si no hay más clientes, evaluar la solución
        if not clientes_restantes:
            if ruta_actual:
                # Agregar retorno al depósito
                ruta_completa = ruta_actual + ["deposito"]
                costo_total = sum(
                    matriz_distancias[ruta_completa[i]][ruta_completa[i + 1]]
                    for i in range(len(ruta_completa) - 1)
                )

                if costo_total < self.mejor_costo:
                    self.mejor_costo = costo_total
                    self.mejor_solucion = ruta_completa.copy()
            return

        # Poda: verificar cota inferior
        cota_inferior = self.calcular_cota_inferior(
            ruta_actual, clientes_restantes, matriz_distancias
        )
        if cota_inferior >= self.mejor_costo:
            return

        # Probar cada cliente restante
        for i, cliente in enumerate(clientes_restantes):
            # Verificar restricciones
            if not self.verificar_restricciones(
                ruta_actual, cliente, vehiculos_disponibles[0], matriz_distancias
            ):
                continue

            # Agregar cliente a la ruta
            ruta_actual.append(cliente["id"])

            # Recursión
            clientes_restantes_nuevo = (
                clientes_restantes[:i] + clientes_restantes[i + 1 :]
            )
            self.backtracking_rutas(
                ruta_actual,
                clientes_restantes_nuevo,
                vehiculos_disponibles,
                matriz_distancias,
                nivel + 1,
            )

            # Backtrack
            ruta_actual.pop()

    def dividir_problema_por_vehiculos(
        self, clientes: List[Dict], vehiculos: List[Dict]
    ) -> List[Dict]:
        """Divide el problema en subproblemas por vehículo"""
        # Ordenar por prioridad y capacidad
        clientes_ordenados = sorted(
            clientes, key=lambda x: (x["prioridad"], -x["pedido"])
        )
        vehiculos_ordenados = sorted(
            vehiculos, key=lambda x: x["capacidad"], reverse=True
        )

        asignaciones = []
        clientes_asignados = set()

        for vehiculo in vehiculos_ordenados:
            if not vehiculo["disponible"]:
                continue

            # Encontrar clientes que pueden ser asignados a este vehículo
            clientes_vehiculo = []
            capacidad_restante = vehiculo["capacidad"]

            for cliente in clientes_ordenados:
                if (
                    cliente["id"] not in clientes_asignados
                    and cliente["pedido"] <= capacidad_restante
                ):
                    clientes_vehiculo.append(cliente)
                    capacidad_restante -= cliente["pedido"]
                    clientes_asignados.add(cliente["id"])

            if clientes_vehiculo:
                asignaciones.append(
                    {"vehiculo": vehiculo, "clientes": clientes_vehiculo}
                )

        return asignaciones

    def optimizar_ruta_individual(
        self, clientes: List[Dict], vehiculo: Dict, matriz_distancias: Dict
    ) -> Dict:
        """Optimiza la ruta para un vehículo individual usando backtracking"""
        if len(clientes) <= 1:
            return {
                "vehiculo_id": vehiculo["id"],
                "placa": vehiculo["placa"],
                "capacidad": vehiculo["capacidad"],
                "clientes": clientes,
                "distancia_total": 0,
                "carga_total": sum(c["pedido"] for c in clientes),
                "tiempo_estimado": 0,
                "ruta_optimizada": [c["id"] for c in clientes],
            }

        # Reinicializar para este subproblema
        self.mejor_solucion = None
        self.mejor_costo = float("inf")
        self.tiempo_inicio = time.time()

        # Ejecutar backtracking
        ruta_inicial = ["deposito"]
        self.backtracking_rutas(ruta_inicial, clientes, [vehiculo], matriz_distancias)

        if self.mejor_solucion:
            distancia_total = sum(
                matriz_distancias[self.mejor_solucion[i]][self.mejor_solucion[i + 1]]
                for i in range(len(self.mejor_solucion) - 1)
            )

            return {
                "vehiculo_id": vehiculo["id"],
                "placa": vehiculo["placa"],
                "capacidad": vehiculo["capacidad"],
                "clientes": clientes,
                "distancia_total": distancia_total,
                "carga_total": sum(c["pedido"] for c in clientes),
                "tiempo_estimado": distancia_total * 2,
                "ruta_optimizada": self.mejor_solucion,
            }
        else:
            # Solución por defecto si no se encuentra optimización
            return {
                "vehiculo_id": vehiculo["id"],
                "placa": vehiculo["placa"],
                "capacidad": vehiculo["capacidad"],
                "clientes": clientes,
                "distancia_total": 0,
                "carga_total": sum(c["pedido"] for c in clientes),
                "tiempo_estimado": 0,
                "ruta_optimizada": ["deposito"]
                + [c["id"] for c in clientes]
                + ["deposito"],
            }

    def optimizar_rutas(self, clientes: List[Dict], vehiculos: List[Dict]) -> Dict:
        """Método principal para optimizar rutas usando Backtracking"""
        tiempo_inicio = time.time()

        try:
            # Construir matriz de distancias
            matriz_distancias = construir_matriz_distancias(clientes)

            # Dividir problema por vehículos
            asignaciones = self.dividir_problema_por_vehiculos(clientes, vehiculos)

            # Optimizar cada subproblema
            rutas_optimizadas = []
            for asignacion in asignaciones:
                ruta = self.optimizar_ruta_individual(
                    asignacion["clientes"], asignacion["vehiculo"], matriz_distancias
                )
                rutas_optimizadas.append(ruta)

            # Calcular métricas
            distancia_total = sum(ruta["distancia_total"] for ruta in rutas_optimizadas)
            tiempo_total = sum(ruta["tiempo_estimado"] for ruta in rutas_optimizadas)
            clientes_atendidos = sum(
                len(ruta["clientes"]) for ruta in rutas_optimizadas
            )
            vehiculos_utilizados = len(rutas_optimizadas)

            tiempo_ejecucion = time.time() - tiempo_inicio

            resultados = {
                "algoritmo": "Backtracking con Poda",
                "tiempo_ejecucion": tiempo_ejecucion,
                "rutas": rutas_optimizadas,
                "metricas": {
                    "distancia_total": distancia_total,
                    "tiempo_total": tiempo_total,
                    "clientes_atendidos": clientes_atendidos,
                    "vehiculos_utilizados": vehiculos_utilizados,
                    "eficiencia": clientes_atendidos / max(vehiculos_utilizados, 1),
                },
                "asignaciones": asignaciones,
                "matriz_distancias": matriz_distancias,
            }

            return resultados

        except Exception as e:
            return {
                "algoritmo": "Backtracking con Poda",
                "error": str(e),
                "tiempo_ejecucion": time.time() - tiempo_inicio,
            }
