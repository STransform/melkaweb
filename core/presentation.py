"""Data transport for the UI-preserving Next.js renderer.

Application views retain their existing authorization, forms and business logic.
For Next.js requests this module exports structured view data, never rendered
HTML. The presentation trees are owned by the frontend.
"""
import datetime
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.core.paginator import Page, Paginator
from django.db import models
from django.forms.boundfield import BoundField
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render as django_render
from django.template import Origin
from django.template.context import make_context
from django.template.loaders.base import Loader as BaseLoader
from django.urls import URLPattern, URLResolver, get_resolver, reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import Promise
from django.utils.translation import gettext
from django.views.decorators.cache import patch_cache_control

MEDIA_TYPE = 'application/vnd.melka.page+json'
PRIVATE_FIELDS = {'password', 'session_data', 'email_for_contact_us'}


@lru_cache(maxsize=1)
def presentations():
    return json.loads((Path(settings.BASE_DIR) / 'frontend/ui/presentation.json').read_text())


class PresentationTemplateLoader(BaseLoader):
    """Virtual template loader so Django/Django-CMS template resolution succeeds without legacy templates on disk."""
    def get_template_sources(self, template_name):
        if template_name in presentations():
            yield Origin(name=template_name, template_name=template_name, loader=self)

    def get_contents(self, origin):
        placeholders = "{% placeholder 'feature' %}{% placeholder 'content' %}{% placeholder 'splashbox' %}" if 'cms_base' in origin.template_name else ""
        return (
            "{% load cms_tags sekizai_tags %}"
            "{% for message in messages %}{{ message }} {{ message.tags }}{% endfor %}"
            "{% if form.errors %}{{ form.errors }}{% endif %}"
            "{% block title %}{% endblock %}{% block css %}{% endblock %}"
            "{% block content %}{% endblock %}{% block cms_extended_content %}{% endblock %}"
            "{% block js %}{% endblock %}"
            f"{placeholders}"
        )


def tokens(value):
    return re.findall(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s]+''', value)


def walk(nodes):
    for node in nodes:
        yield node
        yield from walk(node.get('body', []))
        yield from walk(node.get('empty', []))
        for branch in node.get('branches', []):
            yield from walk(branch['body'])


@lru_cache(maxsize=128)
def requirements(name):
    seen = set()
    nodes = []
    def add(template):
        if template in seen or template not in presentations():
            return
        seen.add(template)
        for node in walk(presentations()[template]):
            nodes.append(node)
            if node['op'] in ('extends', 'include'):
                arg = tokens(node['args'])[0]
                if arg[:1] in ('"', "'"):
                    add(arg[1:-1])
    add(name)
    text = ' '.join(node.get('expr', '') + ' ' + node.get('args', '') + ' ' + ' '.join(branch.get('test') or '' for branch in node.get('branches', [])) for node in nodes)
    # Quoted UI copy and URL names are literals, never data requirements.
    expressions = re.sub(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' ''', '', text, flags=re.X)
    names = set(re.findall(r'\b[a-zA-Z_][a-zA-Z_0-9]*\b', expressions))
    names.update(node['op'] for node in nodes)
    translations = set()
    for node in nodes:
        if node['op'] in ('trans', 'translate'):
            args = tokens(node['args'])
            if args and args[0][:1] in ('"', "'"):
                translations.add(args[0][1:-1])
        elif node['op'] == 'blocktrans':
            value = ''.join(part.get('text', '') for part in node['body'])
            translations.add(' '.join(value.split()) if 'trimmed' in node['args'] else value)
    return names, translations


def scalar(value):
    if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
        return value.isoformat()
    return str(value)


def export_field(bound):
    field, widget = bound.field, bound.field.widget
    value = bound.value()
    file_name = value.name if isinstance(value, models.fields.files.FieldFile) and value else ''
    if isinstance(value, models.fields.files.FieldFile):
        value = value.url if value else None
    if isinstance(widget, forms.PasswordInput):
        value = None
    choices = []
    if hasattr(field, 'choices'):
        choices = [[str(key), str(label)] for key, label in field.choices]
    return {
        '$field': True, 'name': bound.html_name, 'id': bound.auto_id,
        'label': str(bound.label or ''), 'help_text': str(bound.help_text or ''),
        'value': value, 'required': field.required, 'disabled': field.disabled,
        'type': getattr(widget, 'input_type', 'textarea' if isinstance(widget, forms.Textarea) else 'text'),
        'multiple': isinstance(widget, (forms.SelectMultiple, forms.CheckboxSelectMultiple)),
        'textarea': isinstance(widget, forms.Textarea), 'select': isinstance(widget, forms.Select),
        'attrs': widget.attrs, 'choices': choices, 'errors': [str(error) for error in bound.errors],
        'file_name': file_name,
        'clearable': isinstance(widget, forms.ClearableFileInput) and not field.required,
        'clear_name': widget.clear_checkbox_name(bound.html_name) if isinstance(widget, forms.ClearableFileInput) else '',
        'field': {'widget': {'input_type': getattr(widget, 'input_type', None)}},
    }


