from core.BaseService import BaseService
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

class OrderService(BaseService):
    def __init__(self, user):
        self.user = user

    def create_order_from_cart(self):
        try:
            cart = Cart.objects.get(user_id=self.user)
        except ObjectDoesNotExist:
            raise ValueError("Корзина не найдена")

        items = CartItem.objects.filter(cart_id=cart.id)
        if not items.exists():
            raise ValueError("Корзина пуста")

        total_price = sum(item.product.price * item.quantity for item in items)
        order = Order.objects.create(user=self.user, total_price=total_price)

        order_items = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_per_item=item.product.price
            )
            for item in items
        ]
        OrderItem.objects.bulk_create(order_items)
        items.delete()

        return order

class ApiOrderService:

    @staticmethod
    def create_order(user, cart_item_ids=None):
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise ValidationError("Корзина не найдена")

        cart_items = CartItem.objects.filter(cart=cart)

        if cart_item_ids:
            cart_items = cart_items.filter(id__in=cart_item_ids)
            if not cart_items.exists():
                raise ValidationError("Указанные товары не найдены в корзине")
        elif not cart_items.exists():
            raise ValidationError("Корзина пуста")

        with transaction.atomic():
            total = sum(item.product.price * item.quantity for item in cart_items)
            order = Order.objects.create(user=user, total_price=total)

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_per_item=item.product.price
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            cart_items.delete()

        return order
