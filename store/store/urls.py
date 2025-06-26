from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalog.views_api import ProductViewSet, CategoryViewSet
from cart.views_api import CartViewSet
from orders.views_api import OrderViewSet
from accounts.views_api import RegisterAPI, LoginAPI
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'order', OrderViewSet, basename='order')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('catalog/', include('catalog.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', include('catalog.urls')),
]
