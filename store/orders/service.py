from core.BaseService import BaseService
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist


class OrderService(BaseService):
    def __init__(self, user):
        super().__init__()
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
