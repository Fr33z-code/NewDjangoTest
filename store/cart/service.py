from catalog.models import Product
from cart.models import Cart, CartItem
from core.BaseService import BaseService
from django.shortcuts import get_object_or_404
from django.db import transaction


class CartService(BaseService):
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

    @staticmethod
    def add_product_to_cart(user, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return False, 'Product not found'

        if product.count <= 0:
            return False, 'Товара нет в наличии'

        cart = Cart.objects.get_or_create(user=user)[0]
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        product.count -= 1
        product.save()
        return True, None

class ApiCartService(BaseService):
    def add_product_to_cart(self, user, product_id, quantity):
        if not product_id:
            raise ValidationError("product_id обязателен")

        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        available = product.count + (cart_item.quantity if not created else 0)
        requested_total = (cart_item.quantity + quantity) if not created else quantity

        if requested_total > available:
            raise ValidationError(
                f"Недостаточно товара. Доступно: {available - (cart_item.quantity if not created else 0)}")

        cart_item.quantity = requested_total
        cart_item.save()

        product.count = available - requested_total
        product.save()

        return cart_item

    def update_cart_item(user, product_id, quantity):
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except ValueError:
            raise ValidationError("Количество должно быть положительным числом")

        with transaction.atomic():
            item = get_object_or_404(
                CartItem.objects.select_for_update(),
                product_id=product_id,
                cart__user=user
            )
            product = Product.objects.select_for_update().get(id=product_id)

            delta = quantity - item.quantity

            if delta > 0:
                available = product.count
                if delta > available:
                    raise ValidationError(f"Недостаточно товара на складе. Доступно: {available}")
                product.count -= delta
                item.quantity = quantity

            elif delta < 0:
                returned = abs(delta)
                if product.count + returned > product.initial_count:
                    returned = product.initial_count - product.count
                    item.quantity -= returned
                else:
                    item.quantity = quantity
                product.count += returned

            product.save()
            item.save()

        return item, product.count

    def delete_cart_item(user, product_id):
        with transaction.atomic():
            item = get_object_or_404(
                CartItem.objects.select_for_update(),
                product_id=product_id,
                cart__user=user
            )
            product = Product.objects.select_for_update().get(id=product_id)

            returned = item.quantity
            new_count = product.count + returned

            if new_count > product.initial_count:
                product.count = product.initial_count
            else:
                product.count = new_count

            product.save()
            item.delete()

        return product.count
