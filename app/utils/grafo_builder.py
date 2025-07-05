import math
from typing import Dict, List, Tuple, Optional

class GrafoBuilder:
    """Clase para construir y gestionar la estructura del grafo de rutas"""
    
    def __init__(self):
        self.deposito = {
            'id': 'deposito',
            'nombre': 'Depósito Central',
            'latitud': -12.0464,
            'longitud': -77.0428,
            'tipo': 'deposito'
        }
        
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
    
    def construir_grafo(self, clientes: List[Dict]) -> Dict:
        """Construye la estructura del grafo completo"""
        grafo = {
            'nodos': {},
            'aristas': {},
            'matriz_distancias': {},
            'metadata': {
                'total_nodos': len(clientes) + 1,  # +1 por el depósito
                'total_aristas': 0,
                'deposito': self.deposito
            }
        }
        
        # Agregar depósito
        grafo['nodos']['deposito'] = self.deposito
        
        # Agregar clientes como nodos
        for cliente in clientes:
            grafo['nodos'][cliente['id']] = {
                'id': cliente['id'],
                'nombre': cliente['nombre'],
                'latitud': cliente['latitud'],
                'longitud': cliente['longitud'],
                'prioridad': cliente['prioridad'],
                'ventana_inicio': cliente['ventana_inicio'],
                'ventana_fin': cliente['ventana_fin'],
                'pedido': cliente['pedido'],
                'tipo': 'cliente'
            }
        
        # Construir matriz de distancias
        todos_nodos = list(grafo['nodos'].values())
        for i, nodo1 in enumerate(todos_nodos):
            grafo['matriz_distancias'][nodo1['id']] = {}
            for j, nodo2 in enumerate(todos_nodos):
                if i == j:
                    grafo['matriz_distancias'][nodo1['id']][nodo2['id']] = 0
                else:
                    distancia = self.calcular_distancia(
                        nodo1['latitud'], nodo1['longitud'],
                        nodo2['latitud'], nodo2['longitud']
                    )
                    grafo['matriz_distancias'][nodo1['id']][nodo2['id']] = distancia
                    
                    # Agregar arista
                    arista_id = f"{nodo1['id']}_{nodo2['id']}"
                    grafo['aristas'][arista_id] = {
                        'origen': nodo1['id'],
                        'destino': nodo2['id'],
                        'distancia': distancia,
                        'tiempo_estimado': distancia * 2,  # 2 minutos por km
                        'costo': distancia * 0.5  # 0.5 por km
                    }
        
        grafo['metadata']['total_aristas'] = len(grafo['aristas'])
        
        return grafo
    
    def obtener_vecinos(self, grafo: Dict, nodo_id: str) -> List[Dict]:
        """Obtiene los nodos vecinos de un nodo específico"""
        vecinos = []
        if nodo_id in grafo['matriz_distancias']:
            for destino, distancia in grafo['matriz_distancias'][nodo_id].items():
                if destino != nodo_id and distancia > 0:
                    vecinos.append({
                        'nodo': grafo['nodos'][destino],
                        'distancia': distancia
                    })
        return vecinos
    
    def obtener_nodos_por_prioridad(self, grafo: Dict, prioridad: int) -> List[Dict]:
        """Obtiene todos los nodos de una prioridad específica"""
        nodos_prioridad = []
        for nodo in grafo['nodos'].values():
            if nodo.get('tipo') == 'cliente' and nodo.get('prioridad') == prioridad:
                nodos_prioridad.append(nodo)
        return nodos_prioridad
    
    def obtener_nodos_en_radio(self, grafo: Dict, centro_lat: float, centro_lon: float, 
                              radio_km: float) -> List[Dict]:
        """Obtiene nodos dentro de un radio específico desde un punto central"""
        nodos_en_radio = []
        
        for nodo in grafo['nodos'].values():
            distancia = self.calcular_distancia(
                centro_lat, centro_lon,
                nodo['latitud'], nodo['longitud']
            )
            if distancia <= radio_km:
                nodos_en_radio.append(nodo)
        
        return nodos_en_radio
    
    def calcular_centroide(self, nodos: List[Dict]) -> Tuple[float, float]:
        """Calcula el centroide de un conjunto de nodos"""
        if not nodos:
            return (0, 0)
        
        lat_total = sum(nodo['latitud'] for nodo in nodos)
        lon_total = sum(nodo['longitud'] for nodo in nodos)
        
        return (lat_total / len(nodos), lon_total / len(nodos))
    
    def dividir_por_zona_geografica(self, grafo: Dict, num_zonas: int = 4) -> Dict[int, List[Dict]]:
        """Divide los nodos en zonas geográficas"""
        clientes = [nodo for nodo in grafo['nodos'].values() if nodo.get('tipo') == 'cliente']
        
        if not clientes:
            return {}
        
        # Calcular centroide de todos los clientes
        centro_lat, centro_lon = self.calcular_centroide(clientes)
        
        # Dividir en zonas basándose en la distancia al centro
        zonas = {}
        for i in range(num_zonas):
            zonas[i] = []
        
        for cliente in clientes:
            distancia_centro = self.calcular_distancia(
                centro_lat, centro_lon,
                cliente['latitud'], cliente['longitud']
            )
            
            # Asignar a zona basándose en la distancia
            zona = min(int(distancia_centro / 5), num_zonas - 1)  # 5km por zona
            zonas[zona].append(cliente)
        
        return zonas
    
    def calcular_estadisticas_grafo(self, grafo: Dict) -> Dict:
        """Calcula estadísticas del grafo"""
        clientes = [nodo for nodo in grafo['nodos'].values() if nodo.get('tipo') == 'cliente']
        
        if not clientes:
            return {
                'total_clientes': 0,
                'distancia_promedio': 0,
                'prioridad_promedio': 0,
                'pedido_total': 0
            }
        
        # Calcular distancias promedio desde el depósito
        distancias_deposito = []
        for cliente in clientes:
            distancia = grafo['matriz_distancias']['deposito'][cliente['id']]
            distancias_deposito.append(distancia)
        
        return {
            'total_clientes': len(clientes),
            'distancia_promedio': sum(distancias_deposito) / len(distancias_deposito),
            'distancia_maxima': max(distancias_deposito),
            'distancia_minima': min(distancias_deposito),
            'prioridad_promedio': sum(c['prioridad'] for c in clientes) / len(clientes),
            'pedido_total': sum(c['pedido'] for c in clientes),
            'pedido_promedio': sum(c['pedido'] for c in clientes) / len(clientes)
        }
    
    def encontrar_ruta_mas_corta(self, grafo: Dict, origen: str, destino: str) -> Tuple[List[str], float]:
        """Encuentra la ruta más corta entre dos nodos usando Dijkstra"""
        if origen not in grafo['nodos'] or destino not in grafo['nodos']:
            return [], float('inf')
        
        # Implementación simplificada de Dijkstra
        distancias = {nodo_id: float('inf') for nodo_id in grafo['nodos']}
        predecesores = {nodo_id: None for nodo_id in grafo['nodos']}
        visitados = set()
        
        distancias[origen] = 0
        
        while visitados != set(grafo['nodos']):
            # Encontrar nodo no visitado con menor distancia
            nodo_actual = None
            min_distancia = float('inf')
            
            for nodo_id in grafo['nodos']:
                if nodo_id not in visitados and distancias[nodo_id] < min_distancia:
                    min_distancia = distancias[nodo_id]
                    nodo_actual = nodo_id
            
            if nodo_actual is None:
                break
            
            visitados.add(nodo_actual)
            
            # Actualizar distancias a vecinos
            for vecino_id in grafo['matriz_distancias'][nodo_actual]:
                if vecino_id not in visitados:
                    nueva_distancia = distancias[nodo_actual] + grafo['matriz_distancias'][nodo_actual][vecino_id]
                    if nueva_distancia < distancias[vecino_id]:
                        distancias[vecino_id] = nueva_distancia
                        predecesores[vecino_id] = nodo_actual
        
        # Reconstruir ruta
        ruta = []
        nodo_actual = destino
        while nodo_actual is not None:
            ruta.append(nodo_actual)
            nodo_actual = predecesores[nodo_actual]
        
        ruta.reverse()
        
        return ruta, distancias[destino]
    
    def validar_grafo(self, grafo: Dict) -> bool:
        """Valida que el grafo esté correctamente construido"""
        # Verificar que existe el depósito
        if 'deposito' not in grafo['nodos']:
            return False
        
        # Verificar que todos los nodos tienen coordenadas válidas
        for nodo_id, nodo in grafo['nodos'].items():
            if not (-90 <= nodo['latitud'] <= 90):
                return False
            if not (-180 <= nodo['longitud'] <= 180):
                return False
        
        # Verificar que la matriz de distancias es simétrica
        for origen in grafo['matriz_distancias']:
            for destino in grafo['matriz_distancias'][origen]:
                if origen != destino:
                    distancia_origen_destino = grafo['matriz_distancias'][origen][destino]
                    distancia_destino_origen = grafo['matriz_distancias'][destino][origen]
                    
                    # Permitir pequeñas diferencias por errores de redondeo
                    if abs(distancia_origen_destino - distancia_destino_origen) > 0.001:
                        return False
        
        return True 