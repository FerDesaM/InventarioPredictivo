/**
 * Sales Handler JavaScript Module
 * Maneja las operaciones de venta y actualización de stock
 */

// Estado global de ventas
let salesState = {
    selectedProduct: null,
    currentSale: null,
    isProcessing: false,
    dailySummary: {
        sales_count: 0,
        revenue: 0,
        products_sold: 0
    }
};

// Inicializar el módulo de ventas
function initializeSales() {
    console.log('Inicializando módulo de ventas...');
    
    // Cargar resumen diario
    loadDailySummary();
    
    // Configurar event listeners
    setupSalesEventListeners();
    
    // Auto-actualizar resumen cada 2 minutos
    setInterval(loadDailySummary, 120000);
}

// Configurar event listeners para ventas
function setupSalesEventListeners() {
    // Búsqueda de productos en tiempo real
    const productSearch = document.getElementById('product-search');
    if (productSearch) {
        productSearch.addEventListener('input', debounce(handleProductSearch, 300));
        productSearch.addEventListener('keydown', handleProductSearchKeydown);
    }
    
    // Cantidad - actualizar cálculos
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        quantityInput.addEventListener('input', calculateSalePreview);
        quantityInput.addEventListener('change', validateQuantity);
    }
    
    // Tipo de comprobante
    const receiptType = document.getElementById('receipt-type');
    if (receiptType) {
        receiptType.addEventListener('change', updateReceiptType);
    }
}

function updateReceiptType(event) {
    const selected = event.target.value;

    if (selected === 'factura') {
        document.getElementById('ruc-field').style.display = 'block'; // Muestra el campo RUC
    } else {
        document.getElementById('ruc-field').style.display = 'none';  // Oculta el campo RUC
    }
}
// Manejar búsqueda de productos
async function handleProductSearch(event) {
    const query = event.target.value.trim();
    
    if (query.length < 2) {
        hideSuggestions();
        clearSelectedProduct();
        return;
    }
    
    try {
        // Buscar sugerencias
        const response = await fetch(`/api/empleado/sugerencias/?q=${encodeURIComponent(query)}&limit=5`);
        const data = await response.json();
        
        if (data.success && data.suggestions.length > 0) {
            showSuggestions(data.suggestions, query);
        } else {
            hideSuggestions();
        }
        
        // Si parece un código de barras, buscar directamente
        if (query.length >= 6 && /^[A-Z0-9]+$/.test(query)) {
            searchByBarcode(query);
        }
        
    } catch (error) {
        console.error('Error searching products:', error);
        hideSuggestions();
    }
}

// Manejar teclas en búsqueda de productos
function handleProductSearchKeydown(event) {
    const suggestions = document.getElementById('product-suggestions');
    const activeSuggestion = suggestions?.querySelector('.suggestion-item.active');
    
    switch (event.key) {
        case 'ArrowDown':
            event.preventDefault();
            navigateSuggestions('down');
            break;
        case 'ArrowUp':
            event.preventDefault();
            navigateSuggestions('up');
            break;
        case 'Enter':
            event.preventDefault();
            if (activeSuggestion) {
                selectSuggestion(activeSuggestion.textContent);
            }
            break;
        case 'Escape':
            hideSuggestions();
            break;
    }
}

