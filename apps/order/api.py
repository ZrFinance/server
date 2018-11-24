
from rest_framework import viewsets
from rest_framework.decorators import list_route
from core.decorator.response import Core_connector
from utils.exceptions import PubErrorCustom

from apps.order.models import Order,Tranlist
from auth.authentication import Authentication
from apps.order.serializers import OrderSerializer

from apps.public.models import SysParam

from apps.utils import GenericViewSetCustom
from apps.public.utils import daysqbzcount

from apps.user.models import Agent,Users

class OrderAPIView(GenericViewSetCustom):

    def get_authenticators(self):
        return [auth() for auth in [Authentication]]

    @list_route(methods=['GET'])
    @Core_connector(pagination=True)
    def orderquery(self, request,*args,**kwargs):
        user = request.user
        trantype=self.request.query_params.get('trantype',None)
        status=self.request.query_params.get('status',None)

        if not trantype:
            raise PubErrorCustom("trantype是空!")

        if str(trantype) == '0' or str(trantype) == '1':
            orderfilter = Order.objects.filter(userid=user.userid, trantype=trantype,status__in=[0,1],umark=0).order_by('-confirmtime','-matchtime','-createtime')
        elif str(trantype) == '2' :
            orderfilter = Order.objects.filter(userid=user.userid, status=2,umark=0).order_by('-confirmtime')
        else:
            raise PubErrorCustom("trantype非法!")

        return {'data':OrderSerializer(orderfilter,many=True).data}

    @list_route(methods=['POST'])
    @Core_connector(transaction=True)
    def orderadd(self,request,*args,**kwargs):
        user = request.user
        sysparam=SysParam.objects.get()

        if user.pay_passwd != request.data.get('pay_passwd'):
            raise PubErrorCustom('二级密码错误！')

        if daysqbzcount(user.userid,sysparam):
            raise PubErrorCustom("当天申请帮助次数已超！")


        if request.data.get('defaultValue')=='gffh':
            if int(request.data.get('amount')) < sysparam.amount1 :
                raise PubErrorCustom('小于最低额%d'%(sysparam.amount1))
            if int(request.data.get('amount')) % sysparam.amount2 > 0:
                raise PubErrorCustom('必须为%d倍数'%(sysparam.amount2))
            if user.bonus < int(request.data.get('amount')):
                raise PubErrorCustom("股份分红余额不足")
            type=2
            trantype=12
        else:
            if int(request.data.get('amount')) < sysparam.amount4 :
                raise PubErrorCustom('小于最低额%d'%(sysparam.amount4))
            if int(request.data.get('amount')) % sysparam.amount5 > 0:
                raise PubErrorCustom('必须为%d倍数'%(sysparam.amount5))
            if user.spread < int(request.data.get('amount')):
                raise  PubErrorCustom('推广股权余额不足')

            #必须满足推荐人才能提取，1代2个提50%,2代4个提100%(必须满足1代)
            oneagent=Agent.objects.filter(mobile=user.mobile,level=1)
            oneagentcount=0
            for item in oneagent:
                t=Order.objects.raw("""
                    SELECT * FROM `order` as t1
                    INNER JOIN user as t2 on t1.userid=t2.userid
                    where t1.trantype='0' and t1.umark='0' and t1.status='2' and t2.umark='0' and t2.mobile='%s'
                """,[item.mobile1])
                if len(t)>0:
                    oneagentcount+=1

            twoagent=Agent.objects.filter(mobile=user.mobile,level=2)
            twoagentcount=0

            for item in twoagent:
                t=Order.objects.raw("""
                    SELECT * FROM `order` as t1
                    INNER JOIN user as t2 on t1.userid=t2.userid
                    where t1.trantype='0' and t1.umark='0' and t1.status='2' and t2.umark='0' and t2.mobile='%s'
                """,[item.mobile1])
                if len(t)>0:
                    twoagentcount+=1
            if oneagentcount>=2 and twoagentcount>=4:
                pass
                #提取全部
            else:
                if int(request.data.get('amount')) > user.spread / 2.0:
                    raise PubErrorCustom("满足一代2人,二代4人能提取100%,否则提取50%")

            if user.integral <= 100:
                if int(request.data.get('amount')) > 500:
                    raise PubErrorCustom('诚心值积分不够！')
            elif user.integral <= 300:
                if int(request.data.get('amount')) > 1000:
                    raise PubErrorCustom('诚心值积分不够！')
            elif user.integral <= 600:
                if int(request.data.get('amount')) > 2000:
                    raise PubErrorCustom('诚心值积分不够！')
            elif user.integral <= 1000:
                if int(request.data.get('amount')) > 3000:
                    raise PubErrorCustom('诚心值积分不够！')
            type=1
            trantype=11
        Order.objects.create(
            trantype=1,
            subtrantype=type,
            amount=request.data.get('amount'),
            userid=user.userid,
            username=user.username,
            status=0
        )

        if trantype==12:
            Tranlist.objects.create(
                trantype=trantype,
                userid=user.userid,
                username=user.username,
                bal=user.bonus,
                amount=int(request.data.get('amount'))*-1
            )
            user.bonus -= int(request.data.get('amount'))
        else:
            Tranlist.objects.create(
                trantype=trantype,
                userid=user.userid,
                username=user.username,
                bal=user.spread,
                amount=int(request.data.get('amount'))*-1
            )
            user.spread -= int(request.data.get('amount'))
        user.save()
        return None
