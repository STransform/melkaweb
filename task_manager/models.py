from django.db import models
from accounts.models import UserProfile
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
# Task Status Choices
STATUS_CHOICES = (
    ('New', _('New')),
    ('Inprogress', _('Inprogress')),
    ('Completed', _('Completed')),
    ('Overdue', _('Overdue')),
    
    
)

# Priority Choices
PRIORITY_CHOICES = (
    ('High', _('High')),
    ('Medium', _('Medium')),
    ('Low', _('Low')),
)

class Task(models.Model):
    created_by = models.ForeignKey(UserProfile, related_name = 'created_tasks',blank=True, null=True, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(UserProfile, related_name='assigned_tasks')
    monitoring = models.ManyToManyField(UserProfile, related_name='monitoring_tasks')
    task_name = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.")

    assigned_date = models.DateTimeField(auto_now_add=True, editable = True)
    start_date = models.DateTimeField( blank=True, null=True)
    due_date = models.DateTimeField( blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    task_description = models.TextField()
    key_tasks = models.TextField()
    
    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.task_name
    
    def get_list_fields():
        return ['task_name', 'description']
    
    list_fields = get_list_fields()
    
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Comment by {self.user} on {self.task.task_name}"

