from django.shortcuts import redirect

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem


def create_order_for_user(request):
    cart = Cart.objects.get(user_id=request.user)
    items = CartItem.objects.filter(cart_id=cart.id)
    if not items.exists():
        raise ValueError("Корзина пуста")
    order = Order.objects.create(
        user=request.user,
        total_price=sum(item.product.price * item.quantity for item in items)
    )
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price_per_item=item.product.price
        )
    items.delete()
    return redirect('home')