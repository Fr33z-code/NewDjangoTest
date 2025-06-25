import json
from itertools import product

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cart.models import CartItem, Cart
from catalog.models import Product


@login_required
@csrf_exempt
def add_to_cart_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'error': 'No product id'})
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        product.count -= 1
        product.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_amount = sum(item.total_price() for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    return render(request, 'cart.html', context)


@login_required
def update_cart(request):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)

        for item in cart.items.all():
            new_quantity = request.POST.get(f'quantity_{item.id}')
            if new_quantity and new_quantity.isdigit():
                item.quantity = int(new_quantity)
                item.save()
        return redirect('cart')
    return None


@require_POST
@login_required
def update_cart_item(request):
    item_id = request.POST.get('item_id')
    quantity = request.POST.get('quantity')
    if not item_id or not quantity:
        return JsonResponse({'success': False, 'error': 'Недопустимые данные'})

    try:
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Неверное количество'})

    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product = item.product
    old_quantity = item.quantity
    delta = quantity - old_quantity
    if delta > 0 and product.count < delta:
        return JsonResponse({'success': False, 'error': 'Недостаточно товара на складе'})


    product.count -= delta
    product.save()
    item.quantity = quantity
    item.save()

    return JsonResponse({'success': True})


@login_required
def delete_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=product_id, cart=cart)
    product = get_object_or_404(Product, id=item.product_id)
    product.count += item.quantity
    product.save()
    item.delete()

    return redirect('view_cart')