def export(value, names, request, depth=0, seen=()):
    if isinstance(value, type) and issubclass(value, forms.BaseForm):
        value = value()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if depth > 7:
        return str(value) if isinstance(value, models.Model) else None
    if isinstance(value, Promise):
        return str(value)
    if isinstance(value, BoundField):
        return export_field(value)
    if isinstance(value, forms.BaseForm):
        fields = [export_field(bound) for bound in value]
        return {'$form': fields, **{field['name']: field for field in fields},
                'errors': {key: [str(error) for error in errors] for key, errors in value.errors.items()},
                'non_field_errors': [str(error) for error in value.non_field_errors()]}
    if isinstance(value, models.fields.files.FieldFile):
        return {'$label': value.name, 'name': value.name, 'url': value.url if value else '', '$truth': bool(value)}
    if isinstance(value, Page):
        return {'$items': [export(obj, names, request, depth+1) for obj in value],
                'object_list': [export(obj, names, request, depth+1) for obj in value.object_list],
                'number': value.number, 'has_next': value.has_next(), 'has_previous': value.has_previous(),
                'has_other_pages': value.has_other_pages(), 'next_page_number': value.number+1,
                'previous_page_number': value.number-1, 'paginator': export(value.paginator, names, request, depth+1)}
    if isinstance(value, Paginator):
        return {'num_pages': value.num_pages, 'count': value.count, 'page_range': list(value.page_range)}
    if isinstance(value, models.Manager):
        value = value.all()
    if isinstance(value, (list, tuple, set, range, models.QuerySet)):
        return [export(obj, names, request, depth+1, seen) for obj in value]
    if isinstance(value, dict):
        return {str(key): export(item, names, request, depth+1, seen) for key, item in value.items()}
    if isinstance(value, models.Model):
        identity = (value._meta.label, value.pk)
        data = {'$label': str(value), '$model': value._meta.label, 'id': value.pk, 'pk': value.pk}
        if identity in seen:
            return data
        seen = (*seen, identity)
        allowed = set(names) | set(getattr(value, 'list_fields', []))
        if value._meta.label_lower == settings.AUTH_USER_MODEL.lower():
            if not request.user.is_authenticated or (value.pk != request.user.pk and not request.user.has_perm('accounts.view_userprofile')):
                allowed &= {'first_name', 'last_name', 'profile_pic', 'is_staff', 'is_active'}
            data['is_authenticated'] = True
        for field in value._meta.concrete_fields:
            if field.name not in allowed or field.name in PRIVATE_FIELDS:
                continue
            attr = getattr(value, field.name)
            if field.name == 'session_key':
                attr = hashlib.sha256(str(attr).encode()).hexdigest()
            data[field.name] = export(attr, names, request, depth+1, seen)
        for name in allowed:
            if name in data or name in PRIVATE_FIELDS or name.startswith('_'):
                continue
            try:
                attr = getattr(value, name)
            except (AttributeError, ValueError):
                continue
            if callable(attr) and not isinstance(attr, models.Manager):
                if name not in {'category', 'comments', 'file_extension', 'get_full_name', 'get_short_name'} and not (name.startswith('get_') and name.endswith('_display')):
                    continue
                attr = attr()
            if isinstance(attr, (models.Manager, models.QuerySet, str, int, bool, models.Model, list)):
                data[name] = export(attr, names, request, depth+1, seen)
        return data
    return scalar(value)


def route_map():
    result = {}
    def visit(resolver, prefix='', namespace=''):
        for pattern in resolver.url_patterns:
            path = prefix + str(pattern.pattern)
            if isinstance(pattern, URLResolver):
                visit(pattern, path, namespace + (pattern.namespace + ':' if pattern.namespace else ''))
            elif pattern.name:
                name = namespace + pattern.name
                if not path.startswith('^') and '(?P<' not in path:
                    path = re.sub(r'<(?:[^:>]+:)?([^>]+)>', r'{\1}', path)
                    result[name] = '/' + path
                else:
                    try:
                        result[name] = reverse(name)
                    except Exception:
                        pass
    visit(get_resolver())
    return result


class PresentationResponse(JsonResponse):
    is_rendered = True
    def render(self):
        return self


