// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {


    const formDiv = document.getElementById('form-compras');
    const listDiv = document.getElementById('listado-compras');
function mostrarForm(accion) {
  if (accion === 'nueva' || '{{ compra_editar }}' !== '') {
    document.getElementById('listado-compras').style.display = 'none';
    document.getElementById('form-compras').style.display = 'block';
  } else {
    document.getElementById('form-compras').style.display = 'none';
    document.getElementById('listado-compras').style.display = 'block';
  }
}
    function postForm(accion, id) {
      const f = document.createElement('form');
      f.method = 'post';
      f.action = '';
      f.innerHTML = `
        {% csrf_token %}
        <input type="hidden" name="accion" value="${accion}">
        <input type="hidden" name="compra_id" value="${id}">
      `;
      document.body.appendChild(f);
      f.submit();
    }
    if ('{{ compra_editar }}') mostrarForm('editar');
    // Navigation items
    const navItems = document.querySelectorAll('.nav-item a');
    const contentSections = document.querySelectorAll('.content-section');
    
    // Handle navigation clicks
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all nav items
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            
            // Add active class to clicked item
            this.parentElement.classList.add('active');
            
            // Hide all content sections
            contentSections.forEach(section => section.classList.remove('active'));
            
            // Show target section
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
            }
        });
    });
    
    // Modal functionality
    const addProductBtn = document.querySelector('.btn-primary');
    const modal = document.getElementById('addProductModal');
    const closeBtn = document.querySelector('.modal-close');
    
    if (addProductBtn && modal) {
        addProductBtn.addEventListener('click', function() {
            modal.style.display = 'block';
        });
    }
    
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Mobile sidebar toggle
    const createMobileToggle = () => {
        const header = document.querySelector('.header-content');
        const sidebar = document.querySelector('.sidebar');
        
        if (window.innerWidth <= 1024) {
            // Create mobile toggle button if it doesn't exist
            let toggleBtn = document.querySelector('.mobile-toggle');
            if (!toggleBtn) {
                toggleBtn = document.createElement('button');
                toggleBtn.className = 'mobile-toggle';
                toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
                toggleBtn.style.cssText = `
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.2rem;
                    cursor: pointer;
                    padding: 0.5rem;
                `;
                header.insertBefore(toggleBtn, header.firstChild);
                
                toggleBtn.addEventListener('click', function() {
                    sidebar.classList.toggle('open');
                });
            }
        }
    };
    
    createMobileToggle();
    window.addEventListener('resize', createMobileToggle);
    
    // Sample chart initialization (placeholder)
    const initCharts = () => {
        const salesChart = document.getElementById('salesChart');
        const trendsChart = document.getElementById('trendsChart');
        
        if (salesChart) {
            const ctx = salesChart.getContext('2d');
            ctx.fillStyle = '#667eea';
            ctx.fillRect(0, 0, salesChart.width, salesChart.height);
            ctx.fillStyle = 'white';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Gráfico de Ventas', salesChart.width/2, salesChart.height/2);
        }
        
        if (trendsChart) {
            const ctx = trendsChart.getContext('2d');
            ctx.fillStyle = '#28a745';
            ctx.fillRect(0, 0, trendsChart.width, trendsChart.height);
            ctx.fillStyle = 'white';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Análisis de Tendencias', trendsChart.width/2, trendsChart.height/2);
        }
    };
    
    // Initialize charts after a short delay
    setTimeout(initCharts, 100);
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic validation
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#e53e3e';
                } else {
                    field.style.borderColor = '#e2e8f0';
                }
            });
            
            if (isValid) {
                alert('Formulario enviado correctamente');
                form.reset();
                if (modal) {
                    modal.style.display = 'none';
                }
            } else {
                alert('Por favor, complete todos los campos requeridos');
            }
        });
    });
    
    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.content-section').querySelector('.data-table tbody');
            
            if (table) {
                const rows = table.querySelectorAll('tr');
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });
    
    // Filter functionality
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            // Implement filter logic here
            console.log('Filter changed:', this.value);
        });
    });
    
    // Button interactions
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Add click animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
    
    // Notification system
    const showNotification = (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
            color: white;
            border-radius: 8px;
            z-index: 3000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    };
    
    // Add CSS animation for notifications
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Example usage of notifications
    const actionButtons = document.querySelectorAll('.btn-success, .btn-warning, .btn-info');
    actionButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!this.closest('form')) {
                e.preventDefault();
                const action = this.textContent.trim();
                showNotification(`Acción "${action}" ejecutada correctamente`, 'success');
            }
        });
    });
    
    // Real-time updates simulation
    const updateStats = () => {
        const statValues = document.querySelectorAll('.stat-info h3');
        statValues.forEach(stat => {
            if (Math.random() > 0.9) { // 10% chance to update
                const currentValue = parseInt(stat.textContent.replace(/[^0-9]/g, ''));
                const change = Math.floor(Math.random() * 10) - 5;
                const newValue = Math.max(0, currentValue + change);
                stat.textContent = stat.textContent.replace(currentValue.toString(), newValue.toString());
            }
        });
    };
    
    // Update stats every 30 seconds
    setInterval(updateStats, 30000);
    
    // Smooth scrolling for internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Initialize tooltips (simple implementation)
    const addTooltips = () => {
        const elements = document.querySelectorAll('[title]');
        elements.forEach(el => {
            el.addEventListener('mouseenter', function() {
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip';
                tooltip.textContent = this.title;
                tooltip.style.cssText = `
                    position: absolute;
                    background: #333;
                    color: white;
                    padding: 0.5rem;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    z-index: 4000;
                    pointer-events: none;
                `;
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + 'px';
                tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
                
                this.addEventListener('mouseleave', function() {
                    tooltip.remove();
                }, { once: true });
            });
        });
    };
    
    addTooltips();
});

