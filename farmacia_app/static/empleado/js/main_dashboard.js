/**
 * Main Dashboard JavaScript
 * Inicializa y coordina todos los módulos del dashboard de empleado
 */

// Estado global del dashboard
let dashboardState = {
    currentSection: 'inventory',
    isInitialized: false,
    modules: {
        inventory: null,
        sales: null,
        search: null
    }
};

// Inicializar dashboard completo
function initializeDashboard() {
    console.log('Inicializando dashboard de empleado...');
    
    if (dashboardState.isInitialized) {
        console.log('Dashboard ya inicializado');
        return;
    }
    
    try {
        // Inicializar módulos
        initializeModules();
        
        // Configurar navegación
        setupNavigation();
        
        // Configurar utilidades globales
        setupGlobalUtilities();
        
        // Cargar sección inicial
        showSection('inventory');
        
        dashboardState.isInitialized = true;
        console.log('Dashboard inicializado exitosamente');
        
        // Mostrar mensaje de bienvenida
        showToast('Dashboard cargado correctamente', 'success');
        
    } catch (error) {
        console.error('Error inicializando dashboard:', error);
        showToast('Error al cargar dashboard', 'error');
    }
}

// Inicializar todos los módulos
function initializeModules() {
    console.log('Inicializando módulos...');
    
    // Inicializar módulo de búsqueda
    if (window.searchModule) {
        window.searchModule.initializeSearch();
        dashboardState.modules.search = window.searchModule;
    }
    
    // Inicializar módulo de inventario
    if (window.inventoryModule) {
        window.inventoryModule.initializeInventory();
        dashboardState.modules.inventory = window.inventoryModule;
    }
    
    // Inicializar módulo de ventas
    if (window.salesModule) {
        window.salesModule.initializeSales();
        dashboardState.modules.sales = window.salesModule;
    }
    
    // Inicializar historial de ventas
    initializeSalesHistory();
}

// Configurar navegación entre secciones
function setupNavigation() {
    console.log('Configurando navegación...');
    
    // Event listeners para navegación
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            if (section) {
                showSection(section);
            }
        });
    });
    
    // Navegación con teclado
    document.addEventListener('keydown', handleKeyboardNavigation);
}

// Manejar navegación con teclado
function handleKeyboardNavigation(event) {
    // Solo procesar si no hay modales abiertos
    if (document.querySelector('.modal.active')) return;
    
    // Solo procesar si no hay inputs enfocados
    if (document.activeElement.tagName === 'INPUT' || 
        document.activeElement.tagName === 'SELECT' ||
        document.activeElement.tagName === 'TEXTAREA') return;
    
    switch (event.key) {
        case '1':
            showSection('inventory');
            break;
        case '2':
            showSection('sales');
            break;
        case '3':
            showSection('history');
            break;
        case '4':
            showSection('reports');
            break;
        case 'F5':
            event.preventDefault();
            refreshCurrentSection();
            break;
    }
}

// Mostrar sección específica
function showSection(sectionName) {
    console.log(`Mostrando sección: ${sectionName}`);
    
    // Actualizar navegación
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeNavItem = document.querySelector(`[data-section="${sectionName}"]`)?.parentElement;
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
    
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Mostrar sección seleccionada
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Ejecutar lógica específica de la sección
    handleSectionChange(sectionName);
    
    dashboardState.currentSection = sectionName;
}

// Manejar cambio de sección
function handleSectionChange(sectionName) {
    switch (sectionName) {
        case 'inventory':
            // Refrescar inventario si es necesario
            if (dashboardState.modules.inventory) {
                // El inventario ya se carga automáticamente
            }
            break;
            
        case 'sales':
            // Cargar resumen diario
            if (dashboardState.modules.sales) {
                dashboardState.modules.sales.loadDailySummary();
            }
            break;
            
        case 'history':
            // Cargar historial de ventas
            loadSalesHistory();
            break;
            
        case 'reports':
            // Cargar reportes
            loadReports();
            break;
    }
}

