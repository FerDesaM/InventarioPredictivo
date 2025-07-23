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

// Export functions for potential use in other scripts
window.InventoryApp = {
    formatCurrency,
    formatDate,
    calculateDaysUntilExpiry
};

