from django.urls import path
from .views import *

urlpatterns = [
    path('blogs/', BlogList.as_view(), name='blog_list'),
    path('blogs/<int:blog_id>/', blog_detail.as_view(), name='blog_detail'),

]
