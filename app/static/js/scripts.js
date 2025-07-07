// Scripts comunes para la aplicación de optimización de rutas

// Variables globales (cada página maneja su propio estado)
let rutas = [];
let mapaRutas = null;
let rutasLayer = null;
let markersLayer = null;

// Funciones de utilidad
function formatNumber(num) {
    return new Intl.NumberFormat('es-PE').format(num);
}

function formatTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}

function formatDistance(km) {
    return `${formatNumber(km)} km`;
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('es-PE', {
        style: 'currency',
        currency: 'PEN'
    }).format(amount);
}

// Funciones de notificación
function showToast(title, message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');
    
    if (toast && toastTitle && toastMessage) {
        toastTitle.textContent = title;
        toastMessage.textContent = message;
        
        // Cambiar clase según tipo
        toast.className = `toast ${type === 'error' ? 'bg-danger text-white' : type === 'success' ? 'bg-success text-white' : ''}`;
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    } else {
        // Fallback si no existe el toast
        alert(`${title}: ${message}`);
    }
}

// Funciones de validación
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

function validateCoordinates(lat, lng) {
    const latNum = parseFloat(lat);
    const lngNum = parseFloat(lng);
    
    if (isNaN(latNum) || isNaN(lngNum)) {
        return false;
    }
    
    if (latNum < -90 || latNum > 90) {
        return false;
    }
    
    if (lngNum < -180 || lngNum > 180) {
        return false;
    }
    
    return true;
}

function validateTimeFormat(time) {
    const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
    return timeRegex.test(time);
}

// Funciones de mapa
function initializeMap(containerId, center = [-12.0464, -77.0428], zoom = 12) {
    // Asegurarse de que el contenedor del mapa tenga dimensiones
    const container = document.getElementById(containerId);
    if (container) {
        container.style.height = '600px';
        container.style.width = '100%';
        
        // Forzar un redibujado del contenedor
        container.style.display = 'none';
        container.offsetHeight; // Trigger reflow
        container.style.display = 'block';
    }

    // Crear el mapa con más opciones
    const mapaLocal = L.map(containerId, {
        center: center,
        zoom: zoom,
        zoomControl: false, // Desactivamos el control de zoom por defecto para personalizarlo
        preferCanvas: true, // Mejor rendimiento para muchos marcadores
        fadeAnimation: false,
        zoomAnimation: true
    });

    // Capa base de OpenStreetMap
    const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
        detectRetina: true
    });

    // Agregar capa base al mapa
    osmLayer.addTo(mapaLocal);

    // Inicializar los controles después de que el mapa esté listo
    mapaLocal.whenReady(function() {
        // Agregar control de zoom personalizado
        L.control.zoom({
            position: 'topright'
        }).addTo(mapaLocal);

        // Agregar control de escala
        L.control.scale({
            imperial: false,
            metric: true,
            position: 'bottomleft'
        }).addTo(mapaLocal);

        // Forzar actualización del mapa
        setTimeout(function() {
            mapaLocal.invalidateSize();
        }, 100);
    });

    // Manejar errores de carga de teselas
    mapaLocal.on('tileerror', function(error) {
        console.error('Error al cargar el mapa:', error);
    });

    // Configurar controles del mapa
    setupMapControls(mapaLocal);
    
    return mapaLocal;
}

// Personalizar controles de zoom
function setupMapControls(map) {
    if (!map) return;
    
    // Solo agregar controles si no existen ya
    if (!map.zoomControl) {
        L.control.zoom({
            position: 'topright'
        }).addTo(map);
    }

    // Agregar control de escala
    if (!map.scaleControl) {
        L.control.scale({
            imperial: false,
            metric: true,
            position: 'bottomleft'
        }).addTo(map);
    }

    // Agregar botón de pantalla completa si está disponible
    if (L.control.fullscreen && !map.fullscreenControl) {
        map.addControl(L.control.fullscreen({
            position: 'topleft',
            title: 'Pantalla completa',
            titleCancel: 'Salir de pantalla completa',
            forceSeparateButton: true,
            forcePseudoFullscreen: true,
            fullscreenElement: false
        }));
    }
}

