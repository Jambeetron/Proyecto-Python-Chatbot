from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings

class Emocion(models.Model):
    nombre = models.CharField(max_length=50)
    emocion = models.CharField(max_length=50)
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.emocion} ({self.fecha})"

class Mensaje(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    mensaje = models.TextField()
    remitente = models.CharField(
        max_length=10, choices=[("usuario", "Usuario"), ("bot", "Bot")]
    )
    fecha = models.DateTimeField(auto_now_add=True)

class CustomUser(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('CLIENT', 'Cliente'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='CLIENT')

    def is_admin(self):
        return self.role == 'ADMIN'

    def is_client(self):
        return self.role == 'CLIENT'