// Refrescar sección actual
function refreshCurrentSection() {
    const section = dashboardState.currentSection;
    
    switch (section) {
        case 'inventory':
            if (dashboardState.modules.inventory) {
                dashboardState.modules.inventory.refreshInventory();
            }
            break;
            
        case 'sales':
            if (dashboardState.modules.sales) {
                dashboardState.modules.sales.loadDailySummary();
            }
            break;
            
        case 'history':
            loadSalesHistory();
            break;
            
        case 'reports':
            loadReports();
            break;
    }
    
    showToast('Sección actualizada', 'info');
}

// Inicializar historial de ventas
function initializeSalesHistory() {
    console.log('Inicializando historial de ventas...');
    
    // Configurar filtro de historial
    const historyFilter = document.getElementById('history-filter');
    if (historyFilter) {
        historyFilter.addEventListener('change', loadSalesHistory);
    }
}

// Cargar historial de ventas
async function loadSalesHistory() {
    const days = document.getElementById('history-filter')?.value || 30;
    const page = 1; // Siempre empezar en página 1 al cambiar filtros
    
    try {
        showLoading(true);
        
        const response = await fetch(`/api/empleado/historial/?days=${days}&page=${page}&per_page=10`);
        const data = await response.json();
        
        if (data.success) {
            updateHistoryTable(data.data);
            updateHistoryPagination(data.pagination);
        } else {
            showToast('Error al cargar historial: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading sales history:', error);
        showToast('Error de conexión al cargar historial', 'error');
    } finally {
        showLoading(false);
    }
}

// Actualizar tabla de historial
function updateHistoryTable(sales) {
    const tbody = document.getElementById('history-table-body');
    if (!tbody) return;
    
    if (sales.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">
                    <div style="padding: 40px;">
                        <i class="fas fa-inbox" style="font-size: 48px; color: #ccc; margin-bottom: 16px;"></i>
                        <p>No hay ventas en el período seleccionado</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = sales.map(sale => `
        <tr>
            <td>
                <span class="product-code">${sale.codigo_venta}</span>
            </td>
            <td>${sale.producto_nombre}</td>
            <td class="text-center">${sale.cantidad}</td>
            <td class="text-right">
                <span class="price">S/. ${sale.total}</span>
            </td>
            <td>${sale.fecha}</td>
            <td>
                <span class="status-badge status-${sale.estado === 'completada' ? 'available' : 'critical'}">
                    ${sale.estado}
                </span>
            </td>
            <td>
                <span class="product-class">${sale.tipo_comprobante}</span>
            </td>
        </tr>
    `).join('');
}

// Actualizar paginación del historial
function updateHistoryPagination(pagination) {
    const prevBtn = document.getElementById('history-prev-page');
    const nextBtn = document.getElementById('history-next-page');
    const pageNumbers = document.getElementById('history-page-numbers');
    
    if (prevBtn) prevBtn.disabled = !pagination.has_previous;
    if (nextBtn) nextBtn.disabled = !pagination.has_next;
    
    if (pageNumbers) {
        let html = '';
        for (let i = 1; i <= pagination.total_pages; i++) {
            html += `
                <button class="page-number ${i === pagination.current_page ? 'active' : ''}" 
                        onclick="loadSalesHistoryPage(${i})">
                    ${i}
                </button>
            `;
        }
        pageNumbers.innerHTML = html;
    }
}

// Cargar página específica del historial
function loadSalesHistoryPage(page) {
    const days = document.getElementById('history-filter')?.value || 30;
    
    fetch(`/api/empleado/historial/?days=${days}&page=${page}&per_page=10`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateHistoryTable(data.data);
                updateHistoryPagination(data.pagination);
            }
        })
        .catch(error => {
            console.error('Error loading history page:', error);
            showToast('Error al cargar página', 'error');
        });
}

// Cambiar página del historial
function changeHistoryPage(direction) {
    // Esta función sería llamada por los botones de navegación
    // Implementación similar a la paginación del inventario
}

