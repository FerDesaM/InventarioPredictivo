
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from farmacia_app.view.empleado_views import (
    empleado_dashboard,
    api_get_inventory,
    api_search_products,
    api_get_product_details,
    api_process_sale,
    api_validate_sale,
    api_get_sales_history,
    api_get_suggestions,
    api_search_by_barcode,
    api_get_daily_summary
)


urlpatterns = [
    path('', lambda request: redirect('login')),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('empleado/dashboard/', views.empleado_dashboard, name='empleado_dashboard'),
    path('logout/', views.logout_view, name='logout'),

     # NUEVAS URLs para empleado mejorado
    path('empleado/dashboard/', empleado_dashboard, name='empleado_dashboard'),
    
    # APIs de inventario
    path('api/empleado/inventario/', api_get_inventory, name='api_empleado_inventario'),
    path('api/empleado/buscar/', api_search_products, name='api_empleado_buscar'),
    path('api/empleado/producto/<str:producto_id>/', api_get_product_details, name='api_empleado_producto'),
    
    # APIs de ventas
    path('api/empleado/venta/', api_process_sale, name='api_empleado_venta'),
    path('api/empleado/validar-venta/', api_validate_sale, name='api_empleado_validar_venta'),
    path('api/empleado/historial/', api_get_sales_history, name='api_empleado_historial'),
    path('api/empleado/resumen-diario/', api_get_daily_summary, name='api_empleado_resumen_diario'),
    
    # APIs de búsqueda
    path('api/empleado/sugerencias/', api_get_suggestions, name='api_empleado_sugerencias'),
    path('api/empleado/codigo/<str:barcode>/', api_search_by_barcode, name='api_empleado_codigo'),

]