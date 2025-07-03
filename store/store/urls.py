from importlib.resources import as_file
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalog.views_api import *
from orders.views_api import OrderViewSet
from accounts.views_api import RegisterAPI, LoginAPI

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="FursAndFurCoats API",
        default_version='v1',
        description="Документация для API магазина мехов и шуб",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('catalog/', include('catalog.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('api/cart/', include('cart.api_urls')),
    path('api/products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('api/products/<int:id>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='product-detail'),
    path('api/categories/', CategoryViewSet.as_view(), name='category_list'),
    path('api/order/', OrderViewSet.as_view(), name='create_order_for_user'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('', include('catalog.urls')),
]