// Cargar reportes
async function loadReports() {
    console.log('Cargando reportes...');
    
    try {
        // Cargar productos con stock bajo
        await loadLowStockReport();
        
        // Cargar productos más vendidos (esto requeriría una nueva API)
        await loadTopProductsReport();
        
    } catch (error) {
        console.error('Error loading reports:', error);
        showToast('Error al cargar reportes', 'error');
    }
}

// Cargar reporte de stock bajo
async function loadLowStockReport() {
    try {
        const response = await fetch('/api/empleado/inventario/?stock_status=critical&per_page=10');
        const data = await response.json();
        
        if (data.success) {
            updateLowStockList(data.data);
        }
    } catch (error) {
        console.error('Error loading low stock report:', error);
    }
}

// Actualizar lista de stock bajo
function updateLowStockList(products) {
    const container = document.getElementById('low-stock-list');
    if (!container) return;
    
    if (products.length === 0) {
        container.innerHTML = '<p class="text-muted">No hay productos con stock crítico</p>';
        return;
    }
    
    container.innerHTML = products.map(product => `
        <div class="report-item">
            <div class="report-item-info">
                <strong>${product.nombre_producto}</strong>
                <small class="text-muted">${product.producto_id}</small>
            </div>
            <div class="report-item-value">
                <span class="stock-value stock-critical">${product.stock}</span>
            </div>
        </div>
    `).join('');
}

// Cargar reporte de productos más vendidos
async function loadTopProductsReport() {
    // Esta función requeriría una nueva API endpoint
    // Por ahora, mostrar mensaje placeholder
    const container = document.getElementById('top-products-list');
    if (container) {
        container.innerHTML = '<p class="text-muted">Reporte en desarrollo</p>';
    }
}

// Configurar utilidades globales
function setupGlobalUtilities() {
    console.log('Configurando utilidades globales...');
    
    // Configurar auto-refresh
    setupAutoRefresh();
    
    // Configurar manejo de errores global
    setupErrorHandling();
    
    // Configurar shortcuts de teclado
    setupKeyboardShortcuts();
}

// Configurar auto-refresh
function setupAutoRefresh() {
    // Refrescar estadísticas cada 5 minutos
    setInterval(() => {
        if (dashboardState.currentSection === 'inventory') {
            updateQuickStats();
        }
    }, 300000);
}

// Configurar manejo de errores global
function setupErrorHandling() {
    window.addEventListener('error', (event) => {
        console.error('Error global:', event.error);
        showToast('Ha ocurrido un error inesperado', 'error');
    });
    
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Promise rechazada:', event.reason);
        showToast('Error de conexión', 'error');
    });
}

// Configurar shortcuts de teclado
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        // Ctrl/Cmd + R para refrescar
        if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
            event.preventDefault();
            refreshCurrentSection();
        }
        
        // Escape para cerrar modales
        if (event.key === 'Escape') {
            closeAllModals();
        }
    });
}

// Cerrar todos los modales
function closeAllModals() {
    document.querySelectorAll('.modal.active').forEach(modal => {
        modal.classList.remove('active');
    });
}

// Funciones de utilidad global
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.toggle('active', show);
    }
}

function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-header">
            <span class="toast-title">${getToastTitle(type)}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove después del duration
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, duration);
}

function getToastTitle(type) {
    const titles = {
        'success': 'Éxito',
        'error': 'Error',
        'warning': 'Advertencia',
        'info': 'Información'
    };
    return titles[type] || 'Notificación';
}

// Actualizar estadísticas rápidas
async function updateQuickStats() {
    // Esta función sería llamada por el módulo de inventario
    // Aquí solo como placeholder
}

// Exportar funciones principales
window.dashboardMain = {
    initializeDashboard,
    showSection,
    refreshCurrentSection,
    loadSalesHistory,
    loadReports,
    showLoading,
    showToast
};

// Auto-inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDashboard);
} else {
    initializeDashboard();
}

