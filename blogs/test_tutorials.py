import io
import json
import subprocess
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from PIL import Image
from .models import Blog, BlogCategory, BlogComment, BlogLike, BlogVisit
from core.presentation import MEDIA_TYPE

class TutorialTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_superuser('tutorial@example.com', 'Example-password-42', 'Tutorial', 'Author')
        cls.category = BlogCategory.objects.create(name='DevOps')
        cls.post = Blog.objects.create(title='Deploy with Docker', content='## Start\n\n```bash\ndocker compose up\n```', summary='A practical deployment guide.', blog_category=cls.category, created_by=cls.author, published_status='Published', tags='Docker, Cloud', series='Deployments')
        cls.draft = Blog.objects.create(title='Private draft', content='Unpublished secret text', created_by=cls.author)

    def setUp(self):
        cache.clear()

    def page(self, path):
        return self.client.get(path, HTTP_ACCEPT=MEDIA_TYPE)

    def test_drafts_are_private_on_every_public_surface(self):
        for path in [self.draft.get_absolute_url(), f'/blogs/blogs/{self.draft.pk}/', f'/api/frontend/content/blogs/{self.draft.pk}/']:
            self.assertEqual(self.client.get(path, HTTP_ACCEPT=MEDIA_TYPE).status_code, 404, path)
        for path in ['/tutorials/', '/tutorials/feed.xml', '/tutorials/sitemap.xml', '/api/frontend/home/', '/api/frontend/search/?searched_item=Private', '/search/?searched_item=Private', '/api/frontend/content/blogs/']:
            response = self.page(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertNotIn('Unpublished secret text', response.content.decode())
            self.assertNotIn('Private draft', response.content.decode())
        self.assertEqual(self.client.post(f'/api/frontend/blogs/{self.draft.pk}/like/', {'liked':'true'}).status_code,404)

    def test_admin_publish_edit_and_draft_workflow(self):
        self.client.force_login(self.author)
        schema = self.client.get('/api/frontend/admin/Blog/?schema=create').json()
        self.assertFalse(next(f for f in schema['fields'] if f['name']=='images')['required'])
        body = {'title_en':'My new tutorial','content_en':'## First step\n\nFollow along.', 'blog_category':self.category.pk,'published_status':'Hold','content_format':'markdown','difficulty':'Beginner','series_order':'1'}
        response = self.client.post('/api/frontend/admin/Blog/',body)
        self.assertEqual(response.status_code,201,response.content)
        post = Blog.objects.get(pk=response.json()['id'])
        self.assertIsNone(post.published_at)
        self.assertEqual(self.page(post.get_absolute_url()).status_code,404)
        body['published_status']='Published'
        response = self.client.post(f'/api/frontend/admin/Blog/{post.pk}/',body)
        self.assertEqual(response.status_code,200,response.content)
        post.refresh_from_db()
        self.assertIsNotNone(post.published_at)
        original_slug=post.slug
        self.client.logout()
        data=self.page(post.get_absolute_url()).json()['context']['tutorial']
        self.assertEqual(data['title'],'My new tutorial')
        self.assertEqual(data['author'],'Tutorial Author')
        post.title='Changed heading';post.save();self.assertEqual(post.slug,original_slug)
        post.published_status='Hold';post.save()
        self.assertEqual(self.page(post.get_absolute_url()).status_code,404)

    def test_filters_series_and_legacy_redirect(self):
        response=self.page('/tutorials/?q=Docker&category=DevOps&difficulty=Beginner')
        self.assertEqual(response.json()['context']['tutorial_library']['total'],1)
        self.assertEqual(self.page('/tutorials/?q=missing').json()['context']['tutorial_library']['total'],0)
        response=self.client.get(f'/blogs/blogs/{self.post.pk}/')
        self.assertEqual(response.status_code,301)
        self.assertEqual(response['Location'],self.post.get_absolute_url())
        self.assertEqual(len(self.page(self.post.get_absolute_url()).json()['context']['tutorial']['lessons']),1)
        self.assertContains(self.client.get('/tutorials/sitemap.xml'),self.post.slug)

    def test_explicit_publish_action_overrides_draft_status(self):
        self.client.force_login(self.author)
        body={'title_en':'Explicit publish action','content_en':'A complete tutorial.',
              'blog_category':self.category.pk,'published_status':'Hold','publish_action':'Published',
              'content_format':'markdown','difficulty':'Beginner','series_order':'1'}
        response=self.client.post('/api/frontend/admin/Blog/',body)
        self.assertEqual(response.status_code,201,response.content)
        self.assertEqual(response.json()['published_status'],'Published')
        self.assertTrue(response.json()['public_url'].startswith('/tutorials/'))
        self.client.logout()
        self.assertEqual(self.page(response.json()['public_url']).status_code,200)
        self.client.force_login(self.author)
        body['publish_action']='Hold';body['published_status']='Published'
        response=self.client.post(f"/api/frontend/admin/Blog/{response.json()['id']}/",body)
        self.assertEqual(response.json()['published_status'],'Hold')
        self.assertIsNone(response.json()['public_url'])

    def test_publish_preserves_emoji_and_multilingual_content(self):
        self.client.force_login(self.author)
        title = 'Java collections 📌'
        content = '## 📌 Lists and sets\n\n✅ Ordered lists\n🚀 Deploy safely\nአማርኛ — Afaan Oromoo'
        response = self.client.post('/api/frontend/admin/Blog/', {
            'title_en': title, 'content_en': content, 'summary': 'Learn collections 🚀',
            'blog_category': self.category.pk, 'published_status': 'Hold',
            'publish_action': 'Published', 'content_format': 'markdown',
            'difficulty': 'Beginner', 'series_order': '1',
        })
        self.assertEqual(response.status_code, 201, response.content)
        post = Blog.objects.get(pk=response.json()['id'])
        self.assertEqual(post.content, content)
        self.assertEqual(post.title, title)
        self.client.logout()
        data = self.page(post.get_absolute_url()).json()['context']['tutorial']
        self.assertEqual(data['content'], content)
        self.assertEqual(data['summary'], 'Learn collections 🚀')

    def test_likes_and_daily_reads_are_persistent_and_deduplicated(self):
        url=f'/api/frontend/blogs/{self.post.pk}/'
        for _ in range(2):
            self.assertEqual(self.client.post(url+'visit/',{'source':'linkedin'}).status_code,200)
            self.assertEqual(self.client.post(url+'like/',{'liked':'true'}).status_code,200)
        self.assertEqual(BlogLike.objects.count(),1)
        self.assertEqual(BlogVisit.objects.count(),1)
        self.client.post(url+'visit/',{'engaged':'true'})
        self.assertTrue(BlogVisit.objects.get().engaged)
        self.assertEqual(BlogVisit.objects.get().source,'linkedin')
        self.client.post(url+'like/',{'liked':'false'})
        self.assertEqual(BlogLike.objects.count(),0)
        other=Client();other.post(url+'like/',{'liked':'true'})
        self.assertEqual(BlogLike.objects.count(),1)

    def test_comments_are_validated_moderated_and_csrf_protected(self):
        url=f'/api/frontend/blogs/{self.post.pk}/comments/'
        self.assertEqual(Client(enforce_csrf_checks=True).post(url,{}).status_code,403)
        self.assertEqual(self.client.post(url,{'email':'invalid'}).status_code,400)
        response=self.client.post(url,{'author':'Reader','email':'private@example.com','message':'Great lesson'})
        self.assertEqual(response.status_code,201)
        comment=BlogComment.objects.get();self.assertFalse(comment.approved)
        self.assertNotIn('Great lesson',self.page(self.post.get_absolute_url()).content.decode())
        comment.approved=True;comment.save()
        response=self.page(self.post.get_absolute_url())
        self.assertIn('Great lesson',response.content.decode())
        self.assertNotIn('private@example.com',response.content.decode())

    def test_editor_upload_and_analytics_require_permission(self):
        self.assertEqual(self.client.get('/api/frontend/tutorial-analytics/').status_code,302)
        self.client.force_login(self.author)
        image=io.BytesIO();Image.new('RGB',(50,50),'blue').save(image,format='PNG')
        response=self.client.post('/api/frontend/tutorial-images/',{'image':SimpleUploadedFile('screen.png',image.getvalue(),content_type='image/png')})
        self.assertEqual(response.status_code,201,response.content)
        self.assertTrue(response.json()['url'].endswith('.jpg'))
        self.assertEqual(self.client.get('/api/frontend/tutorial-analytics/').status_code,200)
        self.assertEqual(self.client.post('/api/frontend/tutorial-images/',{'image':SimpleUploadedFile('bad.svg',b'<script>alert(1)</script>')}).status_code,400)

    def test_rendered_tutorial_has_safe_code_and_toc(self):
        payload=self.page(self.post.get_absolute_url()).json()
        command="import {renderPresentation} from './frontend/lib/presentation/render.mjs';let s='';for await(const c of process.stdin)s+=c;process.stdout.write(renderPresentation(JSON.parse(s)));"
        result=subprocess.run(['node','--input-type=module','-e',command],input=json.dumps(payload),text=True,capture_output=True,cwd=settings.BASE_DIR,check=True)
        self.assertIn('class="tutorial-prose"',result.stdout)
        self.assertIn('id="section-1"',result.stdout)
        self.assertIn('docker compose up',result.stdout)
        self.assertIn('Share on LinkedIn',result.stdout)

    def test_homepage_tutorial_cards_support_optional_covers(self):
        payload = self.page('/').json()
        self.assertEqual(payload['context']['recent_tutorials'][0]['title'], self.post.title)
        self.assertEqual(payload['context']['recent_tutorials'][0]['image'], '')
        self.assertEqual(payload['context']['recent_tutorials'][0]['url'], self.post.get_absolute_url())
        self.assertEqual(payload['context']['recent_tutorials'][0]['content'], '')
