
from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from utils.exceptions import PubErrorCustom

from apps.order.models import Order
from auth.authentication import Authentication
from apps.order.serializers import OrderSerializer

class OrderAPIView(viewsets.ViewSet):

    def get_authenticators(self):
        return [auth() for auth in [Authentication]]

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def orderquery(self, request,*args,**kwargs):
        user = request.user
        trantype=self.request.query_params.get('trantype',None)
        if not trantype:
            raise PubErrorCustom("trantype是空!")

        if str(trantype) == '0' or str(trantype) == '1':
            orderfilter=Order.objects.filter(userid=user.userid, trantype=trantype).order_by('-updtime')
        elif str(trantype) == '2' :
            orderfilter = Order.objects.filter(userid=user.userid, status=2).order_by('-updtime')
        else:
            raise PubErrorCustom("trantype非法!")

        return {'data':OrderSerializer(orderfilter,many=True).data}

