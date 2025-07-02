from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Cart, CartItem
from catalog.models import Product
from .serializers import CartItemSerializer, ResponseCartDeleteResponseSerializer


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

        available = product.count + (cart_item.quantity if not created else 0)
        requested_total = (cart_item.quantity + quantity) if not created else quantity

        if requested_total > available:
            return Response({
                "error": f"Недостаточно товара. Доступно: {available - (cart_item.quantity if not created else 0)}"
            }, status=400)

        cart_item.quantity = requested_total
        cart_item.save()

        product.count = available - requested_total
        product.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    @extend_schema(summary="Обновить количество товара в корзине",
                   request=CartItemSerializer,
                   responses={200: CartItemSerializer})
    @action(detail=False, methods=["put"])
    def update_item(self, request):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")

        if not product_id or not quantity:
            return Response({"error": "product_id и quantity обязательны"}, status=400)

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except ValueError:
            return Response({"error": "Количество должно быть положительным числом"}, status=400)

        with transaction.atomic():
            item = get_object_or_404(
                CartItem.objects.select_for_update(),
                product_id=product_id,
                cart__user=request.user
            )
            product = Product.objects.select_for_update().get(id=product_id)

            delta = quantity - item.quantity

            if delta > 0:
                available = product.count
                if delta > available:
                    return Response({
                        "error": f"Недостаточно товара на складе. Доступно: {available}"
                    }, status=400)

                product.count -= delta
                item.quantity = quantity

            elif delta < 0:
                returned = abs(delta)
                if (product.count + returned) > product.initial_count:
                    returned = product.initial_count - product.count
                    item.quantity = item.quantity - returned
                else:
                    item.quantity = quantity

                product.count += returned

            product.save()
            item.save()

            serializer = CartItemSerializer(item)
            return Response({
                "cart_item": serializer.data,
                "remaining_stock": product.count
            })

    @extend_schema(summary="Удалить товар из корзины",
                   request=CartItemSerializer,
                   responses={200: ResponseCartDeleteResponseSerializer})
    @action(detail=False, methods=["delete"])
    def delete_item(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"error": "product_id обязателен"}, status=400)

        with transaction.atomic():
            item = get_object_or_404(
                CartItem.objects.select_for_update(),
                product_id=product_id,
                cart__user=request.user
            )
            product = Product.objects.select_for_update().get(id=product_id)

            returned = item.quantity
            new_count = product.count + returned

            if new_count > product.initial_count:
                returned = product.initial_count - product.count
                product.count = product.initial_count
            else:
                product.count = new_count

            product.save()
            item.delete()

            return Response({
                "success": True,
                "returned_to_stock": returned,
                "remaining_stock": product.count
            })
