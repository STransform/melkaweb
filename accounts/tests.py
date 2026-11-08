from django.test import TestCase
from django.urls import reverse

from .backends import FlexibleModelBackend
from .models import UserProfile
from .views import Login


class LoginViewTests(TestCase):
    def test_staff_user_can_log_in_with_email(self):
        password = "StrongPass123!"
        user = UserProfile.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_staff=True,
            is_superuser=True,
            status="Active",
        )
        user.set_password(password)
        user.save()

        response = self.client.post(
            reverse("login"),
            {"email": "admin@example.com", "password": password},
        )

        self.assertRedirects(response, reverse("admin_dashboard"))

    def test_inactive_user_is_not_logged_in(self):
        password = "StrongPass123!"
        user = UserProfile.objects.create(
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            is_active=False,
            is_staff=True,
            status="Active",
        )
        user.set_password(password)
        user.save()

        response = self.client.post(
            reverse("login"),
            {"email": "inactive@example.com", "password": password},
            follow=True,
        )

        self.assertContains(response, "inactive")

    def test_login_helpers_default_status_to_active(self):
        user = type("LegacyUser", (), {"is_superuser": False})()
        self.assertEqual(Login._get_user_status(user), "Active")


class FlexibleModelBackendTests(TestCase):
    def test_authenticates_with_case_insensitive_email(self):
        password = "StrongPass123!"
        user = UserProfile.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_staff=True,
            is_superuser=True,
            status="Active",
        )
        user.set_password(password)
        user.save()

        authenticated = FlexibleModelBackend().authenticate(
            request=None,
            email="ADMIN@EXAMPLE.COM",
            password=password,
        )

        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.pk, user.pk)
