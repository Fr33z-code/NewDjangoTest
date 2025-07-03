from django.db import transaction
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from cart.service import ApiCartService
from rest_framework.exceptions import ValidationError
from .models import Cart, CartItem
from catalog.models import Product
from .serializers import CartItemSerializer, ResponseCartDeleteResponseSerializer, ResponseCartSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(tags=['Cart']))
class ViewCartAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResponseCartSerializer

    def get(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


@method_decorator(name='post', decorator=swagger_auto_schema(tags=['Cart']))
class AddToCartAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        service = ApiCartService()
        try:
            cart_item = service.add_product_to_cart(request.user, product_id, quantity)
        except ValidationError as e:
            return Response({"error": str(e.detail)}, status=400)

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)


@method_decorator(name='put', decorator=swagger_auto_schema(tags=['Cart']))
class UpdateCartItemAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def put(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        if not product_id or quantity is None:
            return Response({"error": "product_id и quantity обязательны"}, status=400)

        try:
            item, remaining_stock = ApiCartService.update_cart_item(request.user, product_id, quantity)
        except ValidationError as e:
            return Response({"error": str(e.detail)}, status=400)

        serializer = self.get_serializer(item)
        return Response({
            "cart_item": serializer.data,
            "remaining_stock": remaining_stock
        })


@method_decorator(name='delete', decorator=swagger_auto_schema(tags=['Cart']))
class DeleteCartItemAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResponseCartDeleteResponseSerializer

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")

        if not product_id:
            return Response({"error": "product_id обязателен"}, status=400)

        try:
            remaining_stock = ApiCartService.delete_cart_item(request.user, product_id)
        except ValidationError as e:
            return Response({"error": str(e.detail)}, status=400)
        except Product.DoesNotExist:
            return Response({"error": "Товар не найден"}, status=404)
        except CartItem.DoesNotExist:
            return Response({"error": "Товар в корзине не найден"}, status=404)

        return Response({"message": "Товар удален из корзины", "remaining_stock": remaining_stock})
