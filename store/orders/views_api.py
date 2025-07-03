from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import Order, OrderItem
from .serializers import RequestOrderSerializer
from cart.models import Cart, CartItem
from orders.service import ApiOrderService


@method_decorator(name='post', decorator=swagger_auto_schema(tags=['Order']))
class OrderViewSet(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestOrderSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        cart_item_ids = request.data.get('cart_item_ids', [])

        try:
            order = ApiOrderService.create_order(user=user, cart_item_ids=cart_item_ids)
        except ValidationError as e:
            return Response({"detail": str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
