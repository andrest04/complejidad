import math
from typing import Dict, List, Tuple, Optional

class MapaUtils:
    """Clase para manejar utilidades relacionadas con mapas y visualización"""
    
    def __init__(self):
        self.centro_lima = (-12.0464, -77.0428)
        self.zoom_default = 12
        
    def obtener_datos_mapa(self, clientes: List[Dict], resultados: Optional[Dict] = None) -> Dict:
        """Obtiene todos los datos necesarios para renderizar el mapa"""
        datos_mapa = {
            'centro': {
                'lat': self.centro_lima[0],
                'lng': self.centro_lima[1],
                'zoom': self.zoom_default
            },
            'deposito': {
                'id': 'deposito',
                'nombre': 'Depósito Central',
                'lat': self.centro_lima[0],
                'lng': self.centro_lima[1],
                'tipo': 'deposito',
                'icon': 'warehouse'
            },
            'clientes': [],
            'rutas': [],
            'capas': {
                'congestion': self.generar_capa_congestion(clientes),
                'zonas_criticas': self.generar_zonas_criticas(clientes),
                'prioridades': self.generar_capa_prioridades(clientes)
            }
        }
        
        # Agregar clientes
        for cliente in clientes:
            datos_mapa['clientes'].append({
                'id': cliente['id'],
                'nombre': cliente['nombre'],
                'lat': cliente['latitud'],
                'lng': cliente['longitud'],
                'prioridad': cliente['prioridad'],
                'pedido': cliente['pedido'],
                'ventana_inicio': cliente['ventana_inicio'],
                'ventana_fin': cliente['ventana_fin'],
                'color': self.obtener_color_prioridad(cliente['prioridad']),
                'icon': 'store'
            })
        
        # Agregar rutas si hay resultados
        if resultados and 'rutas' in resultados:
            datos_mapa['rutas'] = self.generar_datos_rutas(resultados['rutas'])
        
        return datos_mapa
    
    def generar_datos_rutas(self, rutas: List[Dict]) -> List[Dict]:
        """Genera los datos de las rutas para el mapa"""
        datos_rutas = []
        
        for i, ruta in enumerate(rutas):
            ruta_mapa = {
                'id': f"ruta_{i+1}",
                'vehiculo_id': ruta['vehiculo_id'],
                'placa': ruta['placa'],
                'color': self.obtener_color_ruta(i),
                'coordenadas': [],
                'clientes': [],
                'distancia_total': ruta['distancia_total'],
                'tiempo_estimado': ruta['tiempo_estimado'],
                'carga_total': ruta['carga_total']
            }
            
            # Agregar coordenadas de la ruta
            coordenadas = []
            
            # Empezar desde el depósito
            coordenadas.append([self.centro_lima[0], self.centro_lima[1]])
            
            # Agregar clientes en orden
            for cliente in ruta['clientes']:
                coordenadas.append([cliente['latitud'], cliente['longitud']])
                ruta_mapa['clientes'].append({
                    'id': cliente['id'],
                    'nombre': cliente['nombre'],
                    'lat': cliente['latitud'],
                    'lng': cliente['longitud']
                })
            
            # Regresar al depósito
            coordenadas.append([self.centro_lima[0], self.centro_lima[1]])
            
            ruta_mapa['coordenadas'] = coordenadas
            datos_rutas.append(ruta_mapa)
        
        return datos_rutas
    
    def generar_capa_congestion(self, clientes: List[Dict]) -> List[Dict]:
        """Genera capa de congestión basada en densidad de clientes"""
        zonas_congestion = []
        
        # Dividir el área en cuadrículas
        grid_size = 0.01  # Aproximadamente 1km
        
        # Encontrar límites del área
        lats = [cliente['latitud'] for cliente in clientes]
        lngs = [cliente['longitud'] for cliente in clientes]
        
        if not lats or not lngs:
            return zonas_congestion
        
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        
        # Crear cuadrícula
        for lat in range(int(min_lat * 100), int(max_lat * 100) + 1):
            for lng in range(int(min_lng * 100), int(max_lng * 100) + 1):
                lat_centro = lat / 100
                lng_centro = lng / 100
                
                # Contar clientes en esta cuadrícula
                clientes_en_zona = 0
                for cliente in clientes:
                    if (abs(cliente['latitud'] - lat_centro) < grid_size/2 and 
                        abs(cliente['longitud'] - lng_centro) < grid_size/2):
                        clientes_en_zona += 1
                
                if clientes_en_zona > 0:
                    intensidad = min(clientes_en_zona / 3, 1.0)  # Normalizar a 0-1
                    zonas_congestion.append({
                        'lat': lat_centro,
                        'lng': lng_centro,
                        'intensidad': intensidad,
                        'clientes_count': clientes_en_zona
                    })
        
        return zonas_congestion
    
    def generar_zonas_criticas(self, clientes: List[Dict]) -> List[Dict]:
        """Genera zonas críticas basadas en prioridad y pedidos"""
        zonas_criticas = []
        
        # Agrupar clientes por proximidad y prioridad
        clientes_prioridad_alta = [c for c in clientes if c['prioridad'] <= 2]
        
        for cliente in clientes_prioridad_alta:
            # Crear zona crítica alrededor del cliente
            radio = 0.005  # Aproximadamente 500m
            
            zona = {
                'lat': cliente['latitud'],
                'lng': cliente['longitud'],
                'radio': radio,
                'prioridad': cliente['prioridad'],
                'pedido': cliente['pedido'],
                'color': self.obtener_color_prioridad(cliente['prioridad'])
            }
            
            zonas_criticas.append(zona)
        
        return zonas_criticas
    
    def generar_capa_prioridades(self, clientes: List[Dict]) -> Dict[int, List[Dict]]:
        """Genera capa de prioridades agrupando clientes por nivel de prioridad"""
        capa_prioridades = {}
        
        for prioridad in range(1, 6):
            clientes_prioridad = [c for c in clientes if c['prioridad'] == prioridad]
            
            if clientes_prioridad:
                capa_prioridades[prioridad] = []
                
                for cliente in clientes_prioridad:
                    capa_prioridades[prioridad].append({
                        'id': cliente['id'],
                        'nombre': cliente['nombre'],
                        'lat': cliente['latitud'],
                        'lng': cliente['longitud'],
                        'pedido': cliente['pedido'],
                        'color': self.obtener_color_prioridad(prioridad)
                    })
        
        return capa_prioridades
    
    def obtener_color_prioridad(self, prioridad: int) -> str:
        """Obtiene el color correspondiente a una prioridad"""
        colores = {
            1: '#FF0000',  # Rojo - Prioridad más alta
            2: '#FF6600',  # Naranja
            3: '#FFCC00',  # Amarillo
            4: '#00CC00',  # Verde
            5: '#0066CC'   # Azul - Prioridad más baja
        }
        return colores.get(prioridad, '#999999')
    
    def obtener_color_ruta(self, indice: int) -> str:
        """Obtiene el color para una ruta específica"""
        colores_rutas = [
            '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF',
            '#00FFFF', '#FF6600', '#6600FF', '#FF0066', '#66FF00'
        ]
        return colores_rutas[indice % len(colores_rutas)]
    
    def calcular_bounds_mapa(self, clientes: List[Dict]) -> Dict:
        """Calcula los límites del mapa para ajustar la vista"""
        if not clientes:
            return {
                'south': self.centro_lima[0] - 0.1,
                'north': self.centro_lima[0] + 0.1,
                'west': self.centro_lima[1] - 0.1,
                'east': self.centro_lima[1] + 0.1
            }
        
        lats = [cliente['latitud'] for cliente in clientes]
        lngs = [cliente['longitud'] for cliente in clientes]
        
        # Agregar depósito
        lats.append(self.centro_lima[0])
        lngs.append(self.centro_lima[1])
        
        # Agregar margen
        margin = 0.01
        
        return {
            'south': min(lats) - margin,
            'north': max(lats) + margin,
            'west': min(lngs) - margin,
            'east': max(lngs) + margin
        }
    
    def generar_marcadores_cluster(self, clientes: List[Dict]) -> List[Dict]:
        """Genera marcadores agrupados para mejorar el rendimiento del mapa"""
        clusters = {}
        cluster_size = 0.005  # Aproximadamente 500m
        
        for cliente in clientes:
            # Redondear coordenadas para crear clusters
            lat_cluster = round(cliente['latitud'] / cluster_size) * cluster_size
            lng_cluster = round(cliente['longitud'] / cluster_size) * cluster_size
            
            cluster_key = f"{lat_cluster}_{lng_cluster}"
            
            if cluster_key not in clusters:
                clusters[cluster_key] = {
                    'lat': lat_cluster,
                    'lng': lng_cluster,
                    'clientes': [],
                    'count': 0
                }
            
            clusters[cluster_key]['clientes'].append(cliente)
            clusters[cluster_key]['count'] += 1
        
        # Convertir clusters a formato de marcadores
        marcadores = []
        for cluster in clusters.values():
            if cluster['count'] == 1:
                # Cliente individual
                cliente = cluster['clientes'][0]
                marcadores.append({
                    'type': 'individual',
                    'lat': cliente['latitud'],
                    'lng': cliente['longitud'],
                    'cliente': cliente
                })
            else:
                # Cluster de múltiples clientes
                marcadores.append({
                    'type': 'cluster',
                    'lat': cluster['lat'],
                    'lng': cluster['lng'],
                    'count': cluster['count'],
                    'clientes': cluster['clientes']
                })
        
        return marcadores
    
    def generar_heatmap_data(self, clientes: List[Dict]) -> List[List[float]]:
        """Genera datos para un mapa de calor basado en prioridad y pedidos"""
        heatmap_data = []
        
        for cliente in clientes:
            # Calcular intensidad basada en prioridad y pedido
            intensidad_prioridad = (6 - cliente['prioridad']) / 5  # 1 = más alta, 5 = más baja
            intensidad_pedido = min(cliente['pedido'] / 1000, 1.0)  # Normalizar pedido
            
            intensidad_total = (intensidad_prioridad + intensidad_pedido) / 2
            
            heatmap_data.append([
                cliente['latitud'],
                cliente['longitud'],
                intensidad_total
            ])
        
        return heatmap_data
    
    def generar_geojson_rutas(self, rutas: List[Dict]) -> Dict:
        """Genera formato GeoJSON para las rutas"""
        features = []
        
        for i, ruta in enumerate(rutas):
            # Crear línea de la ruta
            coordinates = []
            
            # Empezar desde depósito
            coordinates.append([self.centro_lima[1], self.centro_lima[0]])  # GeoJSON usa [lng, lat]
            
            # Agregar clientes
            for cliente in ruta['clientes']:
                coordinates.append([cliente['longitud'], cliente['latitud']])
            
            # Regresar al depósito
            coordinates.append([self.centro_lima[1], self.centro_lima[0]])
            
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': coordinates
                },
                'properties': {
                    'ruta_id': f"ruta_{i+1}",
                    'vehiculo_id': ruta['vehiculo_id'],
                    'placa': ruta['placa'],
                    'distancia_total': ruta['distancia_total'],
                    'tiempo_estimado': ruta['tiempo_estimado'],
                    'carga_total': ruta['carga_total'],
                    'color': self.obtener_color_ruta(i)
                }
            }
            
            features.append(feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features
        } 