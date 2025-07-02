from django.views.generic import View
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponse
from orders.service import OrderService
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem


class CreateOrderView(View):
    def post(self, request, *args, **kwargs):
        service = OrderService(request.user)
        try:
            service.create_order_from_cart()
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
        return redirect('home')
