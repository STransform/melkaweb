"""Account operations for Next.js, retaining Django forms and permissions."""
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from accounts.forms import EditProfileForm, ChangePasswordForm, ResetPasswordForm, MyUserRegistrationForm
from core.admin_api import _field


def denied():
    return JsonResponse({'detail': 'Permission denied.'}, status=403)


@never_cache
@login_required
@require_http_methods(['GET', 'POST'])
def profile(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    administrator = request.user.has_perm('accounts.change_userprofile')
    if user.pk != request.user.pk and not administrator:
        return denied()
    form = EditProfileForm(request.POST or None, request.FILES or None, instance=user)
    if not administrator:
        for name in ['status', 'groups', 'user_permissions', 'is_active', 'is_superuser']:
            form.fields.pop(name, None)
    if request.method == 'POST':
        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status=400)
        form.save()
    return JsonResponse({'id': user.pk, 'title': 'My Profile' if user.pk == request.user.pk else 'User Profile',
                         'name': str(user), 'email': user.email, 'role': user.role,
                         'own': user.pk == request.user.pk, 'fields': [_field(field) for field in form]})


@never_cache
@login_required
@require_http_methods(['POST'])
def password(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    own = user.pk == request.user.pk
    if not own and not request.user.has_perm('accounts.change_userprofile'):
        return denied()
    form = (ChangePasswordForm if own else ResetPasswordForm)(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    if own and not user.check_password(form.cleaned_data['current_password']):
        return JsonResponse({'errors': {'current_password': ['Current password is not correct.']}}, status=400)
    user.set_password(form.cleaned_data['new_password'])
    user.save(update_fields=['password'])
    if own:
        logout(request)
    return JsonResponse({'redirect': '/accounts/login/' if own else f'/accounts/profile/{pk}/'})


@never_cache
@login_required
@require_http_methods(['GET', 'POST'])
def users(request):
    creating = request.method == 'POST' or request.GET.get('mode') == 'create'
    if not request.user.has_perm('accounts.add_userprofile' if creating else 'accounts.view_userprofile'):
        return denied()
    form = MyUserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status=400)
        user = form.save()
        return JsonResponse({'id': user.pk}, status=201)
    return JsonResponse({'items': [{'id': user.pk, 'email': user.email, 'first_name': user.first_name,
                                   'last_name': user.last_name, 'role': user.role, 'is_active': user.is_active,
                                   'status': user.status, 'date_joined': user.date_joined}
                                  for user in (get_user_model().objects.none() if creating else get_user_model().objects.all())],
                         'fields': [_field(field) for field in form]})


@never_cache
@login_required
@require_http_methods(['DELETE'])
def delete_user(request, pk):
    if not request.user.has_perm('accounts.delete_userprofile'):
        return denied()
    get_object_or_404(get_user_model(), pk=pk).delete()
    return JsonResponse({'message': 'Successfully deleted a user.'})
