from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registrar_emocion/', views.registrar_emocion, name='registrar_emocion'),
    path('historial/', views.ver_historial, name='ver_historial'),
    path('procesar_mensaje/', views.procesar_mensaje, name='procesar_mensaje'),
]
