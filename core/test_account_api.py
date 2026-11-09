from django.contrib.auth import get_user_model
from django.test import TestCase


class AccountApiTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser('admin-account@example.com', 'Password-12345', 'Admin', 'User')
        self.member = get_user_model().objects.create_user('member@example.com', 'Password-12345', 'Member', 'User')
        self.member.is_active = True
        self.member.save()

    def test_own_profile_changes_cannot_escalate_privileges(self):
        self.client.force_login(self.member)
        url = f'/api/frontend/accounts/profile/{self.member.pk}/'
        names = [field['name'] for field in self.client.get(url).json()['fields']]
        self.assertNotIn('is_superuser', names)
        response = self.client.post(url, {'first_name': 'Updated', 'last_name': 'User', 'is_superuser': 'on'})
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_superuser)
        self.assertEqual(self.member.first_name, 'Updated')
        self.assertEqual(self.client.get(f'/api/frontend/accounts/profile/{self.admin.pk}/').status_code, 403)
        self.assertEqual(self.client.get('/api/frontend/accounts/users/').status_code, 403)

    def test_password_requires_current_secret_and_logs_out(self):
        self.client.force_login(self.member)
        url = f'/api/frontend/accounts/password/{self.member.pk}/'
        data = {'current_password': 'wrong', 'new_password': 'New-secret-12345', 'retype_new_password': 'New-secret-12345'}
        self.assertEqual(self.client.post(url, data).status_code, 400)
        data['current_password'] = 'Password-12345'
        self.assertEqual(self.client.post(url, data).status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.member.refresh_from_db()
        self.assertTrue(self.member.check_password('New-secret-12345'))

    def test_admin_creates_user_with_hashed_password(self):
        self.client.force_login(self.admin)
        response = self.client.post('/api/frontend/accounts/users/', {
            'email': 'new-staff@example.com', 'first_name': 'New', 'last_name': 'Staff',
            'role': 'staff', 'password': 'Staff-secret-12345', 'password2': 'Staff-secret-12345'})
        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(pk=response.json()['id'])
        self.assertTrue(user.check_password('Staff-secret-12345'))
        response = self.client.get('/api/frontend/accounts/users/')
        self.assertNotIn(user.password, response.content.decode())
