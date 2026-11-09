from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core import mail
from task_manager.models import Task, Comment


class TaskApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser('tasks@example.com', 'Task-password-42', 'Task', 'Owner')
        self.client.force_login(self.user)
        self.fields = {'task_name': 'Launch website', 'assigned_to': [self.user.pk], 'monitoring': [self.user.pk],
                       'start_date': '2030-01-01T09:00', 'due_date': '2030-01-02T09:00',
                       'priority': 'High', 'status': 'New', 'task_description': 'Verify launch', 'key_tasks': 'Build\nTest'}

    def test_create_update_thread_and_scopes(self):
        response = self.client.post('/api/frontend/tasks/All/', self.fields)
        self.assertEqual(response.status_code, 201)
        pk = response.json()['id']
        self.assertEqual(len(mail.outbox), 2)
        for scope in ['All', 'My', 'Assigned', 'Monitoring']:
            response = self.client.get(f'/api/frontend/tasks/{scope}/')
            self.assertEqual(response.json()['tasks'][0]['id'], pk)
            self.assertTrue(response.json()['fields'])
        response = self.client.post(f'/api/frontend/tasks/detail/{pk}/', {**self.fields, 'status': 'Completed'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.get(pk=pk).status, 'Completed')
        self.assertEqual(len(mail.outbox), 3)
        response = self.client.post(f'/api/frontend/tasks/{pk}/comments/', {'comment_content': 'Ready'})
        self.assertEqual(response.status_code, 201)
        parent = response.json()['comments'][0]['id']
        response = self.client.post(f'/api/frontend/tasks/{pk}/comments/{parent}/', {'comment_content': 'Confirmed'})
        self.assertEqual(response.json()['comments'][0]['replies'][0]['content'], 'Confirmed')

    def test_reject_invalid_dates_cross_task_reply_and_missing_csrf(self):
        response = self.client.post('/api/frontend/tasks/All/', {**self.fields, 'due_date': '2029-01-01T09:00'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Task.objects.exists())
        one = Task.objects.create(task_name='One', created_by=self.user)
        two = Task.objects.create(task_name='Two', created_by=self.user)
        comment = Comment.objects.create(task=two, user=self.user, content='Other task')
        response = self.client.post(f'/api/frontend/tasks/{one.pk}/comments/{comment.pk}/', {'comment_content': 'Invalid'})
        self.assertEqual(response.status_code, 404)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post('/api/frontend/tasks/All/', self.fields).status_code, 403)
