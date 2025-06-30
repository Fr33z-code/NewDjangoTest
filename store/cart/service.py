from catalog.models import Product
from cart.models import Cart, CartItem
from core.BaseService import BaseService
from django.shortcuts import get_object_or_404

class CartService(BaseService):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_or_create_cart(user):
        return Cart.objects.get_or_create(user=user)[0]

    @staticmethod
    def get_cart_items(cart):
        return CartItem.objects.filter(cart=cart)

    @staticmethod
    def calculate_total_amount(cart_items):
        return sum(item.total_price() for item in cart_items)

    @staticmethod
    def update_cart_items(cart, data):
        for item in cart.items.all():
            new_quantity = data.get(f'quantity_{item.id}')
            if new_quantity and new_quantity.isdigit():
                item.quantity = int(new_quantity)
                item.save()

    @staticmethod
    def update_cart_item(user, item_id, quantity):
        item = get_object_or_404(CartItem, id=item_id, cart__user=user)
        product = item.product
        old_quantity = item.quantity
        delta = quantity - old_quantity
        if delta > 0 and product.count < delta:
            return False, 'Недостаточно товара на складе'

        product.count -= delta
        product.save()
        item.quantity = quantity
        item.save()
        return True, None

    @staticmethod
    def delete_item_from_cart(user, item_id):
        cart = get_object_or_404(Cart, user=user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product = item.product
        product.count += item.quantity
        product.save()
        item.delete()
