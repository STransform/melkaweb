from django.urls import path, include
from .views import * 

urlpatterns = [
    
    path('', Dashboard.as_view(), name='admin_dashboard'),
    path('translator/', include('rosetta.urls'), name="translator"),
    path('list/<str:model_name>/', ListView.as_view(), name="list_view"),
    path('create/<str:model_name>/', CreateView.as_view(), name="create_view"),
    path('change/<str:model_name>/<int:pk>/', ChangeView.as_view(), name="change_view"),
    path('delete/<str:model_name>/<int:pk>/', DeleteView.as_view(), name="delete_view"),
    path('approve_comment/<int:pk>/', ApproveComment.as_view(), name="approve_comment"),
    path('supplier_detail/<str:tin>/', SupplierDetail.as_view(), name='supplier_detail'),
 
]

