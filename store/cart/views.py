import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from cart.models import CartItem, Cart
from catalog.models import Product
from rest_framework import generics
from django.views import View
from rest_framework.permissions import IsAuthenticated
from cart.service import CartService
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.mixins import LoginRequiredMixin


class CartUpdateView(generics.GenericAPIView):
    permission_classes = []
    request_serializer_class = ''
    serializer_class = ''

    def post(self):
        pass


# class AddToCartAjaxView(View):
#     def post(self, request, *args, **kwargs):
#         try:
#             data = json.loads(request.body)
#             product_id = data.get('product_id')
#             if not product_id:
#                 return JsonResponse({'success': False, 'error': 'No product id'})
#
#             service = CartService()
#             service.add_product_to_cart(request.user, product_id)
#
#             return JsonResponse({'success': True})
#
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)})
@login_required
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


class CartView(View):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = CartService.get_or_create_cart(request.user)
        cart_items = CartService.get_cart_items(cart)
        total_amount = CartService.calculate_total_amount(cart_items)
        context = {
            'cart_items': cart_items,
            'total_amount': total_amount,
        }
        return render(request, 'cart.html', context)


class UpdateCartView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = CartService.get_or_create_cart(request.user)
        CartService.update_cart_items(cart, request.POST)
        return redirect('cart')


class UpdateCartItemView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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

        success, error = CartService.update_cart_item(request.user, item_id, quantity)
        if not success:
            return JsonResponse({'success': False, 'error': error})

        return JsonResponse({'success': True})


class DeleteFromCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        CartService.delete_item_from_cart(request.user, item_id)
        return redirect('view_cart')
