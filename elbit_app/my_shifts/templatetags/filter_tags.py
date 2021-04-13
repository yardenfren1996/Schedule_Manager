from django import template

register = template.Library()


@register.filter(name='get_value')
def get_value(dictionary, key):
    return dictionary[key]


@register.filter(name='get_capacity')
def get_capacity(dictionary, key):
    return dictionary[key][0]


@register.filter(name='replace_with_space')
def replace_with_space(value, arg):
    return value.replace(arg, ' ')
