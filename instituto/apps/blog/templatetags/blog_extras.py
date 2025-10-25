from django import template
import re
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def first_image_from_html(value):
    """Devuelve el atributo src del primer <img> encontrado en el HTML o cadena vacía."""
    if not value:
        return ''
    # buscar <img ... src="..." ...>
    m = re.search(r'<img[^>]+src=[\'\"]([^\'\"]+)[\'\"]', value, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    return ''


@register.filter
def strip_html_excerpt(value, words=20):
    """Quita etiquetas HTML y trunca a N palabras."""
    if not value:
        return ''
    text = strip_tags(value)
    parts = text.split()
    if len(parts) <= int(words):
        return ' '.join(parts)
    return ' '.join(parts[:int(words)]) + '...'
