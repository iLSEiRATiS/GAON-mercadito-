from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema
from products.models import Product
from .serializers import (
    AddItemSerializer,
    UpdateItemSerializer,
    RemoveItemSerializer,
    CartSerializer
)

SESSION_KEY = 'cart'

def _get_cart(session):
    cart = session.get(SESSION_KEY) or {'items': {}}
    return cart

def _save_cart(session, cart):
    session[SESSION_KEY] = cart
    session.modified = True

def _to_number(x):
    try:
        if isinstance(x, Decimal):
            return float(x)
        return float(Decimal(str(x)))
    except Exception:
        return 0.0

def _serialize_cart(cart):
    items = []
    total_qty = 0
    total_price = Decimal('0')
    for pid, data in cart['items'].items():
        price = Decimal(str(data['price']))
        qty = int(data['qty'])
        subtotal = price * qty
        items.append({
            'product_id': int(pid),
            'name': data['name'],
            'price': _to_number(price),
            'image': data.get('image'),
            'qty': qty,
            'subtotal': _to_number(subtotal)
        })
        total_qty += qty
        total_price += subtotal
    return {
        'items': items,
        'total_qty': total_qty,
        'total_price': _to_number(total_price)
    }

class CartDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: CartSerializer})
    def get(self, request):
        cart = _get_cart(request.session)
        return Response(_serialize_cart(cart))

class CartAddView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=AddItemSerializer, responses={200: CartSerializer, 400: dict})
    def post(self, request):
        ser = AddItemSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, pk=ser.validated_data['product_id'], activo=True)
        qty = ser.validated_data['qty']
        cart = _get_cart(request.session)
        key = str(product.id)
        prev = cart['items'].get(key, {'qty': 0})
        image_url = product.imagen.url if product.imagen else None
        cart['items'][key] = {
            'name': product.nombre,
            'price': _to_number(product.precio),
            'image': image_url,
            'qty': int(prev['qty']) + int(qty)
        }
        _save_cart(request.session, cart)
        return Response(_serialize_cart(cart))

class CartUpdateView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=UpdateItemSerializer, responses={200: CartSerializer, 400: dict})
    def post(self, request):
        ser = UpdateItemSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        pid = str(ser.validated_data['product_id'])
        qty = int(ser.validated_data['qty'])
        cart = _get_cart(request.session)
        if pid not in cart['items']:
            return Response({'detail': 'Item no existe'}, status=status.HTTP_400_BAD_REQUEST)
        if qty <= 0:
            cart['items'].pop(pid, None)
        else:
            item = cart['items'][pid]
            item['qty'] = qty
            cart['items'][pid] = item
        _save_cart(request.session, cart)
        return Response(_serialize_cart(cart))

class CartRemoveView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=RemoveItemSerializer, responses={200: CartSerializer, 400: dict})
    def post(self, request):
        ser = RemoveItemSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        pid = str(ser.validated_data['product_id'])
        cart = _get_cart(request.session)
        cart['items'].pop(pid, None)
        _save_cart(request.session, cart)
        return Response(_serialize_cart(cart))

class CartClearView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=None, responses={200: CartSerializer})
    def post(self, request):
        cart = {'items': {}}
        _save_cart(request.session, cart)
        return Response(_serialize_cart(cart))

class CartCheckoutView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=None, responses={200: CartSerializer})
    def post(self, request):
        cart = _get_cart(request.session)
        return Response(_serialize_cart(cart))
