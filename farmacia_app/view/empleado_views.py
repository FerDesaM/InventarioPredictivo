"""
Vistas para el Dashboard de Empleados
Maneja las operaciones CRUD del inventario para empleados
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from farmacia_app.models import Empleado
from farmacia_app.modules.inventory_module import InventoryManager
from farmacia_app.modules.sales_module import SalesManager
from farmacia_app.modules.search_module import SearchManager
from farmacia_app.modules.validation_module import ValidationManager


def empleado_dashboard(request):
    """
    Vista principal del dashboard de empleado
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return redirect('login')

    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        
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


@csrf_exempt
@require_http_methods(["GET"])
def api_get_inventory(request):
    """
    API para obtener el inventario de la farmacia del empleado
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        inventory_manager = InventoryManager(empleado.farmacia.id)
        
        # Obtener parámetros de paginación
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        result = inventory_manager.get_inventory_by_pharmacy(page, per_page)
        return JsonResponse(result)
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_search_products(request):
    """
    API para búsqueda de productos con filtros
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        search_manager = SearchManager(empleado.farmacia.id)
        validation_manager = ValidationManager(empleado_dni)
        
        # Validar parámetros de búsqueda
        search_params = dict(request.GET)
        # Convertir listas de un elemento a strings
        for key, value in search_params.items():
            if isinstance(value, list) and len(value) == 1:
                search_params[key] = value[0]
        
        validation_result = validation_manager.validate_search_parameters(search_params)
        if not validation_result['valid']:
            return JsonResponse({
                'success': False, 
                'errors': validation_result['errors']
            }, status=400)
        
        validated_params = validation_result['validated_params']
        
        # Extraer query y filtros
        query = validated_params.get('query')
        filters = {k: v for k, v in validated_params.items() if k != 'query'}
        
        # Realizar búsqueda
        page = filters.pop('page', 1)
        per_page = filters.pop('per_page', 10)
        
        result = search_manager.search_products(query, filters, page, per_page)
        return JsonResponse(result)
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_product_details(request, producto_id):
    """
    API para obtener detalles de un producto específico
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        inventory_manager = InventoryManager(empleado.farmacia.id)
        
        result = inventory_manager.get_product_details(producto_id)
        return JsonResponse(result)
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_process_sale(request):
    """
    API para procesar una venta
    """
    

    empleado_dni = request.session.get('dni')
    print(empleado_dni)
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        # Parsear datos JSON
        
        data = json.loads(request.body)
        
        # Validar datos de entrada
        validation_manager = ValidationManager(empleado_dni)
        validation_result = validation_manager.validate_sale_data(data)
        
        if not validation_result['valid']:
            return JsonResponse({
                'success': False, 
                'errors': validation_result['errors']
            }, status=400)
        
        validated_data = validation_result['validated_data']
        
        # Validar stock antes de procesar
        stock_validation = validation_manager.validate_stock_availability(
            validated_data['producto_id'], 
            validated_data['cantidad']
        )
        
        if not stock_validation['valid']:
            return JsonResponse({
                'success': False, 
                'error': stock_validation['error']
            }, status=400)
        
        # Procesar venta
        sales_manager = SalesManager(empleado_dni)
        result = sales_manager.process_sale(
            validated_data['producto_id'],
            validated_data['cantidad'],
            validated_data['tipo_comprobante']
        )
        
        if result['success']:
            return JsonResponse(result, status=201)
        else:
            return JsonResponse(result, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_validate_sale(request):
    """
    API para validar una venta antes de procesarla
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        sales_manager = SalesManager(empleado_dni)
        result = sales_manager.validate_sale_data(
            data.get('producto_id'),
            data.get('cantidad')
        )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_sales_history(request):
    """
    API para obtener el historial de ventas del empleado
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        sales_manager = SalesManager(empleado_dni)
        
        # Obtener parámetros
        days = int(request.GET.get('days', 30))
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        result = sales_manager.get_sales_history(days, page, per_page)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_suggestions(request):
    """
    API para obtener sugerencias de búsqueda
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        search_manager = SearchManager(empleado.farmacia.id)
        
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 10))
        
        result = search_manager.get_search_suggestions(query, limit)
        return JsonResponse(result)
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_search_by_barcode(request, barcode):
    """
    API para búsqueda por código de barras
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        empleado = Empleado.objects.get(dni=empleado_dni)
        search_manager = SearchManager(empleado.farmacia.id)
        
        result = search_manager.search_by_barcode(barcode)
        return JsonResponse(result)
        
    except Empleado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Empleado no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_daily_summary(request):
    """
    API para obtener resumen de ventas del día
    """
    empleado_dni = request.session.get('dni')
    if not empleado_dni:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    
    try:
        sales_manager = SalesManager(empleado_dni)
        
        # Obtener fecha específica si se proporciona
        date_str = request.GET.get('date')
        date = None
        if date_str:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        result = sales_manager.get_daily_sales_summary(date)
        return JsonResponse(result)
        
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Formato de fecha inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

