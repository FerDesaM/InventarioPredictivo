/**
 * Search and Filter JavaScript Module
 * Maneja las funcionalidades de búsqueda y filtrado del inventario
 */

// Estado global de búsqueda y filtros
let searchState = {
    currentQuery: '',
    activeFilters: {},
    isFiltersVisible: false,
    searchTimeout: null,
    suggestions: [],
    activeSuggestionIndex: -1
};

// Inicializar el módulo de búsqueda
function initializeSearch() {
    console.log('Inicializando módulo de búsqueda...');
    
    // Configurar event listeners
    setupSearchEventListeners();
    
    // Cargar opciones de filtros
    loadFilterOptions();
}

// Configurar event listeners para búsqueda
function setupSearchEventListeners() {
    // Búsqueda principal
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearchInput);
        searchInput.addEventListener('keydown', handleSearchKeydown);
        searchInput.addEventListener('focus', handleSearchFocus);
        searchInput.addEventListener('blur', handleSearchBlur);
    }
    
    // Botón de búsqueda
    const searchBtn = document.querySelector('.search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }
    
    // Botón de código de barras
    const barcodeBtn = document.querySelector('.barcode-btn');
    if (barcodeBtn) {
        barcodeBtn.addEventListener('click', toggleBarcodeSearch);
    }
    
    // Filtros
    setupFilterEventListeners();
    
    // Filtros rápidos
    setupQuickFilters();
}

// Configurar event listeners para filtros
function setupFilterEventListeners() {
    // Todos los campos de filtro
    const filterInputs = [
        'filter-class',
        'filter-stock-status',
        'filter-price-min',
        'filter-price-max',
        'filter-stock-min',
        'filter-stock-max',
        'filter-expiring',
        'filter-order'
    ];
    
    filterInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', updateActiveFilters);
        }
    });
}

// Configurar filtros rápidos
function setupQuickFilters() {
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const filterType = e.currentTarget.onclick.toString().match(/'([^']+)'/)[1];
            applyQuickFilter(filterType);
        });
    });
}

// Manejar entrada de búsqueda
function handleSearchInput(event) {
    const query = event.target.value.trim();
    searchState.currentQuery = query;
    
    // Limpiar timeout anterior
    if (searchState.searchTimeout) {
        clearTimeout(searchState.searchTimeout);
    }
    
    // Configurar nuevo timeout para búsqueda
    searchState.searchTimeout = setTimeout(() => {
        if (query.length >= 2) {
            loadSearchSuggestions(query);
        } else {
            hideSuggestions();
        }
        
        // Realizar búsqueda automática si hay más de 3 caracteres
        if (query.length >= 3) {
            performSearch();
        } else if (query.length === 0) {
            clearSearch();
        }
    }, 300);
}

// Manejar teclas en búsqueda
function handleSearchKeydown(event) {
    const suggestions = document.getElementById('search-suggestions');
    
    switch (event.key) {
        case 'ArrowDown':
            event.preventDefault();
            navigateSearchSuggestions('down');
            break;
        case 'ArrowUp':
            event.preventDefault();
            navigateSearchSuggestions('up');
            break;
        case 'Enter':
            event.preventDefault();
            if (searchState.activeSuggestionIndex >= 0) {
                selectSearchSuggestion(searchState.activeSuggestionIndex);
            } else {
                performSearch();
            }
            break;
        case 'Escape':
            hideSuggestions();
            event.target.blur();
            break;
    }
}

// Manejar foco en búsqueda
function handleSearchFocus(event) {
    const query = event.target.value.trim();
    if (query.length >= 2 && searchState.suggestions.length > 0) {
        showSuggestions();
    }
}

// Manejar pérdida de foco en búsqueda
function handleSearchBlur(event) {
    // Retrasar para permitir clics en sugerencias
    setTimeout(() => {
        hideSuggestions();
    }, 200);
}

