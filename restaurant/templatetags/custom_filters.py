from django import template

register=template.Library()

@register.filter(name='capitalize_first')
def capitalize_first(value):
    return value.capitalize()

@register.filter(name='get_first_letter_capitalize')
def get_first_letter_capitalize(value):
    return value[0].upper() if value else ''