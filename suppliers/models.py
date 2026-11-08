from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from accounts.models import UserProfile

SECTOR_CHOICES = [
    ('Private', _('Private')),
    ('Corporate', _('Corporate')),
    ('Retail', _('Retail')),
    ('Merchant', _('Merchant')),
    ]

class Supplier(models.Model):
    # model for blocked suppliers
    tin = models.CharField(max_length=20, unique = True)
    company_name = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.")
    legal_form = models.CharField(max_length=100,help_text="Make sure to submit a max of 100 characters.")
    nationality = models.CharField(max_length=100,help_text="Make sure to submit a max of 100 characters.")
    area_of_business = models.CharField(max_length=255,help_text="Make sure to submit a max of 255 characters.")
    sector = models.CharField(max_length=100, choices=SECTOR_CHOICES)
    description = models.TextField(help_text=" Add a short description why the supplier is blocked.", default="/")
    document = models.FileField(upload_to='supplier/document', default="/")
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True,null=True)
    
    @property
    def get_name(self):
        return self.company_name

    @property
    def get_id(self):
        return self.user.id
    
    class Meta:
        ordering = ["-id"]
    

    def __str__(self):
        return self.company_name
    
    def get_list_fields():
        return ['company_name', 'tin', 'nationality', 'area_of_business', 'created_by']
    
    list_fields = get_list_fields()
    


class ArchivedSupplier(models.Model):
    # model for archived blocked suppliers
    tin = models.CharField(max_length=20,)
    company_name = models.CharField(max_length=255)
    legal_form = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    area_of_business = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, choices=SECTOR_CHOICES)
    description = models.TextField()
    document = models.FileField(upload_to='supplier/document')
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_date = models.DateField()
    archived_date =  models.DateField( auto_now_add=True)
    
    
    @property
    def get_name(self):
        return self.company_name

    @property
    def get_id(self):
        return self.user.id
    
    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.company_name

    def get_list_fields():
        return ['company_name', 'tin', 'nationality', 'area_of_business', 'created_by', 'archived_date']
    
    list_fields = get_list_fields()
    
    