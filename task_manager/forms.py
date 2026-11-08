from django import forms
from .models import Task, STATUS_CHOICES

class TaskForm(forms.ModelForm):
    task_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    key_tasks = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class':'form-control'}), required=False)

    # Use DateTimeInput widget for start_date and due_date
    start_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local', "class":"form-control flatpickr-input datetime"}))
    due_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local', "class":"form-control flatpickr-input datetime"}))
    
    class Meta:
        model = Task
        fields = ['task_name', 'assigned_to', 'monitoring', 'start_date', 'due_date',  'priority', 'task_description', 'key_tasks', 'status']
        widgets = {
            'assigned_to':forms.SelectMultiple(attrs={'class':'form-control','multiple':'true'}),
            'monitoring':forms.SelectMultiple(attrs={'class':'form-control', 'multiple':'true'}),
            # 'status':forms.Select(attrs={}),
        }
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')

        # Ensure start date is less than end date
        if start_date and due_date and start_date >= due_date:
            raise forms.ValidationError("The start date must be less than the end date.")

        return cleaned_data
# forms.py
class CommentForm(forms.Form):
    comment_content = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a comment...'}))
