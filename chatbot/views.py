import json
import unicodedata
import re

from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from .models import Mensaje, Emocion, CustomUser
from django.views.decorators.cache import never_cache
from .forms import EmocionForm
from django.shortcuts import render
from django.contrib import admin
from .models import Cita
import logging

# Lista de emociones válidas
emociones_validas = ["Estrés", "Ansiedad", "Tristeza", "Alegría"]

# Página principal
def home(request):
    """
    Renderiza la página principal.
    """
    return render(request, 'index.html')

# Chatbot
@never_cache
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
        "hola": "¡Hola! Estoy aquí para escucharte y apoyarte. ¿Cómo te sientes hoy?",
        "como estas": "Estoy aquí para ayudarte. ¿Qué emoción estás experimentando en este momento?",
        "adios": "Recuerda que siempre puedes volver cuando lo necesites. ¡Cuídate!",
        "gracias": "¡De nada! Recuerda que está bien pedir ayuda cuando la necesites.",
        "que puedes hacer": "Puedo ayudarte a gestionar tus emociones, brindarte consejos y apoyarte en momentos difíciles.",
        "me siento triste": "Siento que estés pasando por esto. ¿Te gustaría que te comparta algunas técnicas para sentirte mejor?",
        "estoy ansioso": "La ansiedad puede ser difícil de manejar. ¿Te interesa aprender ejercicios de respiración para calmarte?",
        "me siento solo": "Recuerda que no estás solo. Estoy aquí para apoyarte y escucharte. ¿Qué puedo hacer por ti?",
        "no puedo dormir": "El insomnio puede ser complicado. ¿Te gustaría que te comparta algunas recomendaciones para relajarte antes de dormir?",
        "tengo miedo": "Es normal sentir miedo a veces. ¿Quieres hablar más sobre lo que te preocupa?",
        "estoy enojado": "El enojo puede ser intenso. ¿Te gustaría conocer formas de canalizarlo de manera saludable?",
        "me siento abrumado": "Es normal sentirse abrumado a veces. ¿Te gustaría que exploremos juntos cómo priorizar lo que te preocupa?",
        "necesito ayuda": "Estoy aquí para apoyarte. Cuéntame más sobre lo que necesitas.",
        "quiero relajarme": "Puedes intentar cerrar los ojos y tomar respiraciones profundas. ¿Te gustaría que te guíe en una breve meditación?",
        "como gestiono mis emociones": "Gestionar tus emociones puede ser un reto. Te puedo ayudar con estrategias como respiración, meditación o escribir tus pensamientos.",
        "me siento feliz": "¡Me alegra escucharlo! Comparte lo que te hace feliz para celebrarlo juntos.",
        "que es la salud mental": "La salud mental es tu bienestar emocional, psicológico y social. Es tan importante como tu salud física.",
        "estoy estresado": "El estrés puede ser agotador. ¿Quieres que te sugiera formas de reducirlo?",
        "necesito hablar con alguien": "Hablar con alguien es una excelente idea. Puedo ayudarte o conectarte con recursos útiles.",
        "que es la ansiedad": "La ansiedad es una respuesta natural del cuerpo al estrés. Si es frecuente, podemos explorar formas de manejarla.",
        "que es la depresión": "La depresión es un estado emocional complejo. Si sientes que puede estar afectándote, te sugiero buscar apoyo profesional.",
        "como busco ayuda profesional": "Te puedo ayudar a encontrar recursos y guiarte sobre cómo dar el primer paso para buscar ayuda profesional.",
        "como manejo el estrés": "El estrés puede manejarse con ejercicios como respiración, actividad física o hablar sobre lo que te preocupa.",
        "me siento bloqueado": "A veces sentirnos bloqueados puede indicar que necesitamos un descanso. ¿Te gustaría algunas técnicas para despejar tu mente?",
        "quiero llorar": "Está bien llorar, es una forma natural de liberar emociones. Estoy aquí para escucharte si quieres hablar.",
        "me siento inseguro": "Todos sentimos inseguridad a veces. ¿Te gustaría hablar sobre lo que te está preocupando?",
        "que es mindfulness": "El mindfulness es una práctica que ayuda a estar presente en el momento, reduciendo la ansiedad y el estrés.",
        "me siento agotado": "Sentirse agotado puede ser una señal de que necesitas tiempo para ti. ¿Puedo sugerirte maneras de recargar energías?",
        "no puedo concentrarme": "La falta de concentración puede ser causada por estrés o cansancio. ¿Quieres que te comparta técnicas para mejorar tu enfoque?",
        "quiero mejorar mi autoestima": "Mejorar la autoestima lleva tiempo. Podemos explorar afirmaciones positivas y ejercicios para reconocer tu valor.",
        "que hago si tengo un ataque de panico": "Primero, intenta enfocarte en tu respiración. Inhala lentamente contando hasta 4, sostén por 4, y exhala por 4. Estoy aquí para apoyarte.",
        "como practico la gratitud": "Practicar la gratitud puede ser simple. Intenta escribir tres cosas por las que te sientes agradecido cada día.",
        "que es la terapia": "La terapia es un espacio seguro donde un profesional puede ayudarte a explorar y manejar tus emociones.",
        "como busco apoyo en la universidad": "Puedes buscar ayuda en el departamento de bienestar estudiantil de la ECCI. Ellos ofrecen recursos y apoyo para los estudiantes.",
        "como hablo con un amigo que está triste": "Sé empático, escucha sin juzgar y hazle saber que estás ahí para apoyarlo. A veces, estar presente es suficiente.",
        "me siento culpable": "La culpa puede ser una emoción difícil. Reflexionar sobre lo ocurrido y perdonarte a ti mismo puede ayudarte a avanzar.",
        "que hago si estoy abrumado por las tareas": "Divide las tareas en pasos más pequeños, prioriza lo más importante y date descansos regulares.",
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
                return redirect('login')
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

