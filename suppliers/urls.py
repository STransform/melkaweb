from django.urls import path
from . import views
urlpatterns = [
    # Add more URL patterns as needed
    path('locked_supplier_list/', views.view_supplier, name='supplier_list'),
    path('search_supplier/', views.search_supplier, name='search_supplier'),
    
]
