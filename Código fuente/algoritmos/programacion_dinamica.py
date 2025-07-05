import math
import time
from typing import Dict, List, Tuple, Optional
from itertools import combinations

class ProgramacionDinamica:
    """Implementación de Programación Dinámica para optimización de rutas"""
    
    def __init__(self, grafo: Dict):
        self.grafo = grafo
        self.memo = {}
        self.caminos = {}
        
    def calcular_distancia(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula la distancia entre dos puntos usando la fórmula de Haversine"""
        R = 6371  # Radio de la Tierra en km
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def construir_matriz_distancias(self, clientes: List[Dict]) -> Dict:
        """Construye la matriz de distancias entre todos los nodos"""
        matriz = {}
        
        # Agregar depósito
        deposito = {
            'id': 'deposito',
            'nombre': 'Depósito Central',
            'latitud': -12.0464,
            'longitud': -77.0428
        }
        
        todos_nodos = [deposito] + clientes
        
        for i, nodo1 in enumerate(todos_nodos):
            matriz[nodo1['id']] = {}
            for j, nodo2 in enumerate(todos_nodos):
                if i == j:
                    matriz[nodo1['id']][nodo2['id']] = 0
                else:
                    distancia = self.calcular_distancia(
                        nodo1['latitud'], nodo1['longitud'],
                        nodo2['latitud'], nodo2['longitud']
                    )
                    matriz[nodo1['id']][nodo2['id']] = distancia
        
        return matriz
    
    def tsp_programacion_dinamica(self, matriz_distancias: Dict, clientes: List[Dict]) -> Tuple[float, List[str]]:
        """Resuelve el TSP usando Programación Dinámica"""
        n = len(clientes) + 1  # +1 por el depósito
        nodos = ['deposito'] + [cliente['id'] for cliente in clientes]
        
        # Crear todas las combinaciones posibles de nodos
        def generar_subconjuntos(n):
            subconjuntos = []
            for r in range(1, n + 1):
                for combo in combinations(range(1, n), r):  # Excluir depósito (índice 0)
                    subconjuntos.append(frozenset([0] + list(combo)))
            return subconjuntos
        
        subconjuntos = generar_subconjuntos(n - 1)
        
        # Inicializar memoización
        memo = {}
        caminos = {}
        
        # Caso base: desde depósito hasta depósito
        memo[(frozenset([0]), 0)] = 0
        caminos[(frozenset([0]), 0)] = [0]
        
        # Llenar la tabla de memoización
        for subconjunto in subconjuntos:
            for j in subconjunto:
                if j == 0:  # No podemos terminar en el depósito si no hemos visitado otros nodos
                    continue
                
                # Encontrar el costo mínimo para llegar a j visitando todos los nodos en subconjunto
                min_costo = float('inf')
                mejor_predecesor = None
                
                for k in subconjunto:
                    if k != j:
                        subconjunto_sin_j = frozenset([x for x in subconjunto if x != j])
                        if (subconjunto_sin_j, k) in memo:
                            costo = memo[(subconjunto_sin_j, k)] + matriz_distancias[nodos[k]][nodos[j]]
                            if costo < min_costo:
                                min_costo = costo
                                mejor_predecesor = k
                
                if min_costo != float('inf'):
                    memo[(subconjunto, j)] = min_costo
                    if mejor_predecesor is not None:
                        caminos[(subconjunto, j)] = caminos[(frozenset([x for x in subconjunto if x != j]), mejor_predecesor)] + [j]
        
        # Encontrar el camino mínimo que regresa al depósito
        todos_nodos = frozenset(range(n))
        min_costo_final = float('inf')
        mejor_ultimo_nodo = None
        
        for j in range(1, n):  # Probar terminar en cada nodo (excepto depósito)
            if (todos_nodos, j) in memo:
                costo_final = memo[(todos_nodos, j)] + matriz_distancias[nodos[j]][nodos[0]]
                if costo_final < min_costo_final:
                    min_costo_final = costo_final
                    mejor_ultimo_nodo = j
        
        if mejor_ultimo_nodo is not None:
            camino_completo = caminos[(todos_nodos, mejor_ultimo_nodo)] + [0]
            return min_costo_final, [nodos[i] for i in camino_completo]
        else:
            return float('inf'), []
    
    def dividir_clientes_por_prioridad(self, clientes: List[Dict]) -> Dict[int, List[Dict]]:
        """Divide los clientes por nivel de prioridad"""
        clientes_por_prioridad = {}
        for cliente in clientes:
            prioridad = cliente['prioridad']
            if prioridad not in clientes_por_prioridad:
                clientes_por_prioridad[prioridad] = []
            clientes_por_prioridad[prioridad].append(cliente)
        return clientes_por_prioridad
    
    def optimizar_ruta_por_prioridad(self, clientes_grupo: List[Dict], matriz_distancias: Dict) -> Dict:
        """Optimiza la ruta para un grupo de clientes de la misma prioridad"""
        if len(clientes_grupo) <= 1:
            return {
                'distancia_total': 0,
                'clientes': clientes_grupo,
                'orden_visita': [cliente['id'] for cliente in clientes_grupo]
            }
        
        # Resolver TSP para este grupo
        distancia_total, orden_visita = self.tsp_programacion_dinamica(matriz_distancias, clientes_grupo)
        
        return {
            'distancia_total': distancia_total,
            'clientes': clientes_grupo,
            'orden_visita': orden_visita
        }
    
    def asignar_rutas_a_vehiculos(self, rutas_optimizadas: List[Dict], vehiculos: List[Dict]) -> List[Dict]:
        """Asigna las rutas optimizadas a los vehículos disponibles"""
        vehiculos_ordenados = sorted(vehiculos, key=lambda x: x['capacidad'], reverse=True)
        rutas_asignadas = []
        
        for ruta in rutas_optimizadas:
            # Encontrar el vehículo más apropiado
            vehiculo_asignado = None
            for vehiculo in vehiculos_ordenados:
                if vehiculo['disponible'] and vehiculo['capacidad'] >= sum(c['pedido'] for c in ruta['clientes']):
                    vehiculo_asignado = vehiculo
                    vehiculo['disponible'] = False  # Marcar como usado
                    break
            
            if vehiculo_asignado:
                ruta_vehiculo = {
                    'vehiculo_id': vehiculo_asignado['id'],
                    'placa': vehiculo_asignado['placa'],
                    'capacidad': vehiculo_asignado['capacidad'],
                    'clientes': ruta['clientes'],
                    'distancia_total': ruta['distancia_total'],
                    'carga_total': sum(c['pedido'] for c in ruta['clientes']),
                    'tiempo_estimado': ruta['distancia_total'] * 2,  # 2 minutos por km
                    'orden_visita': ruta['orden_visita']
                }
                rutas_asignadas.append(ruta_vehiculo)
        
        return rutas_asignadas
    
    def optimizar_rutas(self, clientes: List[Dict], vehiculos: List[Dict]) -> Dict:
        """Método principal para optimizar rutas usando Programación Dinámica"""
        tiempo_inicio = time.time()
        
        try:
            # Construir matriz de distancias
            matriz_distancias = self.construir_matriz_distancias(clientes)
            
            # Dividir clientes por prioridad
            clientes_por_prioridad = self.dividir_clientes_por_prioridad(clientes)
            
            # Optimizar rutas por prioridad
            rutas_optimizadas = []
            for prioridad in sorted(clientes_por_prioridad.keys()):
                clientes_grupo = clientes_por_prioridad[prioridad]
                ruta_optimizada = self.optimizar_ruta_por_prioridad(clientes_grupo, matriz_distancias)
                rutas_optimizadas.append(ruta_optimizada)
            
            # Asignar rutas a vehículos
            rutas_finales = self.asignar_rutas_a_vehiculos(rutas_optimizadas, vehiculos)
            
            # Calcular métricas
            distancia_total = sum(ruta['distancia_total'] for ruta in rutas_finales)
            tiempo_total = sum(ruta['tiempo_estimado'] for ruta in rutas_finales)
            clientes_atendidos = sum(len(ruta['clientes']) for ruta in rutas_finales)
            vehiculos_utilizados = len(rutas_finales)
            
            tiempo_ejecucion = time.time() - tiempo_inicio
            
            resultados = {
                'algoritmo': 'Programación Dinámica',
                'tiempo_ejecucion': tiempo_ejecucion,
                'rutas': rutas_finales,
                'metricas': {
                    'distancia_total': distancia_total,
                    'tiempo_total': tiempo_total,
                    'clientes_atendidos': clientes_atendidos,
                    'vehiculos_utilizados': vehiculos_utilizados,
                    'eficiencia': clientes_atendidos / max(vehiculos_utilizados, 1)
                },
                'rutas_por_prioridad': rutas_optimizadas,
                'matriz_distancias': matriz_distancias
            }
            
            return resultados
            
        except Exception as e:
            return {
                'algoritmo': 'Programación Dinámica',
                'error': str(e),
                'tiempo_ejecucion': time.time() - tiempo_inicio
            } 