// Utility functions
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-PE', {
        style: 'currency',
        currency: 'PEN'
    }).format(amount);
};

const formatDate = (date) => {
    return new Intl.DateTimeFormat('es-PE').format(new Date(date));
};

const calculateDaysUntilExpiry = (expiryDate) => {
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
};

document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('btnPredecir');
    const select = document.getElementById('productoSelect');

    btn.addEventListener('click', function () {
        const producto = select.value;
        if (!producto) {
            alert("Selecciona un producto");
            return;
        }

        fetch(`/ajax/prediccion/?producto=${encodeURIComponent(producto)}`)
            .then(res => res.json())
            .then(data => renderPrediccion(data));
        
        fetch(`/ajax/ventas/?producto=${encodeURIComponent(producto)}`)
            .then(res => res.json())
            .then(data => renderGraficoVentas(data));
    });

    function renderPrediccion(data) {
        const contenedor = document.getElementById('resultado-prediccion');

        if (data.mensaje_error) {
            contenedor.innerHTML = `<div class="alert alert-warning">${data.mensaje_error}</div>`;
            return;
        }

        const labels = [];
        const valores = [];
        const colores = [];

        const nombreMeses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
                             "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

        contenedor.innerHTML = `
            <div class="prediction-grid mt-4">
                <div class="prediction-chart">
                    <h3>Mes estimado de agotamiento por farmacia</h3>
                    <canvas id="chartPrediccion" height="180"></canvas>
                </div>
                <div class="prediction-card">
                    <h3>Detalle de predicciones</h3>
                    <div class="farmacia-cards">
                        ${data.predicciones.map(p => {
                            const [anioAg, mesAg] = p.fecha_agotamiento.split("-").map(Number);
                            const [anioUl, mesUl] = p.ultima_venta.split("-").map(Number);

                            const fechaAg = new Date(anioAg, mesAg - 1);
                            const fechaUl = new Date(anioUl, mesUl - 1);
                            const mesesRestantes = (fechaAg.getFullYear() - fechaUl.getFullYear()) * 12 + (fechaAg.getMonth() - fechaUl.getMonth());

                            let color, icon, barraColor;
                            if (mesesRestantes <= 4) {
                                color = '#fee2e2'; barraColor = '#dc2626'; icon = '❗';
                            } else if (mesesRestantes <= 8) {
                                color = '#fef9c3'; barraColor = '#facc15'; icon = '⚠️';
                            } else {
                                color = '#dcfce7'; barraColor = '#16a34a'; icon = '✅';
                            }

                            const mesTexto = nombreMeses[mesAg - 1];
                            const porcentaje = Math.min((mesAg / 12) * 100, 100);

                            labels.push(p.farmacia);
                            valores.push(mesAg);
                            colores.push(barraColor);

                            return `
                                <div class="farmacia-card" style="background-color:${color}; padding: 1rem; border-radius: 0.75rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <h4 style="margin: 0;">${icon} ${p.farmacia}</h4>
                                        <span style="font-size: 0.85rem; color: #6b7280;">Mes ${mesAg}</span>
                                    </div>
                                    <div style="margin-top: 0.5rem;">
                                        <p style="margin: 0.2rem 0;"><strong>Stock:</strong> ${p.stock}</p>
                                        <p style="margin: 0.2rem 0;"><strong>Tasa venta:</strong> ${p.tasa} unid/mes</p>
                                        <p style="margin: 0.2rem 0;"><strong>Última venta:</strong> ${p.ultima_venta}</p>
                                        <p style="margin: 0.2rem 0;"><strong>Predecir agotamiento:</strong> ${mesTexto} ${anioAg}</p>
                                        <div style="height: 8px; background: #e5e7eb; border-radius: 999px; overflow: hidden; margin-top: 0.5rem;">
                                            <div style="width: ${porcentaje}%; height: 100%; background-color: ${barraColor};"></div>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                    <!-- Leyenda de colores -->
                    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                        <h4 style="margin-bottom: 0.5rem;">Leyenda de colores:</h4>
                        <ul style="list-style: none; padding-left: 0; font-size: 0.9rem;">
                            <li><span style="display:inline-block;width:12px;height:12px;background-color:#dc2626;border-radius:3px;margin-right:8px;"></span>❗ Rojo: se agotará en ≤ 4 meses desde la última venta</li>
                            <li><span style="display:inline-block;width:12px;height:12px;background-color:#facc15;border-radius:3px;margin-right:8px;"></span>⚠️ Amarillo: se agotará en 5 a 8 meses</li>
                            <li><span style="display:inline-block;width:12px;height:12px;background-color:#16a34a;border-radius:3px;margin-right:8px;"></span>✅ Verde: se agotará en 9 meses o más</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;

        new Chart(document.getElementById('chartPrediccion'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Mes de agotamiento (1–12)',
                    data: valores,
                    backgroundColor: colores
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 12,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Mes (número)'
                        }
                    }
                }
            }
        });
    }

    function renderGraficoVentas(data) {
        const graficoContainer = document.getElementById('grafico-ventas-container');
        graficoContainer.innerHTML = '';
    
        if (data.error) {
            graficoContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }
    
        // Crear contenedor con tamaño controlado
        const chartWrapper = document.createElement('div');
        chartWrapper.style.width = '1200px';
        chartWrapper.style.height = '550px';
        chartWrapper.style.margin = '0 auto'; // Centrado
        chartWrapper.style.padding = '10px';
        chartWrapper.style.backgroundColor = '#fff';
    
        const canvas = document.createElement('canvas');
        canvas.id = 'graficoVentas';
        chartWrapper.appendChild(canvas);
        graficoContainer.appendChild(chartWrapper);
    
        const todasEtiquetas = new Set();
    
        data.ventas_por_farmacia.forEach(f => {
            f.ventas.forEach(v => todasEtiquetas.add(v.mes));
        });
    
        const labels = Array.from(todasEtiquetas).sort((a, b) => {
            const [mesA, anioA] = a.split("-");
            const [mesB, anioB] = b.split("-");
            const parseMes = (mes) => {
                const meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
                               'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
                return meses.indexOf(mes.toLowerCase());
            };
            return parseInt(anioA) - parseInt(anioB) || parseMes(mesA) - parseMes(mesB);
        });
    
        const colores = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']; // Más colores si hay más farmacias
    
        const datasets = data.ventas_por_farmacia.map((farmaciaData, index) => {
            const datosPorMes = new Map(farmaciaData.ventas.map(v => [v.mes, v.cantidad]));
            return {
                label: farmaciaData.farmacia,
                data: labels.map(mes => datosPorMes.get(mes) || 0),
                borderColor: colores[index % colores.length],
                backgroundColor: colores[index % colores.length] + "33",
                fill: false,
                tension: 0.3,
                pointRadius: 4
            };
        });
    
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                maintainAspectRatio: false,  // 👈 esto permite que respete el tamaño del div padre
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Histórico de ventas por farmacia',
                        font: {
                            size: 16
                        }
                    },
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    
});


