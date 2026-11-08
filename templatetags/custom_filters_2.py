# yourapp/templatetags/custom_filters.py
import os
from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='split_links')
def split_links(value, delimiter=','):
    return value.split(delimiter)
