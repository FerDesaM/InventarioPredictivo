from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import Manager,Farmacia, Producto, Empleado, InventarioFarmacia, Compra, Venta
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def home(request):
    return render(request, 'farmacia_app/home.html', {
        'user': request.user
    })
def dashboard_view(request):
    farmacias = Farmacia.objects.all()
    productos = Producto.objects.all()[:10]
    inventario = InventarioFarmacia.objects.select_related('producto').all()[:10]
    stats = {
        'total_productos': Producto.objects.count(),
        'stock_bajo': InventarioFarmacia.objects.filter(stock__lt=20).count(),
        'proximos_vencer': Producto.objects.filter(fecha_vencimiento__lt='2025-12-31').count(),
        'ventas_mes': 12450.00
    }
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
def login_view(request):
    if request.method == 'POST':
        manager_id = request.POST.get('id')
        password   = request.POST.get('password')

        if not manager_id or not password:
            return render(request, 'inventario/login.html', {
                'error': 'Por favor, completa ambos campos.'
            })
        try:
            manager = Manager.objects.get(pk=manager_id, password=password)
            request.session['manager_id'] = manager.id
            return redirect('dashboard')
        except Manager.DoesNotExist:
            return render(request, 'inventario/login.html', {
                'error': 'Credenciales inválidas'
            })

    return render(request, 'inventario/login.html')