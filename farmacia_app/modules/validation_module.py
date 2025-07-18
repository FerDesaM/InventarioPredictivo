"""
Módulo de Validaciones para Empleados
Valida datos y permisos en el sistema de inventario
"""

from farmacia_app.models import Empleado, InventarioFarmacia, Producto
from django.utils import timezone
from datetime import datetime, timedelta
import re


class ValidationManager:
    """Clase para gestionar validaciones del sistema"""
    
    def __init__(self, empleado_dni=None):
        self.empleado_dni = empleado_dni
        self.empleado = None
        if empleado_dni:
            self._load_empleado()
    
    def _load_empleado(self):
        """Carga la información del empleado"""
        try:
            self.empleado = Empleado.objects.get(dni=self.empleado_dni)
        except Empleado.DoesNotExist:
            self.empleado = None
    
    def validate_employee_permissions(self, required_permission=None):
        """
        Valida los permisos del empleado
        
        Args:
            required_permission (str): Permiso requerido
            
        Returns:
            dict: Resultado de la validación
        """
        if not self.empleado:
            return {
                'valid': False,
                'error': 'Empleado no encontrado o no autenticado'
            }
        
        # Validaciones básicas
        validations = {
            'employee_exists': True,
            'has_pharmacy': bool(self.empleado.farmacia),
            'is_active': True  # Asumimos que todos los empleados en BD están activos
        }
        
        # Validar permisos específicos
        if required_permission:
            if required_permission == 'admin' and not self.empleado.es_admin:
                return {
                    'valid': False,
                    'error': 'Se requieren permisos de administrador'
                }
        
        if not all(validations.values()):
            return {
                'valid': False,
                'error': 'El empleado no cumple con los requisitos necesarios'
            }
        
        return {
            'valid': True,
            'employee_data': {
                'dni': self.empleado.dni,
                'nombre': self.empleado.nombre,
                'apellido': self.empleado.apellido,
                'farmacia_id': self.empleado.farmacia.id,
                'farmacia_nombre': self.empleado.farmacia.nombre_farmacia,
                'es_admin': self.empleado.es_admin
            }
        }
    
    def validate_product_access(self, producto_id):
        """
        Valida que el empleado tenga acceso al producto en su farmacia
        
        Args:
            producto_id (str): ID del producto
            
        Returns:
            dict: Resultado de la validación
        """
        if not self.empleado:
            return {
                'valid': False,
                'error': 'Empleado no autenticado'
            }
        
        try:
            inventario_item = InventarioFarmacia.objects.filter(
                farmacia_id=self.empleado.farmacia.id,
                producto__product_id=producto_id
            ).select_related('producto').first()
            
            if not inventario_item:
                return {
                    'valid': False,
                    'error': 'Producto no disponible en esta farmacia'
                }
            
            return {
                'valid': True,
                'product_data': {
                    'producto_id': inventario_item.producto.product_id,
                    'nombre': inventario_item.producto.nombre_producto,
                    'stock': inventario_item.stock,
                    'precio': float(inventario_item.producto.precio_unitario)
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error al validar acceso al producto: {str(e)}'
            }
    
    def validate_sale_data(self, sale_data):
        """
        Valida los datos de una venta
        
        Args:
            sale_data (dict): Datos de la venta
            
        Returns:
            dict: Resultado de la validación
        """
        errors = []
        
        # Validar campos requeridos
        required_fields = ['producto_id', 'cantidad']
        for field in required_fields:
            if field not in sale_data or not sale_data[field]:
                errors.append(f'Campo requerido: {field}')
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        
        # Validar tipos de datos
        try:
            cantidad = int(sale_data['cantidad'])
            if cantidad <= 0:
                errors.append('La cantidad debe ser mayor a 0')
        except (ValueError, TypeError):
            errors.append('La cantidad debe ser un número entero válido')
        
        # Validar producto_id
        producto_id = sale_data['producto_id']
        if not isinstance(producto_id, str) or len(producto_id.strip()) == 0:
            errors.append('ID de producto no válido')
        
        # Validar tipo de comprobante si se proporciona
        if 'tipo_comprobante' in sale_data:
            valid_types = ['boleta', 'factura']
            if sale_data['tipo_comprobante'] not in valid_types:
                errors.append(f'Tipo de comprobante debe ser uno de: {", ".join(valid_types)}')
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        
        return {
            'valid': True,
            'validated_data': {
                'producto_id': producto_id.strip(),
                'cantidad': cantidad,
                'tipo_comprobante': sale_data.get('tipo_comprobante', 'boleta')
            }
        }
    
    def validate_stock_availability(self, producto_id, cantidad_solicitada):
        """
        Valida la disponibilidad de stock para una venta
        
        Args:
            producto_id (str): ID del producto
            cantidad_solicitada (int): Cantidad solicitada
            
        Returns:
            dict: Resultado de la validación
        """
        if not self.empleado:
            return {
                'valid': False,
                'error': 'Empleado no autenticado'
            }
        
        try:
            inventario_item = InventarioFarmacia.objects.filter(
                farmacia_id=self.empleado.farmacia.id,
                producto__product_id=producto_id
            ).select_related('producto').first()
            
            if not inventario_item:
                return {
                    'valid': False,
                    'error': 'Producto no encontrado en el inventario'
                }
            
            # Verificar stock disponible
            if inventario_item.stock < cantidad_solicitada:
                return {
                    'valid': False,
                    'error': f'Stock insuficiente. Disponible: {inventario_item.stock}, Solicitado: {cantidad_solicitada}'
                }
            
            # Verificar fecha de vencimiento
            if inventario_item.producto.fecha_vencimiento < timezone.now().date():
                return {
                    'valid': False,
                    'error': 'El producto está vencido'
                }
            
            # Advertencia si el producto vence pronto
            days_to_expire = (inventario_item.producto.fecha_vencimiento - timezone.now().date()).days
            warning = None
            if days_to_expire <= 30:
                warning = f'Advertencia: El producto vence en {days_to_expire} días'
            
            return {
                'valid': True,
                'stock_info': {
                    'stock_disponible': inventario_item.stock,
                    'stock_restante': inventario_item.stock - cantidad_solicitada,
                    'fecha_vencimiento': inventario_item.producto.fecha_vencimiento.strftime('%Y-%m-%d'),
                    'days_to_expire': days_to_expire,
                    'warning': warning
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error al validar stock: {str(e)}'
            }
    
    def validate_search_parameters(self, search_params):
        """
        Valida los parámetros de búsqueda
        
        Args:
            search_params (dict): Parámetros de búsqueda
            
        Returns:
            dict: Resultado de la validación
        """
        validated_params = {}
        errors = []
        
        # Validar query de búsqueda
        if 'query' in search_params:
            query = search_params['query']
            if query and len(query.strip()) > 0:
                # Limpiar query de caracteres especiales peligrosos
                cleaned_query = re.sub(r'[<>"\';]', '', query.strip())
                validated_params['query'] = cleaned_query
        
        # Validar filtros numéricos
        numeric_filters = ['precio_min', 'precio_max', 'stock_min', 'stock_max', 'expires_in_days']
        for filter_name in numeric_filters:
            if filter_name in search_params:
                try:
                    value = float(search_params[filter_name])
                    if value >= 0:
                        validated_params[filter_name] = value
                    else:
                        errors.append(f'{filter_name} debe ser mayor o igual a 0')
                except (ValueError, TypeError):
                    errors.append(f'{filter_name} debe ser un número válido')
        
        # Validar filtros de texto
        text_filters = ['clase', 'stock_status', 'order_by']
        for filter_name in text_filters:
            if filter_name in search_params:
                value = search_params[filter_name]
                if value and isinstance(value, str):
                    validated_params[filter_name] = value.strip()
        
        # Validar paginación
        if 'page' in search_params:
            try:
                page = int(search_params['page'])
                if page > 0:
                    validated_params['page'] = page
                else:
                    errors.append('El número de página debe ser mayor a 0')
            except (ValueError, TypeError):
                errors.append('El número de página debe ser un entero válido')
        
        if 'per_page' in search_params:
            try:
                per_page = int(search_params['per_page'])
                if 1 <= per_page <= 100:
                    validated_params['per_page'] = per_page
                else:
                    errors.append('Elementos por página debe estar entre 1 y 100')
            except (ValueError, TypeError):
                errors.append('Elementos por página debe ser un entero válido')
        
        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        
        return {
            'valid': True,
            'validated_params': validated_params
        }
    
    def validate_date_range(self, start_date, end_date):
        """
        Valida un rango de fechas
        
        Args:
            start_date (str): Fecha de inicio
            end_date (str): Fecha de fin
            
        Returns:
            dict: Resultado de la validación
        """
        try:
            # Convertir strings a objetos date
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            # Validar que la fecha de inicio no sea posterior a la de fin
            if start_date > end_date:
                return {
                    'valid': False,
                    'error': 'La fecha de inicio no puede ser posterior a la fecha de fin'
                }
            
            # Validar que las fechas no sean muy antiguas o futuras
            today = timezone.now().date()
            max_past = today - timedelta(days=365)  # 1 año atrás
            max_future = today + timedelta(days=365)  # 1 año adelante
            
            if start_date < max_past:
                return {
                    'valid': False,
                    'error': 'La fecha de inicio es muy antigua'
                }
            
            if end_date > max_future:
                return {
                    'valid': False,
                    'error': 'La fecha de fin es muy lejana'
                }
            
            return {
                'valid': True,
                'validated_dates': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
        except ValueError as e:
            return {
                'valid': False,
                'error': f'Formato de fecha inválido. Use YYYY-MM-DD: {str(e)}'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error al validar fechas: {str(e)}'
            }

