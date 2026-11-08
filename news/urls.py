from django.urls import path
from . import views

urlpatterns = [
    # Add more URL patterns as needed

    path('news_view/', views.news_list_visitor, name='news_list_visitor'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),  # Front News Details Page
    
    
    
]