// Mostrar sugerencias de productos
function showSuggestions(suggestions, query) {
    const container = document.getElementById('product-suggestions');
    if (!container) return;
    
    container.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-item" onclick="selectSuggestion('${suggestion}')">
            ${highlightMatch(suggestion, query)}
        </div>
    `).join('');
    
    container.style.display = 'block';
}

// Ocultar sugerencias
function hideSuggestions() {
    const container = document.getElementById('product-suggestions');
    if (container) {
        container.style.display = 'none';
        container.innerHTML = '';
    }
}

// Navegar por sugerencias con teclado
function navigateSuggestions(direction) {
    const suggestions = document.querySelectorAll('.suggestion-item');
    const current = document.querySelector('.suggestion-item.active');
    
    if (suggestions.length === 0) return;
    
    let index = -1;
    if (current) {
        index = Array.from(suggestions).indexOf(current);
        current.classList.remove('active');
    }
    
    if (direction === 'down') {
        index = (index + 1) % suggestions.length;
    } else {
        index = index <= 0 ? suggestions.length - 1 : index - 1;
    }
    
    suggestions[index].classList.add('active');
}

// Seleccionar sugerencia
async function selectSuggestion(productName) {
    hideSuggestions();
    
    // Buscar el producto por nombre
    try {
        const response = await fetch(`/api/empleado/buscar/?query=${encodeURIComponent(productName)}&per_page=1`);
        const data = await response.json();
        
        if (data.success && data.data.length > 0) {
            selectProduct(data.data[0]);
        } else {
            showToast('Producto no encontrado', 'warning');
        }
    } catch (error) {
        console.error('Error selecting product:', error);
        showToast('Error al buscar producto', 'error');
    }
}

// Buscar por código de barras
async function searchByBarcode(barcode) {
    try {
        const response = await fetch(`/api/empleado/codigo/${barcode}/`);
        const data = await response.json();
        
        if (data.success) {
            selectProduct(data.data);
            hideSuggestions();
        }
    } catch (error) {
        console.error('Error searching by barcode:', error);
    }
}

// Seleccionar producto para venta
function selectProduct(product) {
    salesState.selectedProduct = product;
    
    // Actualizar UI
    document.getElementById('product-search').value = product.nombre_producto;
    
    // Mostrar información del producto seleccionado
    const selectedProductDiv = document.getElementById('selected-product');
    if (selectedProductDiv) {
        document.getElementById('selected-product-name').textContent = product.nombre_producto;
        document.getElementById('selected-product-details').textContent = 
            `${product.clase} - Código: ${product.producto_id}`;
        document.getElementById('selected-product-stock').textContent = product.stock;
        
        // Aplicar clase de estado de stock
        const stockElement = document.getElementById('selected-product-stock');
        stockElement.className = `stock-value stock-${product.stock_status}`;
        
        selectedProductDiv.style.display = 'block';
    }
    
    // Configurar cantidad máxima
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        quantityInput.max = product.stock;
        quantityInput.value = 1;
    }
    
    // Calcular preview inicial
    calculateSalePreview();
    
    // Habilitar botón de procesar venta
    updateProcessSaleButton();
}

// Limpiar producto seleccionado
function clearSelectedProduct() {
    salesState.selectedProduct = null;
    
    const selectedProductDiv = document.getElementById('selected-product');
    if (selectedProductDiv) {
        selectedProductDiv.style.display = 'none';
    }
    
    const summaryDiv = document.getElementById('sale-summary');
    if (summaryDiv) {
        summaryDiv.style.display = 'none';
    }
    
    updateProcessSaleButton();
}

// Calcular preview de la venta
function calculateSalePreview() {
    if (!salesState.selectedProduct) return;
    
    const quantity = parseInt(document.getElementById('quantity')?.value) || 0;
    if (quantity <= 0) {
        document.getElementById('sale-summary').style.display = 'none';
        return;
    }
    
    const unitPrice = salesState.selectedProduct.precio_unitario;
    const subtotal = unitPrice * quantity;
    const igv = subtotal * 0.18;
    const total = subtotal + igv;
    
    // Actualizar UI
    document.getElementById('subtotal').textContent = `S/. ${subtotal.toFixed(2)}`;
    document.getElementById('igv').textContent = `S/. ${igv.toFixed(2)}`;
    document.getElementById('total').textContent = `S/. ${total.toFixed(2)}`;
    
    document.getElementById('sale-summary').style.display = 'block';
    
    updateProcessSaleButton();
}

// Validar cantidad
function validateQuantity() {
    if (!salesState.selectedProduct) return;
    
    const quantityInput = document.getElementById('quantity');
    const quantity = parseInt(quantityInput.value) || 0;
    const maxStock = salesState.selectedProduct.stock;
    
    if (quantity > maxStock) {
        quantityInput.value = maxStock;
        showToast(`Cantidad ajustada al stock disponible: ${maxStock}`, 'warning');
        calculateSalePreview();
    } else if (quantity <= 0) {
        quantityInput.value = 1;
        calculateSalePreview();
    }
}

// Actualizar botón de procesar venta
function updateProcessSaleButton() {
    const button = document.getElementById('process-sale-btn');
    if (!button) return;
    
    const quantity = parseInt(document.getElementById('quantity')?.value) || 0;
    const canProcess = salesState.selectedProduct && 
                      quantity > 0 && 
                      quantity <= salesState.selectedProduct.stock &&
                      !salesState.isProcessing;
    
    button.disabled = !canProcess;
}

// Procesar venta
async function processSale() {
    if (!salesState.selectedProduct || salesState.isProcessing) return;
    
    const quantity = parseInt(document.getElementById('quantity').value);
    const receiptType = document.getElementById('receipt-type').value;
    
    // Validar antes de procesar
    const validation = await validateSaleData(salesState.selectedProduct.producto_id, quantity);
    if (!validation.valid) {
        showToast(validation.error, 'error');
        return;
    }
    
    salesState.isProcessing = true;
    showLoading(true);
    
    try {
        const response = await fetch('/api/empleado/venta/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                producto_id: salesState.selectedProduct.producto_id,
                cantidad: quantity,
                tipo_comprobante: receiptType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mostrar modal de éxito
            showSaleSuccessModal(data.data);
            
            // Limpiar formulario
            clearSaleForm();
            
            // Actualizar inventario y resumen diario
            refreshInventory();
            loadDailySummary();
            
            showToast('Venta procesada exitosamente', 'success');
        } else {
            showToast('Error al procesar venta: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error processing sale:', error);
        showToast('Error de conexión al procesar venta', 'error');
    } finally {
        salesState.isProcessing = false;
        showLoading(false);
        updateProcessSaleButton();
    }
}

// Validar datos de venta
async function validateSaleData(productId, quantity) {
    try {
        const response = await fetch('/api/empleado/validar-venta/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                producto_id: productId,
                cantidad: quantity
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error validating sale:', error);
        return { valid: false, error: 'Error de validación' };
    }
}

// Mostrar modal de éxito de venta
function showSaleSuccessModal(saleData) {
    salesState.currentSale = saleData;
    
    // Llenar datos del modal
    document.getElementById('receipt-code').textContent = saleData.codigo_venta;
    document.getElementById('receipt-product').textContent = saleData.producto_nombre;
    document.getElementById('receipt-quantity').textContent = saleData.cantidad;
    document.getElementById('receipt-total').textContent = `S/. ${saleData.total.toFixed(2)}`;
    document.getElementById('receipt-date').textContent = saleData.fecha_venta;
    document.getElementById('receipt-employee').textContent = saleData.empleado;
    document.getElementById('receipt-remaining-stock').textContent = saleData.stock_restante;
    
    // Mostrar modal
    const modal = document.getElementById('sale-success-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

// Cerrar modal de éxito de venta
function closeSaleSuccessModal() {
    const modal = document.getElementById('sale-success-modal');
    if (modal) {
        modal.classList.remove('active');
    }
    salesState.currentSale = null;
}

// Imprimir recibo
function printReceipt() {
    if (!salesState.currentSale) return;
    
    // Crear ventana de impresión
    const printWindow = window.open('', '_blank');
    const receiptHtml = generateReceiptHtml(salesState.currentSale);
    
    printWindow.document.write(receiptHtml);
    printWindow.document.close();
    printWindow.print();
}

// Generar HTML del recibo
function generateReceiptHtml(saleData) {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Recibo de Venta - ${saleData.codigo_venta}</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 300px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 20px; }
                .receipt-item { display: flex; justify-content: space-between; margin: 5px 0; }
                .total { font-weight: bold; border-top: 1px solid #000; padding-top: 10px; }
                .footer { text-align: center; margin-top: 20px; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>${saleData.farmacia}</h2>
                <p>Recibo de Venta</p>
                <p>Código: ${saleData.codigo_venta}</p>
            </div>
            <div class="receipt-item">
                <span>Producto:</span>
                <span>${saleData.producto_nombre}</span>
            </div>
            <div class="receipt-item">
                <span>Cantidad:</span>
                <span>${saleData.cantidad}</span>
            </div>
            <div class="receipt-item">
                <span>Precio Unit.:</span>
                <span>S/. ${saleData.precio_unitario.toFixed(2)}</span>
            </div>
            <div class="receipt-item">
                <span>Subtotal:</span>
                <span>S/. ${saleData.subtotal.toFixed(2)}</span>
            </div>
            <div class="receipt-item">
                <span>IGV (18%):</span>
                <span>S/. ${saleData.igv.toFixed(2)}</span>
            </div>
            <div class="receipt-item total">
                <span>Total:</span>
                <span>S/. ${saleData.total.toFixed(2)}</span>
            </div>
            <div class="footer">
                <p>Fecha: ${saleData.fecha_venta}</p>
                <p>Empleado: ${saleData.empleado}</p>
                <p>¡Gracias por su compra!</p>
            </div>
        </body>
        </html>
    `;
}

