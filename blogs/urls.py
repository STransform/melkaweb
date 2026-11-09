from django.urls import path
from .views import *
from .public_views import TutorialList, TutorialDetail

urlpatterns = [
    path('blogs/', TutorialList.as_view(), name='blog_list'),
    path('blogs/<int:blog_id>/', TutorialDetail.as_view(), name='blog_detail'),

]
