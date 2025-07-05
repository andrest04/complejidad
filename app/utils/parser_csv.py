import csv
import io
from typing import List, Dict
import pandas as pd

class ParserCSV:
    """Clase para leer y procesar archivos CSV de clientes y rutas"""
    
    def __init__(self):
        self.columnas_esperadas = [
            'id', 'nombre', 'latitud', 'longitud', 'prioridad', 
            'ventana_inicio', 'ventana_fin', 'pedido'
        ]
        
    def leer_clientes_csv(self, archivo) -> List[Dict]:
        """Lee un archivo CSV y convierte los datos a formato de clientes"""
        try:
            # Leer el archivo CSV
            contenido = archivo.read()
            archivo.seek(0)  # Resetear el puntero del archivo
            
            # Si el contenido es bytes, decodificarlo
            if isinstance(contenido, bytes):
                contenido = contenido.decode('utf-8')
            
            # Usar pandas para manejar diferentes formatos de CSV
            df = pd.read_csv(io.StringIO(contenido))
            
            # Verificar columnas requeridas
            columnas_faltantes = set(self.columnas_esperadas) - set(df.columns)
            if columnas_faltantes:
                raise ValueError(f"Columnas faltantes en el CSV: {columnas_faltantes}")
            
            # Convertir DataFrame a lista de diccionarios
            clientes = []
            for index, row in df.iterrows():
                cliente = {
                    'id': str(row['id']),
                    'nombre': str(row['nombre']),
                    'latitud': float(row['latitud']),
                    'longitud': float(row['longitud']),
                    'prioridad': int(row['prioridad']),
                    'ventana_inicio': str(row['ventana_inicio']),
                    'ventana_fin': str(row['ventana_fin']),
                    'pedido': float(row['pedido'])
                }
                
                # Validar datos
                self.validar_cliente(cliente)
                clientes.append(cliente)
            
            return clientes
            
        except Exception as e:
            raise ValueError(f"Error al procesar archivo CSV: {str(e)}")
    
    def validar_cliente(self, cliente: Dict) -> bool:
        """Valida que los datos del cliente sean correctos"""
        # Validar coordenadas
        if not (-90 <= cliente['latitud'] <= 90):
            raise ValueError(f"Latitud inválida para cliente {cliente['id']}: {cliente['latitud']}")
        
        if not (-180 <= cliente['longitud'] <= 180):
            raise ValueError(f"Longitud inválida para cliente {cliente['id']}: {cliente['longitud']}")
        
        # Validar prioridad
        if not (1 <= cliente['prioridad'] <= 5):
            raise ValueError(f"Prioridad inválida para cliente {cliente['id']}: {cliente['prioridad']}")
        
        # Validar pedido
        if cliente['pedido'] <= 0:
            raise ValueError(f"Pedido inválido para cliente {cliente['id']}: {cliente['pedido']}")
        
        # Validar ventana horaria
        try:
            self.validar_ventana_horaria(cliente['ventana_inicio'], cliente['ventana_fin'])
        except Exception as e:
            raise ValueError(f"Ventana horaria inválida para cliente {cliente['id']}: {str(e)}")
        
        return True
    
    def validar_ventana_horaria(self, inicio: str, fin: str) -> bool:
        """Valida el formato de ventana horaria (HH:MM-HH:MM)"""
        try:
            # Verificar formato HH:MM
            def validar_hora(hora_str):
                if ':' not in hora_str:
                    raise ValueError("Formato de hora inválido")
                
                horas, minutos = hora_str.split(':')
                horas = int(horas)
                minutos = int(minutos)
                
                if not (0 <= horas <= 23):
                    raise ValueError("Horas deben estar entre 0 y 23")
                
                if not (0 <= minutos <= 59):
                    raise ValueError("Minutos deben estar entre 0 y 59")
                
                return horas * 60 + minutos  # Convertir a minutos
            
            inicio_minutos = validar_hora(inicio)
            fin_minutos = validar_hora(fin)
            
            if inicio_minutos >= fin_minutos:
                raise ValueError("Hora de inicio debe ser menor que hora de fin")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Error en ventana horaria: {str(e)}")
    
    def crear_csv_ejemplo(self) -> str:
        """Crea un ejemplo de CSV para que los usuarios sepan el formato"""
        ejemplo_csv = """id,nombre,latitud,longitud,prioridad,ventana_inicio,ventana_fin,pedido
1,Cliente A,-12.0464,-77.0428,1,08:00,12:00,150.5
2,Cliente B,-12.0564,-77.0328,2,09:00,17:00,200.0
3,Cliente C,-12.0364,-77.0528,3,10:00,16:00,75.25
4,Cliente D,-12.0664,-77.0228,1,08:30,11:30,300.0
5,Cliente E,-12.0264,-77.0628,4,14:00,18:00,125.75"""
        
        return ejemplo_csv
    
    def exportar_clientes_csv(self, clientes: List[Dict]) -> str:
        """Exporta la lista de clientes a formato CSV"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.columnas_esperadas)
        
        writer.writeheader()
        for cliente in clientes:
            writer.writerow(cliente)
        
        return output.getvalue()
    
    def leer_vehiculos_json(self, archivo) -> List[Dict]:
        """Lee un archivo JSON con información de vehículos"""
        try:
            import json
            contenido = archivo.read()
            
            # Si el contenido es bytes, decodificarlo
            if isinstance(contenido, bytes):
                contenido = contenido.decode('utf-8')
            
            vehiculos = json.loads(contenido)
            
            # Validar estructura
            if not isinstance(vehiculos, list):
                raise ValueError("El archivo JSON debe contener una lista de vehículos")
            
            for vehiculo in vehiculos:
                self.validar_vehiculo(vehiculo)
            
            return vehiculos
            
        except Exception as e:
            raise ValueError(f"Error al procesar archivo JSON de vehículos: {str(e)}")
    
    def validar_vehiculo(self, vehiculo: Dict) -> bool:
        """Valida que los datos del vehículo sean correctos"""
        campos_requeridos = ['placa', 'capacidad', 'tipo']
        
        for campo in campos_requeridos:
            if campo not in vehiculo:
                raise ValueError(f"Campo requerido faltante: {campo}")
        
        # Validar capacidad
        if not isinstance(vehiculo['capacidad'], (int, float)) or vehiculo['capacidad'] <= 0:
            raise ValueError(f"Capacidad inválida: {vehiculo['capacidad']}")
        
        # Validar tipo
        tipos_validos = ['Camión', 'Furgón', 'Camioneta', 'Moto']
        if vehiculo['tipo'] not in tipos_validos:
            raise ValueError(f"Tipo de vehículo inválido: {vehiculo['tipo']}")
        
        return True
    
    def crear_json_vehiculos_ejemplo(self) -> str:
        """Crea un ejemplo de JSON para vehículos"""
        import json
        
        ejemplo_vehiculos = [
            {
                "placa": "ABC-123",
                "capacidad": 1000,
                "tipo": "Camión"
            },
            {
                "placa": "XYZ-789",
                "capacidad": 500,
                "tipo": "Furgón"
            },
            {
                "placa": "DEF-456",
                "capacidad": 200,
                "tipo": "Camioneta"
            }
        ]
        
        return json.dumps(ejemplo_vehiculos, indent=2, ensure_ascii=False) 