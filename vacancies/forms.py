from django import forms
from .models import Job, Application


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ['Status']
        widgets = {
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job Title'
            }),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'vacancies': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of Vacancies'
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Skills (comma separated)'
            }),
            'job_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Location'
            }),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detailed job description...',
                'rows': 4
            }),
        }


class ApplicationForm(forms.Form):
    partner_name = forms.CharField(
        max_length=100,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    email_from = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    partner_phone = forms.CharField(
        max_length=20,
        required=False,
        label="Phone",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional phone number'
        })
    )
    cgpa_requirement = forms.FloatField(
        required=False,
        label="CGPA",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'e.g. 3.50'
        })
    )
    experience = forms.IntegerField(
        required=False,
        label="Years of Experience",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 0,
            'placeholder': 'Years of experience'
        })
    )
    linkedin_profile = forms.URLField(
        required=False,
        label="LinkedIn Profile",
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/username'
        })
    )
    attachment_ids = forms.FileField(
        required=False,
        label="Resume",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file'
        })
    )
