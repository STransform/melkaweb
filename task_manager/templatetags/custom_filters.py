import os
from django import template
from task_manager.models import Task  # Correct import statement
register = template.Library()
from django.conf import settings
from pathlib import Path
from datetime import datetime


@register.simple_tag
def get_task_count_by_status(status):
    return Task.objects.filter(status=status).count()


@register.filter(name='get_key_tasks')
def get_key_tasks(task):
    return task.key_tasks.split('\n') if task.key_tasks else []

@register.simple_tag
def get_field_attr(obj, field):
    if hasattr(obj, field):
        value = getattr(obj,field, None)
        if isinstance(value, str) and len(value)>25:
            value = value[:25] +"..."
        elif isinstance(value, datetime):
            value = value.date()
            
        return value 
    return None

@register.filter()
def formalize(field:str):
    return field.capitalize().replace("_"," ")


@register.filter()
def get_file_name(pdf_url):
    file_name = os.path.basename(pdf_url) 
    f = Path(os.path.join(settings.MEDIA_ROOT,"documents/", file_name))
    if f.is_file() :
        return file_name
    return False
    
