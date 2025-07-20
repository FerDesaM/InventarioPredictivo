"""
Módulo de Búsqueda para Empleados
Proporciona funcionalidades de búsqueda avanzada en el inventario
"""

from django.db.models import Q
from farmacia_app.models import InventarioFarmacia, Producto
from django.core.paginator import Paginator
from datetime import datetime, timedelta


class SearchManager:
    """Clase para gestionar búsquedas en el inventario"""
    
    def __init__(self, farmacia_id):
        self.farmacia_id = farmacia_id
    
    def search_products(self, query=None, filters=None, page=1, per_page=10):
        """
        Busca productos en el inventario con filtros avanzados
        
        Args:
            query (str): Término de búsqueda
            filters (dict): Filtros adicionales
            page (int): Número de página
            per_page (int): Elementos por página
            
        Returns:
            dict: Resultados de búsqueda paginados
        """
        try:
            # Base queryset filtrado por farmacia
            queryset = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id
            ).select_related('producto', 'farmacia')
            
            # Aplicar búsqueda por texto
            if query:
                queryset = queryset.filter(
                    Q(producto__nombre_producto__icontains=query) |
                    Q(producto__product_id__icontains=query) |
                    Q(producto__clase__icontains=query)
                )
            
            # Aplicar filtros adicionales
            if filters:
                queryset = self._apply_filters(queryset, filters)
            
            # Ordenar resultados
            order_by = filters.get('order_by', 'producto__nombre_producto') if filters else 'producto__nombre_producto'
            queryset = queryset.order_by(order_by)
            
            # Paginar resultados
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            
            # Formatear datos
            search_results = []
            for item in page_obj:
                search_results.append({
                    'id': item.id,
                    'producto_id': item.producto.product_id,
                    'nombre_producto': item.producto.nombre_producto,
                    'clase': item.producto.clase,
                    'precio_unitario': float(item.producto.precio_unitario),
                    'fecha_vencimiento': item.producto.fecha_vencimiento.strftime('%Y-%m-%d'),
                    'stock': item.stock,
                    'stock_status': self._get_stock_status(item.stock),
                    'days_to_expire': self._days_to_expire(item.producto.fecha_vencimiento),
                    'total_value': float(item.producto.precio_unitario * item.stock)
                })
            
            return {
                'success': True,
                'data': search_results,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                },
                'query': query,
                'filters_applied': filters or {}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en búsqueda: {str(e)}'
            }
    
    def _apply_filters(self, queryset, filters):
        """
        Aplica filtros específicos al queryset
        
        Args:
            queryset: QuerySet base
            filters (dict): Diccionario de filtros
            
        Returns:
            QuerySet: QuerySet filtrado
        """
        # Filtro por clase de producto
        if filters.get('clase'):
            queryset = queryset.filter(producto__clase__icontains=filters['clase'])
        
        # Filtro por rango de precios
        if filters.get('precio_min'):
            queryset = queryset.filter(producto__precio_unitario__gte=filters['precio_min'])
        
        if filters.get('precio_max'):
            queryset = queryset.filter(producto__precio_unitario__lte=filters['precio_max'])
        
        # Filtro por stock
        if filters.get('stock_min'):
            queryset = queryset.filter(stock__gte=filters['stock_min'])
        
        if filters.get('stock_max'):
            queryset = queryset.filter(stock__lte=filters['stock_max'])
        
        # Filtro por estado de stock
        if filters.get('stock_status'):
            if filters['stock_status'] == 'critical':
                queryset = queryset.filter(stock__lte=5)
            elif filters['stock_status'] == 'low':
                queryset = queryset.filter(stock__lte=15, stock__gt=5)
            elif filters['stock_status'] == 'medium':
                queryset = queryset.filter(stock__lte=50, stock__gt=15)
            elif filters['stock_status'] == 'high':
                queryset = queryset.filter(stock__gt=50)
        
        # Filtro por fecha de vencimiento
        if filters.get('expires_in_days'):
            days = int(filters['expires_in_days'])
            target_date = datetime.now().date() + timedelta(days=days)
            queryset = queryset.filter(producto__fecha_vencimiento__lte=target_date)
        
        # Filtro por productos próximos a vencer
        if filters.get('expiring_soon'):
            days_ahead = int(filters.get('expiring_soon', 30))
            target_date = datetime.now().date() + timedelta(days=days_ahead)
            queryset = queryset.filter(producto__fecha_vencimiento__lte=target_date)
        
        return queryset
    
    def get_search_suggestions(self, partial_query, limit=10):
        """
        Obtiene sugerencias de búsqueda basadas en una consulta parcial
        
        Args:
            partial_query (str): Consulta parcial
            limit (int): Límite de sugerencias
            
        Returns:
            dict: Lista de sugerencias
        """
        try:
            if not partial_query or len(partial_query) < 2:
                return {
                    'success': True,
                    'suggestions': []
                }
            
            # Buscar en nombres de productos
            productos = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id,
                producto__nombre_producto__icontains=partial_query
            ).select_related('producto').values_list(
                'producto__nombre_producto', flat=True
            ).distinct()[:limit]
            
            # Buscar en clases de productos
            clases = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id,
                producto__clase__icontains=partial_query
            ).select_related('producto').values_list(
                'producto__clase', flat=True
            ).distinct()[:5]
            
            suggestions = list(productos) + list(clases)
            
            return {
                'success': True,
                'suggestions': suggestions[:limit]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al obtener sugerencias: {str(e)}'
            }
    
    def get_filter_options(self):
        """
        Obtiene las opciones disponibles para filtros
        
        Returns:
            dict: Opciones de filtros disponibles
        """
        try:
            inventario_items = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id
            ).select_related('producto')
            
            # Obtener clases únicas
            clases = inventario_items.values_list(
                'producto__clase', flat=True
            ).distinct().order_by('producto__clase')
            
            # Obtener rangos de precios
            precios = inventario_items.values_list(
                'producto__precio_unitario', flat=True
            )
            precio_min = min(precios) if precios else 0
            precio_max = max(precios) if precios else 0
            
            # Obtener rangos de stock
            stocks = inventario_items.values_list('stock', flat=True)
            stock_min = min(stocks) if stocks else 0
            stock_max = max(stocks) if stocks else 0
            
            return {
                'success': True,
                'options': {
                    'clases': list(clases),
                    'precio_range': {
                        'min': float(precio_min),
                        'max': float(precio_max)
                    },
                    'stock_range': {
                        'min': stock_min,
                        'max': stock_max
                    },
                    'stock_status_options': [
                        {'value': 'critical', 'label': 'Crítico (≤5)'},
                        {'value': 'low', 'label': 'Bajo (6-15)'},
                        {'value': 'medium', 'label': 'Medio (16-50)'},
                        {'value': 'high', 'label': 'Alto (>50)'}
                    ],
                    'order_options': [
                        {'value': 'producto__nombre_producto', 'label': 'Nombre A-Z'},
                        {'value': '-producto__nombre_producto', 'label': 'Nombre Z-A'},
                        {'value': 'producto__precio_unitario', 'label': 'Precio menor a mayor'},
                        {'value': '-producto__precio_unitario', 'label': 'Precio mayor a menor'},
                        {'value': 'stock', 'label': 'Stock menor a mayor'},
                        {'value': '-stock', 'label': 'Stock mayor a menor'},
                        {'value': 'producto__fecha_vencimiento', 'label': 'Vence primero'}
                    ]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al obtener opciones de filtros: {str(e)}'
            }
    
    def _get_stock_status(self, stock):
        """Determina el estado del stock"""
        if stock <= 5:
            return 'critical'
        elif stock <= 15:
            return 'low'
        elif stock <= 50:
            return 'medium'
        else:
            return 'high'
    
    def _days_to_expire(self, fecha_vencimiento):
        """Calcula días hasta el vencimiento"""
        today = datetime.now().date()
        delta = fecha_vencimiento - today
        return delta.days
    
    def search_by_barcode(self, barcode):
        """
        Busca un producto por código de barras (product_id)
        
        Args:
            barcode (str): Código de barras del producto
            
        Returns:
            dict: Información del producto encontrado
        """
        try:
            inventario_item = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id,
                producto__product_id=barcode
            ).select_related('producto', 'farmacia').first()
            
            if not inventario_item:
                return {
                    'success': False,
                    'error': 'Producto no encontrado'
                }
            
            return {
                'success': True,
                'data': {
                    'id': inventario_item.id,
                    'producto_id': inventario_item.producto.product_id,
                    'nombre_producto': inventario_item.producto.nombre_producto,
                    'clase': inventario_item.producto.clase,
                    'precio_unitario': float(inventario_item.producto.precio_unitario),
                    'fecha_vencimiento': inventario_item.producto.fecha_vencimiento.strftime('%Y-%m-%d'),
                    'stock': inventario_item.stock,
                    'stock_status': self._get_stock_status(inventario_item.stock),
                    'days_to_expire': self._days_to_expire(inventario_item.producto.fecha_vencimiento)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en búsqueda por código: {str(e)}'
            }