// Inicializar el mapa
function inicializarMapa() {
  console.log('🔍 Inicializando mapa...');
  
  // Verificar si el contenedor del mapa existe
  const mapContainer = document.getElementById('mapaRutas');
  if (!mapContainer) {
    console.error('❌ No se encontró el contenedor del mapa');
    return null;
  }
  
  console.log('✅ Contenedor del mapa encontrado');
  
  // Asegurarse de que el contenedor sea visible y tenga dimensiones
  mapContainer.style.display = 'block';
  mapContainer.style.height = '600px';
  
  // Forzar un reflow para asegurar que el navegador calcule las dimensiones
  void mapContainer.offsetHeight;
  
  // Limpiar mapa existente si lo hay
  if (window.mapaRutas) {
    console.log('♻️ Mapa ya existe, limpiando...');
    try {
      // Limpiar capas de rutas si existen
      if (window.rutasLayer) {
        if (window.rutasLayer.clearLayers) window.rutasLayer.clearLayers();
        if (window.rutasLayer.remove) window.rutasLayer.remove();
        window.rutasLayer = null;
      }
      
      // Limpiar marcadores si existen
      if (window.markersLayer) {
        if (window.markersLayer.clearLayers) window.markersLayer.clearLayers();
        if (window.markersLayer.remove) window.markersLayer.remove();
        window.markersLayer = null;
      }
      
      // Eliminar el mapa
      if (window.mapaRutas.remove) {
        window.mapaRutas.remove();
      }
      
      // Limpiar referencia
      window.mapaRutas = null;
    } catch (error) {
      console.error('❌ Error al limpiar el mapa anterior:', error);
      window.mapaRutas = null;
    }
  }

  console.log('🗺️ Creando nuevo mapa...');
  
  try {
    // Asegurarse de que el contenedor sea visible y tenga dimensiones
    mapContainer.style.display = 'block';
    if (mapContainer.offsetWidth === 0 || mapContainer.offsetHeight === 0) {
      console.warn('⚠️ El contenedor del mapa no tiene dimensiones visibles');
    }
    
    // Crear un nuevo mapa
    window.mapaRutas = L.map('mapaRutas', {
      center: [-12.0464, -77.0428], // Coordenadas de Lima por defecto
      zoom: 12,
      layers: [
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        })
      ]
    });
    
    // Inicializar capas
    window.rutasLayer = L.layerGroup().addTo(window.mapaRutas);
    window.markersLayer = L.layerGroup().addTo(window.mapaRutas);
    
    // Forzar actualización del tamaño
    setTimeout(() => {
      if (window.mapaRutas) {
        window.mapaRutas.invalidateSize();
      }
    }, 100);
    
    // Agregar marcador de depósito
    L.marker([-12.0464, -77.0428], {
      icon: L.divIcon({
        className: 'depot-marker',
        html: '<i class="fas fa-warehouse"></i>',
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30]
      })
    }).addTo(window.mapaRutas);
    
    console.log('✅ Mapa inicializado correctamente');
    return window.mapaRutas;
    
  } catch (error) {
    console.error('❌ Error al inicializar el mapa:', error);
    return null;
  }
}

// Configurar controles del mapa
function configurarControlesMapa() {
  if (!mapaRutas) return;
  
  // Control de zoom personalizado
  const btnZoomIn = document.getElementById('btnZoomIn');
  const btnZoomOut = document.getElementById('btnZoomOut');
  
  if (btnZoomIn) {
    btnZoomIn.addEventListener('click', () => {
      mapaRutas.zoomIn();
    });
  }
  
  if (btnZoomOut) {
    btnZoomOut.addEventListener('click', () => {
      mapaRutas.zoomOut();
    });
  }
  
  // Control de pantalla completa
  const btnFullscreen = document.getElementById('btnFullscreen');
  if (btnFullscreen) {
    btnFullscreen.addEventListener('click', () => {
      const container = document.getElementById('mapaRutas');
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        container.requestFullscreen().catch(err => {
          console.error('Error al intentar pantalla completa:', err);
        });
      }
    });
  }
  
  // Control para recargar el mapa
  const btnRecargar = document.getElementById('btnRecargarMapa');
  if (btnRecargar) {
    btnRecargar.addEventListener('click', () => {
      limpiarMapa();
      const algoritmoSeleccionado = document.getElementById('algoritmoSeleccionado')?.value;
      if (algoritmoSeleccionado) {
        ejecutarAlgoritmo(algoritmoSeleccionado);
      }
    });
  }
}

// Limpiar el mapa (conservando la capa base)
function limpiarMapa() {
  if (rutasLayer) rutasLayer.clearLayers();
  if (markersLayer) markersLayer.clearLayers();
  
  const mapaInfo = document.getElementById('mapaInfo');
  const btnRecargar = document.getElementById('btnRecargarMapa');
  
  if (mapaInfo) mapaInfo.textContent = 'No hay datos de ruta cargados';
  if (btnRecargar) btnRecargar.style.display = 'none';
}

