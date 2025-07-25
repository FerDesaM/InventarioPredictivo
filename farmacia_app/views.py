from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Manager,Farmacia, Producto, Empleado, InventarioFarmacia, Compra, Venta
from django.contrib.auth.decorators import login_required

from datetime import date
from collections import defaultdict
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta
from datetime import datetime  # asegúrate de tener esta importación arriba
from django.utils.timezone import now
from django.db.models import Sum
import calendar


@login_required(login_url='login')
def home(request):
    return render(request, 'farmacia_app/home.html', {
        'user': request.user
    })


def dashboard_view(request):
    seccion = request.GET.get('seccion', 'dashboard')

    farmacias = Farmacia.objects.all()
    productos = Producto.objects.all()
    clases_disponibles = Producto.objects.values_list('clase', flat=True).distinct()
    inventario = InventarioFarmacia.objects.select_related('producto').all()[:10]

    stats = {
        'total_productos': Producto.objects.count(),
        'stock_bajo': InventarioFarmacia.objects.filter(stock__lt=20).count(),
        'proximos_vencer': Producto.objects.filter(fecha_vencimiento__lt='2025-12-31').count(),
        'ventas_mes': 12450.00,  # Puedes calcular esto dinámicamente si gustas
    }

    alertas = [
        {'tipo': 'urgent', 'mensaje': 'Stock crítico: Paracetamol 500mg', 'tiempo': 'Hace 2 horas'},
        {'tipo': 'warning', 'mensaje': 'Próximo a vencer: Ibuprofeno 400mg', 'tiempo': 'Hace 4 horas'},
        {'tipo': 'info', 'mensaje': 'Predicción: Aumentar stock de Vitamina C', 'tiempo': 'Hace 6 horas'},
    ]

    año_actual = datetime.now().year
    años_disponibles = list(range(año_actual, año_actual - 5, -1))  # [2025, 2024, 2023, 2022, 2021]

    ctx = {
        'seccion': seccion,
        'farmacias': farmacias,
        'productos': productos,
        'clases_disponibles': clases_disponibles,
        'inventario': inventario,
        'stats_dash': stats,
        'alertas': alertas,
        'today': timezone.now().date(),
        'compra_editar': None,
        'años_disponibles': años_disponibles,
    }

    # Sección de compras
    if seccion == 'compras':
        compras = Compra.objects.order_by('-fecha_compra', '-id')
        ctx['compras_recientes'] = compras

        compra_id = request.GET.get('editar')
        if compra_id:
            ctx['compra_editar'] = get_object_or_404(Compra, id=compra_id)

        if request.method == 'POST':
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

        manager_id = request.POST.get('usuario')
        password = request.POST.get('password')

        if not manager_id or not password:

            return render(request, 'inventario/login.html', {
                'error': 'Por favor, completa ambos campos.'
            })

        try:
            manager = Manager.objects.get(email=manager_id)
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
            empleado = Empleado.objects.get(dni=manager_id)
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


