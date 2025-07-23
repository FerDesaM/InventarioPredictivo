from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Manager,Farmacia, Producto, Empleado, InventarioFarmacia, Compra, Venta
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def home(request):
    return render(request, 'farmacia_app/home.html', {
        'user': request.user
    })

def dashboard_view(request):
    seccion = request.GET.get('seccion', 'dashboard')

    farmacias = Farmacia.objects.all()
    productos = Producto.objects.all()  # (asegúrate lista completa para formulario)
    inventario = InventarioFarmacia.objects.select_related('producto').all()[:10]

    stats = {
        'total_productos': Producto.objects.count(),
        'stock_bajo': InventarioFarmacia.objects.filter(stock__lt=20).count(),
        'proximos_vencer': Producto.objects.filter(fecha_vencimiento__lt='2025-12-31').count(),
        'ventas_mes': 12450.00,
    }

    alertas = [
        {'tipo': 'urgent', 'mensaje': 'Stock crítico: Paracetamol 500mg', 'tiempo': 'Hace 2 horas'},
        {'tipo': 'warning', 'mensaje': 'Próximo a vencer: Ibuprofeno 400mg', 'tiempo': 'Hace 4 horas'},
        {'tipo': 'info', 'mensaje': 'Predicción: Aumentar stock de Vitamina C', 'tiempo': 'Hace 6 horas'},
    ]

    ctx = {
        'seccion': seccion,
        'farmacias': farmacias,
        'productos': productos,
        'inventario': inventario,
        'stats_dash': stats,
        'alertas': alertas,
        'today': timezone.now().date(),
        'compra_editar': None,
    }

    if seccion == 'compras':
        compras = Compra.objects.order_by('-fecha_compra', '-id')
        ctx.update({
            'compras_recientes': compras,
        })

        compra_id = request.GET.get('editar')
        if compra_id:
            ctx['compra_editar'] = get_object_or_404(Compra, id=compra_id)

    # Manejo POST
    if request.method == 'POST' and seccion == 'compras':
        accion = request.POST.get('accion')
        if accion == 'nueva':
            f = get_object_or_404(Farmacia, id=request.POST['farmacia'])
            p = get_object_or_404(Producto, id=request.POST['producto'])
            c = int(request.POST['cantidad'])
            pu = float(request.POST['precio_unitarioC'])
            fc = request.POST.get('fecha_compra') or timezone.now().date()

            Compra.objects.create(
                farmacia=f,
                producto=p,
                proveedor=request.POST['proveedor'],
                cantidad=c,
                precio_unitarioC=pu,
                fecha_compra=fc,
                total_compra=c * pu
            )

        elif accion == 'editar':
            comp = get_object_or_404(Compra, id=request.POST['compra_id'])
            comp.farmacia = get_object_or_404(Farmacia, id=request.POST['farmacia'])
            comp.producto = get_object_or_404(Producto, id=request.POST['producto'])
            comp.proveedor = request.POST['proveedor']
            comp.cantidad = int(request.POST['cantidad'])
            comp.precio_unitarioC = float(request.POST['precio_unitarioC'])
            comp.fecha_compra = request.POST.get('fecha_compra') or comp.fecha_compra
            comp.total_compra = comp.cantidad * comp.precio_unitarioC
            comp.save()

        elif accion == 'eliminar':
            comp = get_object_or_404(Compra, id=request.POST['compra_id'])
            comp.delete()

        return redirect(f"{request.path}?seccion=compras")

    return render(request, 'inventario/dashboard.html', ctx)







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