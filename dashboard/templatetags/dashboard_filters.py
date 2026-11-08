from django import template

register = template.Library()
@register.filter
def split_links(value):
    return value.split(',')