from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import Manager,Farmacia, Producto, Empleado, InventarioFarmacia, Compra, Venta
from django.contrib.auth.decorators import login_required

from datetime import date
from collections import defaultdict
from django.http import JsonResponse



@login_required(login_url='login')
def home(request):
    return render(request, 'farmacia_app/home.html', {
        'user': request.user
    })

def dashboard_view(request):
    farmacias = Farmacia.objects.all()
    productos = Producto.objects.all()  # sin slicing
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



def prediccion_producto_ajax(request):
    nombre = request.GET.get('producto')
    predicciones = []
    mensaje_error = ""

    if nombre:
        try:
            producto = Producto.objects.get(nombre_producto__icontains=nombre)
            ventas = Venta.objects.filter(producto=producto)
            ventas_por_farmacia = defaultdict(list)

            for venta in ventas:
                key = (venta.empleado.farmacia.id, venta.month, venta.year)
                ventas_por_farmacia[key].append(venta.quantity)

            tasa_por_farmacia = defaultdict(float)
            meses_por_farmacia = defaultdict(set)

            for (farmacia_id, mes, anio), cantidades in ventas_por_farmacia.items():
                total = sum(cantidades)
                tasa_por_farmacia[farmacia_id] += total
                meses_por_farmacia[farmacia_id].add((mes, anio))

            for f_id in tasa_por_farmacia:
                tasa_por_farmacia[f_id] /= len(meses_por_farmacia[f_id]) or 1

            inventarios = InventarioFarmacia.objects.filter(producto=producto)

            for inv in inventarios:
                tasa = tasa_por_farmacia.get(inv.farmacia.id, 0.1)
                meses_restantes = inv.stock / tasa if tasa else 0
                agotamiento = date.today().month + int(meses_restantes)
                mes_agotamiento = agotamiento % 12 or 12
                predicciones.append({
                    'farmacia': inv.farmacia.nombre_farmacia,
                    'stock': inv.stock,
                    'tasa': round(tasa, 2),
                    'dias_restantes': int(meses_restantes * 30),
                    'mes_agotamiento': mes_agotamiento
                })

            if not predicciones:
                mensaje_error = "No hay datos de inventario o ventas para este producto."

        except Producto.DoesNotExist:
            mensaje_error = "Producto no encontrado."

    return JsonResponse({
        'producto': nombre,
        'predicciones': predicciones,
        'mensaje_error': mensaje_error
    })