from django.shortcuts import render

from django.shortcuts import render
from .models import Farmacia, Producto, Empleado, InventarioFarmacia, Compra, Venta


def dashboard_view(request):
    # Datos de ejemplo para el dashboard
    farmacias = Farmacia.objects.all()
    productos = Producto.objects.all()[:10]
    inventario = InventarioFarmacia.objects.select_related('producto').all()[:10]

    # Estadísticas para las tarjetas
    stats = {
        'total_productos': Producto.objects.count(),
        'stock_bajo': InventarioFarmacia.objects.filter(stock__lt=20).count(),
        'proximos_vencer': Producto.objects.filter(fecha_vencimiento__lt='2025-12-31').count(),
        'ventas_mes': 12450.00
    }

    # Alertas
    alertas = [
        {'tipo': 'urgent', 'mensaje': 'Stock crítico: Paracetamol 500mg', 'tiempo': 'Hace 2 horas'},
        {'tipo': 'warning', 'mensaje': 'Próximo a vencer: Ibuprofeno 400mg', 'tiempo': 'Hace 4 horas'},
        {'tipo': 'info', 'mensaje': 'Predicción: Aumentar stock de Vitamina C', 'tiempo': 'Hace 6 horas'}
    ]

    return render(request, 'inventario/dashboard.html', {
        'farmacias': farmacias,
        'productos': productos,
        'inventario': inventario,
        'stats': stats,
        'alertas': alertas
    })