def snapshot(request, template, context=None, status=200):
    if template not in presentations():
        return PresentationResponse({'error': 'Presentation not found', 'template': template}, status=500)
    names, translations = requirements(template)
    # Existing context processors supply site settings, permissions and identity.
    ctx = make_context(context or {}, request=request)
    with ctx.bind_template(__import__('django.template', fromlist=['engines']).engines['django'].from_string('').template):
        combined = ctx.flatten()
    combined.update(context or {})
    combined['user'] = request.user
    combined['request'] = {'path': request.path, 'GET': request.GET.dict(), 'user': request.user}
    combined['messages'] = [{'$label': str(message), 'tags': message.tags} for message in get_messages(request)]
    permissions = {}
    if request.user.is_authenticated:
        for permission in request.user.get_all_permissions():
            app, codename = permission.split('.', 1)
            permissions.setdefault(app, {})[codename] = True
        # Django's active superuser check also grants permission strings that
        # predate a model move. Preserve that exact behavior in the sidebar.
        for app, codename in re.findall(r'perms\.([a-zA-Z_][\w]*)\.([a-zA-Z_][\w]*)', json.dumps(presentations())):
            permissions.setdefault(app, {})[codename] = request.user.has_perm(f'{app}.{codename}')
        for app in re.findall(r'perms\.([a-zA-Z_][\w]*)', json.dumps(presentations())):
            permissions.setdefault(app, {})
        for app, values in permissions.items():
            values['$truth'] = request.user.has_module_perms(app)
    combined['perms'] = permissions
    if 'current_session_key' in combined:
        combined['current_session_key'] = hashlib.sha256(str(combined['current_session_key']).encode()).hexdigest()
    data = {key: export(value, names, request) for key, value in combined.items() if key in names and key not in {'csrf_token', 'perms'}}
    data['perms'] = permissions
    if 'cms_toolbar' in names and request.user.is_staff:
        data['cms_toolbar'] = str(request.toolbar.render())
        from django.template.loader import render_to_string
        from sekizai.context_processors import sekizai
        from sekizai.helpers import get_varname
        toolbar_context = {**sekizai(request), **request.toolbar.get_render_context()}
        render_to_string('cms/toolbar/toolbar_javascript.html', toolbar_context, request=request)
        holder = toolbar_context[get_varname()]
        data['cms_assets'] = {name: list(holder[name]) for name in ['css', 'js']}
    current_page = getattr(request, 'current_page', None)
    if current_page and 'cms_placeholders' not in data:
        from cms.plugin_rendering import ContentRenderer
        from django.template import RequestContext
        renderer = ContentRenderer(request)
        language = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
        plugin_context = RequestContext(request, combined)
        from django.template import engines
        from sekizai.helpers import get_varname
        with plugin_context.bind_template(engines['django'].from_string('').template):
            data['cms_placeholders'] = {
                placeholder.slot: str(renderer.render_placeholder(
                    placeholder, plugin_context, language=language,
                    page=current_page, editable=False, use_cache=False,
                )) for placeholder in current_page.get_placeholders(language)
            }
            holder = plugin_context[get_varname()]
            for name in ['css', 'js']:
                data.setdefault('cms_assets', {}).setdefault(name, []).extend(list(holder[name]))
    if 'get_task_count_by_status' in names:
        from task_manager.models import Task
        from django.db.models import Count
        data['task_counts'] = dict(Task.objects.values('status').annotate(total=Count('id')).values_list('status', 'total'))
    response = PresentationResponse({'template': template, 'context': data,
        'csrfToken': get_token(request), 'routes': route_map(),
        'translations': {value: gettext(value) for value in translations},
        'language': getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)}, status=status)
    patch_cache_control(response, private=True, no_store=True)
    return response


def render(request, template_name, context=None, content_type=None, status=None, using=None):
    if MEDIA_TYPE in request.headers.get('Accept', ''):
        return snapshot(request, template_name, context, status or 200)
    return django_render(request, template_name, context, content_type=content_type, status=status, using=using)


class PresentationMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if MEDIA_TYPE in request.headers.get('Accept', '') and response.status_code in (403, 404, 500) and 'text/html' in response.get('Content-Type', ''):
            return snapshot(request, f'{response.status_code}.html', status=response.status_code)
        return response

    def process_template_response(self, request, response):
        if MEDIA_TYPE not in request.headers.get('Accept', '') or isinstance(response, PresentationResponse):
            return response
        names = response.template_name
        name = names if isinstance(names, str) else next((name for name in names if name in presentations()), None)
        if name in presentations():
            return snapshot(request, name, response.context_data, response.status_code)
        return response

    def process_exception(self, request, exception):
        if MEDIA_TYPE in request.headers.get('Accept', '') and isinstance(exception, PermissionDenied):
            return snapshot(request, '403.html', status=403)
