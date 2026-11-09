"""Session-authentication endpoints consumed by Next.js account screens.

The endpoints deliberately retain Django's authentication backend, session
cookie handling, password validation and registration form.  No token is
issued or stored in the browser.
"""
from urllib.parse import urlparse

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from accounts.forms import MyUserRegistrationForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.urls import reverse


def _next(value, fallback='/'):
    """Accept relative local redirects only, preventing open redirects."""
    value = value or fallback
    parsed = urlparse(value)
    return value if not parsed.scheme and not parsed.netloc and value.startswith('/') else fallback


def _user_name(user):
    return f'{user.first_name} {user.last_name}'.strip() or user.email


@never_cache
@require_POST
def login_view(request):
    identifier = (request.POST.get('email') or '').strip()
    password = request.POST.get('password') or ''
    user = authenticate(request, email=identifier, username=identifier, password=password)
    if not user:
        return JsonResponse({'errors': {'email': [_('Email/username or password is wrong.')]},
                             'csrfToken': get_token(request)}, status=400)
    if not user.is_active:
        return JsonResponse({'errors': {'email': [_('Your account is inactive. Please contact an administrator.')]},
                             'csrfToken': get_token(request)}, status=403)
    if getattr(user, 'status', 'Active') != 'Active' and not user.is_superuser:
        return JsonResponse({'errors': {'email': [_('Your account is awaiting activation.')]},
                             'csrfToken': get_token(request)}, status=403)
    login(request, user)
    destination = _next(request.POST.get('next'), '/dashboard/' if user.is_staff else '/')
    return JsonResponse({'redirect': destination, 'user': {'id': user.pk, 'name': _user_name(user),
                                                             'staff': user.is_staff}})


@never_cache
@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({'redirect': '/'})


@never_cache
@require_POST
def signup(request):
    form = MyUserRegistrationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors, 'csrfToken': get_token(request)}, status=400)
    user = form.save()
    return JsonResponse({'message': _('Successfully created user account.'), 'user': {'id': user.pk},
                         'redirect': _next(request.POST.get('next'), '/')}, status=201)


@never_cache
@require_POST
def password_reset(request):
    form = PasswordResetForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    form.save(request=request, use_https=request.is_secure())
    return JsonResponse({'redirect': reverse('password_reset_done')})


@never_cache
@require_POST
def password_confirm(request, uidb64, token):
    try:
        user = get_user_model().objects.get(pk=urlsafe_base64_decode(uidb64).decode())
    except (ValueError, UnicodeDecodeError, get_user_model().DoesNotExist, OverflowError):
        user = None
    if user is None or not default_token_generator.check_token(user, token):
        return JsonResponse({'errors': {'__all__': ['This password reset link is invalid or has expired.']}}, status=400)
    form = SetPasswordForm(user, request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    form.save()
    return JsonResponse({'redirect': reverse('password_reset_complete')})
