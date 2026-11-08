# your_app/urls.py
from django.urls import path
from .views import job_list, jobs_apply, application_list

urlpatterns = [
    path('job_list/', job_list, name='job_list'),
    path('job_apply/<int:pk>/', jobs_apply.as_view(), name='jobs_apply'),
    path('application_list/', application_list, name='application_list'),
]