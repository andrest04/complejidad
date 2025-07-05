from flask import Blueprint, request, jsonify, current_app

algoritmos_bp = Blueprint('algoritmos', __name__)

def get_datos_globales():
    return current_app.config['DATOS_GLOBALES']

@algoritmos_bp.route('/ejecutar_algoritmo', methods=['POST'])
def api_ejecutar_algoritmo():
    datos = get_datos_globales()
    BellmanFord = current_app.config['BELLMAN_FORD']
    ProgramacionDinamica = current_app.config['PROGRAMACION_DINAMICA']
    Backtracking = current_app.config['BACKTRACKING']
    try:
        data = request.get_json()
        algoritmo = data['algoritmo']
        if not datos['grafo']:
            return jsonify({'error': 'No hay datos cargados para optimizar'}), 400
        if not datos['vehiculos']:
            return jsonify({'error': 'No hay vehículos registrados'}), 400
        if algoritmo == 'bellman_ford':
            bellman = BellmanFord(datos['grafo'])
            resultados = bellman.optimizar_rutas(datos['clientes'], datos['vehiculos'])
        elif algoritmo == 'programacion_dinamica':
            pd = ProgramacionDinamica(datos['grafo'])
            resultados = pd.optimizar_rutas(datos['clientes'], datos['vehiculos'])
        elif algoritmo == 'backtracking':
            bt = Backtracking(datos['grafo'])
            resultados = bt.optimizar_rutas(datos['clientes'], datos['vehiculos'])
        else:
            return jsonify({'error': 'Algoritmo no válido'}), 400
        datos['resultados'] = resultados
        return jsonify({
            'success': True,
            'message': f'Algoritmo {algoritmo} ejecutado exitosamente',
            'resultados': resultados
        })
    except Exception as e:
        return jsonify({'error': f'Error al ejecutar algoritmo: {str(e)}'}), 500

@algoritmos_bp.route('/obtener_datos_mapa')
def api_obtener_datos_mapa():
    datos = get_datos_globales()
    mapa_utils = current_app.config['MAPA_UTILS']
    try:
        mapa_data = mapa_utils.obtener_datos_mapa(
            datos['clientes'],
            datos.get('resultados')
        )
        return jsonify(mapa_data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener datos del mapa: {str(e)}'}), 500

@algoritmos_bp.route('/estadisticas')
def api_estadisticas():
    datos = get_datos_globales()
    try:
        stats = {
            'total_clientes': len(datos['clientes']),
            'total_vehiculos': len(datos['vehiculos']),
            'vehiculos_disponibles': len([v for v in datos['vehiculos'] if v['disponible']]),
            'capacidad_total': sum(v['capacidad'] for v in datos['vehiculos']),
            'pedidos_total': sum(c['pedido'] for c in datos['clientes']),
            'tiene_resultados': datos.get('resultados') is not None
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'Error al obtener estadísticas: {str(e)}'}), 500 