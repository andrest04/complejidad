import os


class Config:

    def __init__(self):

        self.SECRET_KEY = "optimiza-rutas-2025-lima"

        self.PUERTO = 5000
        self.HOST = "0.0.0.0"
        self.DEBUG = True

        self.UPLOAD_FOLDER = "uploads"
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024

        self.MAPA_CENTRO_LAT = -12.0464
        self.MAPA_CENTRO_LNG = -77.0428
        self.MAPA_ZOOM = 12

        self.TIEMPO_MAXIMO_EJECUCION = 300
        self.MAX_ITERACIONES = 10000

        self.DEPOSITO_LAT = -12.0464
        self.DEPOSITO_LNG = -77.0428
        self.DEPOSITO_NOMBRE = "Depósito Central"

        self.TIPOS_VEHICULO = ["Camión", "Furgón", "Camioneta", "Moto"]
        self.CAPACIDAD_MINIMA = 100
        self.CAPACIDAD_MAXIMA = 5000

        self.PRIORIDADES = [1, 2, 3, 4, 5]
        self.VENTANA_HORARIA_DEFAULT = "08:00-18:00"

        self.COSTO_POR_KM = 0.5
        self.COSTO_POR_HORA = 25.0
        self.COSTO_FIJO_VEHICULO = 100.0

        self.TIEMPO_MAXIMO_RUTA = 480
        self.DISTANCIA_MAXIMA_RUTA = 200

        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER)
