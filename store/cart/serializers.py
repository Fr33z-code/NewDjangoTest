from rest_framework import serializers
from .models import Cart, CartItem
from catalog.models import Product
from catalog.serializers import ProductSerializer


# class CartItemSerializer(serializers.ModelSerializer):
#     product = ProductSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=Product.objects.all(), source='product', write_only=True
#     )
#
#     class Meta:
#         model = CartItem
#         fields = ['id', 'product', 'product_id', 'quantity', 'total_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product not found")
        return value

    def create(self, validated_data):
        raise NotImplementedError("Use CartService instead")



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']


class CartDeleteResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    returned_to_stock = serializers.IntegerField()
    remaining_stock = serializers.IntegerField()
