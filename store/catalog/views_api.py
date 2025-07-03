from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions
from .filters import ProductFilter
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status


@method_decorator(name='get', decorator=swagger_auto_schema(tags=['Category']))
class CategoryViewSet(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'


@method_decorator(name='get', decorator=swagger_auto_schema(tags=['Products']))
@method_decorator(name='post', decorator=swagger_auto_schema(tags=['Products']))
class ProductListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


@method_decorator(name='get', decorator=swagger_auto_schema(tags=['Products']))
@method_decorator(name='put', decorator=swagger_auto_schema(tags=['Products']))
@method_decorator(name='patch', decorator=swagger_auto_schema(tags=['Products']))
@method_decorator(name='delete', decorator=swagger_auto_schema(tags=['Products']))
class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
