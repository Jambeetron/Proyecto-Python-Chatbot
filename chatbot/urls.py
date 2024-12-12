from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('chatbot/enviar/', views.enviar_mensaje, name='enviar_mensaje'),
    path('chatbot/borrar/', views.borrar_mensajes, name='borrar_mensajes'),
    path('registrar_emocion/', views.registrar_emocion, name='registrar_emocion'),
    path('ver_historial/', views.ver_historial, name='ver_historial'),
    path('eliminar_historial/', views.eliminar_historial, name='eliminar_historial'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('procesar_mensaje/', views.procesar_mensaje, name='procesar_mensaje'),
    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),
    path('editar/<int:id>/', views.editar_emocion, name='editar_emocion'),
    path('eliminar/<int:id>/', views.eliminar_emocion, name='eliminar_emocion'),
    path('programar_cita/', views.programar_cita, name='agendar_cita'),
    path('ver_citas/', views.ver_citas, name='ver_citas'),
]