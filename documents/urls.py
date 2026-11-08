# documents/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('list-documents/', list_docs_view, name='list_docs'),
    path('pdf/<str:pk>/', pdf_view, name='pdf-view'),

]
