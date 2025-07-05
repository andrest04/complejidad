import random
import csv
from typing import List, Dict
import math

class GeneradorDatosLima:
    """Generador de datos sintéticos para Lima, Perú"""
    
    def __init__(self):
        # Centro de Lima (Plaza Mayor)
        self.centro_lima = (-12.0464, -77.0428)
        
        # Límites aproximados del área metropolitana de Lima
        self.limites_lima = {
            'norte': -11.8,   # Comas, Los Olivos
            'sur': -12.5,     # Villa El Salvador, Lurín
            'este': -76.8,    # Chaclacayo, Chosica
            'oeste': -77.2    # Callao, La Punta
        }
        
        # Nombres de lugares reales de Lima organizados por categorías
        self.lugares_lima = {
            'supermercados': [
                'Supermercado Metro', 'Plaza Vea', 'Wong', 'Tottus', 'Vivanda', 'Santa Isabel',
                'Supermercado Peruanito', 'Supermercado El Ahorro', 'Supermercado El Rey',
                'Supermercado El Súper', 'Supermercado El Tigre', 'Supermercado El Triunfo'
            ],
            'farmacias': [
                'Farmacia InkaFarma', 'Farmacia Boticas', 'Farmacia Mifarma', 'Farmacia Arcángel',
                'Farmacia San Pablo', 'Farmacia Universal', 'Farmacia Cruz Verde',
                'Farmacia El Ahorro', 'Farmacia El Rey', 'Farmacia El Súper'
            ],
            'centros_comerciales': [
                'Centro Comercial Jockey Plaza', 'Centro Comercial Larcomar', 'Centro Comercial MegaPlaza',
                'Centro Comercial Plaza San Miguel', 'Centro Comercial Plaza Norte', 'Centro Comercial Mall Aventura',
                'Centro Comercial Real Plaza', 'Centro Comercial Plaza Lima Sur', 'Centro Comercial Open Plaza',
                'Centro Comercial Plaza Central', 'Centro Comercial Plaza Bellavista'
            ],
            'restaurantes': [
                'Restaurante La Mar', 'Restaurante Central', 'Restaurante Maido', 'Restaurante Osaka',
                'Restaurante Rafael', 'Restaurante El Mercado', 'Restaurante Amaz',
                'Restaurante El Rincón del Ceviche', 'Restaurante La Picantería', 'Restaurante El Chinito'
            ],
            'hoteles': [
                'Hotel Sheraton', 'Hotel Marriott', 'Hotel Hilton', 'Hotel Westin',
                'Hotel JW Marriott', 'Hotel Belmond', 'Hotel Country Club',
                'Hotel Sonesta', 'Hotel Wyndham', 'Hotel Radisson'
            ],
            'universidades': [
                'Universidad Católica', 'Universidad San Marcos', 'Universidad de Lima',
                'Universidad San Martín', 'Universidad Ricardo Palma', 'Universidad del Pacífico',
                'Universidad ESAN', 'Universidad UPC', 'Universidad Científica del Sur',
                'Universidad Privada del Norte'
            ],
            'hospitales': [
                'Hospital Edgardo Rebagliati', 'Clínica Anglo Americana', 'Clínica Delgado',
                'Hospital Nacional Dos de Mayo', 'Hospital María Auxiliadora',
                'Clínica San Borja', 'Clínica Ricardo Palma', 'Clínica Internacional',
                'Hospital Alberto Sabogal', 'Clínica San Felipe'
            ],
            'parques': [
                'Parque Kennedy', 'Parque de la Reserva', 'Parque de la Exposición',
                'Parque El Olivar', 'Parque de las Leyendas', 'Parque Reducto',
                'Parque de la Amistad', 'Parque de la Pera', 'Parque de la Media Luna',
                'Parque de la Familia'
            ],
            'plazas': [
                'Plaza Mayor de Lima', 'Plaza San Martín', 'Plaza Dos de Mayo',
                'Plaza Bolognesi', 'Plaza Grau', 'Plaza Francia',
                'Plaza de Acho', 'Plaza de la Bandera', 'Plaza de la Democracia',
                'Plaza de la Revolución'
            ],
            'establecimientos': [
                'Estadio Nacional', 'Aeropuerto Jorge Chávez', 'Centro Financiero',
                'Mercado Central', 'Mercado de Surquillo', 'Mercado de Magdalena',
                'Mercado de San Isidro', 'Mercado de Miraflores', 'Mercado de Barranco',
                'Mercado de Chorrillos'
            ]
        }
        
        # Barrios y distritos de Lima
        self.distritos_lima = [
            'Miraflores', 'San Isidro', 'Barranco', 'Surco', 'San Borja', 'La Molina',
            'Santiago de Surco', 'Chorrillos', 'San Miguel', 'Magdalena', 'Pueblo Libre',
            'Jesús María', 'Lince', 'Breña', 'La Victoria', 'San Luis', 'El Agustino',
            'Ate', 'Lurigancho', 'Chaclacayo', 'Chosica', 'San Juan de Lurigancho',
            'Comas', 'Los Olivos', 'San Martín de Porres', 'Independencia', 'Rímac',
            'San Juan de Miraflores', 'Villa María del Triunfo', 'Villa El Salvador',
            'Lurín', 'Pachacámac', 'Callao', 'La Punta', 'Bellavista', 'Carmen de la Legua',
            'Ventanilla', 'Mi Perú', 'Ancón', 'Santa Rosa', 'Puente Piedra', 'Carabayllo'
        ]
    
    def generar_coordenadas_lima(self) -> tuple:
        """Genera coordenadas aleatorias dentro del área metropolitana de Lima"""
        lat = random.uniform(self.limites_lima['sur'], self.limites_lima['norte'])
        lng = random.uniform(self.limites_lima['este'], self.limites_lima['oeste'])
        return (lat, lng)
    
    def generar_coordenadas_distrito(self, distrito: str) -> tuple:
        """Genera coordenadas específicas para un distrito"""
        # Coordenadas aproximadas de algunos distritos principales
        coordenadas_distritos = {
            'Miraflores': (-12.1200, -77.0300),
            'San Isidro': (-12.1000, -77.0400),
            'Barranco': (-12.1400, -77.0200),
            'Surco': (-12.1600, -77.0000),
            'San Borja': (-12.0800, -77.0000),
            'La Molina': (-12.0800, -76.9500),
            'San Miguel': (-12.0600, -77.0800),
            'Magdalena': (-12.0800, -77.0700),
            'Pueblo Libre': (-12.0700, -77.0600),
            'Jesús María': (-12.0600, -77.0500),
            'Lince': (-12.0800, -77.0500),
            'Breña': (-12.0500, -77.0500),
            'La Victoria': (-12.0700, -77.0300),
            'San Luis': (-12.0900, -77.0200),
            'El Agustino': (-12.0500, -77.0200),
            'Ate': (-12.0500, -76.9500),
            'Comas': (-11.9500, -77.0500),
            'Los Olivos': (-11.9800, -77.0700),
            'San Martín de Porres': (-12.0000, -77.0500),
            'Independencia': (-11.9900, -77.0300),
            'Rímac': (-12.0300, -77.0200),
            'Callao': (-12.0500, -77.1500),
            'La Punta': (-12.0700, -77.1700),
            'Bellavista': (-12.0600, -77.1300),
            'Carmen de la Legua': (-12.0400, -77.1200),
            'Ventanilla': (-11.9000, -77.2000),
            'Ancón': (-11.7500, -77.1500),
            'Puente Piedra': (-11.8500, -77.1000),
            'Carabayllo': (-11.9000, -77.0500)
        }
        
        if distrito in coordenadas_distritos:
            centro_lat, centro_lng = coordenadas_distritos[distrito]
            # Agregar variación de ±0.01 grados (aproximadamente ±1km)
            lat = centro_lat + random.uniform(-0.01, 0.01)
            lng = centro_lng + random.uniform(-0.01, 0.01)
            return (lat, lng)
        else:
            return self.generar_coordenadas_lima()
    
    def generar_nombre_cliente(self) -> str:
        """Genera un nombre de cliente basado en lugares reales de Lima"""
        categoria = random.choice(list(self.lugares_lima.keys()))
        nombre_base = random.choice(self.lugares_lima[categoria])
        
        # Agregar variaciones para evitar duplicados
        variaciones = [
            f"{nombre_base} - {random.choice(self.distritos_lima)}",
            f"{nombre_base} Express",
            f"{nombre_base} Plus",
            f"{nombre_base} Premium",
            f"{nombre_base} {random.randint(1, 5)}",
            f"{nombre_base} {random.choice(['Norte', 'Sur', 'Este', 'Oeste'])}",
            f"{nombre_base} {random.choice(['Principal', 'Secundario', 'Terciario'])}"
        ]
        
        return random.choice(variaciones)
    
    def generar_ventana_tiempo(self) -> tuple:
        """Genera una ventana de tiempo realista"""
        horas_inicio = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        hora_inicio = random.choice(horas_inicio)
        duracion = random.choice([2, 3, 4, 6, 8, 12])  # horas
        hora_fin = min(23, hora_inicio + duracion)
        
        return (f"{hora_inicio:02d}:00", f"{hora_fin:02d}:00")
    
    def generar_prioridad(self) -> int:
        """Genera una prioridad basada en distribución realista"""
        # Distribución: 20% prioridad 1, 30% prioridad 2, 25% prioridad 3, 15% prioridad 4, 10% prioridad 5
        rand = random.random()
        if rand < 0.20:
            return 1
        elif rand < 0.50:
            return 2
        elif rand < 0.75:
            return 3
        elif rand < 0.90:
            return 4
        else:
            return 5
    
    def generar_pedido(self, prioridad: int) -> float:
        """Genera un pedido basado en la prioridad"""
        # Pedidos más grandes para prioridades más altas
        if prioridad == 1:
            return random.uniform(200, 500)  # 200-500 kg
        elif prioridad == 2:
            return random.uniform(150, 400)  # 150-400 kg
        elif prioridad == 3:
            return random.uniform(100, 300)  # 100-300 kg
        elif prioridad == 4:
            return random.uniform(50, 200)   # 50-200 kg
        else:
            return random.uniform(25, 150)   # 25-150 kg
    
    def generar_cliente(self, id_cliente: int) -> Dict:
        """Genera un cliente completo"""
        distrito = random.choice(self.distritos_lima)
        lat, lng = self.generar_coordenadas_distrito(distrito)
        prioridad = self.generar_prioridad()
        ventana_inicio, ventana_fin = self.generar_ventana_tiempo()
        pedido = self.generar_pedido(prioridad)
        
        return {
            'id': id_cliente,
            'nombre': self.generar_nombre_cliente(),
            'latitud': round(lat, 4),
            'longitud': round(lng, 4),
            'prioridad': prioridad,
            'ventana_inicio': ventana_inicio,
            'ventana_fin': ventana_fin,
            'pedido': round(pedido, 2),
            'distrito': distrito
        }
    
    def generar_dataset_completo(self, num_clientes: int = 1500) -> List[Dict]:
        """Genera el dataset completo de clientes"""
        clientes = []
        
        print(f"Generando {num_clientes} clientes para Lima, Perú...")
        
        for i in range(1, num_clientes + 1):
            cliente = self.generar_cliente(i)
            clientes.append(cliente)
            
            if i % 100 == 0:
                print(f"Generados {i} clientes...")
        
        print(f"Dataset generado exitosamente con {len(clientes)} clientes")
        return clientes
    
    def guardar_csv(self, clientes: List[Dict], archivo: str = "clientes_lima_1500.csv"):
        """Guarda los clientes en un archivo CSV"""
        with open(archivo, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'nombre', 'latitud', 'longitud', 'prioridad', 'ventana_inicio', 'ventana_fin', 'pedido', 'distrito']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for cliente in clientes:
                writer.writerow(cliente)
        
        print(f"Dataset guardado en {archivo}")
    
    def generar_estadisticas(self, clientes: List[Dict]) -> Dict:
        """Genera estadísticas del dataset"""
        total_pedidos = sum(c['pedido'] for c in clientes)
        prioridades = [c['prioridad'] for c in clientes]
        pedidos = [c['pedido'] for c in clientes]
        
        return {
            'total_clientes': len(clientes),
            'pedido_total': round(total_pedidos, 2),
            'pedido_promedio': round(total_pedidos / len(clientes), 2),
            'pedido_maximo': round(max(pedidos), 2),
            'pedido_minimo': round(min(pedidos), 2),
            'distribucion_prioridades': {
                1: prioridades.count(1),
                2: prioridades.count(2),
                3: prioridades.count(3),
                4: prioridades.count(4),
                5: prioridades.count(5)
            },
            'distritos_unicos': len(set(c['distrito'] for c in clientes))
        }

def main():
    """Función principal para generar el dataset"""
    generador = GeneradorDatosLima()
    
    # Generar 1500 clientes
    clientes = generador.generar_dataset_completo(1500)
    
    # Guardar en CSV
    generador.guardar_csv(clientes, "Dataset/clientes_lima_1500.csv")
    
    # Mostrar estadísticas
    stats = generador.generar_estadisticas(clientes)
    print("\n=== ESTADÍSTICAS DEL DATASET ===")
    print(f"Total de clientes: {stats['total_clientes']}")
    print(f"Pedido total: {stats['pedido_total']} kg")
    print(f"Pedido promedio: {stats['pedido_promedio']} kg")
    print(f"Pedido máximo: {stats['pedido_maximo']} kg")
    print(f"Pedido mínimo: {stats['pedido_minimo']} kg")
    print(f"Distritos únicos: {stats['distritos_unicos']}")
    print("\nDistribución por prioridades:")
    for prioridad, cantidad in stats['distribucion_prioridades'].items():
        porcentaje = (cantidad / stats['total_clientes']) * 100
        print(f"  Prioridad {prioridad}: {cantidad} clientes ({porcentaje:.1f}%)")

if __name__ == "__main__":
    main() 