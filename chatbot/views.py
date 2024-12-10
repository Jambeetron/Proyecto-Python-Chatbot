import json
import unicodedata
import re

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from .models import Mensaje, Emocion, CustomUser

# Lista de emociones válidas
emociones_validas = ["Estrés", "Ansiedad", "Tristeza", "Alegría"]

# Página principal
def home(request):
    """
    Renderiza la página principal.
    """
    return render(request, 'index.html')

# Chatbot
@login_required(login_url='/login/')
def chatbot_view(request):
    """
    Vista del chatbot. Muestra los mensajes ordenados por fecha.
    """
    mensajes = Mensaje.objects.all().order_by("fecha")
    for mensaje in mensajes:
        mensaje.clase = "usuario" if mensaje.remitente == "usuario" else "bot"
    return render(request, "chatbot/chatbot.html", {"mensajes": mensajes})

# Registrar emoción
@login_required(login_url='/login/')
def registrar_emocion(request):
    """
    Registra una nueva emoción en la base de datos.
    """
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        emocion = request.POST.get("emocion", "").strip()
        comentario = request.POST.get("comentario", "").strip()

        if not nombre or emocion not in emociones_validas or not comentario:
            return HttpResponse("Datos inválidos o incompletos", status=400)

        Emocion.objects.create(nombre=nombre, emocion=emocion, comentario=comentario)
        return redirect('ver_historial')
    return render(request, 'registro_emocion.html')

# Ver historial de emociones
@login_required(login_url='/login/')
def ver_historial(request):
    """
    Muestra el historial de emociones registradas.
    """
    historial = Emocion.objects.all().order_by('-fecha')
    return render(request, 'historial_emocional.html', {'historial': historial})

# Procesar mensajes del chatbot
def procesar_mensaje(request):
    """
    Procesa un mensaje enviado por el usuario y genera una respuesta del chatbot.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        mensaje = data.get("mensaje", "")
        respuesta = obtener_respuesta(mensaje)

        usuario = request.user if request.user.is_authenticated else None
        Mensaje.objects.create(usuario=usuario, mensaje=mensaje, remitente="usuario")
        Mensaje.objects.create(usuario=None, mensaje=respuesta, remitente="bot")

        return JsonResponse({
            "respuesta": respuesta,
            "usuario": usuario.username if usuario else "Usuario desconocido",
        })
    return JsonResponse({"error": "Método no permitido"}, status=405)

# Obtener respuesta del chatbot
def obtener_respuesta(mensaje):
    """
    Genera una respuesta predefinida para el chatbot.
    """
    respuestas = {
        "hola": "¡Hola! ¿En qué puedo ayudarte?",
        "como estas": "¡Estoy bien! ¿En qué puedo asistirte hoy?",
        "adios": "¡Hasta luego! Que tengas un buen día.",
        "gracias": "¡De nada! Estoy aquí para ayudarte.",
        "que puedes hacer": "Puedo responder preguntas básicas y ayudarte con lo que necesites.",
    }
    return respuestas.get(mensaje.lower(), "Lo siento, no entiendo tu mensaje. ¿Puedes intentar de otra forma?")

# Registrar usuario
def register_view(request):
    if request.method == 'POST':
        print(request.POST)
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                print(f"Role recibido: {form.cleaned_data.get('role')}")
                user = form.save(commit=False)
                user.role = form.cleaned_data['role']
                user.save()
                login(request, user)
                return redirect('home')
            except Exception as e:
                print(f"Error al guardar el usuario: {e}")
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

# Login de usuario
def login_view(request):
    """
    Autentica un usuario y lo inicia sesión.
    """
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('registrar_emocion')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

# Logout de usuario
def logout_view(request):
    """
    Cierra la sesión del usuario.
    """
    logout(request)
    return redirect('home')

# Normalizar texto
def normalizar_texto(texto):
    """
    Normaliza un texto eliminando tildes y caracteres especiales.
    """
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.lower().strip()

# Borrar mensajes
@login_required(login_url='/login/')
def borrar_mensajes(request):
    """
    Elimina todos los mensajes del chatbot.
    """
    if request.method == "POST":
        Mensaje.objects.all().delete()
        return redirect('chatbot')
    return HttpResponse("Método no permitido", status=405)

# Eliminar historial de emociones
@login_required(login_url='/login/')
def eliminar_historial(request):
    """
    Elimina todo el historial de emociones.
    """
    if request.method == "POST":
        Emocion.objects.all().delete()
        return redirect('ver_historial')

@login_required
def enviar_mensaje(request):
    if request.method == "POST":
        mensaje_texto = request.POST.get("mensaje", "").strip()
        if not mensaje_texto:
            return JsonResponse({"respuesta": "El mensaje no puede estar vacío."}, status=400)

        try:
            # Guarda el mensaje en la base de datos
            Mensaje.objects.create(
                usuario=request.user,  # Asegúrate de que request.user sea válido
                mensaje=mensaje_texto,
                remitente="usuario",
            )
            return JsonResponse({"respuesta": "Mensaje enviado correctamente."})
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
            return JsonResponse({"respuesta": "Hubo un error al enviar el mensaje."}, status=500)
    return JsonResponse({"error": "Método no permitido"}, status=405)

# Verifica si un nombre de usuario ya existe
def check_username(request):
    username = request.GET.get('username', None)
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

# Verifica si un correo electrónico ya existe
def check_email(request):
    email = request.GET.get('email', None)
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})