def editar_emocion(request, id):
    emocion = get_object_or_404(Emocion, id=id)

    if request.method == 'POST':
        form = EmocionForm(request.POST, instance=emocion)
        if form.is_valid():
            form.save()
            return redirect('ver_historial')  # Redirige al historial después de guardar
    else:
        form = EmocionForm(instance=emocion)

    return render(request, 'editar_emocion.html', {'form': form})

def eliminar_emocion(request, id):
    emocion = get_object_or_404(Emocion, id=id)
    emocion.delete()
    return redirect('ver_historial')

def programar_cita(request):
    return render(request, 'programar_cita.html')

@login_required(login_url='/login/')
def ver_citas(request):
    citas = Cita.objects.all().order_by('fecha', 'hora')
    print(f"Citas disponibles para {request.user}: {list(citas)}")  # Agrega este print
    return render(request, 'ver_citas.html', {'citas': citas})

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha', 'hora', 'motivo', 'usuario')
    list_filter = ('fecha',)
    search_fields = ('nombre', 'motivo')

# Configuración del logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@login_required(login_url='/login/')
def agendar_cita(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        motivo = request.POST.get("motivo")

        logger.debug(f"Datos recibidos: Nombre={nombre}, Fecha={fecha}, Hora={hora}, Motivo={motivo}")
        logger.debug(f"Usuario autenticado: {request.user}")

        # Validar campos vacíos
        if not nombre or not fecha or not hora or not motivo:
            logger.error("Faltan datos en el formulario.")
            return render(request, 'programar_cita.html', {
                'error': 'Por favor, completa todos los campos.',
            })

        # Validar datos duplicados (opcional)
        citas_existentes = Cita.objects.filter(usuario=request.user, fecha=fecha, hora=hora)
        if citas_existentes.exists():
            logger.warning("El usuario ya tiene una cita programada en la misma fecha y hora.")
            return render(request, 'programar_cita.html', {
                'error': 'Ya tienes una cita programada en esta fecha y hora.',
            })

        try:
            # Crear una nueva cita
            nueva_cita = Cita.objects.create(
                usuario=request.user,
                nombre=nombre,
                fecha=fecha,
                hora=hora,
                motivo=motivo
            )
            logger.info(f"Cita creada exitosamente: {nueva_cita}")
            return redirect('ver_citas')
        except Exception as e:
            logger.error(f"Error al guardar la cita: {e}")
            return render(request, 'programar_cita.html', {
                'error': 'Hubo un problema al guardar la cita. Por favor, intenta nuevamente.',
            })

    logger.debug("Mostrando formulario para programar una cita.")
    return render(request, 'programar_cita.html')
