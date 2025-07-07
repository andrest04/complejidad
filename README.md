# Sistema de Optimización de Rutas de Entrega

## Descripción

Este sistema permite optimizar rutas de entrega para empresas de distribución, considerando múltiples restricciones como capacidad de carga, prioridades de pedidos y ventanas horarias de atención. La aplicación modela el problema logístico como un grafo dirigido y ponderado, donde los nodos representan clientes y el depósito central, y las aristas representan rutas con costos de tiempo o distancia.

## Características

- **Interfaz Visual Interactiva**: Dashboard completo con mapas interactivos centrados en Lima, Perú
- **Algoritmos de Optimización**: 
  - Bellman-Ford para caminos mínimos
  - Programación Dinámica para optimización de secuencias
  - Backtracking con poda para problemas complejos
- **Gestión de Datos**: Carga de archivos CSV, registro de vehículos y gestión de clientes
- **Visualización Avanzada**: Mapas con capas de congestión, zonas críticas y análisis por prioridad
- **Análisis de Métricas**: Estadísticas detalladas y gráficos de rendimiento

## Tecnologías Utilizadas

### Backend
- **Python 3.10+**: Lenguaje principal
- **Flask**: Framework web para la aplicación
- **Pandas**: Procesamiento de datos CSV
- **NumPy**: Cálculos matemáticos

### Frontend
- **HTML5 + Jinja2**: Plantillas dinámicas
- **Bootstrap 5**: Framework CSS responsivo
- **JavaScript (ES6+)**: Interactividad del cliente
- **Leaflet.js**: Mapas interactivos
- **Chart.js**: Gráficos y visualizaciones
- **Font Awesome**: Iconografía

## Instalación

### � Guía de Instalación Simple

