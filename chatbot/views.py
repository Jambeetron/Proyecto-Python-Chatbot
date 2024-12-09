from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Emocion, Mensaje
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import re
import unicodedata
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

# Lista de emociones válidas
emociones_validas = ["Estrés", "Ansiedad", "Tristeza", "Alegría"]

# Página principal
def home(request):
    return render(request, 'index.html')

def chatbot(request):
    mensajes = Mensaje.objects.all().order_by('fecha')
    for mensaje in mensajes:
        mensaje.clase = "usuario" if mensaje.remitente == "usuario" else "bot"
    return render(request, 'chatbot/chatbot.html', {'mensajes': mensajes})

# Registrar emoción
@login_required
def registrar_emocion(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        emocion = request.POST.get("emocion", "").strip()
        comentario = request.POST.get("comentario", "").strip()

        if not nombre or emocion not in emociones_validas or not comentario:
            return HttpResponse("Datos inválidos o incompletos", status=400)

        # Guardar en la base de datos
        emocion_obj = Emocion(nombre=nombre, emocion=emocion, comentario=comentario)
        emocion_obj.save()

        return redirect('ver_historial')

    return render(request, 'registro_emocion.html')

# Ver historial de emociones
@login_required
def ver_historial(request):
    historial = Emocion.objects.all().order_by('-fecha')
    return render(request, 'historial_emocional.html', {'historial': historial})

# Procesar mensajes del chatbot
def procesar_mensaje(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mensaje = data.get("mensaje", "")
        respuesta = obtener_respuesta(mensaje)  # Usa la función para generar una respuesta adecuada.

        # Guardar el mensaje del usuario en la base de datos
        usuario = request.user if request.user.is_authenticated else None
        Mensaje.objects.create(usuario=usuario, mensaje=mensaje, remitente="usuario")

        # Guardar la respuesta del bot en la base de datos
        Mensaje.objects.create(usuario=None, mensaje=respuesta, remitente="bot")

        return JsonResponse({
            "respuesta": respuesta,
            "usuario": usuario.username if usuario else "Usuario desconocido",
        })


def obtener_respuesta(mensaje):
    respuestas = {
        "hola": "¡Hola! ¿En qué puedo ayudarte?",
        "como estas": "¡Estoy bien! ¿En qué puedo asistirte hoy?",
        "adios": "¡Hasta luego! Que tengas un buen día.",
        "gracias": "¡De nada! Estoy aquí para ayudarte.",
        "que puedes hacer": "Puedo responder preguntas básicas y ayudarte con lo que necesites.",
    }
    return respuestas.get(mensaje.lower(), "Lo siento, no entiendo tu mensaje. ¿Puedes intentar de otra forma?")

def borrar_mensajes(request):
    if request.method == "POST":
        Mensaje.objects.all().delete()
        return redirect('chatbot')

# Vista para registrar usuarios
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print(request.POST)
        if form.is_valid():
            user = form.save()  # Guarda al usuario en la base de datos
            login(request, user)  # Inicia sesión automáticamente después del registro
            messages.success(request, "¡Tu cuenta ha sido creada exitosamente!")
            return redirect('login')  # Redirige al usuario a la página principal
        else:
            print(form.errors)def register_view(request)
            return render(request, 'auth/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form}) 

# Vista para cerrar sesión
def logout_view(request):
    logout(request)
    return redirect('login')

# Función para normalizar texto
def normalizar_texto(texto):
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.lower().strip()

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/registrar_emocion/')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def enviar_mensaje(request):
    if request.method == "POST":
        mensaje_texto = request.POST.get("mensaje", "").strip()
        if not mensaje_texto:
            return JsonResponse({"respuesta": "El mensaje no puede estar vacío."}, status=400)

        try:
            # Guardar el mensaje en la base de datos como remitente "usuario"
            Mensaje.objects.create(
                usuario=request.user,  # Verifica que `request.user` sea válido
                mensaje=mensaje_texto,
                remitente="usuario",
            )
            return JsonResponse({"respuesta": "Mensaje enviado correctamente."})
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
            return JsonResponse({"respuesta": "Hubo un error al enviar el mensaje."}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required(login_url='/login/')
def chatbot_view(request):
    mensajes = Mensaje.objects.all().order_by("fecha")
    return render(request, "chatbot/chatbot.html", {"mensajes": mensajes})

def crear_chatbot():
    User.objects.get_or_create(
        username="Chatbot",
        defaults={"email": "chatbot@example.com", "password": "securepassword"}
    )

def eliminar_historial(request):
    if request.method == "POST":
        Emocion.objects.all().delete()  # Elimina todos los registros
        return redirect('ver_historial')  # Redirige nuevamente al historial
    
@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
    return render(request, 'admin_dashboard.html')

def check_username(request):
    username = request.GET.get('username', None)
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def check_email(request):
    email = request.GET.get('email', None)
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})