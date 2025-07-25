"""
Vistas Simplificadas para el Dashboard de Empleados
Maneja solo búsqueda y ventas básicas
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, date

from farmacia_app.models import Empleado, InventarioFarmacia, Producto, Venta
from django.db.models import Q, Sum, Max
from django.db import transaction


def empleado_dashboard_simple(request):
    """
    Vista principal del dashboard simplificado de empleado
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return redirect('login')

    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        
        context = {
            'empleado': empleado,
        }
        
        return render(request, 'empleado/empleado_dashboard.html', context)
        
    except Empleado.DoesNotExist:
        return redirect('login')


@csrf_exempt
@require_http_methods(["GET"])
def api_buscar_medicamento(request):
    """
    API simplificada para buscar medicamentos
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        query = request.GET.get('query', '').strip()
        
        if not query:
            return JsonResponse({'success': False, 'error': 'Término de búsqueda requerido'}, status=400)
        
        # Buscar productos en el inventario de la farmacia
        productos = InventarioFarmacia.objects.filter(
            farmacia_id=empleado.farmacia.id,
            stock__gt=0  # Solo productos con stock
        ).filter(
            Q(producto__nombre_producto__icontains=query) |
            Q(producto__product_id__icontains=query) |
            Q(producto__clase__icontains=query)
        ).select_related('producto')[:10]  # Limitar a 10 resultados
        
        resultados = []
        for item in productos:
            resultados.append({
                'id': item.id,
                'producto_id': item.producto.product_id,
                'nombre_producto': item.producto.nombre_producto,
                'clase': item.producto.clase,
                'precio_unitario': float(item.producto.precio_unitario),
                'stock': item.stock,
                'fecha_vencimiento': item.producto.fecha_vencimiento.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({
            'success': True,
            'data': resultados,
            'total': len(resultados)
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_procesar_venta_simple(request):
    """
    API simplificada para procesar una venta
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        data = json.loads(request.body)
        
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 0))
        tipo_comprobante = data.get('tipo_comprobante', 'boleta')
        
        # Validaciones básicas
        if not producto_id or cantidad <= 0:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
        
        # Buscar el producto en el inventario
        try:
            inventario_item = InventarioFarmacia.objects.select_related('producto').get(
                farmacia_id=empleado.farmacia.id,
                producto__product_id=producto_id
            )
        except InventarioFarmacia.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
        
        # Verificar stock
        if inventario_item.stock < cantidad:
            return JsonResponse({
                'success': False, 
                'error': f'Stock insuficiente. Disponible: {inventario_item.stock}'
            }, status=400)
        
        # Calcular totales
        precio_unitario = float(inventario_item.producto.precio_unitario)
        subtotal = precio_unitario * cantidad
        igv = subtotal * 0.18
        total = subtotal + igv
        
        # Procesar la venta en una transacción
        with transaction.atomic():
            # Actualizar stock
            inventario_item.stock -= cantidad
            inventario_item.save()
            
            # Crear registro de venta
            today = date.today()
            
            # Generar código de venta único
            ultimo_codigo = Venta.objects.aggregate(max_codigo=Max('codigo_venta'))['max_codigo'] or 0
            nuevo_codigo = ultimo_codigo + 1
            
            venta = Venta.objects.create(
                codigo_venta=nuevo_codigo,
                producto=inventario_item.producto,
                empleado=empleado,
                quantity=cantidad,
                dia=today.day,
                month=today.strftime('%B'),
                year=today.year,
                sales=subtotal,
                igv=igv,
                total=total,
                moneda='PEN',
                estado='completada',
                tipo_comp=tipo_comprobante
            )
        
        return JsonResponse({
            'success': True,
            'data': {
                'codigo_venta': nuevo_codigo,
                'producto': inventario_item.producto.nombre_producto,
                'cantidad': cantidad,
                'total': total,
                'stock_restante': inventario_item.stock
            }
        }, status=201)
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_resumen_diario_simple(request):
    """
    API para obtener resumen de ventas del día actual
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        today = date.today()
        
        # Obtener ventas del día del empleado
        ventas_hoy = Venta.objects.filter(
            empleado=empleado,
            dia=today.day,
            month=today.strftime('%B'),
            year=today.year
        )
        
        # Calcular estadísticas
        total_ventas = ventas_hoy.count()
        total_ingresos = ventas_hoy.aggregate(Sum('total'))['total__sum'] or 0
        total_productos = ventas_hoy.aggregate(Sum('quantity'))['quantity__sum'] or 0
        promedio_venta = total_ingresos / total_ventas if total_ventas > 0 else 0
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_sales': total_ventas,
                'total_revenue': float(total_ingresos),
                'total_products': total_productos,
                'average_sale': float(promedio_venta)
            }
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

