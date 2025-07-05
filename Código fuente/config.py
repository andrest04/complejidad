import os

class Config:
    """Clase de configuración para la aplicación de optimización de rutas"""
    
    def __init__(self):

        self.SECRET_KEY = 'optimiza-rutas-2025-lima'

        # Configuración del servidor
        self.PUERTO = 5000
        self.HOST = '0.0.0.0'
        self.DEBUG = True
        
        # Configuración de archivos
        self.UPLOAD_FOLDER = 'uploads'
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
        
        # Configuración de mapas
        self.MAPA_CENTRO_LAT = -12.0464  # Lima, Perú
        self.MAPA_CENTRO_LNG = -77.0428
        self.MAPA_ZOOM = 12
        
        # Configuración de algoritmos
        self.TIEMPO_MAXIMO_EJECUCION = 300  # 5 minutos
        self.MAX_ITERACIONES = 10000
        
        # Configuración de rutas
        self.DEPOSITO_LAT = -12.0464  # Coordenadas del depósito central
        self.DEPOSITO_LNG = -77.0428
        self.DEPOSITO_NOMBRE = "Depósito Central"
        
        # Configuración de vehículos
        self.TIPOS_VEHICULO = ['Camión', 'Furgón', 'Camioneta', 'Moto']
        self.CAPACIDAD_MINIMA = 100  # kg
        self.CAPACIDAD_MAXIMA = 5000  # kg
        
        # Configuración de clientes
        self.PRIORIDADES = [1, 2, 3, 4, 5]  # 1 = más alta, 5 = más baja
        self.VENTANA_HORARIA_DEFAULT = "08:00-18:00"
        
        # Configuración de costos
        self.COSTO_POR_KM = 0.5  # Costo por kilómetro
        self.COSTO_POR_HORA = 25.0  # Costo por hora de trabajo
        self.COSTO_FIJO_VEHICULO = 100.0  # Costo fijo por vehículo
        
        # Configuración de restricciones
        self.TIEMPO_MAXIMO_RUTA = 480  # 8 horas en minutos
        self.DISTANCIA_MAXIMA_RUTA = 200  # km
        
        # Crear directorio de uploads si no existe
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER) 