def prediccion_producto_ajax(request):
    nombre = request.GET.get('producto')
    predicciones = []
    mensaje_error = ""

    if nombre:
        try:
            producto = Producto.objects.get(nombre_producto__icontains=nombre)
            ventas = Venta.objects.filter(producto=producto)
            ventas_por_farmacia = defaultdict(list)
            ultima_fecha_por_farmacia = {}

            # Agrupar ventas y registrar última fecha por farmacia
            for venta in ventas:
                farmacia_id = venta.empleado.farmacia.id
                ventas_por_farmacia[(farmacia_id, venta.month, venta.year)].append(venta.quantity)

                # Convertir mes en número
                try:
                    mes_num = datetime.strptime(venta.month[:3], "%b").month
                except ValueError:
                    # Si el mes viene completo en español
                    meses_es = {
                        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10,
                        'noviembre': 11, 'diciembre': 12
                    }
                    mes_num = meses_es.get(venta.month.lower(), 1)

                fecha_venta = date(venta.year, mes_num, 1)
                if farmacia_id not in ultima_fecha_por_farmacia or fecha_venta > ultima_fecha_por_farmacia[farmacia_id]:
                    ultima_fecha_por_farmacia[farmacia_id] = fecha_venta

            # Calcular tasa promedio mensual por farmacia
            tasa_por_farmacia = defaultdict(float)
            meses_unicos_por_farmacia = defaultdict(set)

            for (farmacia_id, mes, anio), cantidades in ventas_por_farmacia.items():
                total_mes = sum(cantidades)
                tasa_por_farmacia[farmacia_id] += total_mes
                meses_unicos_por_farmacia[farmacia_id].add((mes, anio))

            for f_id in tasa_por_farmacia:
                tasa_por_farmacia[f_id] /= len(meses_unicos_por_farmacia[f_id]) or 1

            # Consultar inventario
            inventarios = InventarioFarmacia.objects.filter(producto=producto)

            for inv in inventarios:
                farmacia_id = inv.farmacia.id
                tasa = tasa_por_farmacia.get(farmacia_id, 0.1)
                ultima_fecha = ultima_fecha_por_farmacia.get(farmacia_id, date.today())

                meses_restantes = inv.stock / tasa if tasa else 0
                fecha_agotamiento = ultima_fecha + relativedelta(months=int(meses_restantes))

                # Formato para mostrar "mes año" en español
                nombre_meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                                'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                mes_agotamiento = nombre_meses[fecha_agotamiento.month - 1]
                ultima_venta = nombre_meses[ultima_fecha.month - 1] + " " + str(ultima_fecha.year)

                predicciones.append({
                    'farmacia': inv.farmacia.nombre_farmacia,
                    'stock': inv.stock,
                    'tasa': round(tasa, 2),
                    'dias_restantes': int(meses_restantes * 30),
                    'mes_agotamiento': mes_agotamiento,
                    'fecha_agotamiento': fecha_agotamiento.strftime("%Y-%m"),
                    'ultima_venta': ultima_fecha.strftime("%Y-%m")  # 👈 importante para que JS pueda comparar
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


def ventas_producto_ajax(request):
    nombre = request.GET.get('producto')
    ventas_por_farmacia = defaultdict(lambda: defaultdict(int))  # {farmacia: {mes-año: cantidad}}

    if nombre:
        try:
            producto = Producto.objects.get(nombre_producto__icontains=nombre)
            ventas = Venta.objects.filter(producto=producto)

            for venta in ventas:
                farmacia_nombre = venta.empleado.farmacia.nombre_farmacia
                clave_mes = f"{venta.month}-{venta.year}"
                ventas_por_farmacia[farmacia_nombre][clave_mes] += venta.quantity

            # Construir estructura para el gráfico
            data = []
            for farmacia, ventas_mensuales in ventas_por_farmacia.items():
                # Ordenar por año y mes
                ordenadas = sorted(
                    ventas_mensuales.items(),
                    key=lambda x: (
                        int(x[0].split("-")[1]),  # año
                        datetime.strptime(x[0].split("-")[0][:3], "%b").month if len(x[0].split("-")[0]) == 3 else {
                            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
                            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10,
                            'noviembre': 11, 'diciembre': 12
                        }.get(x[0].split("-")[0].lower(), 1)
                    )
                )

                data.append({
                    'farmacia': farmacia,
                    'ventas': [{'mes': k, 'cantidad': v} for k, v in ordenadas]
                })

            return JsonResponse({'ventas_por_farmacia': data})

        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)

    return JsonResponse({'error': 'Nombre de producto no especificado'}, status=400)

def ranking_empleados_mes_anio(request):
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')

    if not mes or not anio:
        return JsonResponse({'error': 'Mes y año requeridos'}, status=400)

    try:
        ventas = Venta.objects.filter(month=mes, year=anio).exclude(empleado__isnull=True)

        ranking = defaultdict(lambda: {'ventas': 0.0, 'cantidad': 0, 'sucursal': ''})

        for v in ventas:
            nombre = f"{v.empleado.nombre} {v.empleado.apellido}"
            ranking[nombre]['ventas'] += v.sales
            ranking[nombre]['cantidad'] += v.quantity
            ranking[nombre]['sucursal'] = v.empleado.farmacia.nombre_farmacia

        lista_ranking = sorted([
            {
                'empleado': nombre,
                'sucursal': data['sucursal'],
                'ventas': round(data['ventas'], 2),
                'cantidad': data['cantidad']
            }
            for nombre, data in ranking.items()
        ], key=lambda x: x['ventas'], reverse=True)

        return JsonResponse({'ranking': lista_ranking})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

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
def compras_view(request):
    if request.method == "POST":
        print("Datos del formulario recibidos:", request.POST)
        accion = request.POST.get("accion")

        if accion == "nueva":
            try:
                farmacia_id = request.POST.get("farmacia")
                producto_id = request.POST.get("producto")
                proveedor = request.POST.get("proveedor")
                cantidad = int(request.POST.get("cantidad"))
                fecha_compra = request.POST.get("fecha_compra")
                precio_unitario = float(request.POST.get("precio_unitarioC"))

                total_compra = cantidad * precio_unitario

                nueva_compra = Compra.objects.create(
                    farmacia_id=farmacia_id,
                    producto_id=producto_id,
                    proveedor=proveedor,
                    cantidad=cantidad,
                    fecha_compra=fecha_compra,
                    precio_unitarioC=precio_unitario,
                    total_compra=total_compra,
                )
                inventario, creado = InventarioFarmacia.objects.get_or_create(
                    farmacia_id=farmacia_id,
                    producto_id=producto_id,
                    defaults={'stock': cantidad}
                )

                if not creado:
                    inventario.stock += cantidad
                    inventario.save()

                return JsonResponse({
                    "status": "success",
                    "message": "Compra registrada correctamente.",
                    "compra_id": nueva_compra.id
                })

            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Error al registrar la compra: {str(e)}"
                })

        else:
            return JsonResponse({"status": "error", "message": "Acción no válida"})

    # Para GET, mostrar la página con el formulario
    farmacias = Farmacia.objects.all()
    productos = Producto.objects.all()
    compras = Compra.objects.all().order_by('-fecha_compra')[:10]
    print("Compras en template:", [c.id for c in compras])
    
    return render(request, "inventario/componentes/compras.html", {
        "farmacias": farmacias,
        "productos": productos,
        "compras": compras
    })
