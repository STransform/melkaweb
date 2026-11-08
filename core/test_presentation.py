import datetime
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from blogs.models import Blog, BlogComment
from core.models import Pages, Settings
from core.presentation import MEDIA_TYPE
from dashboard.models import FAQ, GalleryImage
from documents.models import Document
from task_manager.models import Comment, Task
from vacancies.models import Application, Job


class PresentationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_superuser(email='migration@example.com', password='Example-password-42', first_name='Migration', last_name='Tester')
        Settings.objects.create(title='Melka tech', working_hours='9–5', logo='Logo/test.png')
        Pages.objects.create()
        cls.blog = Blog.objects.create(title='Migration story', created_by=cls.staff, published_status='Published', content='<p>Same content and interface.</p>', images='blog_images/story.jpg')
        BlogComment.objects.create(blog=cls.blog, author='Visitor', email='visitor@example.com', message='Approved comment', approved=True)
        Document.objects.create(title='Guide', description='Download guide', category='Django Training', file='documents/guide.pdf')
        FAQ.objects.create(question='How does it work?', answer='The same way.')
        GalleryImage.objects.create(title='Team event', image='gallery_images/team.jpg')
        cls.task = Task.objects.create(created_by=cls.staff, task_name='Migration task', task_description='Preserve behavior', key_tasks='Compare UI\nCheck forms')
        cls.task.assigned_to.add(cls.staff)
        cls.comment = Comment.objects.create(task=cls.task, user=cls.staff, content='Task comment')
        Comment.objects.create(task=cls.task, user=cls.staff, content='Thread reply', parent_comment=cls.comment)
        cls.job = Job.objects.create(job_title='Engineer', job_type='Full Time', vacancies=1, skills='Python', job_deadline=datetime.date(2030,1,1), location='Addis Ababa', level='Junior', Status='Active', job_description='Build software')

    def payload(self, path, **kwargs):
        with patch('vacancies.views.fetch_odoo_jobs', return_value=[]):
            response = self.client.get(path, HTTP_ACCEPT=MEDIA_TYPE, **kwargs)
        self.assertEqual(response.status_code, 200, path)
        self.assertEqual(response['Content-Type'], 'application/json')
        return response.json()

    def render_frontend(self, payload):
        command = "import {renderPresentation} from './frontend/lib/presentation/render.mjs';let input='';for await(const chunk of process.stdin)input+=chunk;process.stdout.write(renderPresentation(JSON.parse(input)));"
        result = subprocess.run(['node','--input-type=module','-e',command], input=json.dumps(payload), text=True, capture_output=True, cwd=settings.BASE_DIR, check=True)
        return result.stdout

    def test_all_application_families_export_data_without_backend_html(self):
        anonymous = ['/', '/accounts/login/', '/accounts/signup/', '/accounts/reset_password/', '/suppliers/locked_supplier_list/', '/vacancies/job_list/', f'/vacancies/job_apply/{self.job.pk}/', '/news/news_view/', '/blogs/blogs/', f'/blogs/blogs/{self.blog.pk}/', '/documents/list-documents/', '/about-us/about/', '/gallery-images/', '/events/', '/bids/', '/contact-us/']
        for path in anonymous:
            with self.subTest(path=path):
                data = self.payload(path)
                self.assertIn('template',data)
                self.assertIn('context',data)
                self.assertNotIn('html',data)
        self.client.force_login(self.staff)
        for path in ['/dashboard/', '/dashboard/list/Blog/', '/dashboard/create/Blog/', f'/dashboard/change/Blog/{self.blog.pk}/', f'/accounts/profile/{self.staff.pk}/', '/accounts/users_list/', '/accounts/Add_user/', '/taskmanager/task_view/All/', f'/taskmanager/task_details/{self.task.pk}/', '/vacancies/application_list/']:
            with self.subTest(path=path): self.payload(path)

    def test_original_layout_and_content_match_frontend_renderer(self):
        # Compare the migration renderer against the existing UI before retiring
        # its templates. This is an equivalence test, not a new design snapshot.
        paths=['/', '/accounts/login/', '/accounts/signup/', '/accounts/reset_password/', '/blogs/blogs/', f'/blogs/blogs/{self.blog.pk}/', '/documents/list-documents/', '/suppliers/locked_supplier_list/']
        staff_paths=['/dashboard/', '/dashboard/list/Blog/', '/dashboard/create/Blog/', f'/dashboard/change/Blog/{self.blog.pk}/', '/accounts/users_list/', '/taskmanager/task_view/All/', f'/taskmanager/task_details/{self.task.pk}/']
        for staff, page_paths in [(False,paths),(True,staff_paths)]:
            if staff: self.client.force_login(self.staff)
            for path in page_paths:
                with self.subTest(path=path):
                    with patch('vacancies.views.fetch_odoo_jobs', return_value=[]):
                        old=self.client.get(path)
                    self.assertEqual(old.status_code,200,path)
                    rendered=self.render_frontend(self.payload(path))
                    baseline=BeautifulSoup(old.content,'html.parser')
                    migrated=BeautifulSoup(rendered,'html.parser')
                    def summary(soup):
                        return {'headings':[(node.name,node.get_text(' ',strip=True)) for node in soup.select('h1,h2,h3,h4,h5,h6')],
                                'images':[(node.get('src'),node.get('class')) for node in soup.select('img')],
                                'links':[(node.get('href'),node.get_text(' ',strip=True)) for node in soup.select('a[href]')],
                                'controls':[(node.name,node.get('name'),node.get('type'),node.get('class')) for node in soup.select('input:not([name=csrfmiddlewaretoken]),select,textarea')],
                                'styles':[node.get('href') for node in soup.select('link[rel=stylesheet]')]}
                    before, after = summary(baseline), summary(migrated)
                    Path('/tmp/melka-ui-before-'+path.replace('/','_')+'.json').write_text(json.dumps(before,indent=2))
                    Path('/tmp/melka-ui-after-'+path.replace('/','_')+'.json').write_text(json.dumps(after,indent=2))
                    for key in before:
                        with self.subTest(component=key):
                            self.assertEqual(after[key],before[key])

    def test_credentials_and_unused_private_context_are_not_exported(self):
        Application.objects.create(partner_name='Private applicant', email_from='private@example.com', job_odoo_id=4)
        data=self.payload('/')
        self.assertNotIn('applications',data['context'])
        self.assertNotIn('Private applicant',json.dumps(data))
        self.client.force_login(self.staff)
        data=self.payload(f'/accounts/profile/{self.staff.pk}/')
        raw=json.dumps(data)
        self.assertNotIn(self.staff.password,raw)
        self.assertNotIn(self.client.session.session_key,raw)
        for field in data['context']['password_form']['$form']:
            self.assertIsNone(field['value'])

    def test_session_login_invalid_form_and_permissions(self):
        denied=self.client.get('/dashboard/',HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(denied.status_code,302)
        response=self.client.post('/accounts/login/',{'email':self.staff.email,'password':'wrong'},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['template'],'login.html')
        response=self.client.post('/accounts/login/',{'email':self.staff.email,'password':'Example-password-42'},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,302)
        self.assertIn('sessionid',response.cookies)
        self.assertEqual(response['Location'],'/dashboard/')
        self.payload('/dashboard/')

    def test_dashboard_crud_and_validation_use_existing_forms(self):
        self.client.force_login(self.staff)
        response=self.client.post('/dashboard/create/CompanyValues/',{'title_en':'New value','content_en':'Preserved CRUD'},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,302)
        from about_us.models import CompanyValues
        obj=CompanyValues.objects.get()
        self.assertEqual(obj.title,'New value')
        response=self.client.post(f'/dashboard/change/CompanyValues/{obj.pk}/',{'title_en':'Updated value','content_en':'Updated content'},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,302)
        obj.refresh_from_db(); self.assertEqual(obj.title,'Updated value')
        response=self.client.post('/dashboard/create/CompanyValues/',{},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,200)
        self.assertIn('title_en',response.json()['context']['form']['errors'])
        response=self.client.get(f'/dashboard/delete/CompanyValues/{obj.pk}/',HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,302)
        self.assertFalse(CompanyValues.objects.exists())

    def test_local_job_submission_keeps_file_and_data(self):
        with patch('vacancies.views.fetch_odoo_jobs',return_value=[]):
            response=self.client.post(f'/vacancies/job_apply/{self.job.pk}/',{'partner_name':'Candidate','email_from':'candidate@example.com','experience':'2','attachment_ids':SimpleUploadedFile('resume.txt',b'Example resume')},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,302)
        obj=Application.objects.get()
        self.assertEqual(obj.job_odoo_id,self.job.pk)
        self.assertEqual(obj.experience,2)
        self.assertTrue(obj.attachment_ids.name.endswith('.txt'))
        obj.attachment_ids.delete(save=False)

    def test_unknown_page_and_csrf_errors_are_frontend_presentations(self):
        response=self.client.get('/not-a-real-page/',HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json()['template'],'404.html')
        client=Client(enforce_csrf_checks=True)
        response=client.post('/accounts/login/',{},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,403)
        self.assertEqual(response.json()['template'],'403.html')

    def test_cms_content_is_exported_without_rendering_the_page(self):
        from cms.api import create_page, add_plugin
        create_page('CMS Home','front/cms_bases/cms_base.html','en',slug='cms-home')
        page=create_page('CMS Example','front/cms_bases/cms_base.html','en',slug='cms-example')
        placeholder=page.get_placeholders('en').get(slot='content')
        add_plugin(placeholder,'TextPlugin','en',body='<p>CMS content preserved.</p>')
        data=self.payload('/cms-example/')
        self.assertEqual(data['template'],'front/cms_bases/cms_base.html')
        self.assertIn('CMS content preserved.',data['context']['cms_placeholders']['content'])
        self.assertIn('CMS content preserved.',self.render_frontend(data))

    def test_contact_and_task_comments_keep_original_workflows(self):
        with patch('core.views.EmailMultiAlternatives.send',return_value=1):
            response=self.client.post('/contact-us/',{'name':'Visitor','email':'visitor@example.com','phone':'251911000000','subject':'Enquiry','message':'Same form'},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,302)
        from core.models import ContactUs
        self.assertEqual(ContactUs.objects.get().full_name,'Visitor')
        self.client.force_login(self.staff)
        response=self.client.post(f'/taskmanager/add_comment/{self.task.pk}/',{'comment_content':'New task comment'},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,302)
        self.assertTrue(self.task.comments.filter(content='New task comment').exists())
        response=self.client.post(f'/taskmanager/reply_comment/{self.comment.pk}/',{'comment_content':'New threaded reply'},HTTP_ACCEPT=MEDIA_TYPE)
        self.assertEqual(response.status_code,302)
        self.assertTrue(self.comment.replies.filter(content='New threaded reply').exists())