// Cargar sugerencias de búsqueda
async function loadSearchSuggestions(query) {
    try {
        const response = await fetch(`/api/empleado/sugerencias/?q=${encodeURIComponent(query)}&limit=8`);
        const data = await response.json();
        
        if (data.success) {
            searchState.suggestions = data.suggestions;
            displaySearchSuggestions(data.suggestions, query);
        }
    } catch (error) {
        console.error('Error loading search suggestions:', error);
    }
}

// Mostrar sugerencias de búsqueda
function displaySearchSuggestions(suggestions, query) {
    const container = document.getElementById('search-suggestions');
    if (!container || suggestions.length === 0) {
        hideSuggestions();
        return;
    }
    
    container.innerHTML = suggestions.map((suggestion, index) => `
        <div class="suggestion-item" data-index="${index}" onclick="selectSearchSuggestion(${index})">
            ${highlightSearchMatch(suggestion, query)}
        </div>
    `).join('');
    
    showSuggestions();
}

// Mostrar contenedor de sugerencias
function showSuggestions() {
    const container = document.getElementById('search-suggestions');
    if (container) {
        container.style.display = 'block';
    }
}

// Ocultar sugerencias
function hideSuggestions() {
    const container = document.getElementById('search-suggestions');
    if (container) {
        container.style.display = 'none';
    }
    searchState.activeSuggestionIndex = -1;
}

// Navegar por sugerencias
function navigateSearchSuggestions(direction) {
    const suggestions = document.querySelectorAll('.suggestion-item');
    if (suggestions.length === 0) return;
    
    // Limpiar selección anterior
    suggestions.forEach(item => item.classList.remove('active'));
    
    // Calcular nuevo índice
    if (direction === 'down') {
        searchState.activeSuggestionIndex = 
            (searchState.activeSuggestionIndex + 1) % suggestions.length;
    } else {
        searchState.activeSuggestionIndex = 
            searchState.activeSuggestionIndex <= 0 
                ? suggestions.length - 1 
                : searchState.activeSuggestionIndex - 1;
    }
    
    // Aplicar nueva selección
    suggestions[searchState.activeSuggestionIndex].classList.add('active');
}

// Seleccionar sugerencia
function selectSearchSuggestion(index) {
    if (index >= 0 && index < searchState.suggestions.length) {
        const suggestion = searchState.suggestions[index];
        document.getElementById('search-input').value = suggestion;
        searchState.currentQuery = suggestion;
        hideSuggestions();
        performSearch();
    }
}

// Realizar búsqueda
function performSearch() {
    const query = searchState.currentQuery || document.getElementById('search-input').value.trim();
    
    // Actualizar estado
    searchState.currentQuery = query;
    
    // Actualizar información de resultados
    updateResultsInfo(query);
    
    // Cargar inventario con búsqueda
    if (window.inventoryModule) {
        window.inventoryModule.loadInventory(1, searchState.activeFilters, query);
    }
    
    hideSuggestions();
}

// Limpiar búsqueda
function clearSearch() {
    document.getElementById('search-input').value = '';
    searchState.currentQuery = '';
    hideSuggestions();
    
    // Limpiar filtros también
    clearFilters();
    
    // Recargar inventario sin filtros
    if (window.inventoryModule) {
        window.inventoryModule.loadInventory(1, {}, '');
    }
    
    updateResultsInfo('');
}

// Alternar visibilidad de filtros
function toggleFilters() {
    const filtersPanel = document.getElementById('filters-panel');
    if (!filtersPanel) return;
    
    searchState.isFiltersVisible = !searchState.isFiltersVisible;
    filtersPanel.classList.toggle('active', searchState.isFiltersVisible);
    
    // Actualizar texto del botón
    const filterBtn = document.querySelector('[onclick="toggleFilters()"]');
    if (filterBtn) {
        const icon = filterBtn.querySelector('i');
        icon.className = searchState.isFiltersVisible ? 'fas fa-filter-circle-xmark' : 'fas fa-filter';
    }
}

