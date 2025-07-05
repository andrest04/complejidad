// Scripts comunes para la aplicación de optimización de rutas

// Variables globales
let mapa = null;
let marcadores = {};
let rutas = [];
let capas = {
    clientes: true,
    rutas: false,
    congestion: false,
    prioridades: false
};

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

function showLoading(message = 'Procesando...') {
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.textContent = message;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

function hideLoading() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (modal) {
        modal.hide();
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
    if (mapa) {
        mapa.remove();
    }
    
    mapa = L.map(containerId).setView(center, zoom);
    
    // Agregar capa de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(mapa);
    
    return mapa;
}

function addDepositMarker(map, position = [-12.0464, -77.0428]) {
    const depositIcon = L.divIcon({
        className: 'custom-div-icon',
        html: '<i class="fas fa-warehouse fa-2x text-primary"></i>',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
    
    return L.marker(position, {icon: depositIcon})
        .addTo(map)
        .bindPopup('<b>Depósito Central</b><br>Punto de partida de todas las rutas');
}

function addClientMarkers(map, clientes) {
    // Limpiar marcadores existentes
    Object.values(marcadores).forEach(marker => map.removeLayer(marker));
    marcadores = {};
    
    clientes.forEach(cliente => {
        const color = getPriorityColor(cliente.prioridad);
        const icon = L.divIcon({
            className: 'custom-div-icon',
            html: `<i class="fas fa-store fa-lg" style="color: ${color}"></i>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
        
        const marker = L.marker([cliente.lat, cliente.lng], {icon: icon})
            .addTo(map)
            .bindPopup(`
                <b>${cliente.nombre}</b><br>
                Prioridad: ${cliente.prioridad}<br>
                Pedido: ${formatNumber(cliente.pedido)} kg<br>
                Ventana: ${cliente.ventana_inicio} - ${cliente.ventana_fin}
            `);
        
        marcadores[cliente.id] = marker;
    });
}

function addRouteLines(map, rutas) {
    // Limpiar rutas existentes
    rutas.forEach(ruta => {
        if (ruta.polyline) {
            map.removeLayer(ruta.polyline);
        }
    });
    
    rutas.forEach((ruta, index) => {
        if (ruta.coordenadas && ruta.coordenadas.length > 0) {
            const color = getRouteColor(index);
            const polyline = L.polyline(ruta.coordenadas, {
                color: color,
                weight: 3,
                opacity: 0.7
            }).addTo(map);
            
            polyline.bindPopup(`
                <b>Ruta ${ruta.id}</b><br>
                Vehículo: ${ruta.placa}<br>
                Distancia: ${formatDistance(ruta.distancia_total)}<br>
                Tiempo: ${formatTime(ruta.tiempo_estimado)}<br>
                Carga: ${formatNumber(ruta.carga_total)} kg
            `);
            
            ruta.polyline = polyline;
        }
    });
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
    showLoading,
    hideLoading,
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
    animateValue
}; 