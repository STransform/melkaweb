from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class PasswordResetApiTests(TestCase):
    def test_reset_email_token_validation_and_single_use(self):
        user = get_user_model().objects.create_superuser('reset@example.com', 'Old-password-42', 'Reset', 'Member')
        response = self.client.post('/api/frontend/auth/password-reset/', {'email': user.email})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = f'/api/frontend/auth/password-reset/{uid}/{token}/'
        response = self.client.post(url, {'new_password1': 'New-password-56789', 'new_password2': 'Mismatch'})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url, {'new_password1': 'New-password-56789', 'new_password2': 'New-password-56789'})
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password('New-password-56789'))
        self.assertEqual(self.client.post(url, {}).status_code, 400)

    def test_unknown_email_has_same_response_and_invalid_token_fails(self):
        self.assertEqual(self.client.post('/api/frontend/auth/password-reset/', {'email': 'unknown@example.com'}).status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(self.client.post('/api/frontend/auth/password-reset/invalid/invalid/', {}).status_code, 400)
