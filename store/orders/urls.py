from django.urls import path
from orders import views

urlpatterns = [
    path('create/', views.create_order_for_user, name='create_order_for_user'),
]
