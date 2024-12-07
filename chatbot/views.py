from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse

def home(request):
    return render(request, 'index.html')

# Simula tu lógica de base de datos
emociones_validas = ["Estrés", "Ansiedad", "Tristeza", "Alegría"]

def registrar_emocion(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        emocion = request.POST.get("emocion", "").strip()
        comentario = request.POST.get("comentario", "").strip()

        if not nombre or emocion not in emociones_validas or not comentario:
            return HttpResponse("Datos inválidos o incompletos", status=400)

        # Aquí agregas la lógica para guardar en la base de datos (usando modelos)
        print(f"Nombre: {nombre}, Emoción: {emocion}, Comentario: {comentario}")

        return redirect('ver_historial')

    return render(request, 'index.html')

def ver_historial(request):
    # Simula los datos del historial
    historial = [
        {"fecha": "2024-12-06", "emocion": "Alegría", "comentario": "Me siento genial", "nombre": "Juan"},
        {"fecha": "2024-12-05", "emocion": "Ansiedad", "comentario": "Un poco preocupado", "nombre": "María"},
    ]
    return render(request, 'historial_emocional.html', {'historial': historial})

def procesar_mensaje(request):
    if request.method == "POST":
        mensaje = request.POST.get("mensaje", "").lower()
        if "hola" in mensaje:
            respuesta = "¡Hola! ¿En qué puedo ayudarte?"
        elif "adiós" in mensaje:
            respuesta = "¡Hasta luego! Que tengas un buen día."
        else:
            respuesta = "Lo siento, no entiendo tu mensaje. ¿Puedes intentar de otra forma?"

        return JsonResponse({"respuesta": respuesta})