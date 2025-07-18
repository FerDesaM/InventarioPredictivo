"""
Módulo de Ventas para Empleados
Gestiona las operaciones de venta y actualización de stock
"""

from django.db import transaction
from django.utils import timezone
from farmacia_app.models import InventarioFarmacia, Venta, Empleado, Producto
from decimal import Decimal
import datetime


class SalesManager:
    """Clase para gestionar operaciones de venta"""
    
    def __init__(self, empleado_dni):
        self.empleado_dni = empleado_dni
        self.empleado = None
        self._load_empleado()
    
    def _load_empleado(self):
        """Carga la información del empleado"""
        try:
            self.empleado = Empleado.objects.get(dni=self.empleado_dni)
        except Empleado.DoesNotExist:
            self.empleado = None
    
    def process_sale(self, producto_id, cantidad, tipo_comprobante='boleta'):
        """
        Procesa una venta y actualiza el stock
        
        Args:
            producto_id (str): ID del producto a vender
            cantidad (int): Cantidad a vender
            tipo_comprobante (str): Tipo de comprobante
            
        Returns:
            dict: Resultado de la operación de venta
        """
        if not self.empleado:
            return {
                'success': False,
                'error': 'Empleado no válido'
            }
        
        try:
            with transaction.atomic():
                # Verificar que el producto existe en el inventario de la farmacia
                inventario_item = InventarioFarmacia.objects.select_for_update().filter(
                    farmacia_id=self.empleado.farmacia.id,
                    producto__product_id=producto_id
                ).select_related('producto').first()
                
                if not inventario_item:
                    return {
                        'success': False,
                        'error': 'Producto no encontrado en el inventario de esta farmacia'
                    }
                
                # Verificar stock disponible
                if inventario_item.stock < cantidad:
                    return {
                        'success': False,
                        'error': f'Stock insuficiente. Disponible: {inventario_item.stock}, Solicitado: {cantidad}'
                    }
                
                # Calcular valores de la venta
                precio_unitario = inventario_item.producto.precio_unitario
                subtotal = Decimal(str(precio_unitario)) * Decimal(str(cantidad))
                igv = subtotal * Decimal('0.18')  # IGV 18%
                total = subtotal + igv
                
                # Generar código de venta único
                codigo_venta = self._generate_sale_code()
                
                # Crear registro de venta
                venta = Venta.objects.create(
                    codigo_venta=codigo_venta,
                    producto=inventario_item.producto,
                    empleado=self.empleado,
                    quantity=cantidad,
                    dia=timezone.now().day,
                    month=timezone.now().strftime('%B'),
                    year=timezone.now().year,
                    sales=float(subtotal),
                    igv=float(igv),
                    total=float(total),
                    moneda='PEN',
                    estado='completada',
                    tipo_comp=tipo_comprobante
                )
                
                # Actualizar stock
                inventario_item.stock -= cantidad
                inventario_item.save()
                
                return {
                    'success': True,
                    'data': {
                        'codigo_venta': codigo_venta,
                        'producto_nombre': inventario_item.producto.nombre_producto,
                        'cantidad': cantidad,
                        'precio_unitario': float(precio_unitario),
                        'subtotal': float(subtotal),
                        'igv': float(igv),
                        'total': float(total),
                        'stock_restante': inventario_item.stock,
                        'fecha_venta': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'empleado': f"{self.empleado.nombre} {self.empleado.apellido}",
                        'farmacia': self.empleado.farmacia.nombre_farmacia
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al procesar la venta: {str(e)}'
            }
    
    def _generate_sale_code(self):
        """
        Genera un código único para la venta
        
        Returns:
            int: Código de venta único
        """
        try:
            last_sale = Venta.objects.order_by('-codigo_venta').first()
            if last_sale:
                return last_sale.codigo_venta + 1
            else:
                return 1000001  # Código inicial
        except:
            return 1000001
    
    def get_sales_history(self, days=30, page=1, per_page=10):
        """
        Obtiene el historial de ventas del empleado
        
        Args:
            days (int): Días hacia atrás para buscar
            page (int): Número de página
            per_page (int): Elementos por página
            
        Returns:
            dict: Historial de ventas
        """
        if not self.empleado:
            return {
                'success': False,
                'error': 'Empleado no válido'
            }
        
        try:
            from django.core.paginator import Paginator
            from datetime import timedelta
            
            fecha_limite = timezone.now() - timedelta(days=days)
            
            ventas_queryset = Venta.objects.filter(
                empleado=self.empleado
            ).select_related('producto').order_by('-codigo_venta')
            
            paginator = Paginator(ventas_queryset, per_page)
            page_obj = paginator.get_page(page)
            
            sales_data = []
            for venta in page_obj:
                sales_data.append({
                    'codigo_venta': venta.codigo_venta,
                    'producto_nombre': venta.producto.nombre_producto,
                    'cantidad': venta.quantity,
                    'total': venta.total,
                    'fecha': f"{venta.dia}/{venta.month}/{venta.year}",
                    'estado': venta.estado,
                    'tipo_comprobante': venta.tipo_comp
                })
            
            return {
                'success': True,
                'data': sales_data,
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
                'error': f'Error al obtener historial de ventas: {str(e)}'
            }
    
    def validate_sale_data(self, producto_id, cantidad):
        """
        Valida los datos de una venta antes de procesarla
        
        Args:
            producto_id (str): ID del producto
            cantidad (int): Cantidad a vender
            
        Returns:
            dict: Resultado de la validación
        """
        if not self.empleado:
            return {
                'valid': False,
                'error': 'Empleado no válido'
            }
        
        # Validar cantidad
        if not isinstance(cantidad, int) or cantidad <= 0:
            return {
                'valid': False,
                'error': 'La cantidad debe ser un número entero positivo'
            }
        
        # Validar producto
        if not producto_id or not isinstance(producto_id, str):
            return {
                'valid': False,
                'error': 'ID de producto no válido'
            }
        
        try:
            # Verificar que el producto existe en la farmacia
            inventario_item = InventarioFarmacia.objects.filter(
                farmacia_id=self.empleado.farmacia.id,
                producto__product_id=producto_id
            ).select_related('producto').first()
            
            if not inventario_item:
                return {
                    'valid': False,
                    'error': 'Producto no encontrado en esta farmacia'
                }
            
            # Verificar stock
            if inventario_item.stock < cantidad:
                return {
                    'valid': False,
                    'error': f'Stock insuficiente. Disponible: {inventario_item.stock}'
                }
            
            # Verificar fecha de vencimiento
            if inventario_item.producto.fecha_vencimiento < timezone.now().date():
                return {
                    'valid': False,
                    'error': 'El producto está vencido'
                }
            
            return {
                'valid': True,
                'data': {
                    'producto_nombre': inventario_item.producto.nombre_producto,
                    'precio_unitario': float(inventario_item.producto.precio_unitario),
                    'stock_disponible': inventario_item.stock
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error en validación: {str(e)}'
            }
    
    def get_daily_sales_summary(self, date=None):
        """
        Obtiene resumen de ventas del día
        
        Args:
            date (datetime.date): Fecha específica (por defecto hoy)
            
        Returns:
            dict: Resumen de ventas del día
        """
        if not self.empleado:
            return {
                'success': False,
                'error': 'Empleado no válido'
            }
        
        if not date:
            date = timezone.now().date()
        
        try:
            ventas_del_dia = Venta.objects.filter(
                empleado=self.empleado,
                dia=date.day,
                month=date.strftime('%B'),
                year=date.year
            )
            
            total_ventas = ventas_del_dia.count()
            total_ingresos = sum(venta.total for venta in ventas_del_dia)
            productos_vendidos = sum(venta.quantity for venta in ventas_del_dia)
            
            return {
                'success': True,
                'data': {
                    'fecha': date.strftime('%Y-%m-%d'),
                    'total_ventas': total_ventas,
                    'total_ingresos': float(total_ingresos),
                    'productos_vendidos': productos_vendidos,
                    'empleado': f"{self.empleado.nombre} {self.empleado.apellido}",
                    'farmacia': self.empleado.farmacia.nombre_farmacia
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al obtener resumen diario: {str(e)}'
            }

