from django.urls import path
from cart import views
#from cart.views import AddToCartAjaxView
from .views import CartView, UpdateCartView, UpdateCartItemView, DeleteFromCartView

# urlpatterns = [
#     path('', views.view_cart, name='view_cart'),
#     path('add/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
#     path('update_item/', views.update_cart_item, name='update_cart_item'),
#     path('delete/<int:product_id>/', views.delete_from_cart, name='delete_from_cart'),
# ]
urlpatterns = [
    path('', CartView.as_view(), name='view_cart'),
    path('add/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('update/', UpdateCartView.as_view(), name='update_cart'),
    path('update-item/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('delete/<int:item_id>/', DeleteFromCartView.as_view(), name='delete_from_cart'),
]