// Actualizar filtros activos
function updateActiveFilters() {
    const filters = {};
    
    // Recopilar valores de filtros
    const filterMappings = {
        'filter-class': 'clase',
        'filter-stock-status': 'stock_status',
        'filter-price-min': 'precio_min',
        'filter-price-max': 'precio_max',
        'filter-stock-min': 'stock_min',
        'filter-stock-max': 'stock_max',
        'filter-expiring': 'expiring_soon',
        'filter-order': 'order_by'
    };
    
    Object.entries(filterMappings).forEach(([elementId, filterKey]) => {
        const element = document.getElementById(elementId);
        if (element && element.value) {
            filters[filterKey] = element.value;
        }
    });
    
    searchState.activeFilters = filters;
    
    // Actualizar contador de filtros activos
    updateActiveFiltersCount();
}

// Aplicar filtros
function applyFilters() {
    updateActiveFilters();
    
    // Realizar búsqueda con filtros
    if (window.inventoryModule) {
        window.inventoryModule.loadInventory(1, searchState.activeFilters, searchState.currentQuery);
    }
    
    // Ocultar panel de filtros en móvil
    if (window.innerWidth <= 768) {
        toggleFilters();
    }
    
    showToast('Filtros aplicados', 'success');
}

// Limpiar filtros
function clearFilters() {
    // Limpiar campos de filtro
    const filterInputs = [
        'filter-class',
        'filter-stock-status',
        'filter-price-min',
        'filter-price-max',
        'filter-stock-min',
        'filter-stock-max',
        'filter-expiring',
        'filter-order'
    ];
    
    filterInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.value = '';
        }
    });
    
    // Limpiar filtros rápidos
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    searchState.activeFilters = {};
    updateActiveFiltersCount();
    
    // Recargar inventario
    if (window.inventoryModule) {
        window.inventoryModule.loadInventory(1, {}, searchState.currentQuery);
    }
    
    showToast('Filtros limpiados', 'info');
}