// Limpiar formulario de venta
function clearSaleForm() {
    document.getElementById('product-search').value = '';
    document.getElementById('quantity').value = '1';
    document.getElementById('receipt-type').value = 'boleta';
    
    clearSelectedProduct();
    hideSuggestions();
}

// Cargar resumen diario
async function loadDailySummary() {
    try {
        const response = await fetch('/api/empleado/resumen-diario/');
        const data = await response.json();
        
        if (data.success) {
            updateDailySummaryDisplay(data.data);
        }
    } catch (error) {
        console.error('Error loading daily summary:', error);
    }
}

// Actualizar visualización del resumen diario
function updateDailySummaryDisplay(summary) {
    salesState.dailySummary = summary;
    
    document.getElementById('daily-sales-count').textContent = summary.total_ventas;
    document.getElementById('daily-revenue').textContent = `S/. ${summary.total_ingresos.toFixed(2)}`;
    document.getElementById('daily-products-sold').textContent = summary.productos_vendidos;
}

// Abrir modal de venta desde inventario
function openSaleModal(productId) {
    // Buscar producto y abrir modal
    fetch(`/api/empleado/producto/${productId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSaleModal(data.data);
            } else {
                showToast('Error al cargar producto: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error loading product for sale:', error);
            showToast('Error de conexión', 'error');
        });
}

// Mostrar modal de venta
function showSaleModal(product) {
    salesState.selectedProduct = product;
    
    // Llenar datos del modal
    document.getElementById('modal-product-name').textContent = product.nombre_producto;
    document.getElementById('modal-product-code').textContent = product.producto_id;
    document.getElementById('modal-product-price').textContent = product.precio_unitario.toFixed(2);
    document.getElementById('modal-product-stock').textContent = product.stock;
    document.getElementById('max-quantity').textContent = product.stock;
    
    // Configurar cantidad
    const quantityInput = document.getElementById('modal-quantity');
    quantityInput.max = product.stock;
    quantityInput.value = 1;
    
    // Calcular totales iniciales
    calculateSaleTotal();
    
    // Mostrar modal
    const modal = document.getElementById('sale-modal');
    if (modal) {
        modal.classList.add('active');
    }
}

// Cerrar modal de venta
function closeSaleModal() {
    const modal = document.getElementById('sale-modal');
    if (modal) {
        modal.classList.remove('active');
    }
    salesState.selectedProduct = null;
}

// Ajustar cantidad en modal
function adjustQuantity(change) {
    const input = document.getElementById('modal-quantity');
    const currentValue = parseInt(input.value) || 1;
    const newValue = Math.max(1, Math.min(currentValue + change, parseInt(input.max)));
    
    input.value = newValue;
    calculateSaleTotal();
}

// Calcular total en modal
function calculateSaleTotal() {
    if (!salesState.selectedProduct) return;
    
    const quantity = parseInt(document.getElementById('modal-quantity').value) || 1;
    const unitPrice = salesState.selectedProduct.precio_unitario;
    const subtotal = unitPrice * quantity;
    const igv = subtotal * 0.18;
    const total = subtotal + igv;
    
    // Actualizar UI del modal
    document.getElementById('modal-unit-price').textContent = unitPrice.toFixed(2);
    document.getElementById('modal-calc-quantity').textContent = quantity;
    document.getElementById('modal-subtotal').textContent = subtotal.toFixed(2);
    document.getElementById('modal-igv').textContent = igv.toFixed(2);
    document.getElementById('modal-total').textContent = total.toFixed(2);
    
    // Mostrar advertencias si es necesario
    showSaleWarnings(quantity);
}

// Mostrar advertencias de venta
function showSaleWarnings(quantity) {
    const warningsDiv = document.getElementById('sale-warnings');
    const warningMessage = document.getElementById('warning-message');
    
    if (!salesState.selectedProduct) return;
    
    const product = salesState.selectedProduct;
    let warnings = [];
    
    // Verificar stock bajo después de la venta
    const remainingStock = product.stock - quantity;
    if (remainingStock <= 5) {
        warnings.push(`Advertencia: Quedarán solo ${remainingStock} unidades en stock`);
    }
    
    // Verificar fecha de vencimiento
    if (product.days_to_expire <= 30) {
        warnings.push(`Advertencia: El producto vence en ${product.days_to_expire} días`);
    }
    
    if (warnings.length > 0) {
        warningMessage.textContent = warnings.join('. ');
        warningsDiv.style.display = 'block';
    } else {
        warningsDiv.style.display = 'none';
    }
}

// Confirmar venta desde modal

async function confirmSale() {
    
    
    if (!salesState.selectedProduct) {
        showToast('Selecciona un producto antes de vender', 'error');
        return;
    }
    
    
    const quantity = parseInt(document.getElementById('modal-quantity').value);
    const receiptType = document.getElementById('modal-receipt-type').value;
    const producto = salesState.selectedProduct.producto_id;
   

    
    closeSaleModal();
    salesState.isProcessing = true;
    showLoading(true);
    
    
    try {
        
        const response = await fetch('/api/empleado/venta/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                producto_id: producto,
                cantidad: quantity,
                tipo_comprobante: receiptType
            })
        });

            
       
        const data = await response.json();
        
        if (data.success) {
            showSaleSuccessModal(data.data);
            refreshInventory();
            loadDailySummary();
            showToast('Venta procesada exitosamente', 'success');
        } else {
            showToast('Error al procesar venta: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error processing sale:', error);
        showToast('Error de conexión al procesar venta', 'error');
    } finally {
        salesState.isProcessing = false;
        showLoading(false);
    }
}

// Funciones de utilidad
function highlightMatch(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Exportar funciones para uso global
window.salesModule = {
    initializeSales,
    openSaleModal,
    closeSaleModal,
    processSale,
    confirmSale,
    adjustQuantity,
    calculateSaleTotal,
    clearSaleForm,
    loadDailySummary,
    printReceipt,
    closeSaleSuccessModal
};

