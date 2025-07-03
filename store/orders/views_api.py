from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import Order, OrderItem
from .serializers import RequestOrderSerializer
from cart.models import Cart, CartItem


@method_decorator(name='post', decorator=swagger_auto_schema(tags=['Order']))
class OrderViewSet(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestOrderSerializer

    def post(self, request, *args, **kwargs):
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
