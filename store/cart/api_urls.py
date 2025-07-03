from tkinter.font import names

from django.urls import path
from cart.views_api import *

urlpatterns = [
    path('', ViewCartAPIView.as_view(), name='api_view_cart'),
    path('add_item/', AddToCartAPIView.as_view(), name='api_add_cart'),
    path('update_item/', UpdateCartItemAPIView.as_view(), name='api_update_cart'),
    path('delete_item/', DeleteCartItemAPIView.as_view(), name='api_delete_cart')
]
