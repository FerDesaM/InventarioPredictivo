// farmacia_app/static/inventario/js/transferencias.js
document.addEventListener('DOMContentLoaded', function() {
    // 1. Toggle del formulario
    const toggleForm = () => {
        const form = document.getElementById('form-transferencia');
        if (form) form.style.display = form.style.display === 'none' ? 'block' : 'none';
    };

    // 2. Validación origen ≠ destino
    const validateTransfer = () => {
        const origen = document.querySelector('select[name="origen"]');
        const destino = document.querySelector('select[name="destino"]');
        
        if (origen && destino) {
            origen.addEventListener('change', () => {
                Array.from(destino.options).forEach(opt => {
                    opt.disabled = opt.value === origen.value;
                });
            });
        }
    };

    // 3. Envío con feedback visual (sin AJAX)
    const handleSubmit = (e) => {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        }
    };

    // Inicialización
    document.getElementById('btn-nueva-transferencia')?.addEventListener('click', toggleForm);
    document.getElementById('form-transferencia')?.addEventListener('submit', handleSubmit);
    validateTransfer();
});