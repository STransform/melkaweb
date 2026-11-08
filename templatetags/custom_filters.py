from django import template
from task_manager.models import Task

register = template.Library()

@register.filter(name='split_links')
def split_links(value, delimiter=','):
    return value.split(delimiter)

@register.filter
def get_task_count_by_status(status):
    print("2")
    return Task.objects.filter(status=status).count()
@register.filter(name='get_key_tasks')
def get_key_tasks(task):
    return task.key_tasks.split('\n') if task.key_tasks else []