#### Prerrequisitos
- Python 3.10 o superior ([Descargar aquí](https://www.python.org/downloads/))
- pip (gestor de paquetes de Python)

#### Pasos de Instalación

1. **Verificar Python (versión 3.10 o superior)**
   ```bash
   python --version
   ```
   Si no tienes Python instalado, descárgalo desde [python.org](https://www.python.org/downloads/)

2. **Descargar el proyecto**
   - Descarga el proyecto como ZIP y extráelo
   - O clona el repositorio si está disponible

3. **Navegar al directorio del proyecto**
   ```bash
   cd complejidad
   ```

4. **Crear entorno virtual (RECOMENDADO)**
   ```bash
   python -m venv venv
   
   # Activar en Windows
   venv\Scripts\activate
   
   # Activar en macOS/Linux
   source venv/bin/activate
   ```

5. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

6. **Ejecutar la aplicación**
   ```bash
   python run.py
   ```

7. **Abrir en el navegador**
   - Ve a: `http://localhost:5000`
   - Deberías ver el dashboard principal del sistema

### Verificación de Instalación

Si todo funciona correctamente, deberías ver:
- ✅ Un dashboard con un mapa interactivo de Lima
- ✅ Menús para gestionar clientes y vehículos
- ✅ Opciones para cargar datos y ejecutar algoritmos

Si encuentras errores, verifica que:

- Tienes Python 3.10+ instalado
- El entorno virtual está activado
- Todas las dependencias se instalaron correctamente

### 📖 Más ayuda

- Ver `INSTALACION_RAPIDA.md` para instrucciones detalladas y solución de problemas
- Los pasos anteriores funcionan en Windows, macOS y Linux por igual

## Estructura del Proyecto

```
complejidad/
├── app/                               # Lógica principal del sistema
│   ├── __init__.py                    # Inicialización de la aplicación
│   ├── config.py                      # Configuraciones
│   ├── algoritmos/                    # Implementaciones algorítmicas
│   │   ├── bellman_ford.py
│   │   ├── programacion_dinamica.py
│   │   └── backtracking.py
│   ├── routes/                        # Rutas de la aplicación
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api_clientes.py
│   │   ├── api_vehiculos.py
│   │   └── api_general.py
│   ├── utils/                         # Utilidades
│   │   ├── parser_csv.py
│   │   ├── grafo_builder.py
│   │   ├── mapa_utils.py
│   │   ├── calculos_comunes.py
│   │   ├── analisis_dataset.py
│   │   └── resultados_generator.py
│   ├── templates/                     # Plantillas HTML
│   │   ├── layout.html
│   │   ├── index.html
│   │   ├── gestionar_clientes.html
│   │   ├── gestionar_vehiculos.html
│   │   ├── diagnostico.html
│   │   └── resultados.html
│   └── static/                        # Archivos estáticos
│       ├── css/estilos.css
│       └── js/scripts.js
├── Dataset/                           # Datos de ejemplo
│   ├── clientes_lima_1500.csv
│   ├── clientes_rutas.csv
│   ├── flota_lima_1500.json
│   ├── flota.json
│   └── reporte_lima_1500.json
├── uploads/                           # Archivos subidos por usuarios
├── run.py                             # Archivo principal para ejecutar
├── requirements.txt                   # Dependencias del proyecto
└── README.md                         # Este archivo
```

## Uso de la Aplicación

### 1. Dashboard Principal
- Vista general de estadísticas
- Mapa interactivo de Lima
- Acceso rápido a todas las funciones

### 2. Cargar Datos
- Subir archivo CSV con datos de clientes
- Formato requerido: `id,nombre,latitud,longitud,prioridad,ventana_inicio,ventana_fin,pedido`
- Validación automática de datos

### 3. Registrar Vehículos
- Agregar vehículos de la flota
- Especificar capacidad y tipo
- Gestión de disponibilidad

### 4. Gestionar Clientes
- Agregar clientes manualmente
- Editar información existente
- Visualizar en mapa

### 5. Ejecutar Optimización
- Seleccionar algoritmo (Bellman-Ford, Programación Dinámica, Backtracking)
- Configurar parámetros
- Ejecutar optimización

### 6. Ver Resultados
- Visualizar rutas optimizadas en mapa
- Analizar métricas de rendimiento
- Exportar resultados

## Formato de Datos

### Archivo CSV de Clientes
```csv
id,nombre,latitud,longitud,prioridad,ventana_inicio,ventana_fin,pedido
1,Cliente A,-12.0464,-77.0428,1,08:00,12:00,150.5
2,Cliente B,-12.0564,-77.0328,2,09:00,17:00,200.0
```

### Archivo JSON de Vehículos
```json
[
  {
    "placa": "ABC-123",
    "capacidad": 1000,
    "tipo": "Camión"
  }
]
```

## Algoritmos Implementados

### 1. Bellman-Ford
- **Propósito**: Encontrar caminos mínimos desde el depósito
- **Complejidad**: O(VE) donde V=nodos, E=aristas
- **Uso**: Optimización de rutas considerando distancias

### 2. Programación Dinámica
- **Propósito**: Resolver el problema del viajante (TSP)
- **Complejidad**: O(n²2ⁿ)
- **Uso**: Optimización de secuencias de entrega

### 3. Backtracking con Poda
- **Propósito**: Búsqueda exhaustiva con optimizaciones
- **Complejidad**: O(n!) con podas
- **Uso**: Problemas con múltiples restricciones

## Configuración

### Archivo config.py
```python
# Configuración del servidor
PUERTO = 5000
HOST = '0.0.0.0'

# Configuración de mapas
MAPA_CENTRO_LAT = -12.0464  # Lima, Perú
MAPA_CENTRO_LNG = -77.0428
MAPA_ZOOM = 12

# Configuración de algoritmos
TIEMPO_MAXIMO_EJECUCION = 300  # 5 minutos
MAX_ITERACIONES = 10000
```

## Características Avanzadas

### Visualización de Mapas
- **Marcadores de Clientes**: Colores por prioridad
- **Rutas Optimizadas**: Líneas con colores diferenciados
- **Capas de Congestión**: Análisis de densidad
- **Zonas Críticas**: Identificación de áreas prioritarias

### Análisis de Métricas
- **Distancia Total**: Suma de todas las rutas
- **Tiempo Estimado**: Cálculo basado en velocidad promedio
- **Eficiencia**: Clientes atendidos por vehículo
- **Utilización de Capacidad**: Porcentaje de uso de vehículos

### Exportación de Datos
- **CSV**: Resultados en formato tabular
- **JSON**: Datos estructurados
- **Gráficos**: Visualizaciones en PNG

## Solución de Problemas

### Error de Puerto en Uso
```bash
# Cambiar puerto en config.py o usar otro puerto
python app.py --port 5001
```

### Error de Dependencias
```bash
# Reinstalar dependencias
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

### Error de Archivo CSV
- Verificar formato de columnas
- Comprobar codificación UTF-8
- Validar coordenadas geográficas

## Contribución

1. Fork el proyecto
2. Crear rama para nueva funcionalidad
3. Commit cambios
4. Push a la rama
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Contacto

Para preguntas o soporte técnico, contactar al desarrollador del proyecto.

## Changelog

### v1.0.0
- Implementación inicial
- Algoritmos básicos de optimización
- Interfaz web completa
- Visualización de mapas
- Gestión de datos CSV/JSON 