from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='authentication'),
    path('login/intent/', views.login_intent, name='authentication/login_intent'),
    path('listar_vehiculos', views.vehiculos_list, name='vehiculos_list'),
    path('listar_usuarios', views.usuarios_list, name='usuarios_list'),
    path('registrar_vehiculo', views.registrar_vehiculo, name='registrar_vehiculo'),
    path('registrar_usuario', views.registrar_usuario, name='registrar_usuario'),
    path('editar_vehiculo/<int:pk>', views.editar_vehiculo, name='editar_vehiculo'),
    path('listar_multas/<int:pk>', views.listar_multas, name='multas_list'),
    path('registrar_multa/<int:pk>', views.registrar_multa, name='registrar_multa'),
    path('consultar_vehiculo', views.consultar_vehiculo, name='consultar_vehiculo'),
    path('eliminar_vehiculo/<int:pk>', views.eliminar_vehiculo, name='eliminar_vehiculo'),
    path('logs_list', views.logs_list, name='logs_list'),
    path('logout', views.logout_view, name='authentication/logout_view'),
]