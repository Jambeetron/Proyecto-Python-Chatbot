from django.db import models

class Emocion(models.Model):
    nombre = models.CharField(max_length=255)
    emocion = models.CharField(max_length=50)
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.emocion}"
