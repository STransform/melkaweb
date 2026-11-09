"""Permission-aware JSON contract for the Next.js administration portal.

This is deliberately model allowlisted through the same dashboard configuration
used by the legacy views.  It exposes fields created by ``get_form`` only, so
private model attributes and arbitrary Django models never become an API.
"""
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from django import forms

from dashboard.views import get_conf


def _config(request, model_name, permission):
    config = get_conf(request, {'model_name': model_name})
    if not config:
        return None, JsonResponse({'detail': 'Not found.'}, status=404)
    model = config['model']
    codename = f"{config['app_label']}.{permission}_{model._meta.model_name}"
    if not request.user.has_perm(codename):
        return None, JsonResponse({'detail': 'Permission denied.'}, status=403)
    return config, None


def _field(bound):
    field = bound.field
    widget = field.widget
    value = bound.value()
    if isinstance(widget, forms.PasswordInput):
        value = None
    if isinstance(value, models.fields.files.FieldFile):
        try:
            value = value.url if value else None
        except ValueError:
            value = None
    elif hasattr(value, 'url'):
        try:
            value = value.url if value else None
        except ValueError:
            value = None
    return {
        'name': bound.html_name, 'id': bound.auto_id, 'label': str(bound.label),
        'helpText': str(bound.help_text), 'required': field.required,
        'type': getattr(widget, 'input_type', 'textarea' if isinstance(widget, forms.Textarea) else 'text'),
        'textarea': isinstance(widget, forms.Textarea) or widget.__class__.__name__ == 'Textarea',
        'multiple': bool(getattr(widget, 'allow_multiple_selected', False)),
        'disabled': field.disabled,
        'choices': [[str(key), str(label)] for key, label in getattr(field, 'choices', [])],
        'value': value, 'errors': [str(error) for error in bound.errors],
    }


def _object(obj, fields):
    values = {'id': obj.pk}
    for name in fields or ['__str__']:
        value = str(obj) if name == '__str__' else getattr(obj, name, '')
        if callable(value):
            value = value()
        if isinstance(value, models.fields.files.FieldFile):
            try:
                value = value.url if value else ''
            except ValueError:
                value = ''
        elif hasattr(value, 'url'):
            try:
                value = value.url if value else ''
            except ValueError:
                value = ''
        values[name] = str(value) if value is not None else ''
    return values


@login_required
@require_http_methods(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def model(request, model_name, pk=None):
    action = 'view' if request.method == 'GET' else 'delete' if request.method == 'DELETE' else 'change' if pk else 'add'
    config, error = _config(request, model_name, action)
    if error:
        return error
    Model, Form = config['model'], config['form']
    is_create = request.GET.get('action') == 'create' or request.GET.get('schema') == 'create'

    if request.method == 'GET' and pk is None:
        if config['single']:
            obj = Model.objects.first()
            if is_create:
                if obj:
                    return JsonResponse({
                        'single': True,
                        'redirect': f'/dashboard/change/{model_name}/{obj.pk}/'
                    })
                form = Form()
                fields = [_field(field) for field in form]
                return JsonResponse({
                    'model': model_name,
                    'title': str(config['model_name']).capitalize(),
                    'fields': fields,
                    'formFields': fields,
                    'csrfToken': get_token(request),
                    'single': True,
                })
            return JsonResponse({
                'single': True,
                'redirect': f'/dashboard/change/{model_name}/{obj.pk}/' if obj else f'/dashboard/create/{model_name}/'
            })
        form = Form()
        form_fields = [_field(field) for field in form]
        fields = list(getattr(Model, 'list_fields', []))
        if is_create:
            return JsonResponse({
                'model': model_name,
                'title': str(config['model_name']).capitalize(),
                'fields': form_fields,
                'formFields': form_fields,
                'csrfToken': get_token(request),
                'single': False,
            })
        return JsonResponse({
            'model': model_name,
            'title': str(config['model_name']).capitalize(),
            'fields': fields or ['__str__'],
            'formFields': form_fields,
            'csrfToken': get_token(request),
            'items': [_object(obj, fields) for obj in Model.objects.all()],
            'single': False,
        })
    if request.method == 'GET':
        obj = Model.objects.get(pk=pk)
        form = Form(instance=obj)
        fields = [_field(field) for field in form]
        return JsonResponse({
            'model': model_name,
            'title': str(config['model_name']).capitalize(),
            'id': obj.pk,
            'fields': fields,
            'formFields': fields,
            'csrfToken': get_token(request),
            'single': config['single'],
        })
    if request.method == 'DELETE':
        Model.objects.get(pk=pk).delete()
        return JsonResponse({'message': 'Deleted.'})
    instance = None
    if pk:
        instance = Model.objects.get(pk=pk)
    elif config['single']:
        instance = Model.objects.first()
    form = Form(request.POST, request.FILES, instance=instance)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors, 'fields': [_field(field) for field in form]}, status=400)
    obj = form.save(commit=False)
    if not instance and hasattr(Model, 'created_by'):
        obj.created_by = request.user
    obj.save()
    form.save_m2m()
    return JsonResponse({'id': obj.pk, 'message': 'Updated.' if instance else 'Created.', 'single': config['single']}, status=200 if instance else 201)


@login_required
@require_http_methods(['GET'])
def stats(request):
    from blogs.models import Blog
    from news.models import NewsArticle
    from about_us.models import Service
    from documents.models import Document
    from core.models import ContactUs
    from vacancies.models import Job, Application
    from dashboard.models import GalleryImage, GalleryVideo
    from core.models import Settings

    return JsonResponse({
        'site_title': getattr(Settings.objects.first(), 'title', 'MelkaTech'),
        'user': {
            'id': request.user.pk,
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.email,
            'email': request.user.email,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
            'first_name': request.user.first_name,
            'role': request.user.role,
            'profile_pic': request.user.profile_pic.url if request.user.profile_pic else None,
            'permissions': sorted(request.user.get_all_permissions()),
        },
        'counts': {
            'blogs': Blog.objects.count(),
            'news': NewsArticle.objects.count(),
            'services': Service.objects.count(),
            'documents': Document.objects.count(),
            'messages': ContactUs.objects.count(),
            'jobs': Job.objects.count(),
            'applications': Application.objects.count(),
            'galleries': GalleryImage.objects.count(),
            'videos': GalleryVideo.objects.count(),
        },
        'messages': list(ContactUs.objects.values('id', 'full_name', 'email', 'phone', 'subject', 'sent_date')[:5]),
    })
