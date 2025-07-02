from django.urls import path
from cart import views
from .views import CartView, UpdateCartView, UpdateCartItemView, DeleteFromCartView, AddToCartView

urlpatterns = [
    path('', CartView.as_view(), name='view_cart'),
    path('add/', AddToCartView.as_view(), name='add_to_cart_ajax'),
    path('update/', UpdateCartView.as_view(), name='update_cart'),
    path('update-item/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('delete/<int:item_id>/', DeleteFromCartView.as_view(), name='delete_from_cart')
]
