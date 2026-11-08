from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase

from blogs.models import Blog, BlogComment
from core.frontend_api import RESOURCES
from core.models import ContactUs, Settings
from documents.models import Document


class FrontendApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='reader@example.com', password='example-password',
            first_name='Reader', last_name='User',
        )
        self.blog = Blog.objects.create(title='A published story', created_by=self.user,
                                        published_status='Published', content='<p>Story</p>', images='blog_images/story.jpg')
        self.settings = Settings.objects.create(title='Test Melka', email_for_contact_us='staff@example.com',
                                                 email='public@example.com', working_hours='9–5')

    def test_public_site_excludes_private_configuration(self):
        response = self.client.get('/api/frontend/site/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['settings']['email'], 'public@example.com')
        self.assertNotIn('email_for_contact_us', response.json()['settings'])
        self.assertNotContains(response, 'password')
        self.assertFalse(response.json()['user']['authenticated'])
        self.assertIn('no-store', response['Cache-Control'])

    def test_all_allowlisted_collections_and_localized_routes(self):
        for locale in ['', '/ax', '/ox']:
            for name in RESOURCES:
                with self.subTest(locale=locale, resource=name):
                    response = self.client.get(f'{locale}/api/frontend/content/{name}/')
                    self.assertEqual(response.status_code, 200)
                    self.assertIn('items', response.json())

    def test_arbitrary_models_are_not_exposed(self):
        self.assertEqual(self.client.get('/api/frontend/content/accounts/').status_code, 404)
        self.assertEqual(self.client.get('/api/frontend/content/blogs/999999/').status_code, 404)

    def test_blog_detail_exposes_only_approved_comments(self):
        BlogComment.objects.create(blog=self.blog, author='Approved', email='private@example.com', message='Visible', approved=True)
        BlogComment.objects.create(blog=self.blog, author='Hidden', email='private@example.com', message='Private', approved=False)
        response = self.client.get(f'/api/frontend/content/blogs/{self.blog.pk}/')
        comments = response.json()['item']['comments']
        self.assertEqual([comment['author'] for comment in comments], ['Approved'])
        self.assertNotIn('email', comments[0])
        self.assertEqual(response.json()['item']['images'], '/media/blog_images/story.jpg')

    def test_contact_requires_csrf_and_validates_input(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/api/frontend/contact/', {}).status_code, 403)
        token = client.get('/api/frontend/csrf/').json()['csrfToken']
        response = client.post('/api/frontend/contact/', {'email': 'invalid'}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json()['errors'])
        self.assertEqual(ContactUs.objects.count(), 0)

    def test_contact_saves_message_and_notifies_staff(self):
        client = Client(enforce_csrf_checks=True)
        token = client.get('/api/frontend/csrf/').json()['csrfToken']
        response = client.post('/api/frontend/contact/', {
            'full_name': 'Visitor', 'email': 'visitor@example.com', 'phone': '251911000000',
            'subject': 'Project enquiry', 'message': 'Please contact me.',
        }, HTTP_X_CSRFTOKEN=token, HTTP_ORIGIN='http://localhost:3000')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactUs.objects.count(), 1)
        self.assertEqual(mail.outbox[0].to, ['staff@example.com'])
        self.assertEqual(mail.outbox[0].reply_to, ['visitor@example.com'])

    def test_new_comments_stay_unapproved(self):
        response = self.client.post(f'/api/frontend/blogs/{self.blog.pk}/comments/', {
            'author': 'Visitor', 'email': 'visitor@example.com', 'message': 'New comment', 'approved': 'true',
        })
        self.assertEqual(response.status_code, 201)
        self.assertFalse(BlogComment.objects.get().approved)

    def test_document_filter_and_pagination(self):
        for index in range(14):
            Document.objects.create(title=f'Report {index}', category='Annual Plan Report', description='Annual report', file=f'documents/{index}.pdf')
        response = self.client.get('/api/frontend/content/documents/', {'page': '2', 'q': 'Report', 'category': 'Annual Plan Report'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['total'], 14)
        self.assertEqual(len(response.json()['items']), 2)
        self.assertEqual(self.client.get('/api/frontend/content/documents/', {'q': 'missing'}).json()['total'], 0)

    def test_search_and_home_return_public_content(self):
        response = self.client.get('/api/frontend/search/', {'searched_item': 'story'})
        self.assertEqual(response.json()['groups']['blogs']['items'][0]['id'], self.blog.pk)
        response = self.client.get('/api/frontend/home/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('applications', response.json())
        self.assertEqual(response.json()['blogs'][0]['id'], self.blog.pk)

    def test_session_identity_is_preserved(self):
        self.user.is_active = True
        self.user.save(update_fields=['is_active'])
        self.client.force_login(self.user)
        response = self.client.get('/api/frontend/site/')
        self.assertTrue(response.json()['user']['authenticated'])
        self.assertEqual(response.json()['user']['name'], 'Reader')
