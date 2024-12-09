from django import template

register = template.Library()

@register.filter
def upper_case(value):
    """
    Convierte el texto a mayúsculas.
    """
    return value.upper()

@register.filter
def clase_remitente(remitente):
    """
    Devuelve la clase CSS según el remitente.
    """
    return "usuario" if remitente == "usuario" else "bot"
