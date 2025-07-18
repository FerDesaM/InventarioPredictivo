/**
 * Inventory CRUD JavaScript Module
 * Maneja las operaciones CRUD del inventario para empleados
 */

// Estado global del inventario
let inventoryState = {
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    perPage: 10,
    currentView: 'table',
    isLoading: false,
    currentFilters: {},
    currentQuery: '',
    sortBy: 'nombre_producto',
    sortOrder: 'asc'
};

// Inicializar el módulo de inventario
function initializeInventory() {
    console.log('Inicializando módulo de inventario...');
    
    // Cargar inventario inicial
    loadInventory();
    
    // Configurar event listeners
    setupInventoryEventListeners();
    
    // Configurar auto-refresh cada 5 minutos
    setInterval(refreshInventory, 300000);
}

// Configurar event listeners
function setupInventoryEventListeners() {
    // Navegación de páginas
    document.getElementById('prev-page')?.addEventListener('click', () => changePage(-1));
    document.getElementById('next-page')?.addEventListener('click', () => changePage(1));
    
    // Ordenamiento de tabla
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', () => {
            const sortField = header.dataset.sort;
            handleSort(sortField);
        });
    });
    
    // Cambio de vista
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            changeView(view);
        });
    });
}

// Cargar inventario desde la API
async function loadInventory(page = 1, filters = {}, query = '') {
    if (inventoryState.isLoading) return;
    
    inventoryState.isLoading = true;
    showTableLoading(true);
    
    try {
        const params = new URLSearchParams({
            page: page,
            per_page: inventoryState.perPage,
            order_by: `${inventoryState.sortOrder === 'desc' ? '-' : ''}${inventoryState.sortBy}`,
            ...filters
        });
        
        if (query) {
            params.append('query', query);
        }
        
        const response = await fetch(`/api/empleado/inventario/?${params}`);
        const data = await response.json();
        
        if (data.success) {
            updateInventoryDisplay(data.data, data.pagination);
            updatePaginationInfo(data.pagination);
            updateQuickStats();
        } else {
            showToast('Error al cargar inventario: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading inventory:', error);
        showToast('Error de conexión al cargar inventario', 'error');
    } finally {
        inventoryState.isLoading = false;
        showTableLoading(false);
    }
}

// Actualizar la visualización del inventario
function updateInventoryDisplay(products, pagination) {
    inventoryState.currentPage = pagination.current_page;
    inventoryState.totalPages = pagination.total_pages;
    inventoryState.totalItems = pagination.total_items;
    
    if (inventoryState.currentView === 'table') {
        updateTableView(products);
    } else {
        updateGridView(products);
    }
    
    // Mostrar/ocultar estado vacío
    const isEmpty = products.length === 0;
    document.getElementById('empty-state').style.display = isEmpty ? 'block' : 'none';
    document.getElementById('table-view').style.display = isEmpty ? 'none' : 'block';
    document.getElementById('grid-view').style.display = isEmpty ? 'none' : 'block';
}

// Actualizar vista de tabla
function updateTableView(products) {
    const tbody = document.getElementById('inventory-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = products.map(product => `
        <tr data-product-id="${product.producto_id}">
            <td>
                <span class="product-code">${product.producto_id}</span>
            </td>
            <td>
                <div class="product-name" title="${product.nombre_producto}">
                    ${product.nombre_producto}
                </div>
            </td>
            <td>
                <span class="product-class">${product.clase}</span>
            </td>
            <td>
                <span class="price">S/. ${product.precio_unitario}</span>
            </td>
            <td>
                <span class="stock-value stock-${product.stock_status}">
                    ${product.stock}
                </span>
            </td>
            <td>
                <span class="expiry-date ${isExpiringSoon(product.fecha_vencimiento) ? 'expiry-warning' : ''}">
                    ${formatDate(product.fecha_vencimiento)}
                </span>
            </td>
            <td>
                <span class="status-badge status-${getProductStatus(product)}">
                    ${getProductStatusText(product)}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn action-btn-view" onclick="viewProductDetails('${product.producto_id}')" title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn action-btn-sell" 
                            onclick="openSaleModal('${product.producto_id}')" 
                            ${product.stock <= 0 ? 'disabled' : ''} 
                            title="Vender producto">
                        <i class="fas fa-shopping-cart"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Actualizar vista de cuadrícula
function updateGridView(products) {
    const grid = document.getElementById('products-grid');
    if (!grid) return;
    
    grid.innerHTML = products.map(product => `
        <div class="product-card" data-product-id="${product.producto_id}">
            <div class="product-card-header">
                <div>
                    <h4 class="product-card-title">${product.nombre_producto}</h4>
                    <span class="product-card-code">${product.producto_id}</span>
                </div>
                <span class="status-badge status-${getProductStatus(product)}">
                    ${getProductStatusText(product)}
                </span>
            </div>
            <div class="product-card-body">
                <div class="product-card-info">
                    <span>Clase:</span>
                    <span class="product-class">${product.clase}</span>
                </div>
                <div class="product-card-info">
                    <span>Precio:</span>
                    <span class="price">S/. ${product.precio_unitario}</span>
                </div>
                <div class="product-card-info">
                    <span>Stock:</span>
                    <span class="stock-value stock-${product.stock_status}">${product.stock}</span>
                </div>
                <div class="product-card-info">
                    <span>Vence:</span>
                    <span class="expiry-date ${isExpiringSoon(product.fecha_vencimiento) ? 'expiry-warning' : ''}">
                        ${formatDate(product.fecha_vencimiento)}
                    </span>
                </div>
            </div>
            <div class="product-card-footer">
                <button class="action-btn action-btn-view" onclick="viewProductDetails('${product.producto_id}')">
                    <i class="fas fa-eye"></i> Ver
                </button>
                <button class="action-btn action-btn-sell" 
                        onclick="openSaleModal('${product.producto_id}')" 
                        ${product.stock <= 0 ? 'disabled' : ''}>
                    <i class="fas fa-shopping-cart"></i> Vender
                </button>
            </div>
        </div>
    `).join('');
}

// Actualizar información de paginación
function updatePaginationInfo(pagination) {
    const info = document.getElementById('pagination-info');
    if (info) {
        const start = (pagination.current_page - 1) * inventoryState.perPage + 1;
        const end = Math.min(start + inventoryState.perPage - 1, pagination.total_items);
        info.textContent = `Mostrando ${start}-${end} de ${pagination.total_items} productos`;
    }
    
    // Actualizar controles de paginación
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    if (prevBtn) prevBtn.disabled = !pagination.has_previous;
    if (nextBtn) nextBtn.disabled = !pagination.has_next;
    
    // Actualizar números de página
    updatePageNumbers(pagination);
}

// Actualizar números de página
function updatePageNumbers(pagination) {
    const container = document.getElementById('page-numbers');
    if (!container) return;
    
    const currentPage = pagination.current_page;
    const totalPages = pagination.total_pages;
    const maxVisible = 5;
    
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage + 1 < maxVisible) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    let html = '';
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <button class="page-number ${i === currentPage ? 'active' : ''}" 
                    onclick="goToPage(${i})">
                ${i}
            </button>
        `;
    }
    
    container.innerHTML = html;
}

// Cambiar página
function changePage(direction) {
    const newPage = inventoryState.currentPage + direction;
    if (newPage >= 1 && newPage <= inventoryState.totalPages) {
        goToPage(newPage);
    }
}

// Ir a página específica
function goToPage(page) {
    if (page !== inventoryState.currentPage) {
        loadInventory(page, inventoryState.currentFilters, inventoryState.currentQuery);
    }
}

// Manejar ordenamiento
function handleSort(field) {
    if (inventoryState.sortBy === field) {
        inventoryState.sortOrder = inventoryState.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        inventoryState.sortBy = field;
        inventoryState.sortOrder = 'asc';
    }
    
    // Actualizar iconos de ordenamiento
    updateSortIcons(field, inventoryState.sortOrder);
    
    // Recargar con nuevo ordenamiento
    loadInventory(1, inventoryState.currentFilters, inventoryState.currentQuery);
}

// Actualizar iconos de ordenamiento
function updateSortIcons(activeField, order) {
    document.querySelectorAll('.sortable').forEach(header => {
        const icon = header.querySelector('.sort-icon');
        const field = header.dataset.sort;
        
        header.classList.remove('sorted');
        
        if (field === activeField) {
            header.classList.add('sorted');
            icon.className = `fas fa-sort-${order === 'asc' ? 'up' : 'down'} sort-icon`;
        } else {
            icon.className = 'fas fa-sort sort-icon';
        }
    });
}

// Cambiar vista (tabla/cuadrícula)
function changeView(view) {
    inventoryState.currentView = view;
    
    // Actualizar botones de vista
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
    
    // Mostrar/ocultar vistas
    document.getElementById('table-view').classList.toggle('active', view === 'table');
    document.getElementById('grid-view').classList.toggle('active', view === 'grid');
    
    // Si estamos cambiando a grid view, actualizar la vista
    if (view === 'grid') {
        const currentData = getCurrentInventoryData();
        if (currentData.length > 0) {
            updateGridView(currentData);
        }
    }
}

// Obtener datos actuales del inventario
function getCurrentInventoryData() {
    const rows = document.querySelectorAll('#inventory-table-body tr');
    return Array.from(rows).map(row => {
        const productId = row.dataset.productId;
        // Aquí podrías extraer más datos de la fila si es necesario
        return { producto_id: productId };
    });
}

// Ver detalles del producto
async function viewProductDetails(productId) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/empleado/producto/${productId}/`);
        const data = await response.json();
        
        if (data.success) {
            showProductDetailsModal(data.data);
        } else {
            showToast('Error al cargar detalles: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading product details:', error);
        showToast('Error de conexión al cargar detalles', 'error');
    } finally {
        showLoading(false);
    }
}

// Mostrar modal de detalles del producto
function showProductDetailsModal(product) {
    // Crear modal dinámicamente si no existe
    let modal = document.getElementById('product-details-modal');
    if (!modal) {
        modal = createProductDetailsModal();
        document.body.appendChild(modal);
    }
    
    // Llenar datos del modal
    document.getElementById('detail-product-name').textContent = product.nombre_producto;
    document.getElementById('detail-product-code').textContent = product.producto_id;
    document.getElementById('detail-product-class').textContent = product.clase;
    document.getElementById('detail-product-price').textContent = product.precio_unitario;
    document.getElementById('detail-product-stock').textContent = product.stock;
    document.getElementById('detail-product-expiry').textContent = formatDate(product.fecha_vencimiento);
    document.getElementById('detail-product-value').textContent = product.total_value;
    document.getElementById('detail-product-status').textContent = getProductStatusText(product);
    
    // Mostrar modal
    modal.classList.add('active');
}

// Crear modal de detalles del producto
function createProductDetailsModal() {
    const modal = document.createElement('div');
    modal.id = 'product-details-modal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">
                    <i class="fas fa-info-circle"></i>
                    Detalles del Producto
                </h3>
                <button class="modal-close" onclick="closeProductDetailsModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="product-details-grid">
                    <div class="detail-item">
                        <label>Nombre:</label>
                        <span id="detail-product-name"></span>
                    </div>
                    <div class="detail-item">
                        <label>Código:</label>
                        <span id="detail-product-code"></span>
                    </div>
                    <div class="detail-item">
                        <label>Clase:</label>
                        <span id="detail-product-class"></span>
                    </div>
                    <div class="detail-item">
                        <label>Precio Unitario:</label>
                        <span>S/. <span id="detail-product-price"></span></span>
                    </div>
                    <div class="detail-item">
                        <label>Stock Disponible:</label>
                        <span id="detail-product-stock"></span>
                    </div>
                    <div class="detail-item">
                        <label>Fecha de Vencimiento:</label>
                        <span id="detail-product-expiry"></span>
                    </div>
                    <div class="detail-item">
                        <label>Valor Total:</label>
                        <span>S/. <span id="detail-product-value"></span></span>
                    </div>
                    <div class="detail-item">
                        <label>Estado:</label>
                        <span id="detail-product-status"></span>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-secondary" onclick="closeProductDetailsModal()">
                    <i class="fas fa-times"></i>
                    Cerrar
                </button>
            </div>
        </div>
    `;
    return modal;
}

// Cerrar modal de detalles
function closeProductDetailsModal() {
    const modal = document.getElementById('product-details-modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Actualizar estadísticas rápidas
async function updateQuickStats() {
    try {
        // Aquí podrías hacer una llamada específica para estadísticas
        // Por ahora, actualizamos con datos del inventario actual
        const totalProducts = inventoryState.totalItems;
        document.getElementById('total-products').textContent = totalProducts;
        
        // Actualizar conteo de stock bajo
        const response = await fetch('/api/empleado/inventario/?stock_status=critical');
        const data = await response.json();
        if (data.success) {
            document.getElementById('low-stock-count').textContent = data.pagination.total_items;
        }
    } catch (error) {
        console.error('Error updating quick stats:', error);
    }
}

// Refrescar inventario
function refreshInventory() {
    console.log('Refrescando inventario...');
    loadInventory(inventoryState.currentPage, inventoryState.currentFilters, inventoryState.currentQuery);
    showToast('Inventario actualizado', 'success');
}

// Mostrar/ocultar loading de tabla
function showTableLoading(show) {
    const loading = document.getElementById('table-loading');
    if (loading) {
        loading.style.display = show ? 'flex' : 'none';
    }
}

// Funciones de utilidad
function isExpiringSoon(dateString, days = 30) {
    const expiryDate = new Date(dateString);
    const today = new Date();
    const diffTime = expiryDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= days && diffDays >= 0;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function getProductStatus(product) {
    if (new Date(product.fecha_vencimiento) < new Date()) {
        return 'expired';
    }
    if (product.stock <= 0) {
        return 'out-of-stock';
    }
    if (product.stock_status === 'critical') {
        return 'critical';
    }
    if (product.stock_status === 'low') {
        return 'low';
    }
    return 'available';
}

function getProductStatusText(product) {
    const status = getProductStatus(product);
    const statusTexts = {
        'expired': 'Vencido',
        'out-of-stock': 'Agotado',
        'critical': 'Crítico',
        'low': 'Bajo',
        'available': 'Disponible'
    };
    return statusTexts[status] || 'Disponible';
}

// Exportar funciones para uso global
window.inventoryModule = {
    initializeInventory,
    loadInventory,
    refreshInventory,
    changePage,
    goToPage,
    changeView,
    viewProductDetails,
    handleSort
};

