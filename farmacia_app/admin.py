from django.contrib import admin

from .models import Farmacia, Producto, Empleado, Manager, InventarioFarmacia, Compra, Venta


@admin.register(Farmacia)
class FarmaciaAdmin(admin.ModelAdmin):
    list_display = ('nombre_farmacia', 'distrito', 'ciudad', 'pais')
    search_fields = ('nombre_farmacia', 'distrito')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'nombre_producto', 'clase', 'precio_unitario', 'fecha_vencimiento')
    list_filter = ('clase',)
    search_fields = ('nombre_producto', 'product_id')


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni', 'farmacia')
    search_fields = ('nombre', 'apellido', 'dni')


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'farmacia')
    search_fields = ('nombre', 'apellido')


@admin.register(InventarioFarmacia)
class InventarioFarmaciaAdmin(admin.ModelAdmin):
    list_display = ('farmacia', 'producto', 'stock')
    list_filter = ('farmacia',)
    search_fields = ('producto__nombre_producto',)


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('farmacia', 'producto', 'fecha_compra', 'cantidad', 'total_compra')
    list_filter = ('farmacia', 'fecha_compra')
    date_hierarchy = 'fecha_compra'


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'empleado', 'total', 'get_fecha')
    list_filter = ('month', 'year')
    search_fields = ('producto__nombre_producto',)

    def get_fecha(self, obj):
        return f"{obj.dia}/{obj.month}/{obj.year}"

    get_fecha.short_description = 'Fecha'
