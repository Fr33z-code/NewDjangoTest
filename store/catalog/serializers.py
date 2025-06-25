from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'image', 'price', 'category', 'in_stock']


class CategorySerializer(serializers.Serializer):
    key = serializers.CharField()
    name = serializers.CharField()
