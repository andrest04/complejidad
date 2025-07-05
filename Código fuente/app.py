from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algoritmos.bellman_ford import BellmanFord
from algoritmos.programacion_dinamica import ProgramacionDinamica
from algoritmos.backtracking import Backtracking
from utils.parser_csv import ParserCSV
from utils.grafo_builder import GrafoBuilder
from utils.mapa_utils import MapaUtils
from config import Config

app = Flask(__name__)

# Configuración
config = Config()
app.secret_key = config.SECRET_KEY

# Instancias de utilidades
parser_csv = ParserCSV()
grafo_builder = GrafoBuilder()
mapa_utils = MapaUtils()

# Datos globales de la aplicación
datos_globales = {
    'clientes': [],
    'vehiculos': [],
    'grafo': None,
    'resultados': None
}

def cargar_dataset_lima():
    """Carga automáticamente el dataset de 1500 clientes de Lima"""
    try:
        # Verificar si existe el archivo de 1500 clientes
        archivo_lima = "Dataset/clientes_lima_1500.csv"
        if os.path.exists(archivo_lima):
            with open(archivo_lima, 'r', encoding='utf-8') as f:
                # Simular un archivo para el parser
                class MockFile:
                    def __init__(self, content):
                        self.content = content
                        self.position = 0
                    
                    def read(self):
                        return self.content.encode('utf-8')
                    
                    def seek(self, pos):
                        self.position = pos
                
                mock_file = MockFile(f.read())
                clientes = parser_csv.leer_clientes_csv(mock_file)
                datos_globales['clientes'] = clientes
                datos_globales['grafo'] = grafo_builder.construir_grafo(clientes)
                print(f"Dataset de Lima cargado: {len(clientes)} clientes")
                return True
        else:
            print("Dataset de Lima no encontrado, usando dataset vacío")
            return False
    except Exception as e:
        print(f"Error al cargar dataset de Lima: {str(e)}")
        return False

# Cargar dataset al iniciar
cargar_dataset_lima()

@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html', 
                        clientes_count=len(datos_globales['clientes']),
                        vehiculos_count=len(datos_globales['vehiculos']))



@app.route('/registrar_vehiculos')
def registrar_vehiculos():
    """Página para registrar vehículos de la flota"""
    return render_template('registrar_vehiculos.html', 
                         vehiculos=datos_globales['vehiculos'])

@app.route('/gestionar_clientes')
def gestionar_clientes():
    """Página para gestionar clientes y pedidos"""
    return render_template('gestionar_clientes.html', 
                         clientes=datos_globales['clientes'])

@app.route('/ejecutar')
def ejecutar():
    """Página para ejecutar algoritmos de optimización"""
    return render_template('ejecutar.html')

@app.route('/resultados')
def resultados():
    """Página para mostrar resultados de optimización"""
    return render_template('resultados.html', 
                         resultados=datos_globales.get('resultados'))

# API Routes

@app.route('/api/registrar_vehiculo', methods=['POST'])
def api_registrar_vehiculo():
    """API para registrar un nuevo vehículo"""
    try:
        data = request.get_json()
        
        vehiculo = {
            'id': len(datos_globales['vehiculos']) + 1,
            'placa': data['placa'],
            'capacidad': float(data['capacidad']),
            'tipo': data['tipo'],
            'disponible': True,
            'fecha_registro': datetime.now().isoformat()
        }
        
        datos_globales['vehiculos'].append(vehiculo)
        
        return jsonify({
            'success': True,
            'message': 'Vehículo registrado exitosamente',
            'vehiculo': vehiculo
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al registrar vehículo: {str(e)}'}), 500

@app.route('/api/agregar_cliente', methods=['POST'])
def api_agregar_cliente():
    """API para agregar un nuevo cliente"""
    try:
        data = request.get_json()
        
        cliente = {
            'id': len(datos_globales['clientes']) + 1,
            'nombre': data['nombre'],
            'latitud': float(data['latitud']),
            'longitud': float(data['longitud']),
            'prioridad': int(data['prioridad']),
            'ventana_inicio': data['ventana_inicio'],
            'ventana_fin': data['ventana_fin'],
            'pedido': float(data['pedido'])
        }
        
        datos_globales['clientes'].append(cliente)
        
        # Reconstruir grafo si hay clientes
        if datos_globales['clientes']:
            datos_globales['grafo'] = grafo_builder.construir_grafo(datos_globales['clientes'])
        
        return jsonify({
            'success': True,
            'message': 'Cliente agregado exitosamente',
            'cliente': cliente
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al agregar cliente: {str(e)}'}), 500

@app.route('/api/ejecutar_algoritmo', methods=['POST'])
def api_ejecutar_algoritmo():
    """API para ejecutar algoritmos de optimización"""
    try:
        data = request.get_json()
        algoritmo = data['algoritmo']
        
        if not datos_globales['grafo']:
            return jsonify({'error': 'No hay datos cargados para optimizar'}), 400
        
        if not datos_globales['vehiculos']:
            return jsonify({'error': 'No hay vehículos registrados'}), 400
        
        # Ejecutar algoritmo seleccionado
        if algoritmo == 'bellman_ford':
            bellman = BellmanFord(datos_globales['grafo'])
            resultados = bellman.optimizar_rutas(datos_globales['clientes'], datos_globales['vehiculos'])
            
        elif algoritmo == 'programacion_dinamica':
            pd = ProgramacionDinamica(datos_globales['grafo'])
            resultados = pd.optimizar_rutas(datos_globales['clientes'], datos_globales['vehiculos'])
            
        elif algoritmo == 'backtracking':
            bt = Backtracking(datos_globales['grafo'])
            resultados = bt.optimizar_rutas(datos_globales['clientes'], datos_globales['vehiculos'])
            
        else:
            return jsonify({'error': 'Algoritmo no válido'}), 400
        
        datos_globales['resultados'] = resultados
        
        return jsonify({
            'success': True,
            'message': f'Algoritmo {algoritmo} ejecutado exitosamente',
            'resultados': resultados
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al ejecutar algoritmo: {str(e)}'}), 500

@app.route('/api/obtener_datos_mapa')
def api_obtener_datos_mapa():
    """API para obtener datos del mapa"""
    try:
        mapa_data = mapa_utils.obtener_datos_mapa(
            datos_globales['clientes'],
            datos_globales.get('resultados')
        )
        
        return jsonify(mapa_data)
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener datos del mapa: {str(e)}'}), 500

@app.route('/api/estadisticas')
def api_estadisticas():
    """API para obtener estadísticas generales"""
    try:
        stats = {
            'total_clientes': len(datos_globales['clientes']),
            'total_vehiculos': len(datos_globales['vehiculos']),
            'vehiculos_disponibles': len([v for v in datos_globales['vehiculos'] if v['disponible']]),
            'capacidad_total': sum(v['capacidad'] for v in datos_globales['vehiculos']),
            'pedidos_total': sum(c['pedido'] for c in datos_globales['clientes']),
            'tiene_resultados': datos_globales.get('resultados') is not None
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.PUERTO) 