// Mostrar ruta en el mapa
function mostrarRutaEnMapa(ruta, algoritmo) {
  if (!mapaRutas) inicializarMapa();
  
  limpiarMapa();
  
  // Verificar si hay datos de ruta
  if (!ruta || !ruta.coordenadas || ruta.coordenadas.length === 0) {
    console.error('No hay datos de coordenadas para mostrar en el mapa');
    return;
  }
  
  // Convertir coordenadas al formato [lat, lng] para Leaflet
  const coordenadas = ruta.coordenadas.map(coord => [coord.lat, coord.lng]);
  
  // Dibujar la ruta
  const polyline = L.polyline(coordenadas, {
    color: '#3498db',
    weight: 5,
    opacity: 0.8,
    dashArray: '5, 5',
    lineJoin: 'round'
  }).addTo(rutasLayer);
  
  // Agregar marcadores para los puntos de la ruta
  coordenadas.forEach((coord, index) => {
    const esInicio = index === 0;
    const esFin = index === coordenadas.length - 1;
    
    let icono;
    if (esInicio) {
      icono = L.divIcon({
        html: '<i class="fas fa-map-marker-alt fa-2x" style="color: #2ecc71;"></i>',
        className: 'custom-icon',
        iconSize: [24, 40],
        iconAnchor: [12, 40]
      });
    } else if (esFin) {
      icono = L.divIcon({
        html: '<i class="fas fa-flag-checkered fa-2x" style="color: #e74c3c;"></i>',
        className: 'custom-icon',
        iconSize: [24, 40],
        iconAnchor: [12, 40]
      });
    } else {
      icono = L.divIcon({
        html: '<i class="fas fa-map-marker" style="color: #3498db;"></i>',
        className: 'custom-icon',
        iconSize: [24, 40],
        iconAnchor: [12, 40]
      });
    }
    
    L.marker(coord, { icon: icono })
      .bindPopup(`<b>Punto ${index + 1}</b><br>Lat: ${coord[0].toFixed(4)}<br>Lng: ${coord[1].toFixed(4)}`)
      .addTo(markersLayer);
  });
  
  // Ajustar la vista del mapa para mostrar toda la ruta
  mapaRutas.fitBounds(polyline.getBounds(), { padding: [50, 50] });
  
  // Actualizar información del mapa
  const mapaInfo = document.getElementById('mapaInfo');
  if (mapaInfo) {
    mapaInfo.textContent = `Mostrando ruta con ${ruta.coordenadas.length} puntos | ` +
                         `Distancia: ${(ruta.distancia / 1000).toFixed(2)} km`;
  }
  
  const btnRecargar = document.getElementById('btnRecargarMapa');
  if (btnRecargar) {
    btnRecargar.style.display = 'inline-block';
  }
}

// Función para agregar marcador de depósito
function addDepositMarker(map, latlng = [-12.0464, -77.0428]) {
  if (!map || !L) return null;
  
  const icon = L.divIcon({
    className: 'deposit-marker',
    html: '<i class="fas fa-warehouse"></i>',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
  });
  
  return L.marker(latlng, { icon: icon })
    .addTo(map)
    .bindPopup('<b>Depósito Central</b>');
}

// Inicializar cuando el documento esté listo
document.addEventListener('DOMContentLoaded', () => {
  console.log('📄 DOM completamente cargado');
  
  // Solo inicializar el mapa si no hay un mapa global ya inicializado
  if (!window.mapaRutas) {
    console.log('ℹ️ No hay un mapa global, se inicializará cuando sea necesario');
  }
  
  // Configurar el botón de pantalla completa si existe
  const fullscreenBtn = document.getElementById('btnFullscreen');
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', () => {
      const elem = document.documentElement;
      if (!document.fullscreenElement) {
        if (elem.requestFullscreen) {
          elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) { /* Safari */
          elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { /* IE11 */
          elem.msRequestFullscreen();
        }
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.webkitExitFullscreen) { /* Safari */
          document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { /* IE11 */
          document.msExitFullscreen();
        }
      }
    });
  }
});

// Manejar cambios en la selección de algoritmo
const selectAlgoritmo = document.getElementById('algoritmoSeleccionado');
const btnEjecutar = document.getElementById('btnEjecutar');

if (selectAlgoritmo && btnEjecutar) {
  selectAlgoritmo.addEventListener('change', function() {
    btnEjecutar.disabled = !this.value;
    limpiarMapa();
  });
  
  // Inicializar estado del botón
  btnEjecutar.disabled = !selectAlgoritmo.value;
}

// Manejar clic en el botón de ejecutar
if (btnEjecutar) {
  btnEjecutar.addEventListener('click', function() {
    const algoritmo = selectAlgoritmo ? selectAlgoritmo.value : null;
    if (algoritmo) {
      ejecutarAlgoritmo(algoritmo);
    }
  });
}

