"""
Módulo de Inventario para Empleados
Gestiona la visualización y operaciones del inventario por farmacia
"""

from django.db.models import Q
from farmacia_app.models import InventarioFarmacia, Producto, Farmacia
from django.core.paginator import Paginator
from django.http import JsonResponse
import json


class InventoryManager:
    """Clase para gestionar operaciones de inventario"""
    
    def __init__(self, farmacia_id):
        self.farmacia_id = farmacia_id
        
    def get_inventory_by_pharmacy(self, page=1, per_page=10):
        """
        Obtiene el inventario completo de una farmacia específica
        
        Args:
            page (int): Número de página
            per_page (int): Elementos por página
            
        Returns:
            dict: Inventario paginado con productos
        """
        try:
            inventario_queryset = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id
            ).select_related('producto', 'farmacia').order_by('producto__nombre_producto')
            
            paginator = Paginator(inventario_queryset, per_page)
            page_obj = paginator.get_page(page)
            
            inventory_data = []
            for item in page_obj:
                inventory_data.append({
                    'id': item.id,
                    'producto_id': item.producto.product_id,
                    'nombre_producto': item.producto.nombre_producto,
                    'clase': item.producto.clase,
                    'precio_unitario': float(item.producto.precio_unitario),
                    'fecha_vencimiento': item.producto.fecha_vencimiento.strftime('%Y-%m-%d'),
                    'stock': item.stock,
                    'stock_status': self._get_stock_status(item.stock),
                    'farmacia_nombre': item.farmacia.nombre_farmacia
                })
            
            return {
                'success': True,
                'data': inventory_data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al obtener inventario: {str(e)}'
            }
    
    def get_product_details(self, producto_id):
        """
        Obtiene detalles específicos de un producto en la farmacia
        
        Args:
            producto_id (str): ID del producto
            
        Returns:
            dict: Detalles del producto
        """
        try:
            inventario_item = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id,
                producto__product_id=producto_id
            ).select_related('producto', 'farmacia').first()
            
            if not inventario_item:
                return {
                    'success': False,
                    'error': 'Producto no encontrado en esta farmacia'
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
                    'farmacia_nombre': inventario_item.farmacia.nombre_farmacia,
                    'total_value': float(inventario_item.producto.precio_unitario * inventario_item.stock)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al obtener detalles del producto: {str(e)}'
            }
    
    def get_low_stock_products(self, threshold=10):
        """
        Obtiene productos con stock bajo en la farmacia
        
        Args:
            threshold (int): Umbral de stock bajo
            
        Returns:
            dict: Lista de productos con stock bajo
        """
        try:
            low_stock_items = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id,
                stock__lte=threshold
            ).select_related('producto').order_by('stock')
            
            low_stock_data = []
            for item in low_stock_items:
                low_stock_data.append({
                    'producto_id': item.producto.product_id,
                    'nombre_producto': item.producto.nombre_producto,
                    'stock': item.stock,
                    'precio_unitario': float(item.producto.precio_unitario)
                })
            
            return {
                'success': True,
                'data': low_stock_data,
                'count': len(low_stock_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al obtener productos con stock bajo: {str(e)}'
            }
    
    def _get_stock_status(self, stock):
        """
        Determina el estado del stock basado en la cantidad
        
        Args:
            stock (int): Cantidad en stock
            
        Returns:
            str: Estado del stock
        """
        if stock <= 5:
            return 'critical'
        elif stock <= 15:
            return 'low'
        elif stock <= 50:
            return 'medium'
        else:
            return 'high'
    
    def get_inventory_summary(self):
        """
        Obtiene un resumen del inventario de la farmacia
        
        Returns:
            dict: Resumen estadístico del inventario
        """
        try:
            inventario_items = InventarioFarmacia.objects.filter(
                farmacia_id=self.farmacia_id
            ).select_related('producto')
            
            total_products = inventario_items.count()
            total_stock = sum(item.stock for item in inventario_items)
            low_stock_count = inventario_items.filter(stock__lte=10).count()
            critical_stock_count = inventario_items.filter(stock__lte=5).count()
            
            total_value = sum(
                item.stock * item.producto.precio_unitario 
                for item in inventario_items
            )
            
            return {
                'success': True,
                'data': {
                    'total_products': total_products,
                    'total_stock': total_stock,
                    'low_stock_count': low_stock_count,
                    'critical_stock_count': critical_stock_count,
                    'total_inventory_value': float(total_value)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al obtener resumen del inventario: {str(e)}'
            }

