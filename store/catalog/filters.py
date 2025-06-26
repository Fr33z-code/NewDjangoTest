from django_filters.rest_framework import FilterSet, NumberFilter
from .models import Product


class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name='price', lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')
    category_id = NumberFilter(field_name='category__id')

    class Meta:
        model = Product
        fields = ['category_id', 'in_stock']
