from django.urls import path
from catalog.views_api import *

urlpatterns = [
    path('', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('<int:id>/', CategoryViewSet.as_view(), name='category_list'),
]
