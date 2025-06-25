from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.db import transaction

from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart, CartItem


@extend_schema(tags=["Order"])
class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Создать заказ из корзины", responses={201: OrderSerializer})
    def create(self, request):
        user = request.user

        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return Response({"detail": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                total = sum(item.product.price * item.quantity for item in cart_items)
                order = Order.objects.create(user=user, total_price=total)

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price_per_item=item.product.price,
                    )

                cart_items.delete()
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({"detail": "Корзина не найдена"}, status=status.HTTP_404_NOT_FOUND)
