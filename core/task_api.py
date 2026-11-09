"""JSON task workflow for the Next.js task-manager screens."""
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from task_manager.forms import CommentForm, TaskForm
from task_manager.models import Comment, Task
from core.admin_api import _field


def task_data(task, user=None):
    return {'id': task.pk, 'task_name': task.task_name, 'task_description': task.task_description,
            'key_tasks': task.key_tasks, 'assigned_date': task.assigned_date.isoformat(),
            'start_date': task.start_date.isoformat() if task.start_date else '',
            'due_date': task.due_date.isoformat() if task.due_date else '', 'status': task.status,
            'priority': task.priority, 'created_by': str(task.created_by or ''),
            'assigned_to': [str(user) for user in task.assigned_to.all()],
            'monitoring': [str(member) for member in task.monitoring.all()],
            'can_delete': bool(user and (task.created_by_id == user.pk or user.has_perm('task_manager.view_task')))}


def comments(task):
    return [{'id': item.pk, 'content': item.content, 'user': str(item.user),
             'created_at': item.created_at.isoformat(), 'replies': [{'id': reply.pk, 'content': reply.content,
             'user': str(reply.user), 'created_at': reply.created_at.isoformat()} for reply in item.replies.all()]}
            for item in task.comments.filter(parent_comment=None)]


@login_required
@require_http_methods(['GET', 'POST'])
def tasks(request, scope='All'):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if not form.is_valid(): return JsonResponse({'errors': form.errors}, status=400)
        task = form.save(commit=False); task.created_by = request.user; task.save(); form.save_m2m()
        for user in task.assigned_to.all():
            EmailMultiAlternatives(f'Assigned on new task : {task.task_name}',
                                  f'You have been assigned on a new task named: {task.task_name}.',
                                  from_email='Finance Bureau', to=[user.email]).send(fail_silently=True)
        for user in task.monitoring.all():
            EmailMultiAlternatives(f'Assigned as a monitor for a new task : {task.task_name}',
                                  f'You have been assigned to monitor a new task named: {task.task_name}.',
                                  from_email='Finance Bureau', to=[user.email]).send(fail_silently=True)
        return JsonResponse({'id': task.pk}, status=201)
    mapping = {'Assigned': request.user.assigned_tasks.all(), 'Monitoring': request.user.monitoring_tasks.all(), 'My': Task.objects.filter(created_by=request.user), 'All': Task.objects.all()}
    return JsonResponse({'scope': scope, 'tasks': [task_data(task, request.user) for task in mapping.get(scope, Task.objects.none())], 'fields': [_field(field) for field in TaskForm()], 'csrfToken': get_token(request)})


@login_required
@require_http_methods(['GET', 'POST', 'DELETE'])
def detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'DELETE':
        if task.created_by_id != request.user.pk and not request.user.has_perm('task_manager.view_task'):
            return JsonResponse({'detail': 'Permission denied.'}, status=403)
        task.delete()
        return JsonResponse({'message': 'Deleted.'})
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if not form.is_valid(): return JsonResponse({'errors': form.errors}, status=400)
        task = form.save()
        if task.created_by:
            EmailMultiAlternatives(f'Updated task : {task.task_name}', f'A task named: {task.task_name} is updated by {request.user}.', from_email='Finance Bureau', to=[task.created_by.email]).send(fail_silently=True)
        return JsonResponse({'id': task.pk})
    return JsonResponse({'task': task_data(task), 'fields': [_field(field) for field in TaskForm(instance=task)], 'comments': comments(task), 'csrfToken': get_token(request), 'can_edit': task.created_by_id == request.user.id})


@login_required
@require_http_methods(['POST'])
def comment(request, pk, parent=None):
    task = get_object_or_404(Task, pk=pk); form = CommentForm(request.POST)
    if parent is not None:
        get_object_or_404(Comment, pk=parent, task=task, parent_comment=None)
    if not form.is_valid(): return JsonResponse({'errors': form.errors}, status=400)
    Comment.objects.create(task=task, user=request.user, content=form.cleaned_data['comment_content'], parent_comment_id=parent)
    return JsonResponse({'comments': comments(task)}, status=201)