function addClientMarkers(map, clientes, marcadoresObj = {}) {
    // Limpiar marcadores existentes
    Object.values(marcadoresObj).forEach(marker => map.removeLayer(marker));
    marcadoresObj = {};
    
    clientes.forEach(cliente => {
        // Validar coordenadas - soportar tanto lat/lng como latitud/longitud
        const lat = cliente.lat || cliente.latitud;
        const lng = cliente.lng || cliente.longitud;
        
        if (!lat || !lng || isNaN(lat) || isNaN(lng)) {
            console.warn(`Cliente ${cliente.nombre} (ID: ${cliente.id}) tiene coordenadas inválidas:`, 
                        `lat: ${lat}, lng: ${lng}`);
            return; // Saltar este cliente
        }
        
        const color = getPriorityColor(cliente.prioridad);
        const icon = L.divIcon({
            className: 'custom-div-icon',
            html: `<i class="fas fa-store fa-lg" style="color: ${color}"></i>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
        
        try {
            const marker = L.marker([parseFloat(lat), parseFloat(lng)], {icon: icon})
                .addTo(map)
                .bindPopup(`
                    <b>${cliente.nombre}</b><br>
                    Prioridad: ${cliente.prioridad || 'N/A'}<br>
                    Pedido: ${cliente.pedido ? formatNumber(cliente.pedido) : 'N/A'} kg<br>
                    Ventana: ${cliente.ventana_inicio || 'N/A'} - ${cliente.ventana_fin || 'N/A'}
                `);
            
            marcadoresObj[cliente.id] = marker;
        } catch (error) {
            console.error(`Error al crear marcador para cliente ${cliente.nombre}:`, error);
        }
    });
    
    return marcadoresObj;
}

function addRouteLines(map, rutas) {
    // Limpiar rutas existentes
    rutas.forEach(ruta => {
        if (ruta.polyline) {
            map.removeLayer(ruta.polyline);
        }
        if (ruta.markers) {
            ruta.markers.forEach(marker => map.removeLayer(marker));
        }
        if (ruta.vehicleMarker) {
            map.removeLayer(ruta.vehicleMarker);
        }
    });
    
    rutas.forEach((ruta, index) => {
        if (ruta.coordenadas && ruta.coordenadas.length > 0) {
            const color = getRouteColor(index);
            
            // Crear la línea de ruta con un patrón de flechas
            const polyline = L.polyline(ruta.coordenadas, {
                color: color,
                weight: 4,
                opacity: 0.8,
                dashArray: '10, 10',
                lineCap: 'round',
                lineJoin: 'round'
            }).addTo(map);
            
            // Añadir marcadores para los puntos de parada
            const markers = [];
            ruta.paradas?.forEach((parada, i) => {
                const isFirst = i === 0;
                const isLast = i === ruta.paradas.length - 1;
                
                let icon, popupContent;
                
                if (isFirst) {
                    // Icono para el punto de inicio (depósito)
                    icon = L.divIcon({
                        className: 'custom-div-icon',
                        html: '<i class="fas fa-warehouse fa-2x"></i>',
                        iconSize: [25, 25],
                        iconAnchor: [12, 12]
                    });
                    popupContent = `
                        <b>Punto de inicio</b><br>
                        Vehículo: ${ruta.placa}<br>
                        Hora de salida: ${parada.hora || 'N/A'}
                    `;
                } else if (isLast) {
                    // Icono para el punto final (última parada)
                    icon = L.divIcon({
                        className: 'custom-div-icon',
                        html: '<i class="fas fa-flag-checkered fa-2x"></i>',
                        iconSize: [25, 25],
                        iconAnchor: [12, 12]
                    });
                    popupContent = `
                        <b>Punto final</b><br>
                        Vehículo: ${ruta.placa}<br>
                        Hora de llegada: ${parada.hora || 'N/A'}
                    `;
                } else {
                    // Icono para paradas intermedias
                    icon = L.divIcon({
                        className: 'custom-div-icon',
                        html: `<i class="fas fa-map-marker-alt fa-2x" style="color: ${color}"></i>`,
                        iconSize: [25, 25],
                        iconAnchor: [12, 12]
                    });
                    popupContent = `
                        <b>Parada ${i}</b><br>
                        Cliente: ${parada.nombre || 'N/A'}<br>
                        Hora: ${parada.hora || 'N/A'}<br>
                        Carga: ${parada.carga ? formatNumber(parada.carga) + ' kg' : 'N/A'}
                    `;
                }
                
                const marker = L.marker([parada.lat, parada.lng], { icon })
                    .addTo(map)
                    .bindPopup(popupContent);
                
                markers.push(marker);
            });
            
            // Crear marcador móvil para el vehículo
            const vehicleIcon = L.divIcon({
                className: 'custom-div-icon',
                html: `<i class="fas fa-truck fa-2x" style="color: ${color}"></i>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15],
                popupAnchor: [0, -15]
            });
            
            const vehicleMarker = L.marker(ruta.coordenadas[0], {
                icon: vehicleIcon,
                rotationAngle: 0,
                rotationOrigin: 'center'
            }).addTo(map);
            
            // Animación del vehículo
            let currentPos = 0;
            const totalPoints = ruta.coordenadas.length;
            const animationSpeed = 100; // ms por segmento
            
            function animateVehicle() {
                if (currentPos < totalPoints - 1) {
                    const start = ruta.coordenadas[currentPos];
                    const end = ruta.coordenadas[currentPos + 1];
                    
                    // Calcular ángulo de rotación
                    const angle = Math.atan2(end[1] - start[1], end[0] - start[0]) * 180 / Math.PI;
                    
                    // Mover el marcador
                    vehicleMarker.setRotationAngle(angle + 90); // +90 para ajustar el ícono
                    vehicleMarker.setLatLng([start[0], start[1]]);
                    
                    currentPos++;
                    setTimeout(animateVehicle, animationSpeed);
                } else if (ruta.loopAnimation) {
                    // Reiniciar la animación si está configurado para bucle
                    currentPos = 0;
                    setTimeout(animateVehicle, 1000);
                }
            }
            
            // Iniciar animación
            if (ruta.animate) {
                setTimeout(animateVehicle, 1000);
            }
            
            // Popup con información detallada de la ruta
            const popupContent = `
                <div class="route-popup">
                    <h5>Ruta ${ruta.id}</h5>
                    <p><i class="fas fa-truck me-2"></i>Vehículo: ${ruta.placa || 'N/A'}</p>
                    <p><i class="fas fa-route me-2"></i>Distancia: ${formatDistance(ruta.distancia_total)}</p>
                    <p><i class="fas fa-clock me-2"></i>Tiempo estimado: ${formatTime(ruta.tiempo_estimado)}</p>
                    <p><i class="fas fa-box me-2"></i>Carga total: ${formatNumber(ruta.carga_total)} kg</p>
                    <p><i class="fas fa-gas-pump me-2"></i>Combustible estimado: ${ruta.combustible ? ruta.combustible.toFixed(2) + ' L' : 'N/A'}</p>
                    <hr>
                    <button class="btn btn-sm btn-primary w-100" onclick="toggleAnimation(${index})">
                        <i class="fas fa-play me-1"></i> ${ruta.animate ? 'Pausar' : 'Reproducir'} animación
                    </button>
                </div>
            `;
            
            polyline.bindPopup(popupContent);
            
            // Guardar referencias para poder limpiarlas después
            ruta.polyline = polyline;
            ruta.markers = markers;
            ruta.vehicleMarker = vehicleMarker;
            ruta.animate = true;
            ruta.loopAnimation = true;
            
            // Ajustar el zoom para mostrar toda la ruta
            if (index === 0) {
                const bounds = L.latLngBounds(ruta.coordenadas);
                map.fitBounds(bounds.pad(0.1));
            }
        }
    });
    
    // Función para alternar la animación
    window.toggleAnimation = function(index) {
        const ruta = rutas[index];
        if (ruta) {
            ruta.animate = !ruta.animate;
            if (ruta.animate) {
                // Reiniciar animación
                ruta.currentPos = 0;
                animateRoute(ruta);
            }
            // Actualizar el botón en el popup
            const button = document.querySelector(`.route-popup button`);
            if (button) {
                button.innerHTML = `<i class="fas fa-${ruta.animate ? 'pause' : 'play'} me-1"></i> ${ruta.animate ? 'Pausar' : 'Reproducir'} animación`;
            }
        }
    };
}

