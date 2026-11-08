from django.contrib.auth.models import AbstractUser,AbstractBaseUser, Group, Permission,PermissionsMixin,BaseUserManager
from django.db import models
from django.utils import timezone
USER_ROLES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('teamleader', 'Team Leader'),
    )
STATUS = (('Pending','Pending'), ('Email Confirmation', 'Email Confirmation'), ('Account Activation', 'Account Activation'), ('Active', 'Active'))



class MyUserManager(BaseUserManager):
    def create_user (self, email, password, first_name, last_name): # things listed in REQUIRED_FIELDS
        if not email:
            raise ValueError("must have an email")
        myuser = self.model(email=self.normalize_email(email), first_name = first_name,last_name = last_name )
        myuser.is_staff = True # all users are staffs
        myuser.set_password(password)
        myuser.save(using=self.db)
        return myuser


    def create_superuser(self, email, password,  first_name, last_name):
        myuser = self.create_user(email, password,  first_name = first_name,last_name = last_name)
        myuser.is_active = True
        myuser.is_superuser = True
        myuser.role = "admin"
        myuser.status = "Active"
        myuser.save(using = self.db)
        return myuser
    
# model for user account
class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(('first name'), max_length=150, blank=True)
    last_name = models.CharField(('last name'), max_length=150, blank=True)
    
    role = models.CharField(max_length=20, choices=USER_ROLES, default='staff', verbose_name="User Category")
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phonenumber = models.CharField(max_length=15, null=True, blank=True)

    groups = models.ManyToManyField(Group, blank=True, related_name='user_group')
    user_permissions = models.ManyToManyField(
        Permission, blank=True, related_name='user_profiles_permissions'
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=STATUS, default='Pending')
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    date_joined = models.DateTimeField(('date joined'), default=timezone.now)


    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] 

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ('first_name',)

    def get_list_fields():
        return ['email', 'first_name', 'last_name', 'role', 'is_active', 'status', 'date_joined']
    
    list_fields = get_list_fields()
