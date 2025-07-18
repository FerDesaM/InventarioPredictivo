
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('ajax/prediccion/', views.prediccion_producto_ajax, name='prediccion_producto_ajax'),
    path('ajax/ventas/', views.ventas_producto_ajax, name='ventas_producto'),
    path('', views.dashboard_view, name='dashboard'),
]