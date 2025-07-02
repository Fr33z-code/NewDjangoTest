from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db import transaction

from .models import Order, OrderItem
from .serializers import RequestOrderSerializer
from cart.models import Cart, CartItem


@extend_schema(tags=["Order"])
class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создать заказ из корзины",
        request={
            'type': 'object',
            'properties': {
                'cart_item_ids': {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'example': [1, 2, 3],
                    'description': 'Список ID товаров в корзине для заказа. Если не указан, создается заказ из всей корзины'
                }
            },
            'required': []
        },
        responses={
            201: RequestOrderSerializer,
            400: {"description": "Указанные товары не найдены в корзине или корзина пуста"},
            404: {"description": "Корзина не найдена"}
        },

        examples=[
            OpenApiExample(
                "Заказ конкретных товаров",
                value={"cart_item_ids": [1, 2, 3]},
                description="Создать заказ только для указанных товаров из корзины"
            ),
            OpenApiExample(
                "Заказ всех товаров",
                value={},
                description="Создать заказ для всех товаров в корзине"
            )
        ]
    )
    def create(self, request):
        user = request.user
        cart_item_ids = request.data.get('cart_item_ids', [])

        try:
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)

            if cart_item_ids:
                cart_items = cart_items.filter(id__in=cart_item_ids)
                if not cart_items.exists():
                    return Response(
                        {"detail": "Указанные товары не найдены в корзине"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif not cart_items.exists():
                return Response(
                    {"detail": "Корзина пуста"},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
                serializer = RequestOrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response(
                {"detail": "Корзина не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )
