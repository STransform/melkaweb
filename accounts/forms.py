# Create a file named forms.py in your app directory

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

# viewers registration
class MyUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', 
            widget = forms.PasswordInput(attrs={'class': "form-control",'placeholder':'Password', 'autocomplete': "new-password",'placeholder': 'Password','minlength': 8,'style':'padding-left:2.5rem;'}))
    password2 = forms.CharField(label='Password confirmation',
            widget = forms.PasswordInput(attrs={'class':"form-control",'autocomplete':"new-password", 'placeholder':'Confirm password', 'minlength': 8,'style':'padding-left:2.5rem;'}))
    
    class Meta:
        model = UserProfile 
        fields = ['email', 'first_name','last_name','role', 'password', 'password2',  ]
        widgets = {
            'email':forms.EmailInput(attrs={'class':'form-control pl-5','placeholder':'Email','style':'padding-left:2.5rem;'}),
            'first_name':forms.TextInput(attrs={'class':'form-control','placeholder':'First Name','style':'padding-left:2.5rem;'}),
            'last_name':forms.TextInput(attrs={'class':'form-control  pl-5','placeholder':'Last Name','style':'padding-left:2.5rem;'}),
            'role':forms.Select(attrs={'class':'form-control', 'placeholder':'Select Role', 'type':'dropdown','style':'padding-left:2.5rem;'}),
        }
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data by super().
        password = self.cleaned_data.get("password")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)
            
    def save(self, commit=True):
        # Save the provided password in hashed format
        myuser = super(MyUserRegistrationForm, self).save(commit=False)
        myuser.is_staff = True
        myuser.set_password(self.cleaned_data["password"])    
        if commit:
            myuser.save()
        return myuser
    

# form to edit user profile
class EditProfileForm(forms.ModelForm):
    user_permissions = forms.ModelMultipleChoiceField(Permission.objects.all(),required=False,widget = forms.SelectMultiple( attrs = { 'class': ' form-control-light form-control ', 'multiple':True}),)
    groups = forms.ModelMultipleChoiceField( Group.objects.all(),required=False,widget = forms.SelectMultiple( attrs = { 'class': ' form-control-light form-control ', 'multiple':True}),)
    email = forms.CharField(required=False, disabled=True, widget=forms.EmailInput(attrs={'class':'form-control form-control-light','placeholder':'Enter Email'}),)
    
    class Meta:
        model = UserProfile 
        fields = ['email', 'first_name','last_name', 'profile_pic', 'phonenumber', 'status', 'groups', 'user_permissions', 'is_active','is_superuser' ]
        widgets = {
            'first_name':forms.TextInput(attrs={'class':'form-control form-control-light','placeholder':'Enter First Name',}),
            'last_name':forms.TextInput(attrs={'class':'form-control form-control-light','placeholder':'Enter Last Name',}),
            'role':forms.Select(attrs={'class':'form-control form-control-light', 'placeholder':'Select Role', 'type':'dropdown'}),
            'profile_pic':forms.FileInput(attrs={'class':'form-control form-control-light'}),
            'phonenumber':forms.TextInput(attrs={'class':'form-control form-control-light','placeholder':'Enter Phone number',}),
            'status':forms.Select(attrs={'class':'form-control form-control-light', 'placeholder':'Select Status', 'type':'dropdown'}),
            'is_active':forms.CheckboxInput(attrs={'class':'form-control form-control-light',}),
            'is_superuser':forms.CheckboxInput(attrs={'class':'form-control form-control-light',}),
            
        }

# form to change password
class ChangePasswordForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-light','placeholder': 'Current password','minlength': "8",}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-light','placeholder': 'New password','minlength': "8",}))
    retype_new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-light','placeholder': 'Confirm new password','minlength': "8",}))

    class Meta:
        model = UserProfile 
        fields = ['current_password', 'new_password', 'retype_new_password']
    
    def clean_retype_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        retype_new_password = self.cleaned_data.get("retype_new_password")
        if new_password and retype_new_password and new_password == retype_new_password:
            return new_password
        raise forms.ValidationError("The newly entered passwords don't match!")
        
    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data by super().
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            try:
                password_validation.validate_password(new_password)
            except ValidationError as error:
                self.add_error("new_password", error)
            

# form to reset lost password
class ResetPasswordForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-light','placeholder': 'New password','minlength': "8",}))
    retype_new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-light','placeholder': 'Confirm new password','minlength': "8",}))

    class Meta:
        model = UserProfile 
        fields = ['retype_new_password','new_password' ]
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        retype_new_password = self.cleaned_data.get("retype_new_password")
        if new_password and retype_new_password and new_password == retype_new_password:
            return new_password
        raise forms.ValidationError("The newly entered passwords don't match!")
        
    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data by super().
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            try:
                password_validation.validate_password(new_password)
            except ValidationError as error:
                self.add_error("new_password", error)
        