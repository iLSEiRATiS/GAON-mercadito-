import mercadopago
from decimal import Decimal
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema

SESSION_KEY = 'cart'

def _get_cart(session):
    return session.get(SESSION_KEY) or {'items': {}}

class MPCreatePreferenceView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: dict, 400: dict})
    def post(self, request):
        cart = _get_cart(request.session)
        items = []
        for pid, it in cart['items'].items():
            title = it['name']
            qty = int(it['qty'])
            price = float(Decimal(str(it['price'])))
            if qty <= 0:
                continue
            items.append({
                'title': title,
                'quantity': qty,
                'currency_id': 'ARS',
                'unit_price': price
            })
        if not items:
            return Response({'detail': 'Carrito vacío'}, status=status.HTTP_400_BAD_REQUEST)

        mp = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
        back_base = 'http://127.0.0.1:8000/payments'
        preference_data = {
            'items': items,
            'back_urls': {
                'success': f'{back_base}/success/',
                'failure': f'{back_base}/failure/',
                'pending': f'{back_base}/pending/'
            },
            'auto_return': 'approved'
        }
        pref = mp.preference().create(preference_data)
        body = pref.get('response', {})
        return Response({
            'id': body.get('id'),
            'init_point': body.get('init_point'),
            'sandbox_init_point': body.get('sandbox_init_point')
        })