// Funciones de color
function getPriorityColor(prioridad) {
    const colores = {
        1: '#FF0000',  // Rojo - Prioridad más alta
        2: '#FF6600',  // Naranja
        3: '#FFCC00',  // Amarillo
        4: '#00CC00',  // Verde
        5: '#0066CC'   // Azul - Prioridad más baja
    };
    return colores[prioridad] || '#999999';
}

function getRouteColor(index) {
    const colores = [
        '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF',
        '#00FFFF', '#FF6600', '#6600FF', '#FF0066', '#66FF00'
    ];
    return colores[index % colores.length];
}

// Funciones de API
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}

async function uploadFile(url, formData) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('File upload error:', error);
        throw error;
    }
}

// Funciones de gráficos
function createChart(canvasId, type, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    
    const ctx = canvas.getContext('2d');
    
    // Destruir gráfico existente si existe
    if (window.charts && window.charts[canvasId]) {
        window.charts[canvasId].destroy();
    }
    
    // Inicializar objeto de gráficos si no existe
    if (!window.charts) {
        window.charts = {};
    }
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    font: {
                        size: 12
                    }
                }
            }
        }
    };
    
    window.charts[canvasId] = new Chart(ctx, {
        type: type,
        data: data,
        options: { ...defaultOptions, ...options }
    });
    
    return window.charts[canvasId];
}

function createPriorityChart(canvasId, clientes) {
    const prioridades = [1, 2, 3, 4, 5];
    const datos = prioridades.map(p => clientes.filter(c => c.prioridad === p).length);
    const colores = ['#FF0000', '#FF6600', '#FFCC00', '#00CC00', '#0066CC'];
    
    return createChart(canvasId, 'doughnut', {
        labels: ['Prioridad 1', 'Prioridad 2', 'Prioridad 3', 'Prioridad 4', 'Prioridad 5'],
        datasets: [{
            data: datos,
            backgroundColor: colores,
            borderWidth: 2,
            borderColor: '#fff'
        }]
    });
}

function createMetricsChart(canvasId, metrics) {
    return createChart(canvasId, 'bar', {
        labels: ['Distancia Total', 'Tiempo Total', 'Clientes Atendidos', 'Vehículos Utilizados'],
        datasets: [{
            label: 'Métricas',
            data: [
                metrics.distancia_total,
                metrics.tiempo_total,
                metrics.clientes_atendidos,
                metrics.vehiculos_utilizados
            ],
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 205, 86, 1)',
                'rgba(75, 192, 192, 1)'
            ],
            borderWidth: 2
        }]
    });
}

