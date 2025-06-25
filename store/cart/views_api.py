from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Cart, CartItem
from catalog.models import Product
from .serializers import CartItemSerializer


@extend_schema(tags=["Cart"])
class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Просмотр корзины", responses={200: CartItemSerializer(many=True)})
    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)

    @extend_schema(summary="Добавить товар в корзину", request=CartItemSerializer, responses={200: CartItemSerializer})
    @action(detail=False, methods=["post"])
    def add_item(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "product_id обязателен"}, status=400)

        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        total_quantity = cart_item.quantity + quantity if not created else quantity

        if total_quantity > product.count:
            total_quantity = product.count

        used_quantity = total_quantity - cart_item.quantity
        if used_quantity > product.count:
            return Response({"error": "Недостаточно товара на складе"}, status=400)

        cart_item.quantity = total_quantity
        cart_item.save()

        product.count -= used_quantity
        product.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @extend_schema(summary="Обновить количество товара", request=CartItemSerializer,
                   responses={200: CartItemSerializer})
    @action(detail=False, methods=["put"])
    def update_item(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        if not product_id or not quantity:
            return Response({"error": "product_id и quantity обязательны"}, status=400)

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            return Response({"error": "Неверное количество"}, status=400)

        item = get_object_or_404(CartItem, product_id=product_id, cart__user=request.user)
        product = item.product

        delta = quantity - item.quantity

        if delta > 0:
            if delta > product.count:
                quantity = item.quantity + product.count
                delta = product.count
            product.count -= delta
            product.save()
        elif delta < 0:
            product.count += abs(delta)
            product.save()

        item.quantity = quantity
        item.save()
        serializer = CartItemSerializer(item)
        return Response(serializer.data)

    @extend_schema(summary="Удалить товар из корзины", request=CartItemSerializer, responses={200: dict})
    @action(detail=False, methods=["delete"])
    def delete_item(self, request):
        item_id = request.data.get("product_id")
        if not item_id:
            return Response({"error": "product_id обязателен"}, status=400)

        item = get_object_or_404(CartItem, product_id=item_id, cart__user=request.user)

        product = item.product
        product.count += item.quantity
        product.save()

        item.delete()
        return Response({"success": True})
