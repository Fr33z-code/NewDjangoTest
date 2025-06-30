from django.urls import path
from .views import HomeView, CatalogView

urlpatterns = [
    path('', CatalogView.as_view(), name='catalog'),
    path('catalog/', CatalogView.as_view(), name='catalog'),
    path('home/', HomeView.as_view(), name='home')
]
