from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework import viewsets

from .models import Product
from catalog.serializers import ProductSerializer, CategorySerializer
#

class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name='price', lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category']


@extend_schema(tags=["Product"])
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.filter(in_stock=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        sort = self.request.query_params.get('sort')

        sort_options = {
            'price_asc': 'price',
            'price_desc': '-price',
        }
        return queryset.order_by(sort_options[sort]) if sort in sort_options else queryset


@extend_schema(tags=["Category"])
class CategoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    @extend_schema(summary="Список категорий товаров")
    def list(self, request):
        categories = [{'key': key, 'name': name} for key, name in Product.CATEGORY_CHOICES]
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