document.getElementById('btnBuscarRanking').addEventListener('click', () => {
    const mes = document.getElementById('mesSelect').value;
    const anio = document.getElementById('anioSelect').value;

    if (!mes || !anio) {
        alert("Selecciona mes y año");
        return;
    }

    fetch(`/ajax/ranking-empleados-mes-anio/?mes=${mes}&anio=${anio}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            renderTablaEmpleados(data.ranking);
            renderGraficoEmpleados(data.ranking);
        });
});

function renderTablaEmpleados(ranking) {
    if (ranking.length === 0) {
        document.getElementById('tablaRankingContainer').innerHTML = "<div class='alert alert-info'>No hay datos para este mes y año.</div>";
        return;
    }

    let html = `
        <div class="table-responsive">
        <table class="table table-striped table-bordered" style="background-color: white;">
            <thead class="table-primary">
                <tr>
                    <th>#</th>
                    <th>Empleado</th>
                    <th>Sucursal</th>
                    <th>Cantidad</th>
                    <th>Ventas (S/)</th>
                </tr>
            </thead>
            <tbody>
    `;

    ranking.forEach((item, index) => {
        // Colores especiales para top 3 y bottom 2
        let rowClass = '';
        if (index === 0) rowClass = 'table-success';       // 🥇 1ro
        else if (index === 1) rowClass = 'table-info';      // 🥈 2do
        else if (index === 2) rowClass = 'table-warning';   // 🥉 3ro
        else if (index >= ranking.length - 2) rowClass = 'table-danger'; // Últimos 2

        html += `
            <tr class="${rowClass}">
                <td>${index + 1}</td>
                <td>${item.empleado}</td>
                <td>${item.sucursal}</td>
                <td>${item.cantidad}</td>
                <td><strong>S/ ${item.ventas.toFixed(2)}</strong></td>
            </tr>
        `;
    });

    html += `</tbody></table></div>`;
    document.getElementById('tablaRankingContainer').innerHTML = html;
}


let grafico = null;
function renderGraficoEmpleados(ranking) {
    const ctx = document.getElementById('graficoRanking').getContext('2d');
    if (window.grafico) window.grafico.destroy();

    const labels = ranking.map(r => r.empleado);
    const datos = ranking.map(r => r.ventas);

    window.grafico = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas (S/)',
                data: datos,
                fill: false,
                borderColor: '#007bff',         // Azul Bootstrap
                backgroundColor: '#007bff',
                tension: 0.3,                    // Curva suave
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#fff',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: context => `S/ ${context.parsed.y.toFixed(2)}`
                    }
                },
                title: {
                    display: true,
                    text: 'Ranking de Ventas por Empleado',
                    font: {
                        size: 18
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        font: {
                            size: 14
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => `S/ ${value}`,
                        font: {
                            size: 13
                        }
                    }
                }
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const filtro = document.getElementById("filtroFarmacia");
    const botonBuscar = document.getElementById("btnBuscarInventario");

    function cargarInventario(farmaciaId = "todas") {
        fetch(`/inventario/filtrado/?farmacia_id=${farmaciaId}`)
            .then(res => res.json())
            .then(data => {
                const cuerpo = document.getElementById("cuerpoInventario");
                cuerpo.innerHTML = "";

                if (data.inventario.length === 0) {
                    console.log("✔️ Búsqueda completada: sin resultados.");
                    cuerpo.innerHTML = `<tr><td colspan="6" class="text-center">No hay productos en inventario</td></tr>`;
                    return;
                }

                data.inventario.forEach(item => {
                    cuerpo.innerHTML += `
                        <tr>
                            <td>${item.farmacia}</td>
                            <td>${item.producto}</td>
                            <td>${item.clase}</td>
                            <td>S/. ${item.precio.toFixed(2)}</td>
                            <td>${item.stock}</td>
                            <td>${item.vencimiento}</td>
                        </tr>`;
                });

                console.log("✔️ Inventario cargado correctamente para la farmacia ID:", farmaciaId);
            })
            .catch(err => {
                console.error("❌ Error al cargar inventario:", err);
            });
    }

    // Buscar cuando se hace clic
    botonBuscar.addEventListener("click", function () {
        const farmaciaSeleccionada = filtro.value;
        cargarInventario(farmaciaSeleccionada);
    });
});

// Export functions for potential use in other scripts
window.InventoryApp = {
    formatCurrency,
    formatDate,
    calculateDaysUntilExpiry
};