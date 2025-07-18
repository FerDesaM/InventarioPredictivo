from django.shortcuts import render

from django.shortcuts import render, redirect
from .models import Manager,Farmacia, Producto, Empleado, InventarioFarmacia, Compra, Venta
from django.contrib.auth.decorators import login_required

from datetime import date
from collections import defaultdict
from django.http import JsonResponse
from dateutil.relativedelta import relativedelta
from datetime import datetime  # asegúrate de tener esta importación arriba

@login_required(login_url='login')
def home(request):
    return render(request, 'farmacia_app/home.html', {
        'user': request.user
    })


def dashboard_view(request):
    farmacias = Farmacia.objects.all()
    productos = Producto.objects.all()
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

    # Año actual y últimos 5 años, incluyendo el actual (puedes ajustar el rango)
    año_actual = datetime.now().year
    años_disponibles = list(range(año_actual, año_actual - 5, -1))  # Ej: [2025, 2024, 2023, 2022, 2021]

    return render(request, 'inventario/dashboard.html', {
        'farmacias': farmacias,
        'productos': productos,
        'inventario': inventario,
        'stats': stats,
        'alertas': alertas,
        'años_disponibles': años_disponibles,  # 👈 este es el nuevo contexto para el <select>
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
    

