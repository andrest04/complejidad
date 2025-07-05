import csv
import json
from typing import Dict, List
from collections import Counter
import statistics

class AnalizadorDataset:
    """Analizador del dataset de Lima para generar estadísticas detalladas"""
    
    def __init__(self, archivo_csv: str = "Dataset/clientes_lima_1500.csv"):
        self.archivo_csv = archivo_csv
        self.clientes = []
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos del CSV"""
        try:
            with open(self.archivo_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.clientes = list(reader)
            print(f"Datos cargados: {len(self.clientes)} clientes")
        except Exception as e:
            print(f"Error al cargar datos: {e}")
    
    def generar_estadisticas_basicas(self) -> Dict:
        """Genera estadísticas básicas del dataset"""
        if not self.clientes:
            return {}
        
        pedidos = [float(c['pedido']) for c in self.clientes]
        prioridades = [int(c['prioridad']) for c in self.clientes]
        distritos = [c.get('distrito', '') for c in self.clientes if c.get('distrito')]
        
        stats = {
            'total_clientes': len(self.clientes),
            'pedido_total': round(sum(pedidos), 2),
            'pedido_promedio': round(statistics.mean(pedidos), 2),
            'pedido_mediana': round(statistics.median(pedidos), 2),
            'pedido_maximo': round(max(pedidos), 2),
            'pedido_minimo': round(min(pedidos), 2),
            'pedido_desviacion': round(statistics.stdev(pedidos) if len(pedidos) > 1 else 0, 2),
            'prioridad_promedio': round(statistics.mean(prioridades), 2),
            'distritos_unicos': len(set(distritos)),
            'distribucion_prioridades': dict(Counter(prioridades)),
            'distribucion_distritos': dict(Counter(distritos))
        }
        
        return stats
    
    def generar_analisis_geografico(self) -> Dict:
        """Genera análisis geográfico del dataset"""
        if not self.clientes:
            return {}
        
        lats = [float(c['latitud']) for c in self.clientes]
        lngs = [float(c['longitud']) for c in self.clientes]
        
        # Calcular centroide
        centro_lat = statistics.mean(lats)
        centro_lng = statistics.mean(lngs)
        
        # Calcular límites
        limites = {
            'norte': max(lats),
            'sur': min(lats),
            'este': max(lngs),
            'oeste': min(lngs)
        }
        
        # Calcular área aproximada (en grados cuadrados)
        area_grados = (limites['norte'] - limites['sur']) * (limites['este'] - limites['oeste'])
        
        # Convertir a km² (aproximadamente)
        area_km2 = area_grados * 111 * 111  # 1 grado ≈ 111 km
        
        return {
            'centroide': {
                'latitud': round(centro_lat, 4),
                'longitud': round(centro_lng, 4)
            },
            'limites': {k: round(v, 4) for k, v in limites.items()},
            'area_grados': round(area_grados, 6),
            'area_km2': round(area_km2, 2),
            'densidad_clientes_km2': round(len(self.clientes) / area_km2, 2)
        }
    
    def generar_analisis_temporal(self) -> Dict:
        """Genera análisis de las ventanas temporales"""
        if not self.clientes:
            return {}
        
        # Analizar horas de inicio
        horas_inicio = []
        horas_fin = []
        duraciones = []
        
        for cliente in self.clientes:
            inicio = cliente['ventana_inicio']
            fin = cliente['ventana_fin']
            
            # Convertir a minutos desde medianoche
            h_inicio, m_inicio = map(int, inicio.split(':'))
            h_fin, m_fin = map(int, fin.split(':'))
            
            minutos_inicio = h_inicio * 60 + m_inicio
            minutos_fin = h_fin * 60 + m_fin
            
            horas_inicio.append(minutos_inicio)
            horas_fin.append(minutos_fin)
            
            # Calcular duración
            if minutos_fin > minutos_inicio:
                duracion = minutos_fin - minutos_inicio
            else:
                duracion = (24 * 60 - minutos_inicio) + minutos_fin
            
            duraciones.append(duracion)
        
        return {
            'hora_inicio_promedio': round(statistics.mean(horas_inicio) / 60, 2),
            'hora_fin_promedio': round(statistics.mean(horas_fin) / 60, 2),
            'duracion_promedio_horas': round(statistics.mean(duraciones) / 60, 2),
            'duracion_minima_horas': round(min(duraciones) / 60, 2),
            'duracion_maxima_horas': round(max(duraciones) / 60, 2),
            'distribucion_horas_inicio': self.agrupar_por_horas(horas_inicio),
            'distribucion_horas_fin': self.agrupar_por_horas(horas_fin)
        }
    
    def agrupar_por_horas(self, minutos_list: List[int]) -> Dict:
        """Agrupa los minutos en horas"""
        horas = [m // 60 for m in minutos_list]
        return dict(Counter(horas))
    
    def generar_analisis_por_distrito(self) -> Dict:
        """Genera análisis detallado por distrito"""
        if not self.clientes:
            return {}
        
        distritos_data = {}
        
        for cliente in self.clientes:
            distrito = cliente.get('distrito', 'Sin distrito')
            
            if distrito not in distritos_data:
                distritos_data[distrito] = {
                    'clientes': [],
                    'pedido_total': 0,
                    'prioridades': []
                }
            
            distritos_data[distrito]['clientes'].append(cliente)
            distritos_data[distrito]['pedido_total'] += float(cliente['pedido'])
            distritos_data[distrito]['prioridades'].append(int(cliente['prioridad']))
        
        # Calcular estadísticas por distrito
        analisis_distritos = {}
        for distrito, data in distritos_data.items():
            prioridades = data['prioridades']
            pedido_total = data['pedido_total']
            
            analisis_distritos[distrito] = {
                'total_clientes': len(data['clientes']),
                'pedido_total': round(pedido_total, 2),
                'pedido_promedio': round(pedido_total / len(data['clientes']), 2),
                'prioridad_promedio': round(statistics.mean(prioridades), 2),
                'distribucion_prioridades': dict(Counter(prioridades)),
                'porcentaje_total': round(len(data['clientes']) / len(self.clientes) * 100, 2)
            }
        
        return analisis_distritos
    
    def generar_reporte_completo(self) -> Dict:
        """Genera un reporte completo del dataset"""
        return {
            'estadisticas_basicas': self.generar_estadisticas_basicas(),
            'analisis_geografico': self.generar_analisis_geografico(),
            'analisis_temporal': self.generar_analisis_temporal(),
            'analisis_por_distrito': self.generar_analisis_por_distrito(),
            'metadata': {
                'archivo': self.archivo_csv,
                'fecha_analisis': '2024-01-01',
                'version': '1.0'
            }
        }
    
    def guardar_reporte_json(self, archivo: str = "Dataset/reporte_lima_1500.json"):
        """Guarda el reporte en formato JSON"""
        reporte = self.generar_reporte_completo()
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"Reporte guardado en {archivo}")
    
    def imprimir_resumen(self):
        """Imprime un resumen del análisis"""
        stats = self.generar_estadisticas_basicas()
        geo = self.generar_analisis_geografico()
        
        print("\n" + "="*60)
        print("ANÁLISIS DEL DATASET DE LIMA, PERÚ")
        print("="*60)
        
        print(f"\n📊 ESTADÍSTICAS BÁSICAS:")
        print(f"   • Total de clientes: {stats['total_clientes']}")
        print(f"   • Pedido total: {stats['pedido_total']} kg")
        print(f"   • Pedido promedio: {stats['pedido_promedio']} kg")
        print(f"   • Pedido máximo: {stats['pedido_maximo']} kg")
        print(f"   • Pedido mínimo: {stats['pedido_minimo']} kg")
        print(f"   • Prioridad promedio: {stats['prioridad_promedio']}")
        print(f"   • Distritos únicos: {stats['distritos_unicos']}")
        
        print(f"\n🗺️  ANÁLISIS GEOGRÁFICO:")
        print(f"   • Centroide: {geo['centroide']['latitud']}, {geo['centroide']['longitud']}")
        print(f"   • Área cubierta: {geo['area_km2']} km²")
        print(f"   • Densidad: {geo['densidad_clientes_km2']} clientes/km²")
        
        print(f"\n📈 DISTRIBUCIÓN POR PRIORIDADES:")
        for prioridad, cantidad in sorted(stats['distribucion_prioridades'].items()):
            porcentaje = (cantidad / stats['total_clientes']) * 100
            print(f"   • Prioridad {prioridad}: {cantidad} clientes ({porcentaje:.1f}%)")
        
        print(f"\n🏘️  TOP 10 DISTRITOS CON MÁS CLIENTES:")
        distritos_ordenados = sorted(
            stats['distribucion_distritos'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        for distrito, cantidad in distritos_ordenados:
            porcentaje = (cantidad / stats['total_clientes']) * 100
            print(f"   • {distrito}: {cantidad} clientes ({porcentaje:.1f}%)")
        
        print("\n" + "="*60)

def main():
    """Función principal"""
    analizador = AnalizadorDataset()
    analizador.imprimir_resumen()
    analizador.guardar_reporte_json()

if __name__ == "__main__":
    main() 