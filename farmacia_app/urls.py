
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from farmacia_app.view.empleado_views import (
    empleado_dashboard_simple,
    api_buscar_medicamento,
    api_procesar_venta_simple,
    api_resumen_diario_simple
)


urlpatterns = [

   path('', lambda request: redirect('login')),
    path('login/', views.login_view, name='login'),

    path('ajax/prediccion/', views.prediccion_producto_ajax, name='prediccion_producto_ajax'),
    path('ajax/ventas/', views.ventas_producto_ajax, name='ventas_producto'),
    path('ajax/ranking-empleados-mes-anio/', views.ranking_empleados_mes_anio, name='ranking_empleados_mes_anio'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('empleado/dashboard/', empleado_dashboard_simple, name='empleado_dashboard'),
    path('logout/', views.logout_view, name='logout'),

     # URLs simplificadas para empleado
    path('api/empleado/buscar/', api_buscar_medicamento, name='api_empleado_buscar_simple'),
    path('api/empleado/procesar-venta/', api_procesar_venta_simple, name='api_empleado_procesar_venta_simple'),
    path('api/empleado/resumen-diario/', api_resumen_diario_simple, name='api_empleado_resumen_diario_simple'),

    path('compras/', views.compras_view, name='compras'),
    path('inventario/filtrado/', views.inventario_filtrado, name='inventario_filtrado'),
    path('ajax/ventas-farmacia/', views.ventas_por_farmacia, name='ventas_por_farmacia'),
    path('compras/', views.listar_compras, name='listar_compras')
    
]
    
