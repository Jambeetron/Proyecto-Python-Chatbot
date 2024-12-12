from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.apps import apps


class Emocion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Relaciona con el usuario
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=50)
    emocion = models.CharField(max_length=50)
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.emocion} ({self.fecha})"

class Mensaje(models.Model):
    class RemitenteChoices(models.TextChoices):
        USUARIO = "usuario", _("Usuario")
        BOT = "bot", _("Bot")

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    mensaje = models.TextField()
    remitente = models.CharField(
        max_length=10,
        choices=RemitenteChoices.choices
    )
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario}: {self.mensaje[:50]} ({self.remitente})"
    
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

class Cita(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=50)
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.TextField()
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cita de {self.nombre} el {self.fecha} a las {self.hora}"
