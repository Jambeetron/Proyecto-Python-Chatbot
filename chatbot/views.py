from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Emocion

# Lista de emociones válidas
emociones_validas = ["Estrés", "Ansiedad", "Tristeza", "Alegría"]

# Página principal
def home(request):
    return render(request, 'index.html')

def chatbot(request):
    return render(request, 'chatbot/chatbot.html')

# Registrar emoción
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

    return render(request, 'index.html')

# Ver historial de emociones
def ver_historial(request):
    # Obtener datos del modelo
    historial = Emocion.objects.all().order_by('-fecha')  # Ordenar por fecha descendente
    return render(request, 'historial_emocional.html', {'historial': historial})

# Procesar mensajes del chatbot
def procesar_mensaje(request):
    if request.method == "POST":
        mensaje = request.POST.get("mensaje", "").lower()

        # Respuestas predefinidas
        respuestas = {
            "hola": "¡Hola! ¿En qué puedo ayudarte?",
            "adiós": "¡Hasta luego! Que tengas un buen día.",
        }
        respuesta = respuestas.get(mensaje, "Lo siento, no entiendo tu mensaje. ¿Puedes intentar de otra forma?")

        return JsonResponse({"respuesta": respuesta})
