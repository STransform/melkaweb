from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from blogs.models import Blog
from core.models import Settings


class AdminApiTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_superuser(
            email='admin@example.com', password='admin-password-123',
            first_name='Admin', last_name='User',
        )
        self.blog = Blog.objects.create(
            title='Test Blog Post', created_by=self.staff,
            published_status='Published', content='<p>Content</p>',
        )
        self.client.force_login(self.staff)

    def test_admin_api_list_models(self):
        response = self.client.get('/api/frontend/admin/Blog/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['model'], 'Blog')
        self.assertTrue(len(data['items']) >= 1)

    def test_admin_api_get_single_model(self):
        response = self.client.get(f'/api/frontend/admin/Blog/{self.blog.pk}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.blog.pk)
        self.assertIn('fields', data)
        self.assertIn('csrfToken', data)

    def test_admin_api_requires_login(self):
        client = Client()
        response = client.get('/api/frontend/admin/Blog/')
        self.assertEqual(response.status_code, 302)

    def test_admin_api_unknown_model_404(self):
        response = self.client.get('/api/frontend/admin/NonExistentModel/')
        self.assertEqual(response.status_code, 404)

    def test_admin_stats(self):
        response = self.client.get('/api/frontend/admin-stats/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('counts', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], self.staff.email)


    def test_admin_api_create_update_delete(self):
        from about_us.models import CompanyValues
        # Create
        response = self.client.post('/api/frontend/admin/CompanyValues/', {
            'title_en': 'Admin API Value',
            'content_en': 'Admin API Content',
        })
        self.assertEqual(response.status_code, 201)
        pk = response.json()['id']
        obj = CompanyValues.objects.get(pk=pk)
        self.assertEqual(obj.title, 'Admin API Value')

        # Update
        response = self.client.post(f'/api/frontend/admin/CompanyValues/{pk}/', {
            'title_en': 'Updated Admin API Value',
            'content_en': 'Updated Admin API Content',
        })
        self.assertEqual(response.status_code, 200)
        obj.refresh_from_db()
        self.assertEqual(obj.title, 'Updated Admin API Value')

        # Delete
        response = self.client.delete(f'/api/frontend/admin/CompanyValues/{pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CompanyValues.objects.filter(pk=pk).exists())

    def test_ceo_message_single_model_lifecycle(self):
        from dashboard.models import DirectorateMessage
        from django.core.files.uploadedfile import SimpleUploadedFile

        # 1. When no DirectorateMessage exists, list view redirects to create view
        res = self.client.get('/api/frontend/admin/DirectorateMessage/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('single'))
        self.assertEqual(data.get('redirect'), '/dashboard/create/DirectorateMessage/')

        # 2. When creating, ?action=create returns the full form fields schema
        res = self.client.get('/api/frontend/admin/DirectorateMessage/?action=create')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('single'))
        self.assertIn('fields', data)
        self.assertTrue(len(data['fields']) > 0)
        field_names = [f['name'] for f in data['fields']]
        self.assertIn('title_en', field_names)
        self.assertIn('content_en', field_names)
        self.assertIn('image', field_names)

        # 3. POST to create DirectorateMessage
        from io import BytesIO
        from PIL import Image
        img = BytesIO()
        Image.new('RGB', (100, 100), color='blue').save(img, format='JPEG')
        image = SimpleUploadedFile('ceo.jpg', img.getvalue(), content_type='image/jpeg')
        res = self.client.post('/api/frontend/admin/DirectorateMessage/', {
            'title_en': 'CEO Message from Director',
            'content_en': 'Welcome to our platform.',
            'image': image,
        })
        if res.status_code != 201:
            print('DEBUG CREATE ERRORS:', res.json().get('errors'))
        self.assertEqual(res.status_code, 201)
        dm = DirectorateMessage.objects.first()
        self.assertIsNotNone(dm)
        self.assertEqual(dm.title_en, 'CEO Message from Director')

        # 4. Once it exists, list view redirects to change view
        res = self.client.get('/api/frontend/admin/DirectorateMessage/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('single'))
        self.assertEqual(data.get('redirect'), f'/dashboard/change/DirectorateMessage/{dm.pk}/')

        # 5. Accessing create view when already exists also redirects to change view
        res = self.client.get('/api/frontend/admin/DirectorateMessage/?action=create')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get('redirect'), f'/dashboard/change/DirectorateMessage/{dm.pk}/')

        # 6. Detail GET view returns prefilled fields
        res = self.client.get(f'/api/frontend/admin/DirectorateMessage/{dm.pk}/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('single'))
        title_field = next(f for f in data['fields'] if f['name'] == 'title_en')
        self.assertEqual(title_field['value'], 'CEO Message from Director')

        # 7. Detail POST view updates the instance
        res = self.client.post(f'/api/frontend/admin/DirectorateMessage/{dm.pk}/', {
            'title_en': 'Updated CEO Message',
            'content_en': 'Updated platform content.',
        })
        self.assertEqual(res.status_code, 200)
        dm.refresh_from_db()
        self.assertEqual(dm.title_en, 'Updated CEO Message')

    def test_next_auth_api_uses_django_session_and_form_validation(self):
        from django.contrib.auth import get_user_model
        client = Client(enforce_csrf_checks=True)
        token = client.get('/api/frontend/csrf/').json()['csrfToken']
        response = client.post('/api/frontend/auth/login/', {
            'email': self.staff.email, 'password': 'admin-password-123',
        }, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['redirect'], '/dashboard/')
        self.assertIn('_auth_user_id', client.session)
        token = client.get('/api/frontend/csrf/').json()['csrfToken']
        response = client.post('/api/frontend/auth/logout/', {}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', client.session)
        token = client.get('/api/frontend/csrf/').json()['csrfToken']
        response = client.post('/api/frontend/auth/signup/', {
            'email': 'new@example.com', 'first_name': 'New', 'last_name': 'Member',
            'role': 'staff', 'password': 'Correct-horse-42', 'password2': 'Correct-horse-42',
        }, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(get_user_model().objects.filter(email='new@example.com').exists())




