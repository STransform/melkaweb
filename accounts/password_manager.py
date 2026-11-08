# README : This file contains all basic password related implementations for features such as password validation, password update/reset and 
# Forgot password reset functionalities 
import re
from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model,get_user,login, logout
from django.contrib.auth.forms import   _unicode_ci_compare
from django.contrib.auth.forms import (PasswordResetForm as DefaultPasswordResetForm,
                                       SetPasswordForm as DefaultSetPasswordForm)

from django.contrib.auth.views import ( PasswordResetView as DefaultPasswordResetView, 
                                        PasswordResetConfirmView as DefaultPasswordResetConfirmView)
from .emailing import ThreadEmailSender
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect




# Features Related with forgot password reset
class PasswordResetForm(DefaultPasswordResetForm):
    email = forms.EmailField(
        # label=_("Email"), max_length=254,
        widget=forms.EmailInput(
            attrs={'autocomplete': 'email', 'class': 'form-control ',
                   'placeholder': 'Please Enter Your Email Address'})
    )

    def get_users(self, email):
        """Given an email, return matching user(s) who should receive a reset."""
        try:
            UserModel = get_user_model()
            u = UserModel.objects.get(email = email, status__is_active = True)
        except Exception as e:
            print("Exception as ", e)
            return []
        return [u] if u.has_usable_password() and _unicode_ci_compare(email, u.email) else []

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):

        ThreadEmailSender(
            template=email_template_name,
            subject="OTech Engineering password Reset.",
            to_email=to_email,
            params=context
        ).start()


class SetPasswordForm(DefaultSetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password',
                   'class': 'form-control ',
                   'placeholder': 'Enter your new password',
                   'onfocus': "show_note(this)", 'onblur': "show_note(this)"
                   }),
        strip=True,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=True,
        widget=forms.PasswordInput(
            attrs={'autocomplete': 'new-password', 'class': 'form-control ', 'placeholder': 'Confirm your new password'}
        ),
    )


class PasswordResetView(DefaultPasswordResetView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().dispatch(*args, **kwargs)



class PasswordResetConfirmView(DefaultPasswordResetConfirmView):
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    title = _('Enter new password')

