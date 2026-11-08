from django.db import models
from django.utils.translation import gettext as _
import os

def get_file_extension(filename):
    return os.path.splitext(filename)[1]

    
class Document(models.Model):
    CATEGORY_CHOICES = (
        ('OTECH Engineering Docs', _('OTECH Engineering Docs')),
        ('Java Training ', _('Java Training')),
        ('Django Training', _('Django Training')),
        ('Annual Plan Report', _('Annual Plan Report')),
        ('', _('Other')),
    )
    title = models.CharField(max_length=200,help_text="Make sure to submit a max of 200 characters.")
    category = models.CharField(max_length=200, choices=CATEGORY_CHOICES, default='OTH')
    description = models.TextField(help_text="Make sure to submit a max of 255 characters.")
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='documents/')

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return self.title
        
    def file_extension(self):
        return get_file_extension(self.file.name)
    
    def get_list_fields():
        return ['title', 'category', 'upload_date']
    
    list_fields = get_list_fields()

