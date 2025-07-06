# Módulo de Gestión de Clientes - Guía de Usuario

## Descripción General
El módulo de gestión de clientes proporciona una interfaz simplificada para visualizar, filtrar y editar la información de los clientes del sistema de optimización de rutas.

## Características Principales

### 1. Visualización de Clientes
- **Lista de clientes**: Muestra todos los clientes en formato de tarjetas
- **Información por cliente**:
  - Nombre del cliente
  - Distrito de ubicación
  - Valor del pedido (en soles)
  - Horario de atención (ventana de tiempo)
  - Coordenadas geográficas
  - Nivel de prioridad (1-5)

### 2. Sistema de Filtros
- **Por Distrito**: Filtrar clientes por distrito específico
- **Por Prioridad**: Filtrar por nivel de prioridad (1=Crítica, 5=Muy Baja)
- **Filtros combinados**: Aplicar múltiples filtros simultáneamente

### 3. Estadísticas
- **Total de clientes**: Número total de clientes en el sistema
- **Valor total de pedidos**: Suma de todos los pedidos
- **Promedio por pedido**: Valor promedio de los pedidos
- **Distritos cubiertos**: Número de distritos únicos

### 4. Edición de Clientes
- **Editar información**: Modificar datos de clientes existentes
- **Campos editables**:
  - Nombre
  - Coordenadas (latitud/longitud)
  - Distrito
  - Prioridad
  - Ventana horaria
  - Valor del pedido

### 5. Recarga de Datos
- **Recargar desde CSV**: Volver a cargar los datos desde el archivo original
- **Actualización automática**: Los cambios se reflejan inmediatamente en la interfaz

## Códigos de Prioridad

| Prioridad | Descripción | Color |
|-----------|-------------|-------|
| 1 | Crítica | Rojo |
| 2 | Alta | Naranja |
| 3 | Media | Amarillo |
| 4 | Baja | Verde claro |
| 5 | Muy Baja | Verde oscuro |

## API Endpoints

### GET `/api/clientes`
Obtiene la lista de clientes con filtros opcionales:
- `?distrito=NOMBRE_DISTRITO`: Filtrar por distrito
- `?prioridad=NUMERO`: Filtrar por prioridad

### GET `/api/clientes/{id}`
Obtiene un cliente específico por ID.

### PUT `/api/clientes/{id}`
Actualiza la información de un cliente específico.

### GET `/api/clientes/estadisticas`
Obtiene estadísticas generales de los clientes.

### POST `/api/clientes/recargar`
Recarga los clientes desde el archivo CSV original.

## Uso de la Interfaz

### Acceso
1. Desde el dashboard principal, haz clic en "Clientes" en la barra de navegación
2. La página se carga automáticamente con todos los clientes

### Filtrar Clientes
1. Usa los menús desplegables en la sección "Filtros"
2. Selecciona distrito y/o prioridad
3. Haz clic en "Filtrar"
4. Los resultados se actualizarán automáticamente

### Ver Estadísticas
1. Haz clic en el botón "Estadísticas"
2. Se mostrará un panel con información resumida
3. Haz clic nuevamente para ocultar

### Editar Cliente
1. Haz clic en el ícono de edición (📝) en cualquier tarjeta de cliente
2. Modifica los campos necesarios en el modal
3. Haz clic en "Guardar Cambios"
4. Los cambios se aplicarán inmediatamente

### Recargar Datos
1. Haz clic en el botón "Recargar"
2. Confirma la acción en el diálogo
3. Los datos se recargarán desde el archivo CSV original

## Validaciones

El sistema incluye las siguientes validaciones:
- **Coordenadas**: Latitud entre -90 y 90, longitud entre -180 y 180
- **Prioridad**: Valores entre 1 y 5
- **Horarios**: Formato HH:MM válido
- **Pedidos**: Valores mayores a 0

## Tecnologías Utilizadas

- **Backend**: Flask, Python
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Estilos**: Bootstrap 5
- **Iconos**: Font Awesome 6
- **Datos**: CSV con pandas para procesamiento

## Notas Técnicas

- Los datos se mantienen en memoria durante la sesión
- Las modificaciones son temporales hasta recargar desde CSV
- La interfaz es responsive y funciona en dispositivos móviles
- Soporte para archivos CSV con encoding UTF-8
