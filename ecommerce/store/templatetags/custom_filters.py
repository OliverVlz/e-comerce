from django import template

register = template.Library()

@register.filter
def format_cop(value):
    try:
        value = int(value)  # Convertimos a entero
        # Convertir el número al formato de mil con `.`
        formatted = f"{value:,}".replace(",", ".")
        # Reemplazar los millones con `'`
        if value >= 1000000:
            formatted = formatted.replace(".", "'", 1)
        return formatted
    except (ValueError, TypeError):
        return value