// Funciones de tabla
function createTable(containerId, data, columns) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let html = '<table class="table table-striped table-hover">';
    
    // Encabezados
    html += '<thead><tr>';
    columns.forEach(col => {
        html += `<th>${col.header}</th>`;
    });
    html += '</tr></thead>';
    
    // Datos
    html += '<tbody>';
    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = col.formatter ? col.formatter(row[col.key]) : row[col.key];
            html += `<td>${value}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody>';
    
    html += '</table>';
    
    container.innerHTML = html;
}

// Funciones de exportación
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        showToast('Error', 'No hay datos para exportar', 'error');
        return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function exportToJSON(data, filename) {
    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Funciones de utilidad para formularios
function populateSelect(selectId, options, selectedValue = null) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    select.innerHTML = '';
    
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.text;
        
        if (selectedValue && option.value == selectedValue) {
            optionElement.selected = true;
        }
        
        select.appendChild(optionElement);
    });
}

function clearForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.reset();
    
    // Limpiar clases de validación
    const inputs = form.querySelectorAll('.is-invalid, .is-valid');
    inputs.forEach(input => {
        input.classList.remove('is-invalid', 'is-valid');
    });
}

// Funciones de animación
function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    const startValue = parseFloat(start);
    const endValue = parseFloat(end);
    const difference = endValue - startValue;
    
    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = startValue + (difference * progress);
        element.textContent = formatNumber(Math.round(currentValue));
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}

// Funciones de inicialización
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Event listeners globales
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips y popovers
    initializeTooltips();
    initializePopovers();
    
    // El mapa se inicializa automáticamente en cada página que lo necesite
    console.log("🚀 Scripts globales cargados correctamente");
    
    // Agregar listeners para formularios
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form.id)) {
                e.preventDefault();
                showToast('Error', 'Por favor complete todos los campos requeridos', 'error');
            }
        });
    });
    
    // Agregar listeners para inputs de coordenadas
    const coordInputs = document.querySelectorAll('input[data-coord]');
    coordInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const value = this.value;
            if (value && !validateCoordinates(value)) {
                this.classList.add('is-invalid');
                showToast('Error', 'Coordenadas inválidas', 'error');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
    
    // Agregar listeners para inputs de tiempo
    const timeInputs = document.querySelectorAll('input[type="time"]');
    timeInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const value = this.value;
            if (value && !validateTimeFormat(value)) {
                this.classList.add('is-invalid');
                showToast('Error', 'Formato de tiempo inválido (HH:MM)', 'error');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
});

// Exportar funciones para uso global
window.AppUtils = {
    formatNumber,
    formatTime,
    formatDistance,
    formatCurrency,
    showToast,
    validateForm,
    validateCoordinates,
    validateTimeFormat,
    initializeMap,
    addDepositMarker,
    addClientMarkers,
    addRouteLines,
    getPriorityColor,
    getRouteColor,
    apiCall,
    uploadFile,
    createChart,
    createPriorityChart,
    createMetricsChart,
    createTable,
    exportToCSV,
    exportToJSON,
    populateSelect,
    clearForm,
    animateValue,
    // Funciones de carga manual (excepto cargarMapaManual que se eliminó)
    cargarClientesManual,
    cargarVehiculosManual,
    cargarEstadisticasManual,
    mostrarDebugInfo
};

// Función para ejecutar el algoritmo seleccionado
function ejecutarAlgoritmo(algoritmo) {
  // Mostrar indicador de carga
  const btnEjecutar = document.getElementById('btnEjecutar');
  if (btnEjecutar) {
    const textoOriginal = btnEjecutar.innerHTML;
    btnEjecutar.disabled = true;
    btnEjecutar.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Ejecutando...';
    
    // Simular tiempo de procesamiento (en un caso real, aquí iría la llamada a la API)
    setTimeout(() => {
      try {
        // Datos de ejemplo para pruebas
        const datosEjemplo = {
          'bellman-ford': {
            coordenadas: [
              { lat: -12.0464, lng: -77.0428 },
              { lat: -12.0564, lng: -77.0528 },
              { lat: -12.0664, lng: -77.0328 },
              { lat: -12.0764, lng: -77.0228 },
              { lat: -12.0864, lng: -77.0128 }
            ],
            distancia: 12500, // en metros
            tiempo: 1800, // en segundos
            costo: 250.50 // en soles
          },
          'backtracking': {
            coordenadas: [
              { lat: -12.0464, lng: -77.0428 },
              { lat: -12.0664, lng: -77.0628 },
              { lat: -12.0564, lng: -77.0528 },
              { lat: -12.0464, lng: -77.0628 },
              { lat: -12.0364, lng: -77.0528 }
            ],
            distancia: 9800,
            tiempo: 1500,
            costo: 198.75
          },
          'programacion-dinamica': {
            coordenadas: [
              { lat: -12.0464, lng: -77.0428 },
              { lat: -12.0364, lng: -77.0528 },
              { lat: -12.0264, lng: -77.0428 },
              { lat: -12.0364, lng: -77.0328 },
              { lat: -12.0464, lng: -77.0228 }
            ],
            distancia: 11200,
            tiempo: 1680,
            costo: 225.30
          }
        };
        
        const resultado = datosEjemplo[algoritmo];
        
        if (resultado) {
          // Mostrar la ruta en el mapa
          mostrarRutaEnMapa(resultado, algoritmo);
          
          // Actualizar la información de resultados
          actualizarResultados(resultado, algoritmo);
          
          // Mostrar mensaje de éxito
          showToast('¡Éxito!', `El algoritmo ${algoritmo} se ha ejecutado correctamente.`, 'success');
        } else {
          throw new Error('Algoritmo no reconocido');
        }
      } catch (error) {
        console.error('Error al ejecutar el algoritmo:', error);
        showToast('Error', `Ocurrió un error al ejecutar el algoritmo: ${error.message}`, 'error');
      } finally {
        // Restaurar el botón
        if (btnEjecutar) {
          btnEjecutar.disabled = false;
          btnEjecutar.innerHTML = '<i class="fas fa-play me-2"></i>Ejecutar Algoritmo';
        }
      }
    }, 1500); // Simular tiempo de procesamiento
  }
}

// Función para actualizar la información de resultados
function actualizarResultados(datos, algoritmo) {
  // Actualizar tarjeta de resumen
  const resumenElement = document.getElementById('resumenResultados');
  if (resumenElement) {
    resumenElement.innerHTML = `
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Resultados del Algoritmo</h5>
          <div class="row mt-3">
            <div class="col-md-4">
              <div class="d-flex align-items-center mb-3">
                <div class="icon-shape icon-lg bg-light-primary rounded-3 text-primary me-3">
                  <i class="fas fa-route"></i>
                </div>
                <div>
                  <h6 class="mb-0">Distancia</h6>
                  <p class="mb-0 fw-bold">${(datos.distancia / 1000).toFixed(2)} km</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="d-flex align-items-center mb-3">
                <div class="icon-shape icon-lg bg-light-info rounded-3 text-info me-3">
                  <i class="fas fa-clock"></i>
                </div>
                <div>
                  <h6 class="mb-0">Tiempo Estimado</h6>
                  <p class="mb-0 fw-bold">${Math.floor(datos.tiempo / 60)} min ${datos.tiempo % 60} seg</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="d-flex align-items-center mb-3">
                <div class="icon-shape icon-lg bg-light-success rounded-3 text-success me-3">
                  <i class="fas fa-dollar-sign"></i>
                </div>
                <div>
                  <h6 class="mb-0">Costo Estimado</h6>
                  <p class="mb-0 fw-bold">S/ ${datos.costo.toFixed(2)}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-3">
            <button class="btn btn-outline-primary btn-sm me-2" id="btnExportarRuta">
              <i class="fas fa-file-export me-1"></i>Exportar Ruta
            </button>
            <button class="btn btn-outline-secondary btn-sm" id="btnCompartirRuta">
              <i class="fas fa-share-alt me-1"></i>Compartir
            </button>
          </div>
        </div>
      </div>
    `;
    
    // Agregar manejadores de eventos para los botones
    document.getElementById('btnExportarRuta')?.addEventListener('click', () => {
      exportarRuta(datos, algoritmo);
    });
    
    document.getElementById('btnCompartirRuta')?.addEventListener('click', () => {
      compartirRuta(datos, algoritmo);
    });
  }
}

// Función para exportar la ruta
function exportarRuta(datos, formato = 'json') {
  try {
    let contenido, nombreArchivo, tipoMIME;
    
    if (formato === 'json') {
      contenido = JSON.stringify({
        tipo: 'ruta-optimizada',
        algoritmo: 'bellman-ford',
        fecha: new Date().toISOString(),
        datos: datos
      }, null, 2);
      nombreArchivo = `ruta_optimizada_${new Date().toISOString().split('T')[0]}.json`;
      tipoMIME = 'application/json';
    } else {
      // Convertir a CSV
      const encabezados = ['Punto', 'Latitud', 'Longitud'];
      const filas = datos.coordenadas.map((coord, index) => [
        index + 1,
        coord.lat,
        coord.lng
      ]);
      
      contenido = [
        encabezados.join(','),
        ...filas.map(fila => fila.join(','))
      ].join('\n');
      
      nombreArchivo = `ruta_optimizada_${new Date().toISOString().split('T')[0]}.csv`;
      tipoMIME = 'text/csv';
    }
    
    // Crear enlace de descarga
    const blob = new Blob([contenido], { type: `${tipoMIME};charset=utf-8;` });
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement('a');
    enlace.href = url;
    enlace.download = nombreArchivo;
    document.body.appendChild(enlace);
    enlace.click();
    document.body.removeChild(enlace);
    URL.revokeObjectURL(url);
    
    showToast('Éxito', `Ruta exportada correctamente como ${nombreArchivo}`, 'success');
  } catch (error) {
    console.error('Error al exportar la ruta:', error);
    showToast('Error', 'No se pudo exportar la ruta', 'error');
  }
}

// Función para compartir la ruta
function compartirRuta(datos) {
  if (navigator.share) {
    navigator.share({
      title: 'Ruta Optimizada',
      text: `Ruta optimizada con ${datos.coordenadas.length} puntos y ${(datos.distancia / 1000).toFixed(2)} km de distancia`,
      url: window.location.href
    }).catch(error => {
      console.error('Error al compartir:', error);
      showToast('Error', 'No se pudo compartir la ruta', 'error');
    });
  } else {
    // Fallback para navegadores que no soportan Web Share API
    const mensaje = `Ruta optimizada con ${datos.coordenadas.length} puntos y ${(datos.distancia / 1000).toFixed(2)} km de distancia`;
    prompt('Compartir ruta (copia el enlace):', window.location.href + '\n\n' + mensaje);
    showToast('Información', 'Enlace copiado al portapapeles', 'info');
  }
}

// Funciones de carga manual centralizadas
async function cargarClientesManual() {
    console.log("🔄 Carga manual de clientes iniciada...");
    showToast("Info", "Cargando clientes manualmente...", "info");
    
    try {
        const response = await apiCall('/api/clientes');
        console.log("✅ Clientes cargados:", response);
        
        if (response && response.clientes) {
            // Actualizar tabla si existe
            const tbody = document.querySelector('#tabla-clientes tbody');
            if (tbody) {
                tbody.innerHTML = '';
                response.clientes.forEach(cliente => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${cliente.id}</td>
                        <td>${cliente.nombre}</td>
                        <td>${cliente.distrito}</td>
                        <td><span class="badge bg-primary">P${cliente.prioridad}</span></td>
                        <td>${formatNumber(cliente.pedido)} kg</td>
                        <td>${cliente.ventana_inicio} - ${cliente.ventana_fin}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="verDetalle(${cliente.id})">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    `;
                });
            }
            
            // Actualizar contador
            const contador = document.getElementById('total-clientes');
            if (contador) {
                contador.textContent = response.clientes.length;
            }
            
            showToast("Éxito", `${response.clientes.length} clientes cargados correctamente`, "success");
        }
    } catch (error) {
        console.error("❌ Error al cargar clientes:", error);
        showToast("Error", "Error al cargar clientes: " + error.message, "error");
    }
}