// Aplicar filtro rápido
function applyQuickFilter(filterType) {
    // Limpiar filtros anteriores
    clearFilters();
    
    // Aplicar filtro específico
    switch (filterType) {
        case 'low-stock':
            document.getElementById('filter-stock-status').value = 'low';
            break;
        case 'expiring-soon':
            document.getElementById('filter-expiring').value = '30';
            break;
        case 'high-value':
            document.getElementById('filter-price-min').value = '50';
            break;
        case 'recently-added':
            document.getElementById('filter-order').value = '-id';
            break;
    }
    
    // Marcar botón como activo
    document.querySelectorAll('.quick-filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Aplicar filtros
    applyFilters();
}

// Actualizar contador de filtros activos
function updateActiveFiltersCount() {
    const count = Object.keys(searchState.activeFilters).length;
    const counter = document.getElementById('active-filters-count');
    
    if (counter) {
        if (count > 0) {
            counter.textContent = count;
            counter.style.display = 'inline';
        } else {
            counter.style.display = 'none';
        }
    }
}

// Actualizar información de resultados
function updateResultsInfo(query) {
    const resultsCount = document.getElementById('results-count');
    if (!resultsCount) return;
    
    let text = 'Mostrando todos los productos';
    
    if (query) {
        text = `Resultados para: "${query}"`;
    }
    
    const filterCount = Object.keys(searchState.activeFilters).length;
    if (filterCount > 0) {
        text += ` (${filterCount} filtro${filterCount > 1 ? 's' : ''} aplicado${filterCount > 1 ? 's' : ''})`;
    }
    
    resultsCount.textContent = text;
}

// Alternar búsqueda por código de barras
function toggleBarcodeSearch() {
    const searchInput = document.getElementById('search-input');
    const barcodeBtn = document.querySelector('.barcode-btn');
    
    if (!searchInput || !barcodeBtn) return;
    
    const isBarcode = barcodeBtn.classList.contains('active');
    
    if (isBarcode) {
        // Desactivar modo código de barras
        barcodeBtn.classList.remove('active');
        searchInput.placeholder = 'Buscar productos por nombre, código o clase...';
        searchInput.pattern = '';
    } else {
        // Activar modo código de barras
        barcodeBtn.classList.add('active');
        searchInput.placeholder = 'Escanear o escribir código de barras...';
        searchInput.pattern = '[A-Z0-9]+';
        searchInput.focus();
    }
}

// Buscar por código de barras específico
async function searchByBarcode(barcode) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/empleado/codigo/${encodeURIComponent(barcode)}/`);
        const data = await response.json();
        
        if (data.success) {
            // Mostrar producto encontrado
            displayBarcodeResult(data.data);
        } else {
            showToast('Código de barras no encontrado', 'warning');
        }
    } catch (error) {
        console.error('Error searching by barcode:', error);
        showToast('Error al buscar código de barras', 'error');
    } finally {
        showLoading(false);
    }
}

// Mostrar resultado de búsqueda por código de barras
function displayBarcodeResult(product) {
    // Limpiar búsqueda actual
    clearSearch();
    
    // Establecer búsqueda específica
    document.getElementById('search-input').value = product.producto_id;
    searchState.currentQuery = product.producto_id;
    
    // Realizar búsqueda
    performSearch();
    
    // Mostrar toast con información del producto
    showToast(`Producto encontrado: ${product.nombre_producto}`, 'success');
}

// Cargar opciones de filtros
async function loadFilterOptions() {
    try {
        // Esta función podría cargar opciones dinámicas desde el servidor
        // Por ahora, las opciones están en el template HTML
        console.log('Opciones de filtros cargadas desde template');
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

// Cambiar vista (tabla/cuadrícula)
function changeView(view) {
    // Actualizar botones de vista
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
    
    // Delegar a módulo de inventario
    if (window.inventoryModule) {
        window.inventoryModule.changeView(view);
    }
}

// Funciones de utilidad
function highlightSearchMatch(text, query) {
    if (!query) return text;
    
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Detectar si es un código de barras válido
function isValidBarcode(text) {
    // Códigos de barras típicos: solo letras mayúsculas y números, longitud 6-20
    return /^[A-Z0-9]{6,20}$/.test(text);
}

// Manejar entrada de código de barras desde escáner
function handleBarcodeInput(barcode) {
    if (isValidBarcode(barcode)) {
        document.getElementById('search-input').value = barcode;
        searchByBarcode(barcode);
    }
}

// Configurar listener para escáner de código de barras
function setupBarcodeScanner() {
    let barcodeBuffer = '';
    let barcodeTimeout;
    
    document.addEventListener('keypress', (event) => {
        // Solo procesar si el foco está en el campo de búsqueda
        const searchInput = document.getElementById('search-input');
        if (document.activeElement !== searchInput) return;
        
        // Acumular caracteres
        barcodeBuffer += event.key;
        
        // Limpiar timeout anterior
        if (barcodeTimeout) {
            clearTimeout(barcodeTimeout);
        }
        
        // Configurar timeout para procesar código
        barcodeTimeout = setTimeout(() => {
            if (barcodeBuffer.length >= 6 && isValidBarcode(barcodeBuffer)) {
                handleBarcodeInput(barcodeBuffer);
            }
            barcodeBuffer = '';
        }, 100);
    });
}

// Inicializar escáner de código de barras
setupBarcodeScanner();

// Exportar funciones para uso global
window.searchModule = {
    initializeSearch,
    performSearch,
    clearSearch,
    toggleFilters,
    applyFilters,
    clearFilters,
    applyQuickFilter,
    changeView,
    toggleBarcodeSearch,
    searchByBarcode
};

