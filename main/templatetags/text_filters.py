import re
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def italic(text):
    if not text:
        return ""

    # 1. Экранируем весь пользовательский текст
    text = escape(text)

    # 2. Заменяем ТОЛЬКО [i]...[/i] на <em>
    text = re.sub(r'\[курс\](.*?)\[/курс\]', r'<em>\1</em>', text, flags=re.DOTALL)

    # 3. Явно говорим Django: это безопасный HTML
    return mark_safe(text)