async function cargarVehiculosManual() {
    console.log("🔄 Carga manual de vehículos iniciada...");
    showToast("Info", "Cargando vehículos manualmente...", "info");
    
    try {
        const response = await apiCall('/api/vehiculos');
        console.log("✅ Vehículos cargados:", response);
        
        if (response && response.vehiculos) {
            // Actualizar tabla si existe
            const tbody = document.querySelector('#tabla-vehiculos tbody');
            if (tbody) {
                tbody.innerHTML = '';
                response.vehiculos.forEach(vehiculo => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${vehiculo.id}</td>
                        <td>${vehiculo.placa}</td>
                        <td>${vehiculo.modelo}</td>
                        <td>${formatNumber(vehiculo.capacidad)} kg</td>
                        <td><span class="badge bg-success">Disponible</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="verDetalle(${vehiculo.id})">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    `;
                });
            }
            
            // Actualizar contador
            const contador = document.getElementById('total-vehiculos');
            if (contador) {
                contador.textContent = response.vehiculos.length;
            }
            
            showToast("Éxito", `${response.vehiculos.length} vehículos cargados correctamente`, "success");
        }
    } catch (error) {
        console.error("❌ Error al cargar vehículos:", error);
        showToast("Error", "Error al cargar vehículos: " + error.message, "error");
    }
}

async function cargarEstadisticasManual() {
    console.log("🔄 Carga manual de estadísticas iniciada...");
    showToast("Info", "Actualizando estadísticas...", "info");
    
    try {
        const [clientesResponse, vehiculosResponse] = await Promise.all([
            apiCall('/api/clientes'),
            apiCall('/api/vehiculos')
        ]);
        
        if (clientesResponse && clientesResponse.clientes) {
            const clientes = clientesResponse.clientes;
            
            // Actualizar contadores
            const clientesCount = document.querySelector('.card-title:contains("Clientes")') || 
                                document.getElementById('total-clientes');
            if (clientesCount) {
                clientesCount.textContent = clientes.length;
            }
            
            // Calcular total de pedidos
            const totalPedidos = clientes.reduce((sum, c) => sum + (c.pedido || 0), 0);
            const pedidosElement = document.getElementById('pedidos-total');
            if (pedidosElement) {
                animateValue(pedidosElement, 0, totalPedidos, 1000);
            }
        }
        
        if (vehiculosResponse && vehiculosResponse.vehiculos) {
            const vehiculos = vehiculosResponse.vehiculos;
            
            // Actualizar contador de vehículos
            const vehiculosCount = document.querySelector('.card-title:contains("Vehículos")') || 
                                 document.getElementById('total-vehiculos');
            if (vehiculosCount) {
                vehiculosCount.textContent = vehiculos.length;
            }
            
            // Calcular capacidad total
            const capacidadTotal = vehiculos.reduce((sum, v) => sum + (v.capacidad || 0), 0);
            const capacidadElement = document.getElementById('capacidad-total');
            if (capacidadElement) {
                animateValue(capacidadElement, 0, capacidadTotal, 1000);
            }
        }
        
        showToast("Éxito", "Estadísticas actualizadas correctamente", "success");
    } catch (error) {
        console.error("❌ Error al cargar estadísticas:", error);
        showToast("Error", "Error al cargar estadísticas: " + error.message, "error");
    }
}

function mostrarDebugInfo() {
    const info = `
🔍 INFORMACIÓN DE DEBUG:
• Leaflet disponible: ${typeof L !== 'undefined' ? '✅' : '❌'}
• Bootstrap disponible: ${typeof bootstrap !== 'undefined' ? '✅' : '❌'}
• AppUtils disponible: ${typeof window.AppUtils !== 'undefined' ? '✅' : '❌'}
• URL actual: ${window.location.href}
• Página: ${document.title}
• Scripts globales: ✅ Cargados
    `;
    
    console.log(info);
    alert(info);
}

// Hacer funciones disponibles globalmente para compatibilidad (excepto cargarMapaManual que se eliminó)
window.cargarClientesManual = cargarClientesManual;
window.cargarVehiculosManual = cargarVehiculosManual;
window.cargarEstadisticasManual = cargarEstadisticasManual;
window.mostrarDebugInfo = mostrarDebugInfo;