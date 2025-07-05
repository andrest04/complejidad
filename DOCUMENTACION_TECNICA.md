# Documentación Técnica - Sistema de Optimización de Rutas

## Arquitectura del Sistema

### 1. Arquitectura General
El sistema sigue una arquitectura cliente-servidor con las siguientes capas:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Cliente)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   HTML5     │ │   CSS3      │ │ JavaScript  │           │
│  │   Jinja2    │ │ Bootstrap   │ │   ES6+      │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (Servidor)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Flask     │ │  Algoritmos │ │   Utils     │           │
│  │   Web App   │ │  Python     │ │  Helpers    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Datos
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Capa de Datos                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │    CSV      │ │    JSON     │ │   Memoria   │           │
│  │  Clientes   │ │  Vehículos  │ │  Temporal   │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 2. Componentes Principales

#### 2.1 Backend (Flask)
- **app.py**: Servidor principal con rutas HTTP
- **config.py**: Configuraciones centralizadas
- **algoritmos/**: Implementaciones de algoritmos de optimización
- **utils/**: Utilidades para procesamiento de datos

#### 2.2 Frontend
- **templates/**: Plantillas HTML con Jinja2
- **static/css/**: Estilos CSS personalizados
- **static/js/**: JavaScript para interactividad

## Algoritmos Implementados

### 1. Bellman-Ford

#### Propósito
Encontrar los caminos mínimos desde el depósito central a todos los clientes.

#### Implementación
```python
def bellman_ford_caminos_minimos(self, matriz_distancias, origen):
    # Inicialización
    distancias = {nodo: float('inf') for nodo in matriz_distancias.keys()}
    predecesores = {nodo: None for nodo in matriz_distancias.keys()}
    distancias[origen] = 0
    
    # Relajación de aristas
    for _ in range(len(matriz_distancias) - 1):
        for u in matriz_distancias.keys():
            for v in matriz_distancias[u].keys():
                peso = matriz_distancias[u][v]
                if distancias[u] != float('inf') and distancias[u] + peso < distancias[v]:
                    distancias[v] = distancias[u] + peso
                    predecesores[v] = u
    
    return distancias, predecesores
```

#### Complejidad
- **Tiempo**: O(VE) donde V = nodos, E = aristas
- **Espacio**: O(V)

#### Casos de Uso
- Optimización de rutas considerando solo distancias
- Problemas con grafos que pueden tener ciclos negativos
- Cálculo de caminos mínimos desde un origen

### 2. Programación Dinámica (TSP)

#### Propósito
Resolver el problema del viajante (TSP) para optimizar secuencias de entrega.

#### Implementación
```python
def tsp_programacion_dinamica(self, matriz_distancias, clientes):
    n = len(clientes) + 1  # +1 por el depósito
    nodos = ['deposito'] + [cliente['id'] for cliente in clientes]
    
    # Crear todas las combinaciones posibles
    subconjuntos = generar_subconjuntos(n - 1)
    
    # Memoización
    memo = {}
    caminos = {}
    
    # Caso base
    memo[(frozenset([0]), 0)] = 0
    caminos[(frozenset([0]), 0)] = [0]
    
    # Llenar tabla de memoización
    for subconjunto in subconjuntos:
        for j in subconjunto:
            # Encontrar costo mínimo
            min_costo = float('inf')
            for k in subconjunto:
                if k != j:
                    subconjunto_sin_j = frozenset([x for x in subconjunto if x != j])
                    if (subconjunto_sin_j, k) in memo:
                        costo = memo[(subconjunto_sin_j, k)] + matriz_distancias[nodos[k]][nodos[j]]
                        if costo < min_costo:
                            min_costo = costo
            
            if min_costo != float('inf'):
                memo[(subconjunto, j)] = min_costo
    
    return reconstruir_camino(memo, caminos, nodos)
```

#### Complejidad
- **Tiempo**: O(n²2ⁿ)
- **Espacio**: O(n2ⁿ)

#### Casos de Uso
- Optimización de secuencias de entrega
- Problemas con pocos nodos (n ≤ 15)
- Cuando se requiere la solución óptima exacta

### 3. Backtracking con Poda

#### Propósito
Búsqueda exhaustiva con optimizaciones para problemas con múltiples restricciones.

#### Implementación
```python
def backtracking_rutas(self, ruta_actual, clientes_restantes, vehiculos_disponibles, matriz_distancias, nivel=0):
    # Verificar límite de tiempo
    if time.time() - self.tiempo_inicio > self.tiempo_limite:
        return
    
    # Si no hay más clientes, evaluar la solución
    if not clientes_restantes:
        if ruta_actual:
            ruta_completa = ruta_actual + ['deposito']
            costo_total = calcular_costo_total(ruta_completa, matriz_distancias)
            if costo_total < self.mejor_costo:
                self.mejor_costo = costo_total
                self.mejor_solucion = ruta_completa.copy()
        return
    
    # Poda: verificar cota inferior
    cota_inferior = self.calcular_cota_inferior(ruta_actual, clientes_restantes, matriz_distancias)
    if cota_inferior >= self.mejor_costo:
        return
    
    # Probar cada cliente restante
    for i, cliente in enumerate(clientes_restantes):
        if self.verificar_restricciones(ruta_actual, cliente, vehiculos_disponibles[0], matriz_distancias):
            ruta_actual.append(cliente['id'])
            clientes_restantes_nuevo = clientes_restantes[:i] + clientes_restantes[i + 1:]
            self.backtracking_rutas(ruta_actual, clientes_restantes_nuevo, vehiculos_disponibles, matriz_distancias, nivel + 1)
            ruta_actual.pop()
```

#### Complejidad
- **Tiempo**: O(n!) con podas significativas
- **Espacio**: O(n)

#### Casos de Uso
- Problemas con múltiples restricciones
- Cuando se requiere explorar todas las posibilidades
- Problemas de tamaño pequeño a mediano

## Estructura de Datos

### 1. Grafo de Rutas
```python
grafo = {
    'nodos': {
        'deposito': {
            'id': 'deposito',
            'nombre': 'Depósito Central',
            'latitud': -12.0464,
            'longitud': -77.0428,
            'tipo': 'deposito'
        },
        'cliente_1': {
            'id': 'cliente_1',
            'nombre': 'Cliente A',
            'latitud': -12.0464,
            'longitud': -77.0428,
            'prioridad': 1,
            'ventana_inicio': '08:00',
            'ventana_fin': '12:00',
            'pedido': 150.5,
            'tipo': 'cliente'
        }
    },
    'aristas': {
        'deposito_cliente_1': {
            'origen': 'deposito',
            'destino': 'cliente_1',
            'distancia': 5.2,
            'tiempo_estimado': 10.4,
            'costo': 2.6
        }
    },
    'matriz_distancias': {
        'deposito': {
            'deposito': 0,
            'cliente_1': 5.2
        },
        'cliente_1': {
            'deposito': 5.2,
            'cliente_1': 0
        }
    },
    'metadata': {
        'total_nodos': 2,
        'total_aristas': 1,
        'deposito': {...}
    }
}
```

### 2. Cliente
```python
cliente = {
    'id': '1',
    'nombre': 'Supermercado Metro',
    'latitud': -12.0464,
    'longitud': -77.0428,
    'prioridad': 1,  # 1-5, 1=más alta
    'ventana_inicio': '08:00',
    'ventana_fin': '12:00',
    'pedido': 150.5  # kg
}
```

### 3. Vehículo
```python
vehiculo = {
    'id': 1,
    'placa': 'ABC-123',
    'capacidad': 1000,  # kg
    'tipo': 'Camión',
    'disponible': True,
    'fecha_registro': '2024-01-01T10:00:00'
}
```

### 4. Ruta Optimizada
```python
ruta = {
    'vehiculo_id': 1,
    'placa': 'ABC-123',
    'capacidad': 1000,
    'clientes': [cliente1, cliente2, cliente3],
    'distancia_total': 45.2,
    'carga_total': 450.5,
    'tiempo_estimado': 90.4,  # minutos
    'orden_visita': ['deposito', 'cliente_1', 'cliente_2', 'cliente_3', 'deposito']
}
```

## API REST

### Endpoints Principales

#### 1. Cargar Datos CSV
```
POST /api/cargar_csv
Content-Type: multipart/form-data

Response:
{
    "success": true,
    "message": "Se cargaron 20 clientes exitosamente",
    "clientes_count": 20
}
```

#### 2. Registrar Vehículo
```
POST /api/registrar_vehiculo
Content-Type: application/json

Body:
{
    "placa": "ABC-123",
    "capacidad": 1000,
    "tipo": "Camión"
}

Response:
{
    "success": true,
    "message": "Vehículo registrado exitosamente",
    "vehiculo": {...}
}
```

#### 3. Ejecutar Algoritmo
```
POST /api/ejecutar_algoritmo
Content-Type: application/json

Body:
{
    "algoritmo": "bellman_ford"
}

Response:
{
    "success": true,
    "message": "Algoritmo bellman_ford ejecutado exitosamente",
    "resultados": {
        "algoritmo": "Bellman-Ford",
        "tiempo_ejecucion": 0.15,
        "rutas": [...],
        "metricas": {...}
    }
}
```

#### 4. Obtener Datos del Mapa
```
GET /api/obtener_datos_mapa

Response:
{
    "centro": {
        "lat": -12.0464,
        "lng": -77.0428,
        "zoom": 12
    },
    "deposito": {...},
    "clientes": [...],
    "rutas": [...],
    "capas": {...}
}
```

## Configuración del Sistema

### Variables de Entorno
```python
# Servidor
PUERTO = 5000
HOST = '0.0.0.0'
DEBUG = True

# Mapas
MAPA_CENTRO_LAT = -12.0464  # Lima, Perú
MAPA_CENTRO_LNG = -77.0428
MAPA_ZOOM = 12

# Algoritmos
TIEMPO_MAXIMO_EJECUCION = 300  # 5 minutos
MAX_ITERACIONES = 10000

# Restricciones
TIEMPO_MAXIMO_RUTA = 480  # 8 horas en minutos
DISTANCIA_MAXIMA_RUTA = 200  # km
```

### Configuración de Mapas
- **Proveedor**: OpenStreetMap
- **Centro**: Lima, Perú (-12.0464, -77.0428)
- **Zoom**: 12 (nivel de ciudad)
- **Marcadores**: Personalizados con Font Awesome

## Optimizaciones Implementadas

### 1. Cálculo de Distancias
- **Fórmula de Haversine**: Para distancias geográficas precisas
- **Caché de Distancias**: Evita recálculos innecesarios
- **Matriz de Distancias**: Precomputada para acceso rápido

### 2. Poda en Backtracking
- **Cota Inferior**: Usando árbol de expansión mínima
- **Restricciones Tempranas**: Verificación de capacidad y tiempo
- **Límite de Tiempo**: Evita ejecuciones infinitas

### 3. Memoización en Programación Dinámica
- **Tabla de Estados**: Almacena resultados intermedios
- **Subconjuntos**: Optimización de espacio
- **Reconstrucción de Caminos**: Eficiente

### 4. Frontend
- **Lazy Loading**: Carga de mapas bajo demanda
- **Clustering**: Agrupación de marcadores cercanos
- **Caché del Navegador**: Para recursos estáticos

## Métricas de Rendimiento

### 1. Tiempo de Ejecución
- **Bellman-Ford**: O(VE) - Rápido para grafos pequeños
- **Programación Dinámica**: O(n²2ⁿ) - Exponencial
- **Backtracking**: O(n!) - Factorial con podas

### 2. Uso de Memoria
- **Grafo**: O(V²) para matriz de distancias
- **Memoización**: O(n2ⁿ) para programación dinámica
- **Backtracking**: O(n) para pila de recursión

### 3. Escalabilidad
- **Hasta 20 clientes**: Todos los algoritmos
- **20-50 clientes**: Bellman-Ford recomendado
- **50+ clientes**: Heurísticas necesarias

## Consideraciones de Seguridad

### 1. Validación de Entrada
- **Coordenadas**: Rango válido (-90 a 90, -180 a 180)
- **Archivos CSV**: Validación de formato y contenido
- **Tiempos**: Formato HH:MM válido

### 2. Límites de Recursos
- **Tamaño de archivo**: Máximo 16MB
- **Tiempo de ejecución**: Máximo 5 minutos
- **Memoria**: Límites por algoritmo

### 3. Sanitización
- **HTML**: Escape de caracteres especiales
- **JSON**: Validación de estructura
- **SQL**: No aplicable (sin base de datos)

## Pruebas y Validación

### 1. Casos de Prueba
- **Datos de ejemplo**: 20 clientes en Lima
- **Vehículos de prueba**: 8 vehículos variados
- **Escenarios**: Diferentes configuraciones de prioridad

### 2. Validación de Algoritmos
- **Bellman-Ford**: Comparación con Dijkstra
- **Programación Dinámica**: Verificación con fuerza bruta
- **Backtracking**: Validación de restricciones

### 3. Rendimiento
- **Tiempo de respuesta**: < 1 segundo para operaciones básicas
- **Uso de memoria**: < 100MB para casos típicos
- **Escalabilidad**: Pruebas con hasta 50 clientes

## Mantenimiento y Extensibilidad

### 1. Agregar Nuevos Algoritmos
1. Crear clase en `algoritmos/`
2. Implementar método `optimizar_rutas()`
3. Agregar opción en interfaz
4. Actualizar documentación

### 2. Nuevas Restricciones
1. Modificar validación en algoritmos
2. Actualizar interfaz de usuario
3. Agregar campos en estructuras de datos
4. Actualizar métricas

### 3. Nuevas Visualizaciones
1. Crear funciones en `mapa_utils.py`
2. Agregar controles en frontend
3. Implementar en JavaScript
4. Actualizar estilos CSS

## Troubleshooting

### Problemas Comunes

#### 1. Error de Puerto en Uso
```bash
# Solución: Cambiar puerto en config.py
PUERTO = 5001
```

#### 2. Error de Memoria
```bash
# Solución: Reducir tamaño de problema
MAX_ITERACIONES = 5000
```

#### 3. Error de Tiempo de Ejecución
```bash
# Solución: Aumentar límite
TIEMPO_MAXIMO_EJECUCION = 600
```

#### 4. Error de Archivo CSV
- Verificar codificación UTF-8
- Validar formato de columnas
- Comprobar coordenadas geográficas

### Logs y Debugging
- **Flask Debug**: Habilitado en desarrollo
- **Console Logs**: JavaScript en navegador
- **Error Handling**: Try-catch en todas las operaciones

## Futuras Mejoras

### 1. Algoritmos Adicionales
- **Algoritmo Genético**: Para problemas grandes
- **Simulated Annealing**: Optimización estocástica
- **Ant Colony**: Inspirado en comportamiento de hormigas

### 2. Funcionalidades
- **Base de Datos**: Persistencia de datos
- **Autenticación**: Sistema de usuarios
- **API Externa**: Integración con mapas de tráfico

### 3. Optimizaciones
- **Paralelización**: Múltiples núcleos
- **GPU Computing**: Para cálculos intensivos
- **Machine Learning**: Predicción de tiempos

### 4. Interfaz
- **PWA**: Aplicación web progresiva
- **Mobile App**: Aplicación nativa
- **Real-time**: Actualizaciones en tiempo real 