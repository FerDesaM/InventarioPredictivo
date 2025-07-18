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

        user_id = request.POST.get('usuario')
        password = request.POST.get('password')

        if not user_id or not password:

            return render(request, 'inventario/login.html', {
                'error': 'Por favor, completa ambos campos.'
            })

        try:
            manager = Manager.objects.get(email=user_id)
            if manager.check_password(password):
                request.session['manager_id'] = manager.email  
                return redirect('dashboard')
            else:
                return render(request, 'inventario/login.html', {
                    'error': 'Contraseña incorrecta.'
                })
        except Manager.DoesNotExist:
            pass  

        try:
            empleado = Empleado.objects.get(dni=user_id)
            if empleado.check_password(password):
                request.session['dni'] = empleado.dni
                if empleado.es_admin:
                    return redirect('dashboard')
                else:
                    return redirect('empleado_dashboard')
            else:
                return render(request, 'inventario/login.html', {
                    'error': 'Contraseña incorrecta.'
                })
        except Empleado.DoesNotExist:
            return render(request, 'inventario/login.html', {
                'error': 'Usuario no encontrado.'
            })

    return render(request, 'inventario/login.html')

def empleado_dashboard(request):
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return redirect('login')

    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        
        # Importar y usar nuevos managers
        from farmacia_app.modules.inventory_module import InventoryManager
        from farmacia_app.modules.search_module import SearchManager
        
        # Inicializar managers
        inventory_manager = InventoryManager(empleado.farmacia.id)
        search_manager = SearchManager(empleado.farmacia.id)
        
        # Obtener datos iniciales
        inventory_summary = inventory_manager.get_inventory_summary()
        filter_options = search_manager.get_filter_options()
        low_stock_products = inventory_manager.get_low_stock_products()
        
        context = {
            'empleado': empleado,
            'inventory_summary': inventory_summary.get('data', {}),
            'filter_options': filter_options.get('options', {}),
            'low_stock_products': low_stock_products.get('data', []),
            'low_stock_count': low_stock_products.get('count', 0)
        }
        
        return render(request, 'empleado/empleado_dashboard.html', context)
        
    except Empleado.DoesNotExist:
        return redirect('login')

def logout_view(request):
    request.session.flush()
    return redirect('login')