def listar_compras(request):
    compras = Compra.objects.all().select_related("producto", "farmacia").order_by("-fecha_compra")
    return render(request, 'compras/listado.html', {'compras': compras})



def inventario_filtrado(request):
    farmacia_id = request.GET.get('farmacia_id')
    clase = request.GET.get('clase')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    stock_min = request.GET.get('stock_min')
    stock_max = request.GET.get('stock_max')
    vencimiento_max = request.GET.get('vencimiento_max')

    inventario_qs = InventarioFarmacia.objects.select_related('producto', 'farmacia')

    if farmacia_id and farmacia_id != 'todas':
        inventario_qs = inventario_qs.filter(farmacia_id=farmacia_id)
    if clase:
        inventario_qs = inventario_qs.filter(producto__clase__icontains=clase)
    if precio_min:
        inventario_qs = inventario_qs.filter(producto__precio_unitario__gte=precio_min)
    if precio_max:
        inventario_qs = inventario_qs.filter(producto__precio_unitario__lte=precio_max)
    if stock_min:
        inventario_qs = inventario_qs.filter(stock__gte=stock_min)
    if stock_max:
        inventario_qs = inventario_qs.filter(stock__lte=stock_max)
    if vencimiento_max:
        try:
            fecha_limite = datetime.strptime(vencimiento_max, "%Y-%m-%d").date()
            inventario_qs = inventario_qs.filter(producto__fecha_vencimiento__lte=fecha_limite)
        except ValueError:
            pass  # si la fecha no es válida, ignoramos el filtro

    data = [{
        'farmacia': i.farmacia.nombre_farmacia,
        'producto': i.producto.nombre_producto,
        'clase': i.producto.clase,
        'precio': float(i.producto.precio_unitario),
        'stock': i.stock,
        'vencimiento': i.producto.fecha_vencimiento.strftime('%Y-%m-%d') if i.producto.fecha_vencimiento else '',
    } for i in inventario_qs]

    return JsonResponse({'inventario': data})


def ventas_por_farmacia(request):
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')

    from datetime import datetime
    if not mes or not anio:
        mes = datetime.now().strftime("%B")  # Ej: 'July'
        anio = datetime.now().year

    data = []
    farmacias = Farmacia.objects.all()

    for farmacia in farmacias:
        total_ventas = Venta.objects.filter(
            empleado__farmacia=farmacia,
            month__iexact=mes,
            year=anio
        ).aggregate(total=Sum('total'))['total'] or 0

        data.append({
            'farmacia': farmacia.nombre_farmacia,
            'total_ventas': round(total_ventas, 2)
        })

    return JsonResponse